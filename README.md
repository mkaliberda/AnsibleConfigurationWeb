# AnsibleConfigurationWeb

###Manual deploy to CentOS

###install dev dependensies:
``yum install -y python3``

```sudo yum groupinstall 'Development Tools'```


``sudo yum -y install supervisor``

``sudo yum -y install nginx``


##### Install Postgresql From the CentOS Repositories

```sudo yum install postgresql-server postgresql-contrib```

```sudo postgresql-setup initdb```

```sudo systemctl start postgresql```

```sudo systemctl enable postgresql```

create db
 
```sudo passwd postgres```

```psql -d template1 -c "ALTER USER postgres WITH PASSWORD 'UAzPc8vYQn4492Xp';"

```createuser ansible_runner_app```

```createdb ansible_runner_app_db --owner ansible_runner_app```

Python Virtualenv

``sudo apt-get -y install python-virtualenv``

cd to the project folder

``virtualenv --python=python3 venv``

``source venv/bin/activate``

``pip install -r requirements.txt``

`` python manage.py sass static/styles/scss/ static/styles/css/``
