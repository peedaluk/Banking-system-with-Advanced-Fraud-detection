from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()
print(bcrypt.generate_password_hash('1234567').decode('utf-8'))
print(bcrypt.generate_password_hash('7636').decode('utf-8'))
