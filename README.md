# To run this code

### Ensure that python 3.x is installed on your computer you can do this by typing "python -V" into the windows terminal
### Ensure that you have SQLite installed and a server running locally on your pc (otherwise you will get errors when trying to log in)

# Windows commands

python3 -m venv venv

.\venv\Scripts\activate

pip3 install flask Flask-SQLAlchemy quickchart.io

flask run


# Linux commands

pip3 install virtualenv

sudo apt install virtualenv

virtualenv env

source env/bin/activate

pip3 install flask Flask-SQLAlchemy quickchart.io

python3 app.py
