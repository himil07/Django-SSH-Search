# Django-SSH-Search
Web Application to search for SSH keys of specified GitHub user powered by Django Python and PostgreSQL

#### Pre-Requisites
----
- Python (3.5.x)
- Django (1.10.x)
- PostgreSQL (9.6.1)
- Python Requests (2.x.x)
- Argon2 (Password Hashing)

----
#### Installation
- For installing Python, you can refer https://www.python.org/downloads/. Select appropriate binary depending
upon your Operating System.

- Installing Django, Python Requests and argon2
    - `pip install django python argon2-cffi` (In case Linux you might need to append `sudo`)

- Installing PostgreSQL
    - You can download operating system specific binary and proceed with installation, https://www.postgresql.org/download/

#### Setting up Django
- Django needs some additional steps in case Windows operating system. You can refer those steps, https://docs.djangoproject.com/en/1.10/howto/windows/.

  For most other operating systems you will need to refer, https://docs.djangoproject.com/en/1.10/topics/install/

#### To Play with the Project
- `git clone https://github.com/shreyasp/django-ssh-search.git django-ssh-search`
- Setup your PostgreSQL instance with user, database, password.
- Edit `settings.py` in **django_ssh_seach** folder,

        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': <database_name>,
                'USER': <database_user_name>,
                'PASSWORD': <database_password>,
                'HOST': <host_ip_address>,
                'PORT': <host_database_port>
            }
        }

- `python3 manage.py makemigrations`
- `python3 manage.py migrate`
- `python3 manage.py runserver --traceback`
