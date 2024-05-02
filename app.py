from flask import Flask, render_template, request
from datetime import datetime
from quickchart import QuickChart
from flask_sqlalchemy import SQLAlchemy
from flask import session, redirect, url_for
from sqlalchemy.orm import relationship
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data_base.db'
db = SQLAlchemy(app)

#---------------Global Variables---------------------------

app.secret_key = '*Fd#l6#tg2)of}~!'
daysOfWeekAry = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

#---------------Global Variables---------------------------

#----------------------------------------INITIALIZE DATABASE----------------------------------------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    events = relationship('Event', backref='user', lazy=True)
    tasks = relationship('Task', backref='user', lazy=True)
    courses = relationship('Course', backref='user', lazy=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    day_of_week = db.Column(db.String(200), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    day_of_week = db.Column(db.String(200), nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    grade = db.Column(db.String(5), nullable=False)
    credits = db.Column(db.Float, nullable=False)

#----------------------------------------INITIALIZE DATABASE END----------------------------------------------------------


#----------------------------------------FUNCTIONS------------------------------------------------------------------------


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))               #this is from chatgpt, it just checks if the user is logged in or not
        return f(*args, **kwargs)
    return decorated_function



def get_task_float_value(task):
    return float(task.split(": ")[1])

def get_event_time_value(event):
    splitEvent = event.split(":")
    splitTime = splitEvent[2].split(" ")
    splitEvent[1] = splitEvent[1].replace(" ","")
    if splitTime[1] == "AM":
        if splitEvent[1] == "12":
            result = "00" + splitTime[0]
            return int(result)
        else:
            result = splitEvent[1] + splitTime[0]
            return int(result)
    else:
        if splitEvent[1] == "12":
            result = "12" + splitTime[0]
            return int(result)
        else:
            temp = int(splitEvent[1]) + 12
            temp = str(temp)
            result = temp + splitTime[0]
            return int(result)



def convert_grade_to_gpa(grade):

    letter_grades = {
        'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D+': 1.3, 'D': 1.0, 'F': 0.0
    }
    if grade.strip().upper() in letter_grades:
        return letter_grades[grade.strip().upper()]
    try:
        numeric_grade = float(grade)
        if numeric_grade >= 90:
            return 4.0
        elif numeric_grade >= 80:
            return 3.0
        elif numeric_grade >= 70:
            return 2.0
        elif numeric_grade >= 60:
            return 1.0
        else:
            return 0.0
    except ValueError:
        return None

#----------------------------------------FUNCTIONS END------------------------------------------------------------------------

#--------------------------------------------APP ROUTES-----------------------------------------------------------------------

@app.route('/')     #renders index.html with the username associated with the current session
def index():
    username = None
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        if user:
            username = user.username
    return render_template('index.html', username=username)


@app.route('/login', methods=['GET', 'POST'])   #renders login.html, creates a session using the user id assosiacted with a username and password. shows an error if invalid creds are used
def login():
    if request.method == 'POST':
        if 'login' in request.form:
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                session['user_id'] = user.id
                print(f"Logged in as: {username}")
                return render_template('index.html', username=username)
            else:
                error_message = 'Invalid username or password. Please try again.'
                return render_template('login.html', error_message=error_message)
    return render_template('login.html')

@app.route('/logout')     #stops the current session when the "Sign Out" link is clicked
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])    #creates a new user (assuming it doesn't already exist) with a unique user id and starts a new session using that id.
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error_message = 'User already exists. Please try again.'
            return render_template('signup.html', error_message=error_message)
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/gpa', methods=['GET', 'POST'])     #renders gpa.html
@login_required  #makes sure the user is logged in and if not sends them to login.html instead
def gpa_tracker():
    global_gpa = None
    courses = []
    username = None
    if 'user_id' in session:             #grabs the username of the current logged in user
        user_id = session['user_id']
        user = User.query.get(user_id)
        if user:
            username = user.username
    if 'remove_course' in request.form:   #if the delete_course button is pressed it removes the courses from the database and renders gpa.html
        courses_to_delete = Course.query.filter_by(user_id=user_id).all()
        for course in courses_to_delete:
            db.session.delete(course)
        db.session.commit()
        courses = Course.query.filter_by(user_id=user_id).all()
        return render_template('gpa.html', courses=courses, username=username)
    
    else:                   #if its not the delete_course button the only other form is to add courses.
        try:
            course_names = request.form.getlist('course_name[]')
            grades = request.form.getlist('grade[]')
            credits = request.form.getlist('credits[]')

            for name, grade, credit in zip(course_names, grades, credits):
                gpa = convert_grade_to_gpa(grade)
                if gpa is not None:
                    new_course = Course(user_id=user_id, name=name, grade=grade, credits=credit)
                    db.session.add(new_course)

            db.session.commit()


            courses = Course.query.filter_by(user_id=user_id).all()
            total_points = sum(convert_grade_to_gpa(course.grade) * float(course.credits) for course in courses)
            total_credits = sum(float(course.credits) for course in courses)
            global_gpa = total_points / total_credits if total_credits > 0 else 0

            return render_template('gpa.html', gpa=round(global_gpa, 2), courses=courses, username=username)
        except Exception as e:
            return render_template('gpa.html', error="Error calculating GPA: " + str(e), courses=courses, username=username)

