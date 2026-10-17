import os
from PIL import Image
import sqlite3
import psycopg
from psycopg.rows import dict_row
from supabase import create_client
import uuid
Image.MAX_IMAGE_PIXELS = 20_000_000
from dotenv import load_dotenv
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
load_dotenv()
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename 

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# secret_key flash messages ("Message sent!") ke liye chahiye.
# PythonAnywhere par Web tab -> Environment variables me SECRET_KEY set karo.
app.secret_key = os.environ["SECRET_KEY"]

SUPABASE_URL = os.environ.get(
    "SUPABASE_URL",
    "https://djqdezsijblkxbimqsyd.supabase.co"
)

SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY")

supabase = None

if SUPABASE_SECRET_KEY:
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_SECRET_KEY
    )

SUPABASE_BUCKET = "portfolio-uploads"

def upload_to_supabase(file, folder):
    if not supabase:
        raise RuntimeError("Supabase Storage is not configured.")

    filename = secure_filename(file.filename)

    if not filename:
        raise ValueError("Invalid filename.")

    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    storage_path = f"{folder}/{unique_filename}"

    file_bytes = file.read()

    supabase.storage.from_(SUPABASE_BUCKET).upload(
        path=storage_path,
        file=file_bytes,
        file_options={
            "content-type": file.mimetype or "application/octet-stream",
            "upsert": "false"
        }
    )

    return supabase.storage.from_(SUPABASE_BUCKET).get_public_url(
        storage_path
    )

# database.db ka poora rasta (taake PythonAnywhere par bhi sahi file mile)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")



class DatabaseConnection:
    def __init__(self, connection, is_postgres=False):
        self.connection = connection
        self.is_postgres = is_postgres

    @property
    def row_factory(self):
        return getattr(self.connection, "row_factory", None)

    @row_factory.setter
    def row_factory(self, value):
        if not self.is_postgres:
            self.connection.row_factory = value

    def execute(self, query, params=()):
        if self.is_postgres:
            query = query.replace("?", "%s")
        return self.connection.execute(query, params)

    def commit(self):
        return self.connection.commit()

    def close(self):
        return self.connection.close()


def get_db_connection():
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        connection = psycopg.connect(
            database_url,
            row_factory=dict_row,
            connect_timeout=10
        )
        return DatabaseConnection(connection, is_postgres=True)

    connection = sqlite3.connect(DB_PATH)
    return DatabaseConnection(connection)


