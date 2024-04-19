from flask import Flask, render_template, request
from datetime import datetime
from quickchart import QuickChart
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data_base.db'
db = SQLAlchemy(app)


class dataBase(db.Model):
    #this just an example
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    organization = db.Column(db.String(200), nullable=False)

tasks = {
    'Sunday': [],
    'Monday': [],
    'Tuesday': [],
    'Wednesday': [],
    'Thursday': [],
    'Friday': [],
    'Saturday': []
}

events = {
    'Sunday': [],
    'Monday': [],
    'Tuesday': [],
    'Wednesday': [],
    'Thursday': [],
    'Friday': [],
    'Saturday': []
}

daysOfWeekAry = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]



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

global_gpa = None
courses = []

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

@app.route('/calculate_gpa', methods=['POST'])
def calculate_gpa():

    #This is where the courses saved in the database should be loaded into the courses array

    global global_gpa, courses
    try:
        course_names = request.form.getlist('course_name[]')
        grades = request.form.getlist('grade[]')
        credits = request.form.getlist('credits[]')
        course_details = zip(course_names, grades, credits)

        for course_name, grade, credit in course_details:
            gpa = convert_grade_to_gpa(grade)
            if gpa is not None:
                courses.append({'name': course_name, 'grade': grade, 'credits': credit, 'gpa': gpa})
        
        total_points = sum(float(item['gpa']) * float(item['credits']) for item in courses)
        total_credits = sum(float(item['credits']) for item in courses)
        global_gpa = total_points / total_credits if total_credits > 0 else 0
        return render_template('gpa.html', gpa=round(global_gpa, 2), courses=courses)
    except Exception as e:
        return render_template('gpa.html', error="Error calculating GPA: " + str(e), courses=courses)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/gpa')
def gpa_tracker():
    global global_gpa, courses
    return render_template('gpa.html', gpa=global_gpa if global_gpa is not None else None, courses=courses)

@app.route('/schedule', methods=['GET','POST'])
def schedule():

    #this is where the events stored in the database should be loaded into the events[][] array
    #events['Sunday']=["hfjkdsfhjskdhf: 12:12 AM"]

    hidden = "hidden"

    if request.method == 'POST':
        if 'add_event' in request.form:
            event_name = request.form['event_name']
            day_of_week = request.form['due_date']
            time = request.form['time']
            if not event_name or not day_of_week or not time:
                return render_template('schedule.html', error_message="Please fill out all required fields.", daysOfWeekAry=daysOfWeekAry, events=events, 
                    Sunday_events=events['Sunday'], 
                    Monday_events=events['Monday'], 
                    Tuesday_events=events['Tuesday'], 
                    Wednesday_events=events['Wednesday'], 
                    Thursday_events=events['Thursday'], 
                    Friday_events=events['Friday'], 
                    Saturday_events=events['Saturday'])

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

            test = False
            for event in events[day_of_week]:
                if event == event_name:
                    test = True
            if not test:
                events[day_of_week].append(f'{event_name}')


        elif 'remove_event' in request.form:
            day_of_week = request.form['day_of_week']
            event_name = request.form['event_name']
            for event in events[day_of_week]:
                try:
                    if event == event_name:
                        events[day_of_week].remove(event)
                        print(f"Event '{event_name}' removed successfully")
                except Exception as e:
                    print(f"Error removing event: {e}")
        
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
        Saturday_events=events['Saturday'])

@app.route('/planner', methods=['GET', 'POST'])
def planner():

        #this is where the tasks stored in the database should be loaded into the tasks[][] array
    #tasks['Sunday']=["hfjkdsfhjskdhf: 12.2"]

    hidden2 = "hidden"
    if request.method == 'POST':
        if 'add_task' in request.form:
            task_name = request.form['task_name']
            day_of_week = request.form['due_date']
            points = request.form['points']
            percentage = request.form['percentage']
            if not task_name or not day_of_week or not points or not percentage:
                return render_template('planner.html', error_message="Please fill out all required fields.", daysOfWeekAry=daysOfWeekAry, tasks=tasks, 
                    Sunday_tasks=tasks['Sunday'], 
                    Monday_tasks=tasks['Monday'], 
                    Tuesday_tasks=tasks['Tuesday'], 
                    Wednesday_tasks=tasks['Wednesday'], 
                    Thursday_tasks=tasks['Thursday'], 
                    Friday_tasks=tasks['Friday'], 
                    Saturday_tasks=tasks['Saturday'])
            grade_weight = round(float(points) * (float(percentage) / 100), 2)
            tasks[day_of_week].append(f'{task_name}: {grade_weight}')

        elif 'remove_task' in request.form:
            day_of_week = request.form['day_of_week']
            task_name = request.form['task_name']
            for task in tasks[day_of_week]:
                try:
                    if task == task_name:
                        tasks[day_of_week].remove(task)
                        print(f"Task '{task_name}' removed successfully")
                except Exception as e:
                    print(f"Error removing task: {e}")
        
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
        saturday_tasks=tasks['Saturday'])


if __name__ == "__main__":
    app.run(debug=True)

