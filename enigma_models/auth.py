from hashlib import scrypt
from os import urandom

def get_hash(to_hash: str) -> bytes:
    salt = urandom(32)
    return scrypt(
        to_hash.encode('utf-8'),
        salt=salt,
        n=16384,
        r=8,
        p=1
    ) + salt

def get_hash_from_salt(to_hash: str, salt: bytes) -> bytes:
    return scrypt(
        to_hash.encode('utf-8'),
        salt=salt,
        n=16384,
        r=8,
        p=1
    )

def get_hash_from_salted_hash(from_hash: bytes) -> tuple:
    return from_hash[:-32], from_hash[-32:]

def verify_hash(plain_pw: str, hashed_pw: bytes) -> bool:
    split_hash = get_hash_from_salted_hash(hashed_pw)
    return get_hash_from_salt(plain_pw, split_hash[1]) == split_hash[0]