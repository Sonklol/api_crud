from requests import post, get

def login(email, passwd):
    json = {
        'email': email,
        'passwd': passwd
    }

    try:
        return post('http://127.0.0.1:5000/login', json=json).text
    except Exception as e:
        return e

def register(name, fsurname, ssurname, birthdate, email, passwd, passwd_2):
    json = {
        'name': name,
        'fsurname': fsurname,
        'ssurname': ssurname,
        'birthdate': birthdate,
        'email': email,
        'passwd': passwd,
        'passwd_2': passwd_2
    }

    try:
        return post('http://127.0.0.1:5000/register', json=json).text
    except Exception as e:
        return e
    
def get_users(email, passwd):
    json = {
        'email': email,
        'passwd': passwd
    }

    try:
        return post('http://127.0.0.1:5000/get_users', json=json).text
    except Exception as e:
        return e

def resend_mail(email):
    json = {
        'email': email
    }

    try:
        return post('http://127.0.0.1:5000/resend_mail', json=json).text
    except Exception as e:
        return e
    
def activate_user(email, code):
    json = {
        'email': email,
        'code': code
    }

    try:
        return post('http://127.0.0.1:5000/activate_user', json=json).text
    except Exception as e:
        return e

def update_user(email, passwd, name_user, fsurname_user, ssurname_user, birthdate_user, permissions_user, email_user, passwd_user):
    json = {
        'email': email,
        'passwd': passwd,
        'name_user': name_user,
        'fsurname_user': fsurname_user,
        'ssurname_user': ssurname_user,
        'birthdate_user': birthdate_user,
        'permissions_user': permissions_user,
        'email_user': email_user,
        'passwd_user': passwd_user
    }

    try:
        return post('http://127.0.0.1:5000/update_user', json=json).text
    except Exception as e:
        return e

def remove_user(email, passwd, email_remove):
    json = {
        'email': email,
        'passwd': passwd,
        'email_remove': email_remove
    }

    try:
        return post('http://127.0.0.1:5000/remove_user', json=json).text
    except Exception as e:
        return e

#print(send_mail('code', 'code', 'admin@gmail.com'))
#print(register('Nombre', 'Apellido', '', '10/09/2000', 'admin@gmail.com', 'password', 'password'))
#print(login('admin@gmail.com', 'password'))
#print(activate_user('admin@gmail.com', 998042))
#print(update_user('a@gmail.com', 'password', 'Nombreaaa', 'Apellidoaaa', '', '09/04/2002', 'admin', 'admin@gmail.com', 'password'))
#print(get_users('a@gmail.com', 'password'))
#print(remove_user('a@gmail.com', 'password', 'admin@gmail.com'))

print(register('Client', 'Test', 'OptionalSecondSurname', '01/04/2000', 'lvigwkjlbrephsfkim@cazlv.com', 'ASEg$54/5g', 'ASEg$54/5g'))
print(get_users('a@gmail.com', 'password'))
print(remove_user('a@gmail.com', 'password', 'lvigwkjlbrephsfkim@cazlv.com'))
print(get_users('a@gmail.com', 'password'))