@app.route('/schedule', methods=['GET','POST'])   
@login_required
def schedule():
    username = None
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        if user:
            username = user.username

    events = {
    'Sunday': [],
    'Monday': [],
    'Tuesday': [],
    'Wednesday': [],
    'Thursday': [],
    'Friday': [],
    'Saturday': []
    }
    #loads data from the db to events array
    events = {
        'Sunday': [event.description for event in Event.query.filter_by(user_id=user_id, day_of_week='Sunday')],
        'Monday': [event.description for event in Event.query.filter_by(user_id=user_id, day_of_week='Monday')],
        'Tuesday': [event.description for event in Event.query.filter_by(user_id=user_id, day_of_week='Tuesday')],
        'Wednesday': [event.description for event in Event.query.filter_by(user_id=user_id, day_of_week='Wednesday')],
        'Thursday': [event.description for event in Event.query.filter_by(user_id=user_id, day_of_week='Thursday')],   
        'Friday': [event.description for event in Event.query.filter_by(user_id=user_id, day_of_week='Friday')],
        'Saturday': [event.description for event in Event.query.filter_by(user_id=user_id, day_of_week='Saturday')]
    }
    #variable that manages the visibility of the details window associated with events
    hidden = "hidden"

    if request.method == 'POST':
        if 'add_event' in request.form:
            event_name = request.form['event_name']
            day_of_week = request.form['due_date']
            time = request.form['time']

            #retruns an error message if the form wasn't filled out correctly
            if not event_name or not day_of_week or not time:
                return render_template('schedule.html', error_message="Please fill out all required fields.", daysOfWeekAry=daysOfWeekAry, events=events, 
                    Sunday_events=events['Sunday'], 
                    Monday_events=events['Monday'], 
                    Tuesday_events=events['Tuesday'], 
                    Wednesday_events=events['Wednesday'], 
                    Thursday_events=events['Thursday'], 
                    Friday_events=events['Friday'], 
                    Saturday_events=events['Saturday'], username=username)

            #-------------------convert 24 hour format to 12 hour format--------------------------
            hours_minutes = time.split(':')
            hours = int(hours_minutes[0])
            minutes = int(hours_minutes[1])

            if hours == 0:
                event_name = (f'{event_name}: 12:{minutes:02} AM')
            elif hours == 12:
                event_name = (f'{event_name}: 12:{minutes:02} PM')
            elif hours > 12:
                hours -= 12
                event_name = (f'{event_name}: {hours}:{minutes:02} PM')
            else:
                event_name = (f'{event_name}: {hours}:{minutes:02} AM')
            #-------------------convert 24 hour format to 12 hour format END--------------------------

            #checks if the event already exists and loads the event to the database if its not
            test = False
            for event in events[day_of_week]:
                if event == event_name:
                    test = True
            if not test:
                event = Event(user_id=user_id, description=f'{event_name}', day_of_week=day_of_week)
                db.session.add(event)
                db.session.commit()                

        #handles removing events from the database
        elif 'remove_event' in request.form:
            day_of_week = request.form['day_of_week']
            event_name = request.form['event_name']
            user_id = session['user_id']
            event = Event.query.filter_by(user_id=user_id, description=event_name, day_of_week=day_of_week).first()
            if event:
                db.session.delete(event)
                db.session.commit()
                print(f"Event '{event_name}' removed successfully from the database")
        
        #handles sending data to the quickChart api
        elif 'show_chart' in request.form:
            qc = QuickChart()
            qc.width = 500
            qc.height = 300

            qc.config = {
                "type": "bar",
                "data": {
                    "labels": ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
                    "datasets": [{
                        "label": 'Number of Events',
                        "data": [len(events['Sunday']), len(events['Monday']), len(events['Tuesday']), len(events['Wednesday']),len(events['Thursday']),len(events['Friday']),len(events['Saturday'])]
                    }]
                }
            }

            qc.to_file('static/mychart.png')
            hidden = ""
        elif 'hide_chart' in request.form:
            hidden = "hidden"


        #reloads events from the db into the events array
        events = {
        'Sunday': [event.description for event in Event.query.filter_by(user_id=user_id, day_of_week='Sunday')],
        'Monday': [event.description for event in Event.query.filter_by(user_id=user_id, day_of_week='Monday')],
        'Tuesday': [event.description for event in Event.query.filter_by(user_id=user_id, day_of_week='Tuesday')],
        'Wednesday': [event.description for event in Event.query.filter_by(user_id=user_id, day_of_week='Wednesday')],
        'Thursday': [event.description for event in Event.query.filter_by(user_id=user_id, day_of_week='Thursday')],
        'Friday': [event.description for event in Event.query.filter_by(user_id=user_id, day_of_week='Friday')],
        'Saturday': [event.description for event in Event.query.filter_by(user_id=user_id, day_of_week='Saturday')]
        }

        #sorts the erray by time (time is converted from 12 hour format to a number from 0000-2359 where 0000 is 12:00 AM and 2359 is 11:59 PM)
        events['Sunday'] = sorted(events['Sunday'], key=get_event_time_value)
        events['Monday'] = sorted(events['Monday'], key=get_event_time_value)
        events['Tuesday'] = sorted(events['Tuesday'], key=get_event_time_value)
        events['Wednesday'] = sorted(events['Wednesday'], key=get_event_time_value)
        events['Thursday'] = sorted(events['Thursday'], key=get_event_time_value)
        events['Friday'] = sorted(events['Friday'], key=get_event_time_value)
        events['Saturday'] = sorted(events['Saturday'], key=get_event_time_value)

    return render_template('schedule.html', daysOfWeekAry=daysOfWeekAry, events=events, hidden=hidden, 
        Sunday_events=events['Sunday'], 
        Monday_events=events['Monday'], 
        Tuesday_events=events['Tuesday'], 
        Wednesday_events=events['Wednesday'], 
        Thursday_events=events['Thursday'], 
        Friday_events=events['Friday'], 
        Saturday_events=events['Saturday'], username=username)

