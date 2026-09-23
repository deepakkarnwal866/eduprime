from flask import Flask, request, redirect, url_for, session, render_template_string
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "EDUPRIME_SECRET_2026"

DB = "eduprime.db"


# =========================================================
# DATABASE
# =========================================================

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def init_db():

    con = db()

    con.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS courses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price TEXT,
            image TEXT
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            message TEXT
        )
    """)

    # ADMIN
    admin = con.execute(
        "SELECT * FROM users WHERE email=?",
        ("admin@eduprime.com",)
    ).fetchone()

    if not admin:

        con.execute("""
            INSERT INTO users(name,email,password,role)
            VALUES(?,?,?,?)
        """, (
            "Administrator",
            "admin@eduprime.com",
            generate_password_hash("admin123"),
            "admin"
        ))

    # DEMO COURSES

    count = con.execute(
        "SELECT COUNT(*) FROM courses"
    ).fetchone()[0]

    if count == 0:

        courses = [
            (
                "Web Development",
                "Learn HTML, CSS, JavaScript and modern web development.",
                "₹4,999",
                "https://images.unsplash.com/photo-1498050108023-c5249f4df085"
            ),
            (
                "Python Programming",
                "Beginner to advanced Python programming course.",
                "₹3,999",
                "https://images.unsplash.com/photo-1526379095098-d400fd0bf935"
            ),
            (
                "Data Science",
                "Learn Python, Pandas, NumPy and data analysis.",
                "₹5,999",
                "https://images.unsplash.com/photo-1551288049-bebda4e38f71"
            ),
            (
                "AI & Machine Learning",
                "Introduction to Artificial Intelligence and Machine Learning.",
                "₹6,999",
                "https://images.unsplash.com/photo-1555255707-c07966088b7b"
            ),
            (
                "Java Programming",
                "Learn Java and object oriented programming.",
                "₹4,499",
                "https://images.unsplash.com/photo-1515879218367-8466d910aaa4"
            ),
            (
                "SQL & Database",
                "Learn SQL and database management.",
                "₹2,999",
                "https://images.unsplash.com/photo-1544383835-bda2bc66a55d"
            )
        ]

        con.executemany("""
            INSERT INTO courses(title,description,price,image)
            VALUES(?,?,?,?)
        """, courses)

    con.commit()
    con.close()


# =========================================================
# AUTHENTICATION
# =========================================================

def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect("/login")

        return func(*args, **kwargs)

    return wrapper


def admin_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if session.get("role") != "admin":
            return redirect("/admin/login")

        return func(*args, **kwargs)

    return wrapper


# =========================================================
# COMMON HTML
# =========================================================

STYLE = """

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
}

body{
    font-family:Arial,Helvetica,sans-serif;
    background:#f5f7fb;
    color:#172033;
}

a{
    text-decoration:none;
}

.navbar{
    height:72px;
    background:#ffffff;
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:0 6%;
    box-shadow:0 2px 15px rgba(0,0,0,.07);
    position:sticky;
    top:0;
    z-index:1000;
}

.logo{
    font-size:25px;
    font-weight:900;
    color:#111827;
}

.logo span{
    color:#6366f1;
}

.navlinks{
    display:flex;
    gap:20px;
    align-items:center;
}

.navlinks a{
    color:#374151;
    font-size:14px;
    font-weight:600;
}

.navlinks a:hover{
    color:#6366f1;
}

.btn{
    display:inline-block;
    padding:12px 20px;
    border-radius:10px;
    border:0;
    cursor:pointer;
    font-weight:700;
}

