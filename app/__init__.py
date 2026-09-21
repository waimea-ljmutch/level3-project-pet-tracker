#===========================================================
# Lost pet tracker
# By Liam Mutch
#===========================================================

from flask import Flask, request, session, render_template, flash, redirect, send_file, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from datetime import date
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
# Login page
# -----------------------------------------------------------
@app.get("/login")
def show_login_form():
    return render_template("pages/login_page.jinja")
# -----------------------------------------------------------
# Messages page - Show all messages
# -----------------------------------------------------------

@app.get("/messages")
def messages():
    with connect_db() as db:
        sql = """
            SELECT id, pet_name, pet_type, gender, date_lost, location, description, user_id
            FROM messages
            ORDER BY id DESC
        """
        messages = db.execute(sql).fetchall()

    return render_template("pages/messages_page.jinja", messages=messages)

# -----------------------------------------------------------
# Message delete handling
# -----------------------------------------------------------
@app.get(f"/message/<int:id>/delete")
@login_required
def process_delete_message(id):
    with connect_db() as db:
        sql = """
            SELECT user_id FROM messages WHERE id=?
        """
        params = (id,)
        message = db.execute(sql, params).fetchone()

        if message and message["user_id"] == session["user"]["id"]:

            sql = """
                DELETE FROM messages WHERE id=?
            """
            params = (id,)
            db.execute(sql, params)

            flash("Message deleted", "success")
            return redirect("/messages")

        flash("Invalid message", "error")
        return redirect("/messages")
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

# -----------------------------------------------------------
# report pets page
# -----------------------------------------------------------
@app.get("/report/pet")
def show_pets_form():
    today = date.today().isoformat()
    return render_template("pages/report_pets.jinja", today=today)

# -----------------------------------------------------------
# Report a lost pet
# -----------------------------------------------------------
@app.post("/report/pet")
def process_new_pet():

    pet_name = request.form.get("pet_name", "").strip()
    pet_type = request.form.get("pet_type", "").strip()
    gender = request.form.get("gender", "").strip()
    location = request.form.get("location", "").strip()
    date_lost = request.form.get("date_lost", "").strip()
    description = request.form.get("description", "").strip()

    print("=============================================")
    print(gender)
    print(description)
    
    user_id = session["user"]["id"]

    with connect_db() as db:
        sql = """
            INSERT INTO messages
            (pet_name, pet_type, gender, location, date_lost, description, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            pet_name,
            pet_type,
            gender,
            location,
            date_lost,
            description,
            user_id
        )

        db.execute(sql, params)

    flash("Pet report posted", "success")
    return redirect("/messages")
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

