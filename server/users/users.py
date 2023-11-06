from config import Config

from hashlib import sha256
from re import match

# Send mail
from smtplib import SMTP_SSL
from ssl import create_default_context
from email.message import EmailMessage

email_sender = Config.email_sender
email_password  = Config.email_password
app = Config.app
db = Config.db

# Modelo de datos para la tabla users
class Users(db.Model):
    iduser = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    fsurname = db.Column(db.String(100), nullable=False)
    ssurname = db.Column(db.String(100))
    birthdate = db.Column(db.Date, nullable=False)
    permissions = db.Column(db.Enum('user', 'admin'), nullable=False, default='user')
    email = db.Column(db.String(100), nullable=False, unique=True)
    passwd = db.Column(db.String(64), nullable=False)
    code = db.Column(db.Integer)
    active = db.Column(db.Boolean, nullable=False, default=False)

class ActionsUsers:
    def get_sha256(string:str):
        # Codifica el string en bytes antes de calcular el hash
        bytes_string = string.encode('utf-8')

        # Crea un objeto de hash SHA-256
        sha256_obj = sha256()

        # Actualiza el objeto de hash con los bytes del string
        sha256_obj.update(bytes_string)

        # Obtiene el hash en formato hexadecimal
        hash_hexadecimal = sha256_obj.hexdigest()

        return str(hash_hexadecimal)

    def check_email(email:str):
        # Patrón de expresión regular para validar el formato del correo electrónico
        patron_correo = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        # Utiliza el método match de re para verificar si el correo coincide con el patrón
        if match(patron_correo, email):
            return True
        else:
            return False
        
    def check_format_date(fecha:str):
        # Define el patrón de la expresión regular para el formato "DD/MM/YYYY"
        patron = r'^\d{2}/\d{2}/\d{4}$'

        # Utiliza el método match de re para verificar si la fecha coincide con el patrón
        if match(patron, fecha):
            dia = int(fecha.split('/')[0])
            mes = int(fecha.split('/')[1])
            year = int(fecha.split('/')[2])

            # Comprobar que es válido cada apartado
            if dia > 0 and dia <= 31 and mes > 0 and mes <= 12 and year > 1900 and year <= 2022:
                return True
            else:
                return False
        else:
            return False
        
    # Envia emails con la cuenta de correo configurada
    def send_mail(subject:str, body:str, email_receiver:str):
        try:
            em = EmailMessage()
            em['From'] = email_sender
            em['To'] = email_receiver
            em['Subject'] = subject
            em.set_content(body)

            # Add SSL (layer of security)
            context = create_default_context()

            # Log in and send the email
            with SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, em.as_string())
            return True
        except Exception:
            return False