# -----------------------------------------------------
#  1) TUMHARA CONTENT
#  Yahan sirf text badlo. Quotes " " aur commas , na hatao.
#  Project me github ya demo khali "" ho to button nahi dikhta.
# -----------------------------------------------------
PROFILE_DATA = {
    "name": "Abubakar Shaikh",
    "title": "AI & Data Science Professional",
    "lead": "Building intelligent solutions with Machine Learning, Deep Learning, Generative AI and AI Automation.",
    "summary": "I create practical AI applications and automation workflows to solve real-world problems and make technology work smarter for people.",
    "resume": "resume.pdf",  # Resume ke liye: file ko static folder me rakho, phir yahan likho "resume.pdf"
    "social_links": {
        "linkedin": "https://www.linkedin.com/in/abubakar-shaikh-ds/",
        "github": "https://github.com/Abubakarshaikh98",
        "kaggle": "https://www.kaggle.com/abubakarshaikh10",
        "fiverr": "https://www.fiverr.com/s/vbQmjz1",
        "email": "bakarshaikh987@gmail.com",
        "whatsapp": "https://wa.me/+923101117872",
    },
    "skills": [
        {"name": "Python", "icon": "fa-brands fa-python"},
        {"name": "Machine Learning", "icon": "fa-solid fa-brain"},
        {"name": "Deep Learning", "icon": "fa-solid fa-network-wired"},
        {"name": "Generative AI", "icon": "fa-solid fa-wand-magic-sparkles"},
        {"name": "NLP", "icon": "fa-solid fa-comments"},
        {"name": "Computer Vision", "icon": "fa-solid fa-eye"},
        {"name": "n8n", "icon": "fa-solid fa-diagram-project"},
        {"name": "APIs & Integration", "icon": "fa-solid fa-plug"},
        {"name": "Git & GitHub", "icon": "fa-brands fa-github"},
        {"name": "Docker", "icon": "fa-brands fa-docker"},
        {"name": "Streamlit", "icon": "fa-solid fa-chart-line"},
        {"name": "Google Cloud", "icon": "fa-brands fa-google"},
    ],
    "services": [
        {"title": "Machine Learning Solutions", "icon": "fa-brain",
         "points": ["Model development & training", "Data analysis & prediction", "Custom ML solutions"]},
        {"title": "AI Automation", "icon": "fa-gears",
         "points": ["n8n workflow automation", "Email & CRM integrations", "Business process automation"]},
        {"title": "AI Chatbots & Agents", "icon": "fa-robot",
         "points": ["LLM integration", "Custom chatbot development", "AI agents for business"]},
        {"title": "AI Integration & APIs", "icon": "fa-plug",
         "points": ["OpenAI / LLM integration", "Third-party APIs", "Web applications & dashboards"]},
    ],
    # Mockup shows Coursera / Udemy; your old data had these two. Edit to the ones you really hold.
    
"certifications": [
    {
        "name": "Artificial Intelligence and Data Science",
        "issuer": "Saylani Mass Training Programme (SMIT)",
        "year": "2026",
        "credential_url": "",
        "image": "static/images/Smit.png"
    },
    {
        "name": "Advanced Python Programming & Applications",
        "issuer": "NAVTTC",
        "year": "2026",
        "credential_url": "",
        "image": "static/images/python-certificate.png"
    },
],

    # featured=True -> "Featured Projects", False -> "More Projects". Empty github/demo -> button hidden.
    "projects": [
        {"name": "Mind Predict AI", "category": "Machine Learning", "icon": "fa-brain", "featured": True,
         "description": "A mental health score prediction web application using ML models.", "github": "", "demo": "https://mind-predict-ai.vercel.app/",
         "image": "static/images/mind-predict-ai.png",},
        {"name": "AI Face Recognition System", "category": "Computer Vision · Deep Learning", "icon": "fa-face-smile", "featured": True,
         "description": "Face recognition, attendance tracking and emotion detection system.", "github": "https://github.com/Abubakarshaikh98/AI_Face_Emotion", "demo": "",
         "image": "static/images/ai-face-recognition.png",},
        {"name": "AI Lead Management & Automation", "category": "n8n · AI Automation", "icon": "fa-diagram-project", "featured": True,
         "description": "Automated lead capture, AI analysis, classification and follow-up using n8n.", "github": "", "demo": "",
         "image": "static/images/ai-lead-management.png",},
        {"name": "AI Document Assistant", "category": "Generative AI · LLMs", "icon": "fa-file-lines", "featured": True,
         "description": "Chat with your documents using advanced LLMs and embeddings.", "github": "", "demo": "",
         "image": "static/images/ai-document-assistant.png",},
        {"name": "Cardiovascular Disease Prediction", "category": "Machine Learning", "icon": "fa-heart-pulse", "featured": False,
         "description": "Predict cardiovascular disease risk using machine learning with patient health data.",
         "github": "https://github.com/Abubakarshaikh98/Data_science_project", "demo": ""},
        {"name": "Customer Segmentation", "category": "Machine Learning", "icon": "fa-users", "featured": False,
         "description": "Segment customers using clustering algorithms for better marketing.",
         "github": "https://github.com/Abubakarshaikh98/Data_science_project", "demo": ""},
    ],
}


# -----------------------------------------------------
#  2) DATABASE  -  messages ka table banata hai
# -----------------------------------------------------
def init_db():
    if os.environ.get("DATABASE_URL"):
        return
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)
    con.commit()
    con.close()

init_db()   # website start hote hi table ban jata hai

