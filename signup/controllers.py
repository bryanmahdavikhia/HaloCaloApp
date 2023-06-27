import hashlib
from uploadBarang import models as ub_md

def encrypt_password(password):
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    return hashed_password

def decrypt_password(user, password):
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    return (hashed_password == user.password)