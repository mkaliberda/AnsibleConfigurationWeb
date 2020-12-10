###Manual deploy to AWS instance CentOS

after clone this project 

``mv env_example .env`` please check information inside

## install dev dependensies:

``yum install -y python3``

``sudo yum groupinstall 'Development Tools'``

``sudo yum -y install supervisor``

``sudo yum -y install nginx``

## Postgresql

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

create db
 
```sudo passwd postgres```

``psql -d template1 -c "ALTER USER postgres WITH PASSWORD 'PASSWORD';"``

``createuser web_app``

``psql -d template1 -c "ALTER USER web_app WITH PASSWORD 'PASSWORD';"``

``createdb web_prod_db --owner web_app``

``exit``

##Python Virtualenv

``sudo apt-get -y install python-virtualenv``

cd to the project folder

``virtualenv --python=python3 venv``

``source venv/bin/activate``

``pip install -r requirements.txt``

``sudo mkdir /srv/static_root``

``chmod 777 /srv/static_root``

``python manage.py sass static/styles/scss/ static/styles/css/`` # for compile stlyes

``python manage.py collectstatic`` # for move static files to the static root

``python manage.py migrate`` for create tables at the database

##gunicorn and supervisor

create empty folder to store socket file
``mkdir ./venv/run``

at the ``venv/bin/`` create file ``gunicorn_start`` following template [deploy/gunicorn_start](./gunicorn_start)

at the ``/etc/supervisord.d/`` create file ``ansible-web.ini`` following template [deploy/ansible-web.ini](./ansible-web.ini) 

``sudo supervisorctl reread``

``sudo supervisorctl update``

``sudo supervisorctl status ansible-web`` to check the status

``sudo supervisorctl restart ansible-web`` to restart task

 
##nginx

at the ``/etc/nginx/conf.d/`` create file ``*.conf`` following template [deploy/nginx.conf](./nginx.conf)

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