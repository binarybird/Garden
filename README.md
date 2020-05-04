# Garden
A REST api using Flask for managing/recording/polling i2c sensors and data on my Raspberry pi

To run
1) Install your db of choice (postgres used here). Create a DATABASE
2) vi ~/.bashrc (or .bash_profile)
3) add envars:
export FLASK_ENV=development
export DATABASE_URL=postgres://USER:PASS5@HOST:PORT/DATABASE
export JWT_SECRET_KEY=somesupersecretkeyshhhdontshare
export PORT=8080
4) cd Garden
5) python3 manage.py db init
6) python3 manage.py db migrate
7) python3 manage.py db upgrade
8) python3 run.py

Ill document the API and i2c device interface later!
