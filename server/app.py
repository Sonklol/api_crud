from flask import request, jsonify
from random import randint

from users.users import Users, ActionsUsers

# Config
from config import Config

page_name = Config.page_name
app = Config.app
db = Config.db

@app.route('/login', methods=['POST'])
def login():
    """
    Inicio de Sesión

    Args:
        email:str
        passwd:str no hashed

    Returns:
        FORMAT JSON
        {
            'access': True/False,
            'permissions': 'user'/admin
        }
    """

    data = request.get_json()

    email = str(data.get('email'))
    passwd = str(data.get('passwd'))
    
    # Comprobaciones
    # Comprobar que nos pasan parámetros
    if email and passwd:
        # Comprobar que es un correo
        if ActionsUsers.check_email(email):
            # Hash para comprobar con DB
            passwd = ActionsUsers.get_sha256(passwd)
            # Query correo y contraseña
            try:
                users = Users.query.filter_by(email=email, passwd=passwd).first()
            except:
                return jsonify({'access': False, 'error': "DB connection error."})
        
            # Comprobar que la cuenta esté activa
            if users.active == 0:
                # Generar código de verificación
                code = randint(000000, 999999)

                # Insertar en la base de datos
                try:
                    users.code = code
                    # Realizar el commit para guardar los cambios en la base de datos
                    db.session.commit()
                except:
                    db.session.rollback()
                    return jsonify({'access': False, 'error': "DB connection error."})

                # Envio de correo de verificación
                mail_title = f'Código de verificación de {page_name}: {str(code)}'
                mail_body = f'Estimado usuario de {page_name}:\n\nTe enviamos tu código de verificación para poder activar tu cuenta y así acceder a ella.\n\nTu código de verificación es: {str(code)}.\n\nNo reenvíes este correo electrónico ni des el código a nadie.\n\nAtentamente,\n\nEl Equipo de Cuentas de {page_name}.'
                if not ActionsUsers.send_mail(mail_title, mail_body, email):
                    return jsonify({'access': False, 'error': "Your account is unverified and there was a problem sending the verification email. Please try to resend the verification email."})
                
                return jsonify({'access': False, 'error': 'You must confirm the email we have sent you.'})
        else:
            return jsonify({'access': False, 'error': 'The email is not valid, enter a valid email.'})
    else:
        return jsonify({'access': False, 'error': 'No email/password provided.'})
    
    # Existencia en la base de datos
    if users:
        return jsonify({'access': True, 'permissions': users.permissions})
    else:
        return jsonify({'access': False})
    