# -----------------------------------------------------
# PROJECTS DATABASE TABLE
# -----------------------------------------------------
def init_projects_table():
    if os.environ.get("DATABASE_URL"):
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                github TEXT DEFAULT '',
                demo TEXT DEFAULT '',
                image TEXT DEFAULT '',
                featured INTEGER DEFAULT 0
            )
        """)

        # New skills table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT DEFAULT '',
            level TEXT DEFAULT ''
            )
        """)
        conn.commit()
    finally:
        conn.close()


init_projects_table()


def init_certifications_table():
    if os.environ.get("DATABASE_URL"):
        return

    conn = sqlite3.connect(DB_PATH)

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS certifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                issuer TEXT NOT NULL,
                year TEXT DEFAULT '',
                credential_url TEXT DEFAULT '',
                image TEXT DEFAULT ''
            )
        """)
        conn.commit()
    finally:
        conn.close()


init_certifications_table()

# -----------------------------------------------------
#  3) PAGES (routes)
# -----------------------------------------------------

# Home page: home.html ko PROFILE_DATA bhej deta hai


@app.route("/")
def home():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row

    try:
        saved_projects = conn.execute(
            "SELECT * FROM projects ORDER BY id DESC"
        ).fetchall()

        saved_certifications = conn.execute(
            "SELECT * FROM certifications ORDER BY id DESC"
        ).fetchall()

        
        saved_skills = conn.execute(
            "SELECT * FROM skills ORDER BY id DESC"
        ).fetchall()

    finally:
        conn.close()

    profile = dict(PROFILE_DATA)

    profile["projects"] = PROFILE_DATA["projects"] + [
        dict(project) for project in saved_projects
    ]

    profile["certifications"] = PROFILE_DATA["certifications"] + [
        dict(certification) for certification in saved_certifications
    ]
    
    
    profile["skills"] = PROFILE_DATA["skills"] + [
        dict(skill) for skill in saved_skills
    ]

    print("PUBLIC SKILLS:", profile["skills"])
    return render_template("home.html", profile=profile)


# Contact form: jab koi "Send Message" dabaye
@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()
    spam_field = request.form.get("website", "")   # chhupa hua field, sirf bots bharte hain

    # Bot ne chhupa field bhara ho to chup-chap wapas bhej do
    if spam_field:
        return redirect(url_for("home") + "#contact")

    # Check: sab fields bhari hui hain?
    if not name or not email or not message:
        flash("Please fill all fields.", "error")
        return redirect(url_for("home") + "#contact")

    # Database me message save karo
    con = get_db_connection()
    try:
        con.execute(
            "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
            (name, email, message),
        )
        con.commit()
        flash("Your message has been sent successfully!", "success")
    except (sqlite3.Error, psycopg.Error):
        flash("Unable to save your message. Please try again.", "error")
    finally:
        con.close()

    return redirect(url_for("home") + "#contact")


# Galat address par 404 page dikhao
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", profile=PROFILE_DATA), 404


# Chhote API links (optional): /api/projects wagaira

@app.route("/api/projects")
def api_projects():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row

    try:
        saved_projects = conn.execute(
            "SELECT * FROM projects ORDER BY id DESC"
        ).fetchall()
    finally:
        conn.close()

    projects = PROFILE_DATA["projects"] + [
        dict(project) for project in saved_projects
    ]

    return jsonify(projects)


@app.route("/api/certifications")
def api_certifications():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row

    try:
        saved_certifications = conn.execute(
            "SELECT * FROM certifications ORDER BY id DESC"
        ).fetchall()
    finally:
        conn.close()

    certifications = PROFILE_DATA["certifications"] + [
        dict(certification) for certification in saved_certifications
    ]

    return jsonify(certifications)


# Computer par chalane ke liye: python app.py
# ---------------- ADMIN LOGIN ----------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        expected_username = os.environ.get("ADMIN_USERNAME", "")
        password_hash = os.environ.get("ADMIN_PASSWORD_HASH", "")

        if (
            username == expected_username
            and password_hash
            and check_password_hash(password_hash, password)
        ):
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("admin/login.html")


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("admin_login"))


@app.route("/admin")
def admin_dashboard():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    return render_template("admin/dashboard.html")

@app.route("/admin/messages")
def admin_messages():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row

    try:
        messages = conn.execute(
            "SELECT id, name, email, message FROM messages ORDER BY id DESC"
        ).fetchall()
    finally:
        conn.close()

    return render_template("admin/messages.html", messages=messages)

@app.route("/admin/projects")
def admin_projects():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row

    try:
        saved_projects = conn.execute(
            "SELECT * FROM projects ORDER BY id DESC"
        ).fetchall()
    finally:
        conn.close()

    projects = PROFILE_DATA["projects"] + [
        dict(project) for project in saved_projects
    ]

    return render_template(
        "admin/projects.html",
        projects=projects
    )


@app.route("/admin/projects/add", methods=["GET", "POST"])
def admin_add_project():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        github = request.form.get("github", "").strip()
        demo = request.form.get("demo", "").strip()
        image_file = request.files.get("image")
        image = ""
        featured = request.form.get("featured") == "yes"

        if not name or not category or not description:
            flash("Please fill all required fields.", "error")
            return render_template("admin/add_project.html")

        if not image_file or not image_file.filename:
            flash("Please select a project image.", "error")
            return render_template("admin/add_project.html")

        try:
            img = Image.open(image_file.stream)
            img.verify()

            image_file.stream.seek(0)
            img = Image.open(image_file.stream)
            image_format = img.format

            allowed_formats = {
                "JPEG": "jpg",
                "PNG": "png",
                "WEBP": "webp",
                "GIF": "gif"
            }

            if image_format not in allowed_formats:
                flash("Please upload a JPG, PNG, WEBP, or GIF image.", "error")
                return render_template("admin/add_project.html")
            image_file.stream.seek(0)

            if supabase:
                image_file.filename = (
                    f"{uuid.uuid4().hex}.{allowed_formats[image_format]}"
                )
                image = upload_to_supabase(image_file, "projects")
            else:
                filename = f"{uuid.uuid4().hex}.{allowed_formats[image_format]}"
                upload_dir = os.path.join(app.static_folder, "uploads")
                os.makedirs(upload_dir, exist_ok=True)

                img = Image.open(image_file.stream)
                img.save(os.path.join(upload_dir, filename))

                image = f"uploads/{filename}"

        except (Image.UnidentifiedImageError, Image.DecompressionBombError, OSError):
            flash("Invalid image file. Please choose a valid image.", "error")
            return render_template("admin/add_project.html")

        conn = get_db_connection()
        try:
            conn.execute("""
                INSERT INTO projects
                (name, category, description, github, demo, image, featured)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                name, category, description,
                github, demo, image, featured
            ))
            conn.commit()
        finally:
            conn.close()

        flash("Project saved successfully!", "success")
        return redirect(url_for("admin_projects"))

    return render_template("admin/add_project.html")

