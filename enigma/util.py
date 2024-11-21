import tomllib, random, csv, json, uuid
from os import listdir
from os.path import isfile, join, splitext
import logging

from enigma.checks import *
from enigma.models import Team, TeamCreds, ScoreReport, SLAReport, ScoreHistory
from enigma.settings import boxes_path, creds_path, points_info, possible_services

log = logging.getLogger(__name__)

# Class Box
# Represents a box and its services
class Box():

    def __init__(self, name: str, identifier: int, services: list):
        self.name = name
        self.identifier = identifier
        self.services = services
    
    def __repr__(self):
        return '<{}> named \'{}\' with services {}'.format(type(self).__name__, self.name, self.services)

    # Get every service for the box in the format box.service
    def get_service_names(self):
        log.debug('getting service names for box {}'.format(self.name))
        names = list()
        for service in self.services:
            names.append(f'{self.name}.{service.name}')
        log.debug('service names found: {}'.format(names))
        return names

    # Takes a dict of service config data and creates new Service objects based off of them
    @classmethod
    def compile_services(cls, data: dict):
        log.debug('compiling a dict of Services')
        services = list()
        for service in possible_services:
            if service.name in data:
                services.append(service.new(data[service.name]))
        log.debug('services found: {}'.format(services))
        return services
    
    # Performs get_service_names() for every box in the list
    @classmethod
    def full_service_list(self, boxes: list):
        log.debug('getting a list of all service names')
        services = list()
        for box in boxes:
            services.extend(box.get_service_names())
        log.debug('all services found: {}'.format(services))
        return services

    # Creates a new Box object from a config file
    @classmethod
    def new(cls, path: str):
        with open(join(boxes_path, path), 'rb') as f:
            data = tomllib.load(f)
        try:
            box = cls(
                splitext(path)[0].lower(), 
                data['identifier'],
                cls.compile_services(data),
                )
        except:
            log.critical('{} is not configured correctly'.format(path))
            raise SystemExit(0)
        log.debug('created a Box')
        return box

