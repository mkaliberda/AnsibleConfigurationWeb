# Update the Code on an Existing Web Server

## EMEA Web Server

1. Update the Code in GitLab
2. SSH to the EMEA Web Server and run the following commands to update the code base

``sudo su - webuse``

``cd /srv/static_root/vmclusterautomation-webfrontend/``

``git pull``

3. Run the following commands to update and restart the Web Server

``APP_PATH=/srv/static_root/vmclusterautomation-webfrontend/``

``yes | $APP_PATH/venv/bin/python manage.py migrate``

``$APP_PATH/venv/bin/python manage.py collectstatic``

``yes | $APP_PATH/venv/bin/pip install -r requirements.txt``

4. Exit the webuse user so you're running as your local account and run the following command sudo to root and restart the web server

``sudo su - root``

``supervisorctl restart ansible-web``
