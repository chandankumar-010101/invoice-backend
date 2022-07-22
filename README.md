# jasiri-django

for migrations you have to run these below command in the same sequence
because i have override User model of django to direct migrate command will not work.

python manage.py migrate --fake account zero --settings=jasiri.settings.local
python manage.py migrate --fake --settings=jasiri.settings.local
python manage.py makemigrations customer --settings=jasiri.settings.local
python manage.py makemigrations invoice --settings=jasiri.settings.local

runserver local: 
python manage.py runserver --settings=jasiri.settings.local

python manage.py makemigrations --settings=jasiri.settings.local


python manage.py migrate --settings=jasiri.settings.staging

before all these commands you need to setup postgres database.
configuration are in .env file for database.