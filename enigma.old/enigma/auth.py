import hashlib, os
import logging

log = logging.getLogger('enigma')

# PWHash class
# A class to hold password hashes for verification.
# One can do 'pwexample' == hashpwvar for PW comparisons
# Uses the scrypt algorithm for hashing with a salt of length 32

class PWHash():
    
    def __init__(self, hash_, salt_):
        assert len(hash_) == 64
        if isinstance(hash_, str):
            self.hash = hash_.encode('utf-8')
        else:
            self.hash = hash_
        if isinstance(salt_, str):
            self.salt = salt_.encode('utf-8')
        else:
            self.salt = salt_
    
    def __eq__(self, candidate):
        if isinstance(candidate, str):
                candidate = candidate.encode('utf-8')
        return hashlib.scrypt(candidate, salt=self.salt, n=16384, r=8, p=1) == self.hash
    
    def __repr__(self):
        return '<{}>'.format(type(self).__name__)
    
    def combined(self):
        return self.hash + self.salt
    
    @classmethod
    def new(cls, password, salt_=os.urandom(32)):
        if isinstance(password, str):
            password = password.encode('utf-8')
        log.debug('Created PWHash')
        return cls(hashlib.scrypt(password, salt=salt_, n=16384, r=8, p=1), salt_)