.btn-primary{
    background:linear-gradient(135deg,#4f46e5,#7c3aed);
    color:#fff!important;
}

.btn-dark{
    background:#111827;
    color:white;
}

.container{
    width:88%;
    max-width:1250px;
    margin:auto;
}

.hero{
    min-height:620px;
    display:flex;
    align-items:center;
    background:
    linear-gradient(120deg,rgba(17,24,39,.95),rgba(79,70,229,.78)),
    url('https://images.unsplash.com/photo-1522202176988-66273c2fd55f')
    center/cover;
    color:white;
}

.hero-content{
    max-width:700px;
}

.hero h1{
    font-size:58px;
    line-height:1.05;
    margin-bottom:25px;
}

.hero p{
    font-size:19px;
    line-height:1.7;
    color:#e5e7eb;
    margin-bottom:30px;
}

.section{
    padding:80px 0;
}

.section-title{
    text-align:center;
    margin-bottom:45px;
}

.section-title h2{
    font-size:38px;
    margin-bottom:10px;
}

.section-title p{
    color:#6b7280;
}

.grid{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:25px;
}

.card{
    background:white;
    border-radius:18px;
    overflow:hidden;
    box-shadow:0 8px 30px rgba(0,0,0,.07);
    transition:.3s;
}

.card:hover{
    transform:translateY(-7px);
}

.card img{
    width:100%;
    height:200px;
    object-fit:cover;
}

.card-content{
    padding:25px;
}

.card h3{
    margin-bottom:10px;
}

.card p{
    color:#6b7280;
    line-height:1.6;
    margin-bottom:15px;
}

.price{
    color:#4f46e5;
    font-size:22px;
    font-weight:800;
}

.footer{
    background:#111827;
    color:white;
    padding:60px 6%;
    margin-top:50px;
}

.footer-grid{
    display:grid;
    grid-template-columns:2fr 1fr 1fr 1fr;
    gap:30px;
}

.footer a{
    color:#d1d5db;
    display:block;
    margin:10px 0;
}

.auth{
    min-height:100vh;
    display:flex;
    justify-content:center;
    align-items:center;
    background:
    linear-gradient(135deg,#111827,#4f46e5);
}

.auth-box{
    width:420px;
    background:white;
    padding:40px;
    border-radius:25px;
    box-shadow:0 30px 80px rgba(0,0,0,.3);
}

.auth-box h1{
    text-align:center;
    margin-bottom:30px;
}

.input{
    margin-bottom:18px;
}

.input label{
    display:block;
    margin-bottom:7px;
    font-weight:700;
}

.input input,
.input textarea,
.input select{
    width:100%;
    padding:14px;
    border:1px solid #d1d5db;
    border-radius:10px;
    outline:none;
}

.input textarea{
    min-height:130px;
}

.full{
    width:100%;
}

.dashboard{
    display:flex;
    min-height:calc(100vh - 72px);
}

.sidebar{
    width:250px;
    background:#111827;
    padding:25px;
    color:white;
}

.sidebar h2{
    margin-bottom:30px;
}

.sidebar a{
    display:block;
    color:#d1d5db;
    padding:12px;
    border-radius:8px;
    margin:5px 0;
}

.sidebar a:hover{
    background:#374151;
    color:white;
}

.main{
    flex:1;
    padding:35px;
}

.stats{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:20px;
    margin:25px 0;
}

.stat{
    background:white;
    padding:25px;
    border-radius:15px;
    box-shadow:0 5px 20px rgba(0,0,0,.05);
}

.stat h2{
    color:#4f46e5;
    margin-top:10px;
}

.table-box{
    background:white;
    padding:25px;
    border-radius:15px;
    overflow:auto;
}

table{
    width:100%;
    border-collapse:collapse;
}

th,td{
    padding:15px;
    text-align:left;
    border-bottom:1px solid #eee;
}

.badge{
    display:inline-block;
    padding:6px 10px;
    border-radius:20px;
    background:#eef2ff;
    color:#4f46e5;
    font-size:12px;
    font-weight:bold;
}

.alert{
    padding:12px;
    background:#dcfce7;
    color:#166534;
    border-radius:10px;
    margin-bottom:20px;
}

@media(max-width:900px){

    .navlinks{
        display:none;
    }

    .grid{
        grid-template-columns:1fr 1fr;
    }

    .stats{
        grid-template-columns:1fr 1fr;
    }

    .footer-grid{
        grid-template-columns:1fr 1fr;
    }

    .hero h1{
        font-size:42px;
    }

}

@media(max-width:600px){

    .grid,
    .stats,
    .footer-grid{
        grid-template-columns:1fr;
    }

    .hero{
        min-height:550px;
    }

    .hero h1{
        font-size:35px;
    }

    .auth-box{
        width:90%;
    }

    .sidebar{
        width:70px;
    }

    .sidebar h2{
        font-size:0;
    }

    .sidebar a{
        font-size:0;
    }

}

"""


def page(content, title="EduPrime"):

    return f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,initial-scale=1.0">

<title>{title}</title>

<style>{STYLE}</style>

</head>

<body>

{content}

</body>

</html>
"""


def navbar():
    return """
<nav class="navbar">

<a href="/" class="logo">
Edu<span>Prime</span>
</a>

<div class="navlinks">

<a href="/">Home</a>
<a href="/about">About</a>
<a href="/services">Services</a>
<a href="/courses">Courses</a>
<a href="/teachers">Teachers</a>
<a href="/gallery">Gallery</a>
<a href="/blog">Blog</a>
<a href="/contact">Contact</a>

""" + (
    '<a href="/dashboard" class="btn btn-primary">Dashboard</a>'
    if "user_id" in session
    else '<a href="/login" class="btn btn-primary">Login</a>'
) + """

</div>

</nav>
"""


def footer():

    return """

<footer class="footer">

<div class="footer-grid">

<div>

<h2>EduPrime</h2>

<p style="margin-top:15px;color:#9ca3af;line-height:1.7">

Premium learning platform for students,
professionals and future developers.

</p>

</div>

<div>

<h3>Company</h3>

<a href="/about">About</a>
<a href="/services">Services</a>
<a href="/careers">Careers</a>

</div>

<div>

<h3>Learning</h3>

<a href="/courses">Courses</a>
<a href="/teachers">Teachers</a>
<a href="/events">Events</a>

</div>

<div>

<h3>Support</h3>

<a href="/faq">FAQ</a>
<a href="/contact">Contact</a>
<a href="/privacy">Privacy</a>

</div>

</div>

<p style="margin-top:40px;text-align:center;color:#9ca3af">

© 2026 EduPrime. All Rights Reserved.

</p>

</footer>

"""


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    con = db()
    courses = con.execute(
        "SELECT * FROM courses LIMIT 6"
    ).fetchall()
    con.close()

    cards = ""

    for c in courses:

        cards += f"""

<div class="card">

<img src="{c['image']}?auto=format&fit=crop&w=900&q=80">

<div class="card-content">

<span class="badge">Popular Course</span>

<h3>{c['title']}</h3>

<p>{c['description']}</p>

<div style="display:flex;justify-content:space-between;align-items:center">

<span class="price">{c['price']}</span>

<a href="/course/{c['id']}"
class="btn btn-primary">

View Course

</a>

</div>

</div>

</div>

"""

    content = navbar() + f"""

<section class="hero">

<div class="container">

<div class="hero-content">

<span class="badge"
style="background:#ffffff22;color:white">

🚀 Premium Learning Platform

</span>

<h1>
Learn Skills.<br>
Build Your Future.
</h1>

<p>
Master Web Development, Python, AI, Data Science,
Java and more with expert-led courses.
</p>

<a href="/courses"
class="btn btn-primary">

Explore Courses

</a>

<a href="/register"
class="btn"
style="background:white;color:#111827;margin-left:10px">

Join Now

</a>

</div>

</div>

</section>


<section class="section">

<div class="container">

<div class="section-title">

<h2>Popular Courses</h2>

<p>
Choose the skill you want to master.
</p>

</div>

<div class="grid">

{cards}

</div>

</div>

</section>


<section class="section"
style="background:white">

<div class="container">

<div class="section-title">

<h2>Why Choose EduPrime?</h2>

</div>

<div class="grid">

<div class="card">

<div class="card-content">

<h3>🎓 Expert Teachers</h3>

<p>
Learn from experienced industry professionals.
</p>

</div>

</div>

<div class="card">

<div class="card-content">

<h3>💻 Practical Projects</h3>

<p>
Build real-world projects for your portfolio.
</p>

</div>

</div>

<div class="card">

<div class="card-content">

<h3>🏆 Certificates</h3>

<p>
Earn certificates after completing your courses.
</p>

</div>

</div>

</div>

</div>

</section>

"""

    return page(content + footer(), "EduPrime | Home")


# =========================================================
# AUTH
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    message = ""

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        con = db()

        user = con.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()

        con.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect("/admin")

            return redirect("/dashboard")

        message = "Invalid email or password."

    html = f"""

<div class="auth">

<div class="auth-box">

<h1>Edu<span style="color:#6366f1">Prime</span></h1>

<p style="text-align:center;color:#6b7280;margin-bottom:25px">

Login to your account

</p>

{f'<div class="alert">{message}</div>' if message else ''}

<form method="POST">

<div class="input">

<label>Email</label>

<input
type="email"
name="email"
placeholder="Enter email"
required>

</div>

<div class="input">

<label>Password</label>

<input
type="password"
name="password"
placeholder="Enter password"
required>

</div>

<button
class="btn btn-primary full">

Login

</button>

</form>

<p style="text-align:center;margin-top:20px">

Don't have an account?

<a href="/register">Register</a>

</p>

<p style="text-align:center;margin-top:10px">

<a href="/forgot-password">
Forgot Password?
</a>

</p>

</div>

</div>

"""

    return page(html, "Login")


@app.route("/register", methods=["GET", "POST"])
def register():

    message = ""

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        con = db()

        try:

            con.execute("""
                INSERT INTO users
                (name,email,password)
                VALUES(?,?,?)
            """, (
                name,
                email,
                generate_password_hash(password)
            ))

            con.commit()

            con.close()

            return redirect("/login")

        except sqlite3.IntegrityError:

            message = "Email already registered."

            con.close()

    html = f"""

<div class="auth">

<div class="auth-box">

<h1>Create Account</h1>

{f'<div class="alert">{message}</div>' if message else ''}

<form method="POST">

<div class="input">

<label>Name</label>

<input
name="name"
placeholder="Full name"
required>

</div>

<div class="input">

<label>Email</label>

<input
type="email"
name="email"
placeholder="Email"
required>

</div>

<div class="input">

<label>Password</label>

<input
type="password"
name="password"
placeholder="Password"
minlength="6"
required>

</div>

<button class="btn btn-primary full">
Create Account
</button>

</form>

<p style="text-align:center;margin-top:20px">

Already registered?
<a href="/login">Login</a>

</p>

</div>

</div>

"""

    return page(html, "Register")


@app.route("/forgot-password")
def forgot():

    return page(
        navbar() + """

<section class="section">

<div class="container">

<div style="max-width:500px;margin:auto;background:white;padding:35px;border-radius:20px">

<h2>Forgot Password</h2>

<p style="margin:15px 0;color:#6b7280">

Enter your registered email address.
We will send a verification code.

</p>

<form>

<div class="input">

<label>Email</label>

<input type="email"
placeholder="Enter your email">

</div>

<button class="btn btn-primary">
Send OTP
</button>

</form>

</div>

</div>

</section>

""" + footer(),
        "Forgot Password"
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================================================
# ABOUT / SERVICES
# =========================================================

@app.route("/about")
def about():

    return page(
        navbar() + """

<section class="section">

<div class="container">

<div class="section-title">

<h2>About EduPrime</h2>

<p>Learn. Practice. Build. Grow.</p>

</div>

<div class="grid">

<div class="card">

<div class="card-content">

<h3>Our Mission</h3>

<p>
Our mission is to make quality technical
education accessible to every learner.
</p>

</div>

</div>

<div class="card">

<div class="card-content">

<h3>Our Vision</h3>

<p>
We help students develop practical skills
needed for modern technology careers.
</p>

</div>

</div>

<div class="card">

<div class="card-content">

<h3>Our Community</h3>

<p>
Students, teachers and developers learn
together through projects and practice.
</p>

</div>

</div>

</div>

</div>

</section>

""" + footer(),
        "About"
    )


@app.route("/services")
def services():

    services = [
        ("💻 Web Development","Build modern responsive websites."),
        ("🐍 Python","Learn Python from beginner to advanced."),
        ("🤖 Artificial Intelligence","Understand AI concepts and applications."),
        ("📊 Data Science","Learn data analysis and visualization."),
        ("☕ Java","Master Java and OOP."),
        ("🗄️ Database","Learn SQL and database systems.")
    ]

    cards = ""

    for title,desc in services:

        cards += f"""

<div class="card">

<div class="card-content">

<h3>{title}</h3>

<p>{desc}</p>

<a href="/courses"
class="btn btn-primary">

Learn More

</a>

</div>

</div>

"""

    return page(
        navbar() +
        f"""

<section class="section">

<div class="container">

<div class="section-title">

<h2>Our Services</h2>

<p>Everything you need to build your career.</p>

</div>

<div class="grid">

{cards}

</div>

</div>

</section>

""" + footer(),
        "Services"
    )


# =========================================================
# COURSES
# =========================================================

@app.route("/courses")
def courses():

    con = db()

    data = con.execute(
        "SELECT * FROM courses"
    ).fetchall()

    con.close()

    cards = ""

    for c in data:

        cards += f"""

<div class="card">

<img src="{c['image']}?auto=format&fit=crop&w=900&q=80">

<div class="card-content">

<h3>{c['title']}</h3>

<p>{c['description']}</p>

<p class="price">{c['price']}</p>

<a href="/course/{c['id']}"
class="btn btn-primary">

View Details

</a>

</div>

</div>

"""

    return page(
        navbar() +
        f"""

<section class="section">

<div class="container">

<div class="section-title">

<h2>All Courses</h2>

<p>Choose your learning path.</p>

</div>

<div class="grid">

{cards}

</div>

</div>

</section>

""" + footer(),
        "Courses"
    )


@app.route("/course/<int:course_id>")
def course(course_id):

    con = db()

    c = con.execute(
        "SELECT * FROM courses WHERE id=?",
        (course_id,)
    ).fetchone()

    con.close()

    if not c:
        return redirect("/courses")

    return page(
        navbar() +
        f"""

<section class="section">

<div class="container">

<div class="grid">

<div class="card">

<img src="{c['image']}?auto=format&fit=crop&w=1000&q=80">

</div>

<div>

<span class="badge">
Premium Course
</span>

<h1 style="font-size:45px;margin:20px 0">

{c['title']}

</h1>

<p style="line-height:1.8;color:#6b7280">

{c['description']}

</p>

<h2 style="color:#4f46e5;margin:25px 0">

{c['price']}

</h2>

<a href="/dashboard"
class="btn btn-primary">

Enroll Now

</a>

</div>

</div>

</div>

</section>

""" + footer(),
        c["title"]
    )


# =========================================================
# TEACHERS
# =========================================================

@app.route("/teachers")
def teachers():

    teachers = [
        ("Rahul Sharma","Senior Web Developer"),
        ("Priya Verma","Python Developer"),
        ("Amit Kumar","Data Scientist"),
        ("Neha Singh","AI/ML Engineer")
    ]

    cards = ""

    for name,role in teachers:

        cards += f"""

<div class="card">

<img src="https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=700&q=80">

<div class="card-content">

<h3>{name}</h3>

<p>{role}</p>

<span class="badge">Expert Instructor</span>

</div>

</div>

"""

    return page(
        navbar() +
        f"""

<section class="section">

<div class="container">

<div class="section-title">

<h2>Our Teachers</h2>

<p>Learn from experienced professionals.</p>

</div>

<div class="grid">

{cards}

</div>

</div>

</section>

""" + footer(),
        "Teachers"
    )


# =========================================================
# GALLERY
# =========================================================

@app.route("/gallery")
def gallery():

    imgs = [
        "photo-1522202176988-66273c2fd55f",
        "photo-1516321318423-f06f85e504b3",
        "photo-1524178232363-1fb2b075b655",
        "photo-1497366811353-6870744d04b2",
        "photo-1531482615713-2afd69097998",
        "photo-1517245386807-bb43f82c33c4"
    ]

    cards = ""

    for x in imgs:

        cards += f"""

<div class="card">

<img src="https://images.unsplash.com/{x}?auto=format&fit=crop&w=900&q=80">

</div>

"""

    return page(
        navbar() +
        f"""

<section class="section">

<div class="container">

<div class="section-title">

<h2>Gallery</h2>

<p>Our learning environment.</p>

</div>

<div class="grid">

{cards}

</div>

</div>

</section>

""" + footer(),
        "Gallery"
    )


# =========================================================
# BLOG
# =========================================================

@app.route("/blog")
def blog():

    posts = [
        ("How to Start Web Development","Begin your web development journey."),
        ("Why Learn Python?","Python is one of the most popular programming languages."),
        ("Introduction to AI","Understand the basics of Artificial Intelligence.")
    ]

    cards = ""

    for title,desc in posts:

        cards += f"""

<div class="card">

<img src="https://images.unsplash.com/photo-1499750310107-5fef28a66643?auto=format&fit=crop&w=900&q=80">

<div class="card-content">

<span class="badge">Technology</span>

<h3>{title}</h3>

<p>{desc}</p>

<a href="/blog/1"
class="btn btn-primary">

Read Article

</a>

</div>

</div>

"""

    return page(
        navbar() +
        f"""

<section class="section">

<div class="container">

<div class="section-title">

<h2>Latest Blog</h2>

</div>

<div class="grid">

{cards}

</div>

</div>

</section>

""" + footer(),
        "Blog"
    )


@app.route("/blog/<int:blog_id>")
def blog_details(blog_id):

    return page(
        navbar() +
        """

<section class="section">

<div class="container">

<div style="max-width:850px;margin:auto;background:white;padding:40px;border-radius:20px">

<h1>How to Start Your Web Development Journey</h1>

<p style="margin-top:20px;line-height:2;color:#4b5563">

Web development is a practical technology skill.
Start with HTML, then learn CSS and JavaScript.
After understanding the fundamentals, build projects
and create a portfolio.

</p>

<h2 style="margin-top:30px">
Step 1 — HTML
</h2>

<p style="margin-top:10px;line-height:1.8">
Learn headings, paragraphs, links, images,
forms, tables and semantic HTML.
</p>

<h2 style="margin-top:30px">
Step 2 — CSS
</h2>

<p style="margin-top:10px;line-height:1.8">
Learn layouts, Flexbox, Grid, responsive design
and animations.
</p>

<h2 style="margin-top:30px">
Step 3 — JavaScript
</h2>

<p style="margin-top:10px;line-height:1.8">
Learn variables, functions, DOM manipulation,
events and APIs.
</p>

</div>

</div>

</section>

""" + footer(),
        "Blog Details"
    )


# =========================================================
# OTHER PUBLIC PAGES
# =========================================================

@app.route("/events")
def events():

    return simple_page(
        "Upcoming Events",
        "Join our workshops, coding bootcamps and career events."
    )


@app.route("/testimonials")
def testimonials():

    return simple_page(
        "Student Testimonials",
        "Students share their learning experience with EduPrime."
    )


@app.route("/faq")
def faq():

    return simple_page(
        "Frequently Asked Questions",
        "Find answers about courses, certificates, accounts and support."
    )


@app.route("/location")
def location():

    return simple_page(
        "Our Location",
        "Visit our learning centre or contact our support team."
    )


@app.route("/pricing")
def pricing():

    return simple_page(
        "Pricing Plans",
        "Choose a learning plan that matches your goals."
    )


@app.route("/careers")
def careers():

    return simple_page(
        "Careers",
        "Explore opportunities to work with our education team."
    )


@app.route("/privacy")
def privacy():

    return simple_page(
        "Privacy Policy",
        "EduPrime respects your privacy and protects account information."
    )


@app.route("/terms")
def terms():

    return simple_page(
        "Terms & Conditions",
        "Please read our terms before using EduPrime services."
    )


def simple_page(title, text):

    return page(
        navbar() +
        f"""

<section class="section">

<div class="container">

<div style="background:white;padding:50px;border-radius:20px;text-align:center">

<h1>{title}</h1>

<p style="margin-top:20px;color:#6b7280;line-height:1.8">

{text}

</p>

</div>

</div>

</section>

""" + footer(),
        title
    )


# =========================================================
# CONTACT
# =========================================================

@app.route("/contact", methods=["GET", "POST"])
def contact():

    message = ""

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        msg = request.form["message"]

        con = db()

        con.execute("""
            INSERT INTO messages(name,email,message)
            VALUES(?,?,?)
        """, (name,email,msg))

        con.commit()
        con.close()

        message = "Your message has been sent successfully!"

    return page(
        navbar() +
        f"""

<section class="section">

<div class="container">

<div style="max-width:650px;margin:auto;background:white;padding:40px;border-radius:20px">

<h2>Contact Us</h2>

{f'<div class="alert">{message}</div>' if message else ''}

<form method="POST">

<div class="input">

<label>Name</label>

<input name="name" required>

</div>

<div class="input">

<label>Email</label>

<input type="email" name="email" required>

</div>

<div class="input">

<label>Message</label>

<textarea name="message" required></textarea>

</div>

<button class="btn btn-primary">

Send Message

</button>

</form>

</div>

</div>

</section>

""" + footer(),
        "Contact"
    )


# =========================================================
# USER DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    con = db()

    courses = con.execute(
        "SELECT COUNT(*) FROM courses"
    ).fetchone()[0]

    con.close()

    return page(
        dashboard_nav() +
        f"""

<div class="main">

<h1>Welcome, {session['name']} 👋</h1>

<p style="color:#6b7280;margin-top:10px">

Your learning dashboard

</p>

<div class="stats">

<div class="stat">

<p>Available Courses</p>

<h2>{courses}</h2>

</div>

<div class="stat">

<p>My Courses</p>

<h2>4</h2>

</div>

<div class="stat">

<p>Completed</p>

<h2>2</h2>

</div>

<div class="stat">

<p>Certificates</p>

<h2>2</h2>

</div>

</div>

<div class="table-box">

<h2>Learning Progress</h2>

<table>

<tr>

<th>Course</th>
<th>Progress</th>
<th>Status</th>

</tr>

<tr>

<td>Web Development</td>
<td>75%</td>
<td><span class="badge">In Progress</span></td>

</tr>

<tr>

<td>Python Programming</td>
<td>100%</td>
<td><span class="badge">Completed</span></td>

</tr>

<tr>

<td>Java</td>
<td>45%</td>
<td><span class="badge">In Progress</span></td>

</tr>

</table>

</div>

</div>

</div>

""",
        "Dashboard"
    )


def dashboard_nav():

    return """

<div class="dashboard">

<div class="sidebar">

<h2>EduPrime</h2>

<a href="/dashboard">📊 Dashboard</a>

<a href="/dashboard/profile">👤 My Profile</a>

<a href="/dashboard/courses">📚 My Courses</a>

<a href="/dashboard/progress">📈 Progress</a>

<a href="/dashboard/certificates">🏆 Certificates</a>

<a href="/dashboard/wishlist">❤️ Wishlist</a>

<a href="/dashboard/messages">💬 Messages</a>

<a href="/dashboard/notifications">🔔 Notifications</a>

<a href="/dashboard/settings">⚙️ Settings</a>

<a href="/logout">🚪 Logout</a>

</div>

"""


@app.route("/dashboard/profile")
@login_required
def profile():

    return dashboard_page(
        "My Profile",
        f"""
        <h3>{session['name']}</h3>
        <p>Student Account</p>
        <p>Email account is securely connected.</p>
        """
    )


@app.route("/dashboard/courses")
@login_required
def my_courses():

    return dashboard_page(
        "My Courses",
        """
        <div class="card-content">
        <h3>Web Development</h3>
        <p>Progress: 75%</p>
        </div>

        <br>

        <div class="card-content">
        <h3>Python Programming</h3>
        <p>Progress: 100%</p>
        </div>
        """
    )


@app.route("/dashboard/progress")
@login_required
def progress():

    return dashboard_page(
        "Learning Progress",
        """
        <h3>Overall Progress: 78%</h3>

        <br>

        <p>Web Development — 75%</p>
        <p>Python — 100%</p>
        <p>Java — 45%</p>
        """
    )


@app.route("/dashboard/certificates")
@login_required
def certificates():

    return dashboard_page(
        "Certificates",
        """
        <h3>🏆 Python Programming Certificate</h3>
        <br>
        <h3>🏆 Web Development Certificate</h3>
        """
    )


@app.route("/dashboard/wishlist")
@login_required
def wishlist():

    return dashboard_page(
        "Wishlist",
        """
        <h3>AI & Machine Learning</h3>
        <p>Saved course</p>
        """
    )


@app.route("/dashboard/messages")
@login_required
def dashboard_messages():

    return dashboard_page(
        "Messages",
        """
        <h3>Support Team</h3>
        <p>Welcome to EduPrime support.</p>
        """
    )


@app.route("/dashboard/notifications")
@login_required
def notifications():

    return dashboard_page(
        "Notifications",
        """
        <h3>New course added</h3>
        <p>AI & Machine Learning course is now available.</p>
        """
    )


@app.route("/dashboard/settings")
@login_required
def settings():

    return dashboard_page(
        "Settings",
        """
        <h3>Account Settings</h3>
        <p>Change password and notification preferences.</p>
        """
    )


def dashboard_page(title, body):

    return page(
        dashboard_nav() +
        f"""

<div class="main">

<h1>{title}</h1>

<div class="table-box" style="margin-top:25px">

{body}

</div>

</div>

</div>

""",
        title
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin/login", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        con = db()

        admin = con.execute("""
            SELECT * FROM users
            WHERE email=? AND role='admin'
        """,(email,)).fetchone()

        con.close()

        if admin and check_password_hash(
            admin["password"],
            password
        ):

            session["user_id"] = admin["id"]
            session["name"] = admin["name"]
            session["role"] = "admin"

            return redirect("/admin")

    return page("""

<div class="auth">

<div class="auth-box">

<h1>Admin Login</h1>

<form method="POST">

<div class="input">

<label>Email</label>

<input
type="email"
name="email"
required>

</div>

<div class="input">

<label>Password</label>

<input
type="password"
name="password"
required>

</div>

<button class="btn btn-primary full">

Admin Login

</button>

</form>

<p style="margin-top:20px;text-align:center">

admin@eduprime.com<br>

admin123

</p>

</div>

</div>

""","Admin Login")


# =========================================================
# ADMIN PANEL
# =========================================================

def admin_nav():

    return """

<div class="dashboard">

<div class="sidebar">

<h2>ADMIN</h2>

<a href="/admin">📊 Dashboard</a>

<a href="/admin/users">👥 Users</a>

<a href="/admin/courses">📚 Courses</a>

<a href="/admin/teachers">👨‍🏫 Teachers</a>

<a href="/admin/gallery">🖼 Gallery</a>

<a href="/admin/blogs">📝 Blogs</a>

<a href="/admin/testimonials">⭐ Testimonials</a>

<a href="/admin/messages">💬 Messages</a>

<a href="/admin/orders">🛒 Orders</a>

<a href="/admin/reports">📈 Reports</a>

<a href="/admin/settings">⚙️ Settings</a>

<a href="/logout">🚪 Logout</a>

</div>

"""


@app.route("/admin")
@admin_required
def admin():

    con = db()

    users = con.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    courses = con.execute(
        "SELECT COUNT(*) FROM courses"
    ).fetchone()[0]

    messages = con.execute(
        "SELECT COUNT(*) FROM messages"
    ).fetchone()[0]

    con.close()

    return page(
        admin_nav() +
        f"""

<div class="main">

<h1>Admin Dashboard</h1>

<div class="stats">

<div class="stat">

<p>Total Users</p>

<h2>{users}</h2>

</div>

<div class="stat">

<p>Courses</p>

<h2>{courses}</h2>

</div>

<div class="stat">

<p>Messages</p>

<h2>{messages}</h2>

</div>

<div class="stat">

<p>Enrollments</p>

<h2>128</h2>

</div>

</div>

<div class="table-box">

<h2>System Overview</h2>

<table>

<tr>

<th>Module</th>
<th>Status</th>

</tr>

<tr>

<td>User Management</td>
<td><span class="badge">Active</span></td>

</tr>

<tr>

<td>Course Management</td>
<td><span class="badge">Active</span></td>

</tr>

<tr>

<td>Messages</td>
<td><span class="badge">Active</span></td>

</tr>

</table>

</div>

</div>

</div>

""",
        "Admin Dashboard"
    )


@app.route("/admin/users")
@admin_required
def admin_users():

    con = db()

    users = con.execute(
        "SELECT * FROM users"
    ).fetchall()

    con.close()

    rows = ""

    for u in users:

        rows += f"""

<tr>

<td>{u['id']}</td>

<td>{u['name']}</td>

<td>{u['email']}</td>

<td>{u['role']}</td>

<td>
<span class="badge">Active</span>
</td>

</tr>

"""

    return admin_table(
        "Manage Users",
        """
        <tr>
        <th>ID</th>
        <th>Name</th>
        <th>Email</th>
        <th>Role</th>
        <th>Status</th>
        </tr>
        """ + rows
    )


@app.route("/admin/courses")
@admin_required
def admin_courses():

    con = db()

    courses = con.execute(
        "SELECT * FROM courses"
    ).fetchall()

    con.close()

    rows = ""

    for c in courses:

        rows += f"""

<tr>

<td>{c['id']}</td>

<td>{c['title']}</td>

<td>{c['price']}</td>

<td>
<span class="badge">Published</span>
</td>

</tr>

"""

    return admin_table(
        "Manage Courses",
        """
        <tr>
        <th>ID</th>
        <th>Course</th>
        <th>Price</th>
        <th>Status</th>
        </tr>
        """ + rows
    )


@app.route("/admin/messages")
@admin_required
def admin_messages():

    con = db()

    data = con.execute(
        "SELECT * FROM messages ORDER BY id DESC"
    ).fetchall()

    con.close()

    rows = ""

    for m in data:

        rows += f"""

<tr>

<td>{m['name']}</td>
<td>{m['email']}</td>
<td>{m['message']}</td>

</tr>

"""

    return admin_table(
        "Contact Messages",
        """
        <tr>
        <th>Name</th>
        <th>Email</th>
        <th>Message</th>
        </tr>
        """ + rows
    )


def admin_table(title, rows):

    return page(
        admin_nav() +
        f"""

<div class="main">

<h1>{title}</h1>

<div class="table-box" style="margin-top:25px">

<table>

{rows}

</table>

</div>

</div>

</div>

""",
        title
    )


# =========================================================
# ADMIN OTHER MODULES
# =========================================================

@app.route("/admin/teachers")
@admin_required
def admin_teachers():

    return admin_simple("Manage Teachers")


@app.route("/admin/gallery")
@admin_required
def admin_gallery():

    return admin_simple("Manage Gallery")


@app.route("/admin/blogs")
@admin_required
def admin_blogs():

    return admin_simple("Manage Blogs")


@app.route("/admin/testimonials")
@admin_required
def admin_testimonials():

    return admin_simple("Manage Testimonials")


@app.route("/admin/orders")
@admin_required
def admin_orders():

    return admin_simple("Manage Orders & Enrollments")


@app.route("/admin/reports")
@admin_required
def admin_reports():

    return admin_simple("Reports & Analytics")


@app.route("/admin/settings")
@admin_required
def admin_settings():

    return admin_simple("Admin Settings")


def admin_simple(title):

    return page(
        admin_nav() +
        f"""

<div class="main">

<h1>{title}</h1>

<div class="table-box" style="margin-top:25px">

<h3>{title}</h3>

<p style="margin-top:15px;color:#6b7280">

This module is ready for CRUD operations.

</p>

</div>

</div>

</div>

""",
        title
    )


# =========================================================
# 404
# =========================================================

@app.errorhandler(404)
def error404(e):

    return page(
        navbar() +
        """

<section class="section">

<div class="container"
style="text-align:center">

<h1 style="font-size:100px;color:#4f46e5">

404

</h1>

<h2>Page Not Found</h2>

<p style="margin:20px;color:#6b7280">

The page you are looking for does not exist.

</p>

<a href="/" class="btn btn-primary">

Go Home

</a>

</div>

</section>

""" + footer(),
        "404"
    ),404


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )