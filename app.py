from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from datetime import datetime
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Secret key from environment (used for sessions & security)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret")

bcrypt = Bcrypt(app)

# MongoDB Configuration (safe from .env)
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)

db = client['flask_auth']
users_collection = db['users']
appointments_collection = db['appointments']

# Home Route
@app.route('/')
def home():

    return render_template ('home.html')
@app.route('/home2')
def home2():
    return render_template('home2.html')
# About Route
tests = {
    "Blood Test": {
        "purpose": "Check general health and detect diseases.",
        "category": "Pathology",
        "procedure": "Blood is drawn from a vein.",
        "preparation": "Fast for 8-12 hours if required.",
        "cost": "$50",
        "duration": "10 minutes"
    },
    "X-Ray": {
        "purpose": "Diagnose fractures and injuries.",
        "category": "Radiology",
        "procedure": "Images are taken using X-ray machines.",
        "preparation": "Wear comfortable clothes. Remove metal objects.",
        "cost": "$100",
        "duration": "20 minutes"
    },
    "MRI Scan": {
        "purpose": "Detailed images of organs and tissues.",
        "category": "Radiology",
        "procedure": "Lie still in a scanner for imaging.",
        "preparation": "Avoid eating for 4 hours if required.",
        "cost": "$500",
        "duration": "45 minutes"
    },
    "CT Scan": {
        "purpose": "Generate detailed cross-sectional images of the body.",
        "category": "Radiology",
        "procedure": "Lie on a table that slides into a CT scanner.",
        "preparation": "May require fasting for a few hours.",
        "cost": "$400",
        "duration": "30 minutes"
    },
    "Urine Test": {
        "purpose": "Detect infections, diseases, or other medical conditions.",
        "category": "Pathology",
        "procedure": "Provide a urine sample in a sterile container.",
        "preparation": "Cleanse the area before providing the sample.",
        "cost": "$20",
        "duration": "5 minutes"
    },
    "Ultrasound": {
        "purpose": "Visualize internal organs and structures.",
        "category": "Radiology",
        "procedure": "A gel is applied, and a probe is moved over the area.",
        "preparation": "May need to drink water or fast beforehand.",
        "cost": "$150",
        "duration": "30 minutes"
    },
    "ECG (Electrocardiogram)": {
        "purpose": "Measure the electrical activity of the heart.",
        "category": "Cardiology",
        "procedure": "Electrodes are attached to the skin to record activity.",
        "preparation": "Avoid caffeine before the test.",
        "cost": "$75",
        "duration": "15 minutes"
    },
    "Allergy Test": {
        "purpose": "Identify specific allergens causing reactions.",
        "category": "Immunology",
        "procedure": "Skin pricking or blood test is conducted.",
        "preparation": "Avoid antihistamines for a few days prior.",
        "cost": "$200",
        "duration": "30 minutes"
    },
    "Liver Function Test": {
        "purpose": "Assess the health and functionality of the liver.",
        "category": "Pathology",
        "procedure": "Blood sample is taken for analysis.",
        "preparation": "Avoid eating or drinking for 8-10 hours.",
        "cost": "$60",
        "duration": "10 minutes"
    },
    "Thyroid Test": {
        "purpose": "Check thyroid hormone levels.",
        "category": "Endocrinology",
        "procedure": "Blood sample is collected for testing.",
        "preparation": "No specific preparation needed.",
        "cost": "$40",
        "duration": "10 minutes"
    }
}
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/test_details")
def test_details():
    return render_template("testdetails.html", test_list=list(tests.keys()))

@app.route("/get_test_details/<test_name>")
def get_test_details(test_name):
    details = tests.get(test_name, {})
    return jsonify(details)

    

# Login Route
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
        
#         # Check if user exists
#         user = users_collection.find_one({'email': email})
#         if user and bcrypt.check_password_hash(user['password'], password):
#             session['user'] = user['name']
#             flash('Login successful!', 'success')
#             return redirect(url_for('home2'))
#         else:
#             flash('Invalid credentials. Try again!', 'danger')
#             return redirect(url_for('register'))
#     return render_template('login.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if user exists in the database
        user = users_collection.find_one({'email': email})
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user'] = user['name']
            return redirect(url_for('home2', message="success"))  # Pass message as query parameter
        else:
            return redirect(url_for('login', message="failure"))  # Pass message as query parameter

    # Get the message from query parameters (if any)
    message = request.args.get('message', None)
    return render_template('login.html', message=message)

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Check if email already exists
        if users_collection.find_one({'email': email}):
            flash('Email already registered. Try logging in!', 'warning')
            return redirect(url_for('login'))
        
        # Hash password and save to MongoDB
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        users_collection.insert_one({'name': name, 'email': email, 'password': hashed_password})
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('home2'))
    
    return render_template('register.html')

