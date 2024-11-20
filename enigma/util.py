import tomllib, random, csv
from os import listdir
from os.path import isfile, join, splitext

from enigma.checks import *
from enigma.settings import boxes_path, creds_path

possible_services = Service.__subclasses__()

# Class Box
# Represents a box and its services
class Box():

    def __init__(self, name: str, identifier: int, services: list):
        self.name = name
        self.identifier = identifier
        self.services = services
    
    def __repr__(self):
        return '<{}> named \'{}\' with services {}'.format(type(self).__name__, self.name, self.services)

    # Takes a dict of service config data and creates new Service objects based off of them
    @classmethod
    def compile_services(cls, data: dict):
        services = list()
        for service in possible_services:
            if service.name in data:
                services.append(service.new(data[service.name]))
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
            raise RuntimeError(
                '{} is not configured correctly'.format(path)
            )
        return box

# Class CredList
# Represents a set of credentials for use in score checks
class CredList():

    def __init__(self, name: str, creds: dict):
        self.name = name
        self.creds = creds

    # Returns a random user and password
    def get_random_user(self):
        chosen = random.choice([self.creds.keys()])
        return {
            chosen: self.creds[chosen]
        }
    
    # Returns a random user and password but this time with additional options
    def get_random_user_addon(self, addon: dict):
        both = list()
        both.extend(self.creds.keys())
        both.extend(addon.keys())
        chosen = random.choice(both)
        if chosen in self.creds.keys():
            return {
                chosen: self.creds[chosen]
            }
        else:
            return {
                chosen: addon[chosen]
            }
    
    # Wrapper for dict.update() because i want to type CredList.pcr()
    def pcr(self, updated_creds: dict):
        self.creds.update(updated_creds)

    def __repr__(self):
        return '<{}> with name {} and {} creds'.format(type(self).__name__, self.name, len(self.creds.keys()))

    # Creates a new CredList from a CSV
    @classmethod
    def new(cls, path: str):
        with open(join(creds_path, path), 'r+') as f:
            data = csv.reader(f)
            creds = dict()
            for row in data:
                creds.update({row[0]: row[1]})
        return cls(splitext(path)[0].lower(), creds)

# Class ScoreBreakdown
# A class to store every single scoring option
# A central place to store and reveal scores
# Does not track score history, those are in the ScoreReport records
class ScoreBreakdown():

    def __init__(self, services: list, service_points: int, sla_points: int):
        self.total_score = 0
        self.raw_score = 0
        self.penalty_score = 0

        self.scores = dict.fromkeys(services, 0)
        self.penalty_scores = dict()

        self.service_points = service_points
        self.sla_points = sla_points

    # Updates total score
    def update_total(self):
        total = 0
        for service, points in self.scores.items():
            total = total + points
        self.raw_score = total

        total = 0
        for penalty, points in self.penalty_scores.items():
            total = total + points
        self.penalty_score = total

        self.total_score = self.raw_score - self.penalty_score

    # Service adding/removal
    def add_service(self, name: str):
        if name in self.scores.keys():
            raise RuntimeError(
                'Cannot add \'{}\' to score, already exists'.format(name)
            )
        self.scores.update({
            name: 0
        })

    def remove_service(self, name: str):
        if name not in self.scores.keys():
            raise RuntimeError(
                'Cannot remove \'{}\' from score, does not exist'.format(name)
            )
        self.scores.pop(name)
        self.update_total()

    # Point awarding
    def award_service_points(self, service: str):
        if service not in self.scores.keys():
            raise RuntimeError(
                'Service \'{}\' does not exist, cannot award points'.format(service)
            )
        self.scores.update({
            service: (self.scores.pop(service) + self.service_points)
        })
        self.update_total()

    def award_inject_points(self, inject_num: int, points: int):
        inject_str = f'inject{inject_num}'
        if inject_str in self.scores.keys():
            raise RuntimeError(
                'Cannot add inject {} to score, already exists'.format(inject_num)
            )
        self.scores.update({
            inject_str: points
        })
        self.update_total()
    
    def award_correction_points(self, points: int):
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