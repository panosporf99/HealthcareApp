from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_,func
import matplotlib.pyplot as plt
from flask import send_file
import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    blood_type = db.Column(db.String(5))
    medical_condition = db.Column(db.String(100))
    date_of_admission = db.Column(db.String(20))
    doctor = db.Column(db.String(50))
    hospital = db.Column(db.String(50))
    insurance_provider = db.Column(db.String(50))
    billing_amount = db.Column(db.Float)
    room_number = db.Column(db.String(10))
    admission_type = db.Column(db.String(20))
    discharge_date = db.Column(db.String(20))
    medication = db.Column(db.String(100))
    test_results = db.Column(db.String(100))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

@app.route('/')
@login_required
def index():
    patients = Patient.query.all()
    return render_template('index.html', patients=patients)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print("User is already authenticated.")
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful.', 'success')

            # Redirect to index page after successful login
            print(f"User {user.username} logged in successfully.")
            return redirect(url_for('index'))

        flash('Login failed. Check your username and password.', 'error')

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful.', 'success')
    return redirect(url_for('login'))

# Inside the register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        print("Form validation successful")  # Add this line for debugging
        username = form.username.data
        password = form.password.data

        # Check if the username is already taken
        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Choose a different one.', 'error')
            return redirect(url_for('register'))

        new_user = User(username=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))
    else:
        print("Form validation failed")  # Add this line for debugging
        print(form.errors)  # Add this line to print form errors for debugging

    return render_template('register.html', form=form)


@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        gender = request.form['gender']
        blood_type = request.form['blood_type']
        medical_condition = request.form['medical_condition']
        date_of_admission = request.form['date_of_admission']
        doctor = request.form['doctor']
        hospital = request.form['hospital']
        insurance_provider = request.form['insurance_provider']
        billing_amount = request.form['billing_amount']
        room_number = request.form['room_number']
        admission_type = request.form['admission_type']
        discharge_date = request.form['discharge_date']
        medication = request.form['medication']
        test_results = request.form['test_results']

        patient = Patient(
            name=name,
            age=age,
            gender=gender,
            email=email,
            blood_type=blood_type,
            medical_condition=medical_condition,
            date_of_admission=date_of_admission,
            doctor=doctor,
            hospital=hospital,
            insurance_provider=insurance_provider,
            billing_amount=billing_amount,
            room_number=room_number,
            admission_type=admission_type,
            discharge_date=discharge_date,
            medication=medication,
            test_results=test_results
        )

        db.session.add(patient)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('add_patient.html')

# app.py

@app.route('/search_patient', methods=['GET', 'POST'])
def search_patient():
    return render_template('search_patient.html')


# app.py

@app.route('/search_results', methods=['POST'])
def search_results():
    search_query = request.form['search_query']
    
    # Perform a search in the database based on the query (searching by name or id)
    # Replace the following line with your actual search logic
    patients = Patient.query.filter(
        or_(
            Patient.name.ilike(f"%{search_query}%"),
            Patient.id == int(search_query) if search_query.isdigit() else False
        )
    ).all()
    
    return render_template('search_results.html', patients=patients, search_query=search_query)

@app.route('/get_gender_distribution_data')
def get_gender_distribution_data():
    try:
        # Query the database to get the gender distribution
        gender_distribution = db.session.query(Patient.gender, func.count()).group_by(Patient.gender).all()

        # Prepare data for the chart
        labels = [item[0] for item in gender_distribution]
        values = [item[1] for item in gender_distribution]

        # Create a dictionary with the data
        data = {
            'labels': labels,
            'values': values,
        }

        return jsonify(data)
    except Exception as e:
        return str(e)


@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/get_graph_data/<graph>')
def get_graph_data(graph):
    # Depending on the selected graph, call the appropriate function
    if graph == 'gender_distribution':
        data = get_gender_distribution_data()
    elif graph == 'age_distribution':
        data = get_age_distribution_data()
    elif graph == 'billing_amount_by_admission':
        data = get_billing_by_admission_type_data()
    elif graph == 'medical_conditions':
        data = get_medical_conditions_data()
    elif graph == 'blood_type':
        data = get_blood_type_data()

    return json.dumps(data)

def get_gender_distribution_data():
    # Query the database to get the age distribution
        # Query the database to get the gender distribution
        gender_distribution = db.session.query(Patient.gender, func.count()).group_by(Patient.gender).all()

        # Prepare data for the chart
        labels = [item[0] for item in gender_distribution]
        values = [item[1] for item in gender_distribution]

        print(labels,values)

        return {
        'labels': labels,
        'datasets': [{
            'label': 'Number of Patients',
            'data': values,
            'backgroundColor': '#4CA64C',
        }]
    }

def get_age_distribution_data():
    # Query the database to get the age distribution
    age_distribution = db.session.query(Patient.age, func.count()).group_by(Patient.age).all()

    # Prepare data for the chart
    ages = [item[0] for item in age_distribution]
    counts = [item[1] for item in age_distribution]

    return {
        'labels': ages,
        'datasets': [{
            'label': 'Number of Patients',
            'data': counts,
            'backgroundColor': '#4CA64C',
        }]
    }

def get_billing_by_admission_type_data():
    try:
        # Query the database to get billing amount by admission type
        result = db.session.query(Patient.admission_type, func.sum(Patient.billing_amount)).group_by(Patient.admission_type).all()

        # Prepare data for the chart
        admission_types = [item[0] for item in result]
        billing_amounts = [item[1] for item in result]

        return {
            'labels': admission_types,
            'datasets': [{
                'label': 'Billing Amount',
                'data': billing_amounts,
                'backgroundColor': '#4CA64C',  # Change color as needed
            }]
        }
    except Exception as e:
        return str(e)
    
from sqlalchemy import func

# ... (existing code) ...

def get_medical_conditions_data():
    try:
        # Query the database to get medical conditions distribution
        result = db.session.query(Patient.medical_condition, func.count()).group_by(Patient.medical_condition).all()

        # Prepare data for the chart
        conditions = [item[0] for item in result]
        counts = [item[1] for item in result]

        return {
            'labels': conditions,
            'datasets': [{
                'label': 'Number of Patients',
                'data': counts,
                'backgroundColor': '#4CA64C',  # Change color as needed
            }]
        }
    except Exception as e:
        return str(e)
    
def get_blood_type_data():
    try:
        # Query the database to get blood type distribution
        result = db.session.query(Patient.blood_type, func.count()).group_by(Patient.blood_type).all()

        # Prepare data for the chart
        blood_types = [item[0] for item in result]
        counts = [item[1] for item in result]

        return {
            'labels': blood_types,
            'datasets': [{
                'label': 'Number of Patients',
                'data': counts,
                'backgroundColor': '#4CA64C',  # Change color as needed
            }]
        }
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