@app.route('/register', methods=['POST'])
def register():
    """
    Registro

    Args:
        name:str

        fsurname:str
        ssurname:str

        birthdate:str (FORMAT 2023-07-11)

        email:str
        passwd:str
        passwd_2:str

    Returns:
        FORMAT JSON
        {
            'register': 'sucess/failed',
            'error': 'error
        }
    """

    data = request.get_json()

    name = str(data.get('name'))
    fsurname = str(data.get('fsurname'))
    ssurname = str(data.get('ssurname'))
    birthdate = str(data.get('birthdate'))

    email = str(data.get('email'))
    passwd = str(data.get('passwd'))
    passwd_2 = str(data.get('passwd_2'))

    # Comprobaciones
    # Comprobar que todos los valores están
    if name and fsurname and birthdate and email and passwd and passwd_2:
        # Comprobar que es un correo
        if ActionsUsers.check_email(email):
            # Comprobar que el email no exista ya
            try:
                users = Users.query.filter_by(email=email).first()
            except:
                return jsonify({'register': 'failed', 'error': "DB connection error."})
            if not users:
                # Comprobar que la contraseña sea igual a la de verificación
                if passwd == passwd_2:
                    # Comprobar validez y formato (DD/MM/YYYY) de fecha de nacimiento
                    if ActionsUsers.check_format_date(birthdate):
                        # Hash de contraseña
                        passwd = ActionsUsers.get_sha256(passwd)

                        # Cambiar formato a la fecha de nacimiento
                        dia = int(birthdate.split('/')[0])
                        mes = int(birthdate.split('/')[1])
                        year = int(birthdate.split('/')[2])
                        
                        birthdate = f'{str(year)}-{str(mes)}-{str(dia)}'
                    else:
                        return jsonify({'register': 'failed', 'error': "Wrong date of birth format."})
                else:
                    return jsonify({'register': 'failed', 'error': "Passwords aren't the same."})
            else:
                return jsonify({'register': 'failed', 'error': "You cannot register again with that email."})
        else:
            return jsonify({'register': 'failed', 'error': 'No email/password provided.'})
    else:
        return jsonify({'register': 'failed', 'error': "You must fill all the fields."})
    
    # Generar código de verificación
    code = randint(000000, 999999)
    # Comprobar que tiene segundo apellido
    if ssurname:
        # Añadir el segudo apellido
        adduser = Users(
            name=name,
            fsurname=fsurname,
            ssurname=ssurname,
            birthdate=birthdate,
            permissions='user',
            email=email,
            passwd=passwd,
            code=code
        )
    else:
        adduser = Users(
            name=name,
            fsurname=fsurname,
            birthdate=birthdate,
            permissions='user',
            email=email,
            passwd=passwd,
            code=code
        )
    
    try:
        db.session.add(adduser)
        db.session.commit()

        # Envio de correo de verificación
        mail_title = f'Código de verificación de {page_name}: {str(code)}'
        mail_body = f'Estimado usuario de {page_name}:\n\nTe enviamos tu código de verificación para poder activar tu cuenta y así acceder a ella.\n\nTu código de verificación es: {str(code)}.\n\nNo reenvíes este correo electrónico ni des el código a nadie.\n\nAtentamente,\n\nEl Equipo de Cuentas de {page_name}.'
        if not ActionsUsers.send_mail(mail_title, mail_body, email):
            return jsonify({'register': 'success', 'error': "The account has been created successfully but there was a problem sending the verification email. Please try to resend the verification email."})
        
        return jsonify({'register': 'success'})
    except:
        db.session.rollback()
        return jsonify({'register': 'failed', 'error': f"Connection problem while registering, please try again."})

@app.route('/get_users', methods=['POST'])
def get_users():
    
    data = request.get_json()

    email = str(data.get('email'))
    passwd = str(data.get('passwd'))

    # Comprobaciones
    # Comprobar que todos los valores están
    if email and passwd:
        if ActionsUsers.check_email(email):
            passwd = ActionsUsers.get_sha256(passwd)
            # Comprobar que el usuario y contraseña es correcto
            try:
                users = Users.query.filter_by(email=email, passwd=passwd).first()
            except:
                return jsonify({'access': 'failed', 'error': "DB connection error."})
            
            if users:
                # Comprobar si es admin
                if users.permissions != 'admin':
                    return jsonify({'access': 'failed', 'error': 'The user is not administrator.'})
            else:
                return jsonify({'access': 'failed', 'error': 'Invalid email/password.'})
        else:
            return jsonify({'access': 'failed', 'error': 'The email is not valid, enter a valid email.'})
    else:
        return jsonify({'access': 'failed', 'error': "You must fill all the fields."})
    
    # Consulta todos los usuarios de la tabla
    try:
        users = Users.query.all()
    except:
        return jsonify({'access': 'failed', 'error': "DB connection error."})

    lista_usuarios = []
    # Obtener de todos los usuarios en la query el formato json que quiero
    for usuario in users:
        datos_usuario = {
            #'iduser': usuario.iduser,
            'name': usuario.name,
            'fsurname': usuario.fsurname,
            'ssurname': usuario.ssurname,
            'birthdate': usuario.birthdate.strftime('%d/%m/%Y'),  # Formatea la fecha como string
            'permissions': usuario.permissions,
            'email': usuario.email,
            'passwd': usuario.passwd,
            'active': usuario.active
        }
        lista_usuarios.append(datos_usuario)

    # Retorna la lista de usuarios como una respuesta JSON
    return jsonify(lista_usuarios)