# Class ScoreBreakdown
# A class to store every single scoring option
# A central place to store and reveal scores
# Does not track score history, those are in the ScoreReport records
class ScoreBreakdown():

    def __init__(self, team: int, services: list, service_points: int, sla_points: int):
        self.total_score = 0
        self.raw_score = 0
        self.penalty_score = 0

        self.scores = dict.fromkeys(services, 0)
        self.penalty_scores = dict()

        self.service_points = service_points
        self.sla_points = sla_points

        self.team = team

    def __repr__(self):
        return '<{}> object with a total score of {}'.format(type(self).__name__, self.total_score)

    # Updates total score
    def update_total(self):
        log.debug('recalculated score total for team {}'.format(self.team))
        total = 0
        for service, points in self.scores.items():
            total = total + points
        self.raw_score = total

        total = 0
        for penalty, points in self.penalty_scores.items():
            total = total + points
        self.penalty_score = total

        self.total_score = self.raw_score - self.penalty_score
        
        team = db_session.get(Team, self.team)
        team.score = self.total_score
        db_session.commit()
        db_session.close()
        log.debug('new total for team {} is {}'.format(self.team, self.total_score))

    # Service adding/removal
    def add_service(self, name: str):
        log.debug('adding service {} for team {}'.format(name, self.team))
        if name in self.scores.keys():
            log.error('cannot add \'{}\' to score, already exists'.format(name))
            return
        self.scores.update({
            name: 0
        })

    def remove_service(self, name: str):
        log.debug('removing service {} for team {}'.format(name, self.team))
        if name not in self.scores.keys():
            log.error('cannot remove \'{}\' from score, does not exist'.format(name))
            return
        self.scores.pop(name)
        self.update_total()

    # Point awarding
    def award_service_points(self, service: str):
        log.debug('awarding points for service {} for team {}'.format(service, self.team))
        if service not in self.scores.keys():
            log.error('service \'{}\' does not exist, cannot award points'.format(service))
            return
        self.scores.update({
            service: (self.scores.pop(service) + self.service_points)
        })
        self.update_total()

    def award_inject_points(self, inject_num: int, points: int):
        log.debug('awarding inject points for inject {} for team {}'.format(inject_num, self.team))
        inject_str = f'inject{inject_num}'
        if inject_str in self.scores.keys():
            log.error('cannot add inject {} to score, already exists'.format(inject_num))
            return
        self.scores.update({
            inject_str: points
        })
        self.update_total()
    
    def award_correction_points(self, points: int):
        log.debug('awarding correction of {} for team {}'.format(points, self.team))
        if 'correction' not in self.scores.keys():
            self.scores.update({
                'correction': points
            })
        else:
            self.scores.update({
                'correction': (self.scores.pop('correction') + points)
            })
        self.update_total()

    def award_misc_points(self, points: int):
        log.debug('awarding {} misc points for team {}'.format(points, self.team))
        if 'misc' not in self.scores.keys():
            self.scores.update({
                'misc': points
            })
        else:
            self.scores.update({
                'misc': (self.scores.pop('misc') + points)
            })
        self.update_total()
    
    # Point deductions
    def award_sla_penalty(self, service: str):
        log.debug('awarding sla penalty for service {} for team {}'.format(service, self.team))
        sla_str = f'sla-{service}'
        if sla_str not in self.penalty_scores.keys():
            self.penalty_scores.update({
                sla_str: self.sla_points
            })
        else:
            self.penalty_scores.update({
                sla_str: (self.penalty_scores.pop(sla_str) + self.sla_points)
            })
        self.update_total()

    def award_misc_penalty(self, points: int):
        log.debug('awarding misc penalty {} for service {} for team {}'.format(points, self.team))
        if 'misc' not in self.penalty_scores.keys():
            self.penalty_scores.update({
                'misc': points
            })
        else:
            self.penalty_scores.update({
                'misc': (self.penalty_scores.pop('misc') + points)
            })
        self.update_total()

    # Things to do with the data
    def export_csv(self, name: str, path: str):
        filepath = join(path, f'{name}-scores.csv')
        fieldnames = [
            'point_category',
            'raw_points',
            'penalty_points',
            'total_points'
        ]

        with open(filepath, 'w+', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerow({
                fieldnames[0]: 'total',
                fieldnames[1]: self.raw_score,
                fieldnames[2]: self.penalty_score,
                fieldnames[3]: self.total_score
            })
            
            rows = list()

            for cat, val in self.scores.items():
                row = {
                    fieldnames[0]: cat,
                    fieldnames[1]: val,
                    fieldnames[2]: 0,
                    fieldnames[3]: 0
                }
                rows.append(row)

            for cat, val in self.penalty_scores.items():
                pfield = cat.split('-')
                if len(pfield) == 2:
                    pfield = pfield[1]
                else:
                    pfield = pfield[0]

                for i in range(0, len(rows)):
                    if rows[i][fieldnames[0]] == pfield:
                        rows[i].update({
                            fieldnames[2]: val
                        })
            
            for i in range(0, len(rows)):
                rows[i].update({
                    fieldnames[3]: (rows[i][fieldnames[1]] - rows[i][fieldnames[2]])
                })

            for row in rows:
                writer.writerow(row)
        log.info('exported a score breakdown to {}'.format(filepath))

    # Creates a new ScoreBreakdown object from the config info
    @classmethod
    def new(cls, team: id, services: list):
        log.debug('created a ScoreBreakdown')
        return cls(
            team,
            services,
            points_info['check_points'],
            points_info['sla_penalty']
        )

# Class InjectManager
# Keeps track of injects and scores
class InjectManager():
    pass

# Class TeamManager
# Keeps a team's ScoreBreakdown and cred lists in one place
# Also interacts with the database for those things
class TeamManager():

    def __init__(self, id: int, sb: ScoreBreakdown, credlists: dict):
        self.id = id
        self.scores = sb
        self.sla_tracker = dict()

        for name, creds in credlists.items():
            db_session.add(
                TeamCreds(
                    name = name,
                    team_id = self.id,
                    creds = json.dumps(creds)
                )
            )
        db_session.commit()
        db_session.close()

    def __repr__(self):
        return '<{}> with team id {}, scores object {}, and credlist with {}'.format(
            type(self).__name__,
            self.id,
            self.scores,
            db_session.query(TeamCreds).filter(TeamCreds.team_id == self.id).all()
        )

    # Methods related to scores
    
    # Gathers all score reports for a round
    # This should be called at the end of every round
    def tabulate_scores(self, round: int):
        log.debug('tabulating scores for round {} for team {}'.format(round, self.id))
        score_reports = db_session.query(ScoreReport).filter(ScoreReport.round == round, ScoreReport.team_id == self.id).all()

        print(round)
        print(self.sla_tracker)

        pertinent_info = list()
        for report in score_reports:
            pertinent_info.append({
                'service': report.service,
                'result': report.result
            })

        db_session.close()

        log.debug('score reports found')
        for report in pertinent_info:
            if report.get('result'):
                log.info('awarding service points to team {} for service {}'.format(self.id, report.get('service')))
                self.scores.award_service_points(report.get('service'))
                if report.get('service') in self.sla_tracker:
                    self.sla_tracker.pop(report.get('service'))
            else:
                if report.get('service') not in self.sla_tracker.keys():
                    log.info('starting to track team {} SLA violation for service {}, 1 of {}'.format(
                        self.id, 
                        report.get('service'),
                        points_info.get('sla_requirement')
                        ))
                    self.sla_tracker.update({
                        report.get('service'): 1
                    })
                else:
                    if self.sla_tracker.get(report.get('service')) == points_info.get('sla_requirement') - 1:
                        log.info('full sla violation for team {} service {}, deducting points'.format(self.id, report.get('service')))
                        self.scores.award_sla_penalty(report.get('service'))
                        self.sla_tracker.pop(report.get('service'))
                        db_session.add(
                            SLAReport(
                                team_id = self.id,
                                round = round,
                                service = report.get('service')
                            )
                        )
                        db_session.commit()
                    else:
                        log.info('sla violation tracking extended for team {} service {}, {} of {}'.format(
                            self.id, 
                            report.get('service'),
                            self.sla_tracker.get(report.get('service')),
                            points_info.get('sla_requirement')
                            ))
                        self.sla_tracker.update({
                            report.get('service'): self.sla_tracker.pop(report.get('service')) + 1
                        })
        db_session.close()

        db_session.add(
            ScoreHistory(
                team_id = self.id,
                round = round,
                score = self.scores.total_score
            )
        )
        db_session.commit()
        db_session.close()

        print(self.sla_tracker)

        log.debug('completed score tabulation for team {} for round {}'.format(self.id, round))


    # Methods related to creds

    # Returns a dict with all of the creds
    # Mostly used for debugging
    def get_all_creds(self) -> dict:
        log.debug('getting a dict of all creds for team {}'.format(self.id))
        data = db_session.query(TeamCreds).filter(TeamCreds.team_id == self.id).all()
        credslist = dict()
        for creds in data:
            credslist.update({
                creds.name.split('-')[1]: json.loads(creds.creds)
            })
        return credslist

    # Returns a random user and password for use in service check
    # Parameter credlists is a list of names of the credlists to choose from
    def get_random_cred(self, credlists: list) -> dict:
        log.debug('choosing random user creds for team {}'.format(self.id))
        chosen_list = json.loads(
            db_session.query(TeamCreds).filter(
                TeamCreds.name == random.choice(credlists), 
                TeamCreds.team_id == self.id
                ).all()[0].creds)
        chosen = random.choice(list(chosen_list.items()))
        choice = {
            chosen[0]: chosen[1]
        }
        log.debug('chose {} for team {}'.format(choice, self.id))
        return choice

    # Performs a password change request
    # Parameter new_creds is a 2D dict, where the first key is the credlist name and the second is the user
    def pcr(self, new_creds: dict) -> None:
        log.debug('performing pcr request for team {}'.format(self.id))
        for credlist, creds in new_creds.items():
            team = db_session.query(TeamCreds).filter(TeamCreds.name == credlist, TeamCreds.team_id == self.id).all()[0]
            mod_creds = json.loads(team.creds)
            for user in creds.keys():
                if user not in mod_creds:
                    log.warning('User {} does not exist! Ignoring'.format(user))
                else:
                    mod_creds.update({
                        user: creds.get(user)
                    })
            team.creds = json.dumps(mod_creds)
            db_session.commit()

    @classmethod
    def new(cls, id: int, services: list, cred_data: dict):
        log.debug('created new TeamManager')
        return cls(
            id,
            ScoreBreakdown.new(
                id,
                services
            ),
            cred_data.copy()
        )