@app.route('/planner', methods=['GET', 'POST']) #renders planner.html
@login_required
def planner():
    username = None
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        if user:
            username = user.username

    tasks = {
    'Sunday': [],
    'Monday': [],
    'Tuesday': [],
    'Wednesday': [],
    'Thursday': [],
    'Friday': [],
    'Saturday': []
    }
    #loads tasks from db into  tasks array
    tasks = {
        'Sunday': [task.description for task in Task.query.filter_by(user_id=user_id, day_of_week='Sunday')],
        'Monday': [task.description for task in Task.query.filter_by(user_id=user_id, day_of_week='Monday')],
        'Tuesday': [task.description for task in Task.query.filter_by(user_id=user_id, day_of_week='Tuesday')],
        'Wednesday': [task.description for task in Task.query.filter_by(user_id=user_id, day_of_week='Wednesday')],
        'Thursday': [task.description for task in Task.query.filter_by(user_id=user_id, day_of_week='Thursday')],
        'Friday': [task.description for task in Task.query.filter_by(user_id=user_id, day_of_week='Friday')],
        'Saturday': [task.description for task in Task.query.filter_by(user_id=user_id, day_of_week='Saturday')]
    }
    #variable that manages the visibility of the details window associated with each task
    hidden2 = "hidden"
    if request.method == 'POST':
        if 'add_task' in request.form:
            task_name = request.form['task_name']
            day_of_week = request.form['due_date']
            points = request.form['points']
            percentage = request.form['percentage']

            #returns an error message if the form is not filled out correctly
            if not task_name or not day_of_week or not points or not percentage:
                return render_template('planner.html', error_message="Please fill out all required fields.", daysOfWeekAry=daysOfWeekAry, tasks=tasks, 
                    Sunday_tasks=tasks['Sunday'], 
                    Monday_tasks=tasks['Monday'], 
                    Tuesday_tasks=tasks['Tuesday'], 
                    Wednesday_tasks=tasks['Wednesday'], 
                    Thursday_tasks=tasks['Thursday'], 
                    Friday_tasks=tasks['Friday'], 
                    Saturday_tasks=tasks['Saturday'], username=username)

                    #calculates the grade weight and adds the task to the db
            grade_weight = round(float(points) * (float(percentage) / 100), 2)
            task = Task(user_id=user_id, description=f'{task_name}: {grade_weight}', day_of_week=day_of_week)
            db.session.add(task)
            db.session.commit()   

        #handles removing tasks
        elif 'remove_task' in request.form:
            day_of_week = request.form['day_of_week']
            task_name = request.form['task_name']
            user_id = session['user_id']
            task = Task.query.filter_by(user_id=user_id, description=task_name, day_of_week=day_of_week).first()

            #if the task is found it deletes it from the db
            if task:
                db.session.delete(task)
                db.session.commit()
                print(f"Task '{task_name}' removed successfully from the database")
        

        #handles sending data to the quickChart api
        elif 'show_chart' in request.form:
            qc = QuickChart()
            qc.width = 600
            qc.height = 400

            qc.config = {
                "type": "bar",
                "data": {
                    "labels": ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
                    "datasets": [{
                        "label": 'Number of Tasks',
                        "data": [len(tasks['Sunday']), len(tasks['Monday']), len(tasks['Tuesday']), len(tasks['Wednesday']),len(tasks['Thursday']),len(tasks['Friday']),len(tasks['Saturday'])]
                    }]
                }
            }

            qc.to_file('static/mychart2.png')
            hidden2 = ""
        elif 'hide_chart' in request.form:
            hidden2 = "hidden"

    #reloads the data in the db to the tasks array
    tasks = {
        'Sunday': [task.description for task in Task.query.filter_by(user_id=user_id, day_of_week='Sunday')],
        'Monday': [task.description for task in Task.query.filter_by(user_id=user_id, day_of_week='Monday')],
        'Tuesday': [task.description for task in Task.query.filter_by(user_id=user_id, day_of_week='Tuesday')],
        'Wednesday': [task.description for task in Task.query.filter_by(user_id=user_id, day_of_week='Wednesday')],
        'Thursday': [task.description for task in Task.query.filter_by(user_id=user_id, day_of_week='Thursday')],
        'Friday': [task.description for task in Task.query.filter_by(user_id=user_id, day_of_week='Friday')],
        'Saturday': [task.description for task in Task.query.filter_by(user_id=user_id, day_of_week='Saturday')]
    }

    #sorts the tasks by grade weight (higher grade weight comes first)
    tasks['Sunday'] = sorted(tasks['Sunday'], key=get_task_float_value, reverse=True)
    tasks['Monday'] = sorted(tasks['Monday'], key=get_task_float_value, reverse=True)
    tasks['Tuesday'] = sorted(tasks['Tuesday'], key=get_task_float_value, reverse=True)
    tasks['Wednesday'] = sorted(tasks['Wednesday'], key=get_task_float_value, reverse=True)
    tasks['Thursday'] = sorted(tasks['Thursday'], key=get_task_float_value, reverse=True)
    tasks['Friday'] = sorted(tasks['Friday'], key=get_task_float_value, reverse=True)
    tasks['Saturday'] = sorted(tasks['Saturday'], key=get_task_float_value, reverse=True)

    return render_template('planner.html', daysOfWeekAry=daysOfWeekAry, hidden=hidden2, tasks=tasks, sunday_tasks=tasks['Sunday'], monday_tasks=tasks['Monday'], 
        tuesday_tasks=tasks['Tuesday'], wednesday_tasks=tasks['Wednesday'], 
        thursday_tasks=tasks['Thursday'], friday_tasks=tasks['Friday'], 
        saturday_tasks=tasks['Saturday'], username=username)

#--------------------------------------------APP ROUTES END-----------------------------------------------------------------------


if __name__ == "__main__":
    app.run(debug=True)

