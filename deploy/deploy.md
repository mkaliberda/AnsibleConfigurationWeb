## Code Deployment

``cd /srv``

``sudo git clone`` this project

Rename env_example to .env: ``sudo mv env_example .env``

## Permissions

Identify a user account that will be used to run the web app

``sudo chown -R <username> /srv/<projectfolder>``

## Install Dependencies

``sudo yum install -y python3``

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

Verify DB ownership : ``\l``

Exit psql : ``\q``

Exit back to your shell: ``exit``

Reload psql: ``/usr/bin/pg_ctl reload``

## Setup .env configuration file

``sudo vi .env``

Fill in the path for the Nutanix and VMware playbooks on the Ansible server. <br>
Fill in the database connection information - be careful with special characters in the password section <br>
Remove the comments in the DB section <br>

## Setup Python Virtualenv

``sudo yum install -y install python-virtualenv``

cd to the project folder

``virtualenv --python=python3 venv``

``source venv/bin/activate``

``sudo pip install -r requirements.txt``

``sudo mkdir /srv/static_root``

``sudo chown -R <username> /srv/static_root``

``sudo chmod 777 /srv/static_root``

``sudo python manage.py sass static/styles/scss/ static/styles/css/`` # to compile stlyes

``sudo python manage.py collectstatic`` # to move static files to the static root

``sudo python manage.py migrate`` to create tables in the database

## Setup gunicorn and supervisor

Create an empty folder to store the socket file: ``mkdir ./venv/run``

Create an empty folder for gunicorn logs: ``mkdir ./logs``

cd to ``venv/bin/``

Create file ``gunicorn_start`` 

Use the following template and update DIR, USER and BIND lines: [deploy/gunicorn_start](./gunicorn_start)

cd to``/etc/supervisord.d/`` 

Create file ``ansible-web.ini`` 

Use the following template and update [deploy/ansible-web.ini](./ansible-web.ini) 

``sudo systemctl enable supervisord.service``

``sudo systemctl enable supervisord``

``sudo service supervisord start``

``sudo supervisorctl reread``

``sudo supervisorctl update``

``sudo supervisorctl status ansible-web`` to check the status

`python manage.py loaddata playbook_generator/fixtures/prod_static_vart.json` to load default static vars

 
## Setup nginx

cd to ``/etc/nginx/conf.d/`` 

Create or edit ``default.conf`` following template [deploy/nginx.conf](./nginx.conf)

**IMPORTANT**
 
the path:
```
location /uploads/ {
  alias /srv/AnsibleConfigurationWeb/uploads/;
}
```
should be the same as ``PATH_UPLOAD_CONFIGS`` in .env file variables

``sudo nginx -t`` to test <br>
``sudo nginx`` to start <br>
``sudo nginx -s reload`` to restart <br>

## Troubleshooting

When trying to run migrate.py an Ident authentication error is generated - Be sure you didn't skip the step to reload psql after changing the configuration file (/usr/bin/pg_ctl reload).