@app.route('/resend_mail', methods=['POST'])
def resend_mail():
    data = request.get_json()

    email = str(data.get('email'))
    
    # Comprobaciones
    # Comprobar que el email no esté vacío
    if email:
        try:
            users = Users.query.filter_by(email=email).first()
        except:
            return jsonify({'send_code': 'failed', 'error': "DB connection error."})
        
        # Comprobar que exista en la base de datos
        if users:
            # Comprobar que esté inactivo
            if users.active != 0:
                return jsonify({'send_code': 'failed', 'error': 'The user is already active. No need to verify.'})
        else:
            return jsonify({'send_code': 'failed', 'error': 'Invalid email/password.'})
    else:
        return jsonify({'send_code': 'failed', 'error': "No email provided."})

    # Generar código de verificación
    code = randint(000000, 999999)

    # Insertar en la base de datos
    try:
        users.code = code
        # Realizar el commit para guardar los cambios en la base de datos
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({'send_code': 'failed', 'error': "DB connection error."})

    # Envio de correo de verificación
    mail_title = f'Código de verificación de {page_name}: {str(code)}'
    mail_body = f'Estimado usuario de {page_name}:\n\nTe enviamos tu código de verificación para poder activar tu cuenta y así acceder a ella.\n\nTu código de verificación es: {str(code)}.\n\nNo reenvíes este correo electrónico ni des el código a nadie.\n\nAtentamente,\n\nEl Equipo de Cuentas de {page_name}.'
    if ActionsUsers.send_mail(mail_title, mail_body, email):
        return jsonify({'send_code': 'success'})
    else:
        return jsonify({'send_code': 'success', 'error': "The verification email could not be sent correctly."})

@app.route('/activate_user', methods=['POST'])
def activate_user():
    data = request.get_json()

    email = str(data.get('email'))
    code = str(data.get('code'))

    # Comprobaciones
    # Comprobar que el email no esté vacío
    if email and code:
        try:
            users = Users.query.filter_by(email=email, code=code).first()
        except:
            return jsonify({'activate': 'failed', 'error': "DB connection error."})
        
        # Comprobar que el correo tenga ese código
        if users:
            # Comprobar si el usuario tiene la cuenta habilitada
            if users.active != 0:
                return jsonify({'activate': 'failed', 'error': "The account is already activated."})
        else:
            return jsonify({'activate': 'failed'})
    else:
        return jsonify({'activate': 'failed', 'error': "The necessary data has not been provided."})
    

    try:
        # Actualizar el active en la DB para activar cuenta
        users.active = 1
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({'activate': 'failed', 'error': "DB connection error."})
    
    return jsonify({'activate': 'success'})

@app.route('/update_user', methods=['POST'])
def update_user():
    data = request.get_json()

    email = str(data.get('email'))
    passwd = ActionsUsers.get_sha256(str(data.get('passwd')))

    name_user = str(data.get('name_user'))
    fsurname_user = str(data.get('fsurname_user'))
    ssurname_user = str(data.get('ssurname_user'))
    birthdate_user = str(data.get('birthdate_user'))
    permissions_user = str(data.get('permissions_user'))
    email_user = str(data.get('email_user'))
    passwd_user = ActionsUsers.get_sha256(str(data.get('passwd_user')))

    # Comprobaciones
    # Comprobar los datos no vayan vacíos
    if email and passwd and name_user and fsurname_user and birthdate_user and permissions_user and email_user and passwd_user:
        if ActionsUsers.check_email(email) and ActionsUsers.check_email(email_user):
            if ActionsUsers.check_format_date(birthdate_user):
                # Cambiar formato a la fecha de nacimiento
                dia = int(birthdate_user.split('/')[0])
                mes = int(birthdate_user.split('/')[1])
                year = int(birthdate_user.split('/')[2])
                
                birthdate_user = f'{str(year)}-{str(mes)}-{str(dia)}'

                # Buscar email y contraseña
                try:
                    users = Users.query.filter_by(email=email, passwd=passwd).first()
                except:
                    return jsonify({'update': 'failed', 'error': "DB connection error."})
                # Comprobar que usuario y contraseña sean correctos y que sea admin o el correo del usuario sea igual al que se quiere modificar
                if users and (users.permissions == 'admin' or email == email_user):
                    # Buscar email a borrar para comprobar si está
                    try:
                        users_m = Users.query.filter_by(email=email_user).first()
                    except:
                        return jsonify({'update': 'failed', 'error': "DB connection error."})
                    
                    # Comprobar si existe la cuenta a modificar
                    if not users:
                        return jsonify({'update': 'failed', 'error': "The account you want to modify does not exist."})
                else:
                    return jsonify({'update': 'failed', 'error': "Invalid Email/Password or without sufficient permissions."})
                    # Comprobar que el usuario esté habilitado
                    #if users.active == 1:
                    #else:
                    #    return jsonify({'update': 'failed', 'error': 'The account is not active. Verify your account with the email we sent you.'})
            else:
                return jsonify({'update': 'failed', 'error': "Wrong date of birth format."})
        else:
            return jsonify({'update': 'failed', 'error': 'The email is not valid, enter a valid email.'})
    else:
        return jsonify({'update': 'failed', 'error': "The necessary data has not been provided."})

    # Buscar email del que queremos modificar y modificamos
    try:
        if users_m.name != name_user:
            users_m.name = name_user
        if users_m.fsurname != fsurname_user:
            users_m.fsurname = fsurname_user
        #if users_m.ssurname != ssurname_user:
        users_m.ssurname = ssurname_user
        if users_m.birthdate != birthdate_user:
            users_m.birthdate = birthdate_user
        if users_m.permissions != permissions_user and users.permissions == 'admin':
            users_m.permissions = permissions_user
        if users_m.email != email_user:
            users_m.email = email_user
        if users_m.passwd != passwd_user:
            users_m.passwd = passwd_user
        
        db.session.commit()
        return jsonify({'update': 'success'})
    except:
        db.session.rollback()
        return jsonify({'update': 'failed', 'error': "DB connection error."})

