###################################################
# Credlist class
# Holds a credlist and its name

class Credlist():
    
    def __init__(self, name: str, creds: dict):
        self.name = name
        self.creds = creds

    def __repr__(self):
        return '<{}> named {} with creds {}'.format(type(self).__name__, self.name, self.creds)

    def __eq__(self, obj):
        if isinstance(obj, Credlist):
            if self.name == obj.name and self.creds == obj.creds:
                return True
        return False

    @classmethod
    def new(cls, data: dict):
        return cls(
            name = data['name'],
            creds = data['creds']
        )