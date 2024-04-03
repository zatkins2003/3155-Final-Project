from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

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
    return render_template('gpa.html')

@app.route('/schedule', methods=['GET','POST'])
def schedule():
    if request.method == 'POST':
        if 'add_event' in request.form:
            event_name = request.form['event_name']
            day_of_week = request.form['due_date']
            time = request.form['time']
            events[day_of_week].append(f'{event_name}: {time}')

        elif 'remove_event' in request.form:
            day_of_week = request.form['day_of_week']
            event_name = request.form['event_name']
            events[day_of_week] = [event for event in events[day_of_week] if event.split(':')[0].strip() != event_name]

    return render_template('schedule.html', sunday_events=events['Sunday'], monday_events=events['Monday'], 
        tuesday_events=events['Tuesday'], wednesday_events=events['Wednesday'], 
        thursday_events=events['Thursday'], friday_events=events['Friday'], 
        saturday_events=events['Saturday'])

@app.route('/planner', methods=['GET', 'POST'])
def planner():
    if request.method == 'POST':
        if 'add_task' in request.form:
            task_name = request.form['task_name']
            day_of_week = request.form['due_date']
            points = request.form['points']
            percentage = request.form['percentage']
            grade_weight = round(float(points) * (float(percentage) / 100), 2)
            tasks[day_of_week].append(f'{task_name}: {grade_weight}')

        elif 'remove_task' in request.form:
            day_of_week = request.form['day_of_week']
            task_name = request.form['task_name']
            tasks[day_of_week] = [task for task in tasks[day_of_week] if task.split(':')[0].strip() != task_name]          #got using chatGPT it removes the task from the array

    return render_template('planner.html', sunday_tasks=tasks['Sunday'], monday_tasks=tasks['Monday'], 
        tuesday_tasks=tasks['Tuesday'], wednesday_tasks=tasks['Wednesday'], 
        thursday_tasks=tasks['Thursday'], friday_tasks=tasks['Friday'], 
        saturday_tasks=tasks['Saturday'])


if __name__ == "__main__":
    app.run(debug=True)

