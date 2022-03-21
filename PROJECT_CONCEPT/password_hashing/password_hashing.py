"""
source: https://medium.com/python-in-plain-english/store-passwords-safely-in-python-e38a8c0c8618
source: https://hackernoon.com/hashing-passwords-in-python-bcrypt-tutorial-with-examples-77dh36ef
"""
import bcrypt


class PasswordDatabase:
    def __init__(self):
        self.data = dict()

    def register(self, user, password):
        if user in self.data:
            return False
        pwd_hash = self.hash_password(password)
        self.data[user] = pwd_hash
        return True

    def hash_password(self, password):
        """
        A salt is a random string of data hashed alongside a password to keep the hash result unique.
        Salts should be recreated each time a new password is saved, and the salt is stored alongside
        the hashed result so that it can be used again for comparison. Libraries like bcrypt are smart
        enough to store the salt IN the resulting string so that developers don’t need to do the extra work.
        """
        pwd_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt)

    def login_check(self, user, password):
        if user not in self.data:
            return False
        pwd_bytes = password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, self.data[user])


if __name__ == '__main__':
    db = PasswordDatabase()
    print("Registering users".center(45, '-'))
    print(db.register("john", "password"))
    print(db.register("Seth", "HelloWorld"))
    print(db.register("john", "new_password"))
    print(" Example 1: Login Check ".center(45, '-'))
    print(db.login_check("abc", "password"))
    print(db.login_check("john", "pwd"))
    print(db.login_check("john", "password"))

    print(f"{db.hash_password('password') = }")
    salt = bcrypt.gensalt()
    print(f'{salt = }')

    print(" Example 2: hash mechanics ".center(45, '-'))
    plain_pw = 'userPlainTextPassword'.encode('utf-8')
    print(f'{plain_pw = }')
    salt = bcrypt.gensalt()
    print(f'{salt = }')
    hashAndSalt = bcrypt.hashpw(plain_pw, salt)
    print(f'{hashAndSalt = }')

    # Check the hashed password:
    # password = userInput
    valid = bcrypt.checkpw(plain_pw, hashAndSalt)
    print(f'Check if hashAndSalt matches the encoded plain_pw: {valid}')