#appointment route
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('appointment.html') # Show appointment form
    else:
        flash('You need to log in first!', 'danger')
        return render_template('appointment.html')


        


# @app.route('/book_appointment', methods=['POST'])
# def book_appointment():
#     if 'user' in session:
#         name = session['user']
#         email = request.form['email']
#         date = request.form['date']
#         time = request.form['time']
#         doctor = request.form['doctor']
#         phone_number = request.form['phone_number']
#         description = request.form['description']
        
#         # Store the appointment in the MongoDB appointments collection
#         appointments_collection.insert_one({
#             'name': name,
#             'email': email,
#             'date': date,
#             'time': time,
           
#             'doctor': doctor,
#             'phone_number': phone_number,
#             'description': description,
#             'created_at': datetime.now()
#         })
        
#         flash('Appointment booked successfully!', 'success')
#         return redirect(url_for('appointments'))
#     else:
#         flash('You need to log in first!', 'danger')
#         return redirect(url_for('appointments'))

@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    if 'user' in session:
        name = session['user']
        email = request.form['email']
        date = request.form['date']
        time = request.form['time']
        test = request.form['test']
        phone_number = request.form['phone_number']
        description = request.form['description']
        
        # Store the appointment in the MongoDB appointments collection
        appointments_collection.insert_one({
            'name': name,
            'email': email,
            'date': date,
            'time': time,
            'test': test,
            'phone_number': phone_number,
            'description': description,
            'created_at': datetime.now()
        })

        # Store appointment details in session for the thank-you page
        session['appointment_details'] = {
            'name': name,
            'email': email,
            'date': date,
            'time': time,
            'test': test,
            'phone_number': phone_number,
            'description': description
        }

        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('thank_you'))
    else:
        flash('You need to log in first!', 'danger')
        return redirect(url_for('thank_you'))
    

@app.route('/thank_you')
def thank_you():
    if 'appointment_details' in session:
        details = session.pop('appointment_details')  # Remove after use for security
        return render_template('response.html', details=details)
    else:
        
        return render_template('appointment.html')  
    


# Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


def predict_disease(symptoms):
    # Simple symptom to disease mapping
    disease_dict = {
  "fever cough": "Flu or Chest Infection",
        "headache nausea": "Migraine",
        "chest pain shortness of breath": "Heart Attack",
        "stomach pain nausea": "Food Poisoning",
        "fatigue weakness": "Anemia",
        "rash joint pain": "Lupus",
        "difficulty breathing wheezing": "Asthma",
        "painful urination blood in urine": "Urinary Tract Infection",
        "fever chills headache": "Malaria",
        "abdominal pain yellow skin": "Hepatitis",
        "joint pain swelling": "Rheumatoid Arthritis",
        "nausea dizziness": "Vertigo",
        "persistent cough weight loss": "Tuberculosis",
        "bloody stool diarrhea": "Colorectal Cancer",
        "blurry vision headaches": "Diabetes",
        "swollen lymph nodes fever": "Lymphoma",
        "severe headache stiff neck": "Meningitis",
        "swelling in legs high blood pressure": "Kidney Disease",
        "night sweats cough": "Pneumonia",
        "yellowing of eyes dark urine": "Hepatitis",
        "chronic back pain tingling": "Sciatica",
        "sore throat swollen glands": "Strep Throat"
    }
    
    symptoms = symptoms.lower().strip()
    for symptom_key, disease in disease_dict.items():
        if symptom_key in symptoms:
            return disease
    return "Disease not identified. Please consult a doctor."


