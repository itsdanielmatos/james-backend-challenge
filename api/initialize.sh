#!/bin/bash
# START DATABASE SERVICE
/etc/init.d/postgresql start

# INITILIAZE, MIGRATE AND UPGRADE
python manage.py db init && python manage.py db migrate && python manage.py db upgrade

# RUN FLASK APPLICATION
flask run --host=0.0.0.0
