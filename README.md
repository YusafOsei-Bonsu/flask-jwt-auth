# What I've learnt

## Couldn't log into "Yusaf" postgres account
Entered the following command: `psql -U postgres -h localhost -W` in the terminal to login into postgres as "postgres".

## Couldn't perform first migration (i.e. "python manage.py create_db") since the password wasn't supplied
In `config.py`, I changed the connection string to `postgresql://postgres:Rasengan1@localhost:5432/`

## Couldn't run "python manage.py db migrate" in the terminal 
I solved this issue by implementing the green-ticked [solution](https://stackoverflow.com/questions/58351958/psycopg2-programmingerror-column-cons-consrc-does-not-exist) (i.e. upgrading sqlalchemy via `pip install --upgrade sqlalchemy`)