def prevention_method(disease):
    prevention_dict = {
       "Flu or Chest Infection": "Get vaccinated, avoid contact with sick individuals, wash hands regularly.",
        "Migraine": "Maintain a regular sleep schedule, reduce stress, avoid known triggers.",
        "Heart Attack": "Exercise regularly, eat a heart-healthy diet, avoid smoking.",
        "Food Poisoning": "Wash hands before eating, avoid undercooked food, drink clean water.",
        "Anemia": "Eat iron-rich foods, avoid caffeine with meals, take iron supplements if prescribed.",
        "Lupus": "Manage stress, avoid sun exposure, take prescribed medications.",
        "Asthma": "Avoid triggers, use prescribed inhalers, keep the airways open.",
        "Urinary Tract Infection": "Drink plenty of water, practice good hygiene, urinate after interlab.",
        "Malaria": "Use insect repellent, sleep under mosquito nets, take anti-malarial medications.",
        "Hepatitis": "Get vaccinated, avoid sharing needles, avoid alcohol.",
        "Rheumatoid Arthritis": "Take prescribed medications, exercise regularly, maintain a healthy weight.",
        "Vertigo": "Avoid sudden head movements, stay hydrated, manage stress.",
        "Tuberculosis": "Follow prescribed medication regimen, avoid contact with infected individuals, wear a mask.",
        "Colorectal Cancer": "Get screened regularly, eat a high-fiber diet, exercise regularly.",
        "Diabetes": "Maintain a healthy weight, exercise regularly, monitor blood sugar levels.",
        "Lymphoma": "Consult a doctor for early detection, manage stress, avoid smoking.",
        "Meningitis": "Get vaccinated, avoid close contact with infected individuals, practice good hygiene.",
        "Kidney Disease": "Monitor blood pressure, stay hydrated, avoid excessive salt intake.",
        "Pneumonia": "Get vaccinated, avoid smoking, practice good hygiene, stay away from infected individuals.",
        "Sciatica": "Exercise regularly, maintain good posture, avoid heavy lifting.",
        "Strep Throat": "Wash hands regularly, avoid close contact with infected individuals, finish prescribed antibiotics."
    }
    
    return prevention_dict.get(disease, "Consult a healthcare professional for prevention tips.")

def test_method(disease):
    test_dict = {
        "Flu or Chest Infection": "Rapid Influenza Diagnostic Test (RIDT), Chest X-ray, Sputum Culture",
        "Migraine": "MRI, CT scan, Blood tests",
        "Heart Attack": "Electrocardiogram (ECG), Blood tests (Troponin levels), Coronary Angiogram",
        "Food Poisoning": "Stool Culture, Blood tests",
        "Anemia": "Complete Blood Count (CBC), Iron studies",
        "Lupus": "Antinuclear Antibody (ANA) test, Blood tests",
        "Asthma": "Spirometry, Peak Flow Measurement, Blood tests",
        "Urinary Tract Infection": "Urine Culture, Urinalysis",
        "Malaria": "Blood Smear, Rapid Diagnostic Test (RDT)",
        "Hepatitis": "Hepatitis B Surface Antigen (HBsAg), Hepatitis C Antibody Test",
        "Rheumatoid Arthritis": "Rheumatoid Factor (RF), Anti-CCP Antibody Test, X-rays",
        "Vertigo": "MRI, CT scan, Vestibular Testing",
        "Tuberculosis": "Tuberculin Skin Test (TST), Chest X-ray, Sputum Culture",
        "Colorectal Cancer": "Colonoscopy, Fecal Occult Blood Test (FOBT), Biopsy",
        "Diabetes": "Fasting Blood Sugar Test, HbA1c Test, Oral Glucose Tolerance Test",
        "Lymphoma": "Biopsy, Blood tests, PET scan, CT scan",
        "Meningitis": "Lumbar Puncture (Spinal Tap), Blood Culture, CT scan",
        "Kidney Disease": "Urinalysis, Kidney Function Tests (Creatinine, GFR), Ultrasound",
        "Pneumonia": "Chest X-ray, Sputum Culture, Blood tests",
        "Sciatica": "MRI, CT scan, X-ray",
        "Strep Throat": "Rapid Antigen Test, Throat Culture"
    }
    
    return test_dict.get(disease, "Consult a healthcare professional for the necessary test.")


@app.route('/symptoms', methods=['GET', 'POST'])
def symptoms():
    predicted_disease = None
    prevention = None
    test_methods = None
    symptoms_input = session.get('symptoms_input', '')  # Retrieve previous input from session

    if request.method == 'POST':
        symptoms_input = request.form['symptoms']
        session['symptoms_input'] = symptoms_input  # Store input in session
        predicted_disease = predict_disease(symptoms_input)
        prevention = prevention_method(predicted_disease)
        test_methods = test_method(predicted_disease)
    
    return render_template(
        'symptoms.html',
        symptoms_input=symptoms_input,
        predicted_disease=predicted_disease,
        prevention=prevention,
        test_methods=test_methods
    )