@app.route("/admin/projects/delete/<int:project_id>", methods=["POST"])
def admin_delete_project(project_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    try:
        conn.execute(
            "DELETE FROM projects WHERE id = ?",
            (project_id,)
        )
        conn.commit()
    finally:
        conn.close()

    flash("Project deleted successfully!", "success")
    return redirect(url_for("admin_projects"))

@app.route("/admin/projects/edit/<int:project_id>", methods=["GET", "POST"])
def admin_edit_project(project_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row

    try:
        project = conn.execute(
            "SELECT * FROM projects WHERE id = ?",
            (project_id,)
        ).fetchone()

        if project is None:
            flash("Project not found.", "error")
            return redirect(url_for("admin_projects"))

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            category = request.form.get("category", "").strip()
            description = request.form.get("description", "").strip()
            github = request.form.get("github", "").strip()
            demo = request.form.get("demo", "").strip()
            image = request.form.get("image", "").strip()
            featured = request.form.get("featured") == "yes"

            if not name or not category or not description:
                flash("Please fill all required fields.", "error")
                return render_template(
                    "admin/edit_project.html",
                    project=project
                )

            conn.execute("""
                UPDATE projects
                SET name = ?, category = ?, description = ?,
                    github = ?, demo = ?, image = ?, featured = ?
                WHERE id = ?
            """, (
                name, category, description, github, demo,
                image, featured, project_id
            ))
            conn.commit()

            flash("Project updated successfully!", "success")
            return redirect(url_for("admin_projects"))

        return render_template(
            "admin/edit_project.html",
            project=project
        )
    finally:
        conn.close()

@app.route("/admin/certifications")
def admin_certifications():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row

    try:
        saved_certifications = conn.execute(
            "SELECT * FROM certifications ORDER BY id DESC"
        ).fetchall()
    finally:
        conn.close()

    certifications = PROFILE_DATA["certifications"] + [
        dict(certification) for certification in saved_certifications
    ]

    return render_template(
        "admin/certifications.html",
        certifications=certifications
    )


@app.route("/admin/skills")
def admin_skills():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row

    try:
        skills = conn.execute(
            "SELECT * FROM skills ORDER BY id DESC"
        ).fetchall()
    finally:
        conn.close()

    return render_template(
        "admin/skills.html",
        skills=skills
    )


@app.route("/admin/skills/add", methods=["POST"])
def admin_add_skill():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    level = request.form.get("level", "").strip()

    if not name:
        flash("Please enter a skill name.", "error")
        return redirect(url_for("admin_skills"))

    conn = get_db_connection()

    try:
        conn.execute(
            "INSERT INTO skills (name, category, level) VALUES (?, ?, ?)",
            (name, category, level)
        )
        conn.commit()
    finally:
        conn.close()

    flash("Skill added successfully!", "success")
    return redirect(url_for("admin_skills"))


@app.route("/admin/skills/delete/<int:skill_id>", methods=["POST"])
def admin_delete_skill(skill_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    try:
        conn.execute(
            "DELETE FROM skills WHERE id = ?",
            (skill_id,)
        )
        conn.commit()
    finally:
        conn.close()

    flash("Skill deleted successfully!", "success")
    return redirect(url_for("admin_skills"))


@app.route("/admin/certifications/add", methods=["GET", "POST"])
def admin_add_certification():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        issuer = request.form.get("issuer", "").strip()
        year = request.form.get("year", "").strip()
        credential_url = request.form.get("credential_url", "").strip()

        uploaded_file = request.files.get("image")
        image = ""

        if not name or not issuer:
            flash("Please enter the certificate name and issuer.", "error")
            return render_template("admin/add_certification.html")

        
        if uploaded_file and uploaded_file.filename:
            allowed_extensions = {"png", "jpg", "jpeg", "webp"}
            original_name = secure_filename(uploaded_file.filename)
            extension = (
                original_name.rsplit(".", 1)[-1].lower()
                if "." in original_name else ""
            )

            if extension not in allowed_extensions:
                flash(
                    "Please upload a PNG, JPG, JPEG, or WEBP image.",
                    "error"
                )
                return render_template("admin/add_certification.html")

            try:
                with Image.open(uploaded_file.stream) as img:
                    actual_format = img.format
                    img.verify()

                format_extensions = {
                    "PNG": {"png"},
                    "JPEG": {"jpg", "jpeg"},
                    "WEBP": {"webp"}
                }

                if extension not in format_extensions.get(
                    actual_format, set()
                ):
                    raise ValueError("Image format does not match.")

                uploaded_file.stream.seek(0)

            except (OSError, ValueError, Image.DecompressionBombError):
                flash(
                    "Invalid image file. Please upload a valid PNG, JPG, JPEG, or WEBP image.",
                    "error"
                )
                return render_template("admin/add_certification.html")

            if supabase:
                uploaded_file.filename = (
                    f"{uuid.uuid4().hex}.{extension}"
                )
                image = upload_to_supabase(
                uploaded_file, "certifications"
                )
            else:
                filename = f"{uuid.uuid4().hex}.{extension}"
                upload_folder = os.path.join(
                    app.root_path, "static", "uploads"
                )
                os.makedirs(upload_folder, exist_ok=True)

                uploaded_file.save(
                os.path.join(upload_folder, filename)
                )
                image = f"static/uploads/{filename}"
        conn = get_db_connection()

        try:
            conn.execute("""
                INSERT INTO certifications
                (name, issuer, year, credential_url, image)
                VALUES (?, ?, ?, ?, ?)
            """, (name, issuer, year, credential_url, image))

            conn.commit()
        finally:
            conn.close()

        flash("Certification saved successfully!", "success")
        return redirect(url_for("admin_certifications"))

    return render_template("admin/add_certification.html")



@app.route("/admin/certifications/delete/<int:certification_id>", methods=["POST"])
def admin_delete_certification(certification_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    try:
        conn.execute(
            "DELETE FROM certifications WHERE id = ?",
            (certification_id,)
        )
        conn.commit()
    finally:
        conn.close()

    flash("Certification deleted successfully!", "success")
    return redirect(url_for("admin_certifications"))

@app.route(
    "/admin/certifications/edit/<int:certification_id>",
    methods=["GET", "POST"]
)
def admin_edit_certification(certification_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row

    try:
        certification = conn.execute(
            "SELECT * FROM certifications WHERE id = ?",
            (certification_id,)
        ).fetchone()

        if certification is None:
            flash("Certification not found.", "error")
            return redirect(url_for("admin_certifications"))

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            issuer = request.form.get("issuer", "").strip()
            year = request.form.get("year", "").strip()
            credential_url = request.form.get("credential_url", "").strip()
            
            image = certification["image"] or ""
            uploaded_file = request.files.get("image")

            
            if uploaded_file and uploaded_file.filename:
                allowed_extensions = {"png", "jpg", "jpeg", "webp"}
                original_name = secure_filename(uploaded_file.filename)
                extension = (
                    original_name.rsplit(".", 1)[-1].lower()
                    if "." in original_name else ""
                )

                if extension not in allowed_extensions:
                    flash(
                        "Please upload a PNG, JPG, JPEG, or WEBP image.",
                        "error"
                    )
                    return render_template(
                        "admin/edit_certification.html",
                        certification=certification
                    )

                try:
                    with Image.open(uploaded_file.stream) as img:
                        actual_format = img.format
                        img.verify()

                    format_extensions = {
                        "PNG": {"png"},
                        "JPEG": {"jpg", "jpeg"},
                        "WEBP": {"webp"}
                    }

                    if extension not in format_extensions.get(
                        actual_format, set()
                    ):
                        raise ValueError("Image format does not match.")

                    uploaded_file.stream.seek(0)

                except (OSError, ValueError, Image.DecompressionBombError):
                    flash(
                        "Invalid image file. Please upload a valid PNG, JPG, JPEG, or WEBP image.",
                        "error"
                    )
                    return render_template(
                        "admin/edit_certification.html",
                        certification=certification
                    )

                if supabase:
                    uploaded_file.filename = (
                        f"{uuid.uuid4().hex}.{extension}"
                    )
                    image = upload_to_supabase(
                        uploaded_file, "certifications"
                    )
                else:
                    filename = f"{uuid.uuid4().hex}.{extension}"
                    upload_folder = os.path.join(
                        app.root_path, "static", "uploads"
                    )
                    os.makedirs(upload_folder, exist_ok=True)

                    uploaded_file.save(
                        os.path.join(upload_folder, filename)
                    )
                    image = f"static/uploads/{filename}"

            if not name or not issuer:
                flash(
                    "Please enter the certificate name and issuer.",
                    "error"
                )
                return render_template(
                    "admin/edit_certification.html",
                    certification=certification
                )

            conn.execute("""
                UPDATE certifications
                SET name = ?, issuer = ?, year = ?,
                    credential_url = ?, image = ?
                WHERE id = ?
            """, (
                name, issuer, year, credential_url,
                image, certification_id
            ))
            conn.commit()

            flash("Certification updated successfully!", "success")
            return redirect(url_for("admin_certifications"))

        return render_template(
            "admin/edit_certification.html",
            certification=certification
        )
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)