@app.route('/remove_user', methods=['POST'])
def remove_admin():
    data = request.get_json()

    email = str(data.get('email'))
    passwd = ActionsUsers.get_sha256(str(data.get('passwd')))

    email_remove = str(data.get('email_remove'))

    # Comprobaciones
    # Comprobar los datos no vayan vacíos
    if email and passwd and email_remove:
        if ActionsUsers.check_email(email) and ActionsUsers.check_email(email_remove):
            # Buscar email y contraseña
            try:
                users = Users.query.filter_by(email=email, passwd=passwd).first()
            except:
                return jsonify({'remove': 'failed', 'error': "DB connection error."})
            
            # Comprobar que usuario y contraseña sean correctos y que sea admin o el correo del usuario sea igual al que se quiere borrar
            if users and (email == email_remove or users.permissions == 'admin'):
                # Buscar email a borrar para comprobar si está
                try:
                    users_r = Users.query.filter_by(email=email_remove).first()
                except:
                    return jsonify({'remove': 'failed', 'error': "DB connection error."})
                
                # Comprobar si existe la cuenta a borrar
                if not users_r:
                    return jsonify({'remove': 'failed', 'error': "The account you want to delete does not exist."})
            else:
                return jsonify({'update': 'failed', 'error': "Invalid Email/Password or without sufficient permissions."})

        else:
            return jsonify({'remove': 'failed', 'error': 'The email is not valid, enter a valid email.'})
    else:
        return jsonify({'remove': 'failed', 'error': "The necessary data has not been provided."})
    

    # Borrar el email
    try:
        db.session.delete(users_r)
        db.session.commit()
        return jsonify({'remove': 'success'})
    except:
            db.session.rollback()
            return jsonify({'remove': 'failed', 'error': "DB connection error."})
    
# Podría hacer lista de baneos por IP y otra por cuenta basada en intentos añadiendo otra tabla a la DB y modificando cosas en alguna def de rutas PERO PARA ELLO HABRÍA QUE METER UN SISTEMA DE 
# TIEMPO PORQUE IMAGINATE QUE UN USUARIO LOGUEA 20 VECES EN UN DÍA (COSA POSIBLE). Lo que no queremos es que inicie 20 veces en 1 minuto al login/register.
# También se podría implementar un sistema de logs (MUY RECOMENDABLE)




@app.route('/version', methods=['GET'])
def get_version():
    return jsonify({'version': '1.0'})

if __name__ == '__main__':
    app.run(debug=True)