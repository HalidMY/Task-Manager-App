import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from utils.helpers import *
from flask import jsonify

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# -------------------------------------------------------
# ABSOLUTE PATH FOR SQLITE (WINDOWS SAFE)
# -------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "tasks.db").replace("\\", "/")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -------------------------------------------------------
# MODELS
# -------------------------------------------------------
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    project_id = db.Column(db.Integer)
    category_id = db.Column(db.Integer)

    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    priority = db.Column(db.String, default="medium")
    due_date = db.Column(db.Date)

    status = db.Column(db.String, default="todo")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

# -------------------------------------------------------
# ROUTES
# -------------------------------------------------------

@app.route("/tasks")
@login_required()
def all_tasks():
    user_id = session["user_id"]

    todo_tasks = Task.query.filter_by(user_id=user_id, status="todo").all()
    in_progress_tasks = Task.query.filter_by(user_id=user_id, status="in_progress").all()
    done_tasks = Task.query.filter_by(user_id=user_id, status="done").all()

    return render_template(
        "tasks.html",
        todo_tasks=todo_tasks,
        in_progress_tasks=in_progress_tasks,
        done_tasks=done_tasks
    )


@app.route("/dashboard")
@login_required()
def dashboard():
    user_id = session["user_id"]

    total_tasks = Task.query.filter_by(user_id=user_id).count()
    todo_count = Task.query.filter_by(user_id=user_id, status="todo").count()
    in_progress_count = Task.query.filter_by(user_id=user_id, status="in_progress").count()
    done_count = Task.query.filter_by(user_id=user_id, status="done").count()

    completion_percentage = 0
    if total_tasks > 0:
        completion_percentage = round((done_count / total_tasks) * 100)

    today_tasks = Task.query.filter(
        Task.user_id == user_id,
        Task.status != "done"
    ).order_by(
        Task.priority.desc(),
        Task.due_date.asc()
    ).limit(3).all()

    return render_template(
        "dashboard.html",
        total_tasks=total_tasks,
        todo_count=todo_count,
        in_progress_count=in_progress_count,
        done_count=done_count,
        completion_percentage=completion_percentage,
        today_tasks=today_tasks
    )


@app.route("/")
@login_required()
def index():
    user_id = session["user_id"]

    important_task = Task.query.filter(
        Task.user_id == user_id,
        Task.status != "done"
    ).order_by(
        Task.priority.desc(),
        Task.due_date.asc()
    ).first()

    return render_template("index.html", important_task=important_task)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid credentials", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        flash("Logged in!", "success")
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
@login_required()
def logout():
    session.clear()
    flash("You've been logged out successfully", "success")
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")

        if not username:
            flash("Username required", "danger")
            return redirect(url_for("register"))

        if not password:
            flash("Password required", "danger")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match", "danger")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists", "danger")
            return redirect(url_for("register"))

        new_user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Registered!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/settings", methods=["GET", "POST"])
@login_required()
def settings():
    user = User.query.filter_by(id=session["user_id"]).first()

    if request.method == "POST":
        new_username = request.form.get("username").strip()
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if new_username and new_username != user.username:
            existing_user = User.query.filter_by(username=new_username).first()
            if existing_user:
                flash("Username already taken", "danger")
                return redirect(url_for("settings"))
        user.username = new_username

        if new_password:
            if not check_password_hash(user.password_hash, current_password):
                flash("Current password is incorrect", "danger")
                return redirect(url_for("settings"))
            if new_password != confirm_password:
                flash("New password do not match", "danger")
                return redirect(url_for("settings"))
            
            user.password_hash = generate_password_hash(new_password)

        db.session.commit()
        flash("Settings updated successfully", "success")
        return redirect(url_for("settings"))
    
    return render_template("settings.html", user=user)


@app.route("/task/create", methods=["POST"])
@login_required()
def task_create():
    title = request.form.get("title")
    description = request.form.get("description")
    priority = request.form.get("priority")
    due_date = request.form.get("due_date")

    if not title or not due_date:
        flash("Title and due date are required", "danger")
        return redirect(url_for("index"))
    
    try:
        due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid date format", "danger")
        return redirect(url_for("index"))
    
    new_task = Task(
        user_id=session["user_id"],
        title=title,
        description=description,
        priority=priority,
        due_date=due_date
    )
    
    db.session.add(new_task)
    db.session.commit()

    flash("Task created successfully", "success")
    return redirect(url_for("index"))


@app.route("/task/update/<int:task_id>", methods=["POST"])
@login_required()
def update_task(task_id):
    data = request.get_json()
    task = Task.query.filter_by(id=task_id, user_id=session["user_id"]).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    task.title = data["title"]
    task.description = data["description"]
    task.priority = data["priority"]
    task.status = data["status"]
    task.updated_at = datetime.utcnow()

    db.session.commit()
    
    return jsonify({"success": True})


@app.route("/task/update-status/<int:task_id>", methods=["POST"])
@login_required()
def update_task_status(task_id):
    data = request.get_json()
    new_status = data.get("status")

    task = Task.query.filter_by(id=task_id, user_id=session["user_id"]).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    task.status = new_status
    task.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"success": True})

# -------------------------------------------------------
# CREATE DATABASE
# -------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
