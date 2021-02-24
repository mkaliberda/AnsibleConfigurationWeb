## Code Deployment

clone this project into `srv/folder`

Rename env_example to .env ``mv env_example .env``

## Install Dependencies

``yum install -y python3``

``sudo yum groupinstall 'Development Tools'``

``sudo yum -y install supervisor``

``sudo yum -y install nginx``

## Postgresql Install

```sudo yum install postgresql-server postgresql-contrib```

```sudo postgresql-setup initdb```

```sudo systemctl start postgresql```

```sudo systemctl enable postgresql```

add auth method

``sudo vim /var/lib/pgsql/data/pg_hba.conf``

values should be:

local all all peer <br>
host all all 127.0.0.1/32 md5 <br>
host all all ::1/128 md5 <br>

## Create Postgres DB & User

```sudo passwd postgres```

``su postgres``

``psql``

``CREATE USER web_app;``

``CREATE DATABASE web_prod_db;``

``ALTER USER postgres WITH PASSWORD 'PASSWORD';``

``ALTER USER web_app WITH PASSWORD 'PASSWORD';``

``ALTER DATABASE web_prod_db OWNER TO web_app;``

Verify DB ownership with \l command

``exit``

## Setup Python Virtualenv

``sudo apt-get -y install python-virtualenv``

cd to the project folder

``virtualenv --python=python3 venv``

``source venv/bin/activate``

``pip install -r requirements.txt``

``sudo mkdir /srv/static_root``

``chmod 777 /srv/static_root``

``python manage.py sass static/styles/scss/ static/styles/css/`` # to compile stlyes

``python manage.py collectstatic`` # to move static files to the static root

``python manage.py migrate`` to create tables in the database

``python manage.py migrate`` to create tables in the database

## Setup gunicorn and supervisor

create empty folder to store socket file
``mkdir ./venv/run``

at the ``venv/bin/`` create file ``gunicorn_start`` following template [deploy/gunicorn_start](./gunicorn_start)

at the ``/etc/supervisord.d/`` create file ``ansible-web.ini`` following template [deploy/ansible-web.ini](./ansible-web.ini) 

``sudo supervisorctl reread``

``sudo supervisorctl update``

``sudo supervisorctl status ansible-web`` to check the status

`python manage.py loaddata playbook_generator/fixtures/prod_static_vart.json` to load default static vars

 
## Setup nginx

at ``/etc/nginx/conf.d/`` create file ``*.conf`` following template [deploy/nginx.conf](./nginx.conf)

**IMPORTANT**
 
the path:
```
location /uploads/ {
  alias /srv/AnsibleConfigurationWeb/uploads/;
}
```
should be the same as ``PATH_UPLOAD_CONFIGS`` at .env file variables

``sudo nginx -t`` to test 
``sudo nginx`` to start
``sudo nginx -s reload`` to restart
