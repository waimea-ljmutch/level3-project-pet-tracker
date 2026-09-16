#===========================================================
# Lost pet tracker
# By Liam Mutch
#===========================================================

from flask import Flask, request, session, render_template, flash, redirect, send_file, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from os import getenv
from io import BytesIO
import html
from app.helpers import *


# Create the app
app = Flask(__name__)


#===========================================================
# App Routes Handlers
#===========================================================

#-----------------------------------------------------------
# Home page - Show all notes
#-----------------------------------------------------------
@app.get("/")
def show_notes():
    with connect_db() as db:
        return render_template("pages/home_page.jinja",)

# -----------------------------------------------------------
# Signup page
# -----------------------------------------------------------
@app.get("/user/new")
def show_signup_form():
    return render_template("pages/sign_up.jinja")

# -----------------------------------------------------------
# report pets page
# -----------------------------------------------------------
@app.get("/report/pet")
def show_pets_form():
    return render_template("pages/report_pets.jinja")

# -----------------------------------------------------------
# Login page
# -----------------------------------------------------------
@app.get("/login")
def show_login_form():
    return render_template("pages/login_page.jinja")

#-------------------------------------------------------------
#
#-------------------------------------------------------------
@app.post("/report_pets")
def add_note():
    # Get form data
    title    = request.form.get('title', '').strip()
    body     = request.form.get('body', '').strip()
    priority = request.form.get('priority', '3').strip()
    tag_list = request.form.getlist('tags')
    pinned   = bool(request.form.get('pinned'))

    # Validate data
    if not title:
        flash("Title is required", "error")
        return redirect("/note/new")

    if len(title) > 40:
        flash("Title is too long (max 40 chars)", "error")
        return redirect("/note/new")

    if not priority.isdigit():
        flash("Priority should be numeric", "error")
        return redirect("/note/new")

    priority = int(priority)
    if priority < 1 or priority > 5:
        flash("Priority should be between 1 and 5", "error")
        return redirect("/note/new")

    # Escape text inputs
    title = html.escape(title)
    body = html.escape(body)

    # Join tags
    tags = ", ".join(tag_list)

    # Add to the database
    with connect_db() as db:
        sql = """
            INSERT INTO notes (title, body, priority, tags, pinned)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (title, body, priority, tags, pinned)
        db.execute(sql, params)

        flash(f"Note added")
        return redirect("/messages")  

# -----------------------------------------------------------
# Messages page - Show all notes
# -----------------------------------------------------------

@app.get("/messages")
def messages():
    with connect_db() as db:
        sql = """
            SELECT id, title, body, priority, tags, pinned
            FROM messages
            ORDER BY pinned DESC, id DESC
        """
        notes = db.execute(sql).fetchall()

    return render_template("pages/messages_page.jinja", notes=notes)
# -----------------------------------------------------------
# Handle user signup
# -----------------------------------------------------------
@app.post("/user")
def process_new_user():
    firstname = request.form.get("firstname", "").strip()
    lastname = request.form.get("lastname", "").strip()
    username = request.form.get("username", "").strip().lower()
    password = request.form.get("password", "").strip()

    with connect_db() as db:
        sql = "SELECT id FROM users WHERE username=?"
        params = (username,)
        user = db.execute(sql, params).fetchone()

        if user:
            flash(f"Username '{username}' already exists", "error")
            return redirect("/user/new")

        pass_hash = generate_password_hash(password)

        sql = """
            INSERT INTO users (firstname, lastname, username, password_hash)
            VALUES (?, ?, ?, ?)
        """
        params = (firstname, lastname, username, pass_hash)
        db.execute(sql, params)

        flash("Account created. Please login", "success")
        return redirect("/login")
    
# -----------------------------------------------------------
# Handle user login
# -----------------------------------------------------------

@app.post("/login")
def login_user():
    username = request.form.get("username", "").strip().lower()
    password = request.form.get("password", "").strip()

    with connect_db() as db:
        sql = """
            SELECT id, username, firstname, lastname, password_hash
            FROM users
            WHERE username=?
        """
        params = (username,)
        user = db.execute(sql, params).fetchone()

        if not user:
            flash("Unknown user", "error")
            return redirect("/login")

        if not check_password_hash(user["password_hash"], password):
            flash("Incorrect password", "error")
            return redirect("/login")

        session["logged_in"] = True
        session["user"] = {
            "id": user["id"],
            "username": user["username"],
            "firstname": user["firstname"],
            "lastname": user["lastname"],
        }

        flash("Login successful", "success")
        return redirect("/")

#------------------------------------------------------------
# New messages
#------------------------------------------------------------
@app.post("/message")
# @login_required
def process_new_message():
    pet = request.form.get("pet", "").strip()
    location = request.form.get("location", "").strip()

    user_id = session["user"]["id"]

    with connect_db() as db:
        sql = """
            INSERT INTO messages (pet, location, user_id)
            VALUES (?, ?, ?)
        """
        params = (pet, location, user_id)
        db.execute(sql, params)

        flash("Message posted", "success")
        return redirect("/")

# -----------------------------------------------------------
# Handle user logout
# -----------------------------------------------------------
@app.get("/logout")
def handle_logout():
    session.clear()
    flash(f"You have been logged out", "success")
    return redirect("/")

#===========================================================
# Configure the app
#===========================================================
load_dotenv()
app.config.from_prefixed_env()
init_logging(app)
init_text_filters(app)
init_date_filters(app)
init_error_handlers(app)
init_database()
register_commands(app)