quiz_data = [
    {"question": "Do you experience frequent headaches? Click on Yes or No", "id": "headache", "options": ["Yes", "No"]},
    {"question": "Do you have a history of heart disease? Click on Yes or No", "id": "heart_disease", "options": ["Yes", "No"]},
    {"question": "Do you exercise regularly? Click on Yes or No", "id": "exercise", "options": ["Yes", "No"]},
    {"question": "Are you a smoker? Click on Yes or No", "id": "smoker", "options": ["Yes", "No"]},
    {"question": "Do you experience shortness of breath? Click on Yes or No", "id": "breathing", "options": ["Yes", "No"]},
    {"question": "Do you have any family history of diabetes? Click on Yes or No", "id": "family_diabetes", "options": ["Yes", "No"]},
    {"question": "Do you have any digestive issues (e.g., bloating, pain)? Click on Yes or No", "id": "digestive_issues", "options": ["Yes", "No"]},
]

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        # Get user responses
        answers = {}
        for question in quiz_data:
            answer = request.form.get(question['id'])
            answers[question['id']] = answer
        
       
   
        
        
        recommended_tests = recommend_tests(answers)
        
        return render_template('result.html', recommended_tests=recommended_tests, answers=answers)
    
    return render_template('quiz.html', quiz_data=quiz_data)


def recommend_tests(answers):
    tests = []
    
    # Heart-related tests
    if answers['heart_disease'] == 'Yes' and answers['breathing'] == 'Yes':
        tests.append("Electrocardiogram (ECG), Coronary Angiogram, Blood Tests (Cholesterol, Lipids)")
    
    # Headache-related tests
    if answers['headache'] == 'Yes':
        tests.append("MRI, CT scan, Blood Pressure Monitoring")
    
    # Diabetes-related tests
    if answers['family_diabetes'] == 'Yes' or answers['exercise'] == 'No':
        tests.append("Fasting Blood Sugar Test, HbA1c Test, Oral Glucose Tolerance Test")
    
    # Smoking-related tests
    if answers['smoker'] == 'Yes':
        tests.append("Chest X-ray, Spirometry, Blood tests (for Carbon Monoxide levels)")
    
    # Digestive issues-related tests
    if answers['digestive_issues'] == 'Yes':
        tests.append("Stool Culture, Endoscopy, Liver Function Tests")
    
    # General health check-up
    if not tests:
        tests.append("Complete Blood Count (CBC), Liver Function Test, Kidney Function Test")
    
    return tests


# ////admin/////

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']


        if username == "admin" and password == "admin123":
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials. Try again.', 'danger')

    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        flash('You need to log in as admin!', 'danger')
        return redirect(url_for('admin_login'))

 
    users = users_collection.find()
    appointments = appointments_collection.find()

    return render_template('admin_dashboard.html', users=users, appointments=appointments)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash('Admin logged out successfully.', 'info')
    return redirect(url_for('admin_login'))



@app.route('/admin/appointments/delete/<id>')
def delete_appointment(id):
    if 'admin' not in session:
        flash('You need to log in as admin!', 'danger')
        return redirect(url_for('admin_login'))

    appointments_collection.delete_one({'_id': ObjectId(id)})
    flash('Appointment deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route("/chat")
def chat():
  
    return render_template('chatbot.html') 
# Contact Route
@app.route('/contact')
def contact():
    # Renders the contact form template
    return render_template('contact.html')


# @app.route('/submit_message', methods=['POST'])
# def submit_message():
#     # Retrieve form data
#     name = request.form.get('name')
#     email = request.form.get('email')
#     message = request.form.get('message')

#     # Basic validation
#     if not name or not email or not message:
#         flash("All fields are required!", "error")
#         return redirect('home2')  # Redirect back to the contact page

#     # Log the message (or handle it in any other way, like storing in a database or sending an email)
#     print(f"New Message Received:\nName: {name}\nEmail: {email}\nMessage: {message}")

#     # Feedback to the user
#     flash("Your message has been sent successfully!", "success")
#     return redirect('/')  # Redirect back to the contact page




if __name__ == '__main__':
    app.run(debug=True)
