from flask import Flask
from flask_sqlalchemy import SQLAlchemy

class Config:
    app = Flask(__name__)

    # Nombre de la página
    page_name = 'SONK'

    # Configuración de la base de datos MySQL
    DB_USER = 'root'
    DB_PASSWORD = ''
    DB_HOST = '127.0.0.1'
    DB_NAME = 'api_crud'

    # Credentials Email
    email_sender = ''
    email_password = '' # 2FA https://www.youtube.com/watch?v=g_j6ILT-X0k

    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 10  # Tiempo de espera en segundos
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db = SQLAlchemy(app)