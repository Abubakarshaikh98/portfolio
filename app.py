from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'cyberpunk_secret_key'  # Replace with a secure secret key in production

# --- profile data ---
PROFILE_DATA = {
    "name": "Abubakar Shaikh",
    "title": "AI & Data Science Student",
    "tagline": "AI & Data Science | Machine Learning | Python Developer | Freelancer",
    "summary": "I am an AI & Data Science student with knowledge of Python, Machine Learning, Data Science and Artificial Intelligence. I enjoy building practical projects and learning new technologies.",
    "stats": [
    {"label": "Certifications", "value": 2, "suffix": "+"},
    {"label": "ML Algorithms", "value": 12, "suffix": "+"},
    {"label": "Projects", "value": 5, "suffix": ""}
],
"social_links": {
    "linkedin": "https://www.linkedin.com/in/abubakar-shaikh-ds/",
    "github": "https://github.com/Abubakarshaikh98",
    "kaggle": "https://www.kaggle.com/abubakarshaikh10",
    "fiverr": "https://www.fiverr.com/s/vbQmjz1",
    "email": "bakarshaikh987@gmail.com",
    "whatsapp": "https://wa.me/+923101117872"
},
"hero_strings": [
    "AI & Data Science Student",
    "Machine Learning Enthusiast",
    "Python Developer",
    "Data Science Enthusiast",
    "AI Enthusiast",
    "Freelancer"
],
"skills": [
    "Python",
    "Machine Learning",
    "Data Science",
    "Artificial Intelligence",
    "Data Analysis",
    "Data Preprocessing",
    "Feature Engineering",
    "Data Visualization",
    "Pandas",
    "NumPy",
    "Matplotlib",
    "Scikit-learn",
    "SQL",
    "Flask",
    "Git",
    "GitHub",
    "Jupyter Notebook",
    "Google Colab",
    "Kaggle"
],
"services": [
    {
        "title": "Machine Learning",
        "icon": "fa-brain",
        "desc": "Machine learning models, predictive analysis, and data-driven solutions."
    },
    {
        "title": "Data Analysis",
        "icon": "fa-chart-line",
        "desc": "Data cleaning, analysis, visualization, and insights using Python."
    },
    {
        "title": "Python Development",
        "icon": "fa-code",
        "desc": "Python-based applications, automation, and data science solutions."
    },
    {
        "title": "AI Solutions",
        "icon": "fa-robot",
        "desc": "AI-powered solutions and intelligent applications for real-world problems."
    }
],
"certifications": [
  {
    "name": "Artificial Intelligence and Data Science",
    "issuer": "Saylani Mass Training Programme (Saylani Welfare International Trust)",
    "year": "2026",
    "credential_url": ""
  },
  {
    "name": "Advanced Python Programming & Applications",
    "issuer": "NAVTTC (National Vocational & Technical Training Commission)",
    "year": "2026",
    "credential_url": ""
  }
],
"projects": [
  {
    "name": "House Price Prediction",
    "description": "A machine learning regression project that predicts house prices based on property features.",
    "technologies": ["Python", "Pandas", "NumPy", "Scikit-learn", "Machine Learning"],
    "github": "https://github.com/Abubakarshaikh98/Data_science_project",
    "demo": ""
  },
  {
    "name": "Customer Segmentation",
    "description": "An unsupervised machine learning project that segments customers into groups using K-Means clustering.",
    "technologies": ["Python", "Pandas", "NumPy", "Scikit-learn", "K-Means"],
    "github": "https://github.com/Abubakarshaikh98/Data_science_project",
    "demo": ""
  }
]
}

# home route

@app.route("/")
def home():
    return render_template("home.html", profile=PROFILE_DATA)


# --- Database Initialization ---

def init_db():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()

# Contact Form route

@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    if not name or not email or not message:
        flash("Please fill all fields.")
    return redirect(url_for("home"))

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO messages (name, email, message)
        VALUES (?, ?, ?)
    """, (name, email, message))

    connection.commit()
    connection.close()

    flash("Your message has been sent successfully!", "success")

    return redirect(url_for("home"))

# --- API Endpoints ---
@app.route('/api/profile')
def get_profile():
    return jsonify({
            "name": PROFILE_DATA["name"],
            "title": PROFILE_DATA["title"],
            "summary": PROFILE_DATA["summary"],
            "social_links": PROFILE_DATA["social_links"],
        })

@app.route('/api/services')
def get_services():
    return jsonify(PROFILE_DATA["services"])

@app.route('/api/projects')
def get_projects():
    return jsonify(PROFILE_DATA["projects"])

@app.route('/api/certifications')
def get_certifications():
    return jsonify(PROFILE_DATA["certifications"])

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
