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

# Global variable to store courses and the GPA
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

@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

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
            tasks[day_of_week] = [task for task in tasks[day_of_week] if task.split(':')[0].strip() != task_name]

    return render_template('planner.html', sunday_tasks=tasks['Sunday'], monday_tasks=tasks['Monday'], 
        tuesday_tasks=tasks['Tuesday'], wednesday_tasks=tasks['Wednesday'], 
        thursday_tasks=tasks['Thursday'], friday_tasks=tasks['Friday'], 
        saturday_tasks=tasks['Saturday'])

if __name__ == "__main__":
    app.run(debug=True)
