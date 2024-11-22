import tomllib, random, csv, json
from os.path import join, splitext
import logging

import plotly.express as px
import pandas as pd

from enigma.checks import *
from enigma.models import Team, TeamCreds, ScoreReport, SLAReport, ScoreHistory, InjectReport
from enigma.settings import boxes_path, points_info, possible_services, injects_path

log = logging.getLogger(__name__)

# Class Box
# Represents a box and its services
class Box():

    def __init__(self, name: str, identifier: int, services: list[Service]):
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
    def full_service_list(cls, boxes: list):
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
                cls.compile_services(data)
                )
        except:
            log.critical('{} is not configured correctly'.format(path))
            raise SystemExit(0)
        log.debug('created a Box named {}'.format(splitext(path)[0].lower()))
        return box

# Class ScoreBreakdown
# A class to store every single scoring option
# A central place to store and reveal scores
# Does not track score history, those are in the ScoreReport records
class ScoreBreakdown():

    def __init__(self, team: int, services: list[str], service_points: int, sla_points: int):
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
        filepath = join(path, f'{name}.csv')
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

            for cat in sorted(self.scores.keys()):
                row = {
                    fieldnames[0]: cat,
                    fieldnames[1]: self.scores.get(cat),
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
        log.debug('created a ScoreBreakdown for team {}'.format(team))
        return cls(
            team,
            services,
            points_info['check_points'],
            points_info['sla_penalty']
        )

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
        score_reports = db_session.query(ScoreReport).filter(ScoreReport.team_id == self.id).all()

        # Dump all of the score report data here because the db_session keeps timing out
        pertinent_info = list()
        for report in score_reports:
            pertinent_info.append({
                'service': report.service,
                'result': report.result
            })

        db_session.close()

        # Delete all ScoreReport records because it gets too heavy to store everything indefinitely
        db_session.query(ScoreReport).delete()
        db_session.commit()
        db_session.close()

        # Service check tabulation
        log.debug('score reports found')
        for report in pertinent_info:
            if report.get('result'):
                # Service check is successful, awards points

                log.info('awarding service points to team {} for service {}'.format(self.id, report.get('service')))
                self.scores.award_service_points(report.get('service'))
                if report.get('service') in self.sla_tracker:
                    self.sla_tracker.pop(report.get('service'))
            else:
                # Service check is unsuccessful, checking if there is an SLA violation

                if report.get('service') not in self.sla_tracker.keys():
                    # No previous SLA violation tracking, adding service to tracker

                    log.info('starting to track team {} SLA violation for service {}, 1 of {}'.format(
                        self.id, 
                        report.get('service'),
                        points_info.get('sla_requirement')
                        ))
                    self.sla_tracker.update({
                        report.get('service'): 1
                    })
                else:
                    # Previous SLA violating tracking is found, determining if SLA threshold is met

                    if self.sla_tracker.get(report.get('service')) == points_info.get('sla_requirement') - 1:
                        # Full SLA violation, creating SLA report and deducting points

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
                        # Threshold not met, extending SLA tracker

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

        # Inject tabulation
        inject_reports = db_session.query(InjectReport).filter(InjectReport.team_id == self.id).all()
        for inject in inject_reports:
            self.scores.award_inject_points(inject.inject_num, inject.score)

        # Publish score report
        db_session.add(
            ScoreHistory(
                team_id = self.id,
                round = round,
                score = self.scores.total_score
            )
        )
        db_session.commit()
        db_session.close()

        log.debug('completed score tabulation for team {} for round {}'.format(self.id, round))

    # Creates a graph based on score history
    # TODO: fix the rows and columns being completely swapped
    @classmethod
    def graph_scores(cls, managers: dict):
        log.debug('graphing scores')
        data = dict()
        row_names = list()
        team_nums = list()

        for team in managers.keys():
            row_names.append(
                db_session.get(Team, team).username
            )
            db_session.close()
            team_nums.append(team)

        last_round = max(db_session.query(ScoreHistory.round).order_by(ScoreHistory.round).all())[0]

        for round in range(1, last_round + 1):
            round_data = list()
            for team in team_nums:
                round_data.append(
                    db_session.query(ScoreHistory.score).filter(ScoreHistory.team_id == team, ScoreHistory.round == round).first()[0]
                )
                db_session.close()
            data.update({
                round: round_data
            })

        print(data)
        df = pd.DataFrame(data, row_names)
        plot = px.line(df)
        print(df)
        plot.show()

    # Methods related to creds

    # Returns a dict with all of the creds
    # Mostly used for debugging
    def get_all_creds(self) -> dict:
        log.debug('getting a dict of all creds for team {}'.format(self.id))
        data = db_session.query(TeamCreds).filter(TeamCreds.team_id == self.id).all()
        credslist = dict()
        for creds in data:
            credslist.update({
                creds.name: json.loads(creds.creds)
            })
        return credslist

    # Adds a new credslist
    def add_creds(self, credslist: dict):
        log.debug('adding new credslist for team {}'.format(self.id))
        db_session.add(
            TeamCreds(
                name = credslist.items()[0].keys()[0],
                team_id = self.id,
                creds = credslist.items()[0].keys()[1]
            )
        )
        db_session.commit()
        db_session.close()

    # Returns a random user and password for use in service check
    # Parameter credlists is a list of names of the credlists to choose from
    def get_random_cred(self, credlists: list[str]) -> dict:
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

    # Creates a new TeamManager from the config info
    @classmethod
    def new(cls, id: int, services: list, cred_data: dict):
        log.debug('created new TeamManager for team {}'.format(id))
        return cls(
            id,
            ScoreBreakdown.new(
                id,
                services
            ),
            cred_data.copy()
        )
    
# Class Inject
# Represents an inject
class Inject():
    
    def __init__(self, id: int, name: str, desc: str, worth: int, path: str, rubric: dict):
        self.id = id
        self.name = name
        self.desc = desc
        self.worth = worth
        self.path = path
        self.rubric = rubric
        self.breakdown = self.calculate_score_breakdown()

    def __repr__(self):
        return '<{}> with id {} and name {}'.format(type(self).__name__, self.id, self.name)

    # Calculates the corresponding scores for each scoring category and scoring option
    def calculate_score_breakdown(self):
        breakdown = dict()
        for key in self.rubric.keys():
            weight = self.worth * self.rubric[key]['weight']
            base_cat_score = weight / (len(self.rubric[key]['categories']) - 1)
            possible_cat_scores = dict()
            for i in range(0, len(self.rubric[key]['categories'].keys())):\
                possible_cat_scores.update({
                    list(self.rubric[key]['categories'].keys())[i]: base_cat_score * i
                })
            breakdown.update({
                key: possible_cat_scores
            })
        return breakdown
    
    # Calculates the score of an inject and creates a record
    # scores should be in the format {scoring category: score}
    # where 'score' is a str, see the example inject
    # If the record already exists, update the score
    def score_inject(self, team_id: int, scores: dict):
        score = 0
        for cat in self.breakdown.keys():
            score = score + self.breakdown.get(cat).get(scores.get(cat))

        inject_report = db_session.query(InjectReport).filter(
            InjectReport.team_id == team_id,
            InjectReport.inject_num == self.id
            ).first()
        if inject_report is None:
            db_session.add(
                InjectReport(
                    team_id = team_id,
                    inject_num = self.id,
                    score = score
                )
            )
        else:
            inject_report.score = score
        db_session.commit()
        db_session.close()

    # Creates a new Inject based on the config info
    @classmethod
    def new(cls, path: str):
        with open(join(injects_path, path), 'rb') as f:
            data = tomllib.load(f)
        try:
            rubric = dict()
            for cat in data['rubric']:
                rubric.update(cat)
            inject = cls(
                int(splitext(path)[0].lower()[-1]),
                data['name'],
                data['description'],
                data['worth'],
                data['path'],
                rubric
            )
        except:
            log.critical('{} is not configured correctly'.format(path))
            raise SystemExit(0)
        log.debug('created an Inject with name {}'.format(data['name']))
        return inject

# Class InjectManager
# Keeps track of all injects
class InjectManager():

    def __init__(self):
        pass

    def add_inject(self):
        pass

    def remove_inject(self):
        pass