from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Genre, Authors, Alabels
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


#login page
@auth.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        loginas = request.form.get("as")

        user = User.query.filter(User.email == email, User.person == loginas).first()

        #checking if user exists and password correct
        if user:
            if check_password_hash(user.password, password):
                flash("logged in successfully!", category="success")

                #login user using flask_login
                login_user(user, remember=True)

                #redirect different for user and employee
                if loginas == "user":
                    return redirect(url_for('views.home'))
                else:
                    return redirect(url_for('views.ehome'))
            else:
                flash("password is incorrect!", category="error")
        else:
            flash("user does not exist.", category="error")

    return render_template("login.html")


#logout function
@auth.route('/logout')
@login_required         #to make sure only if logged in, can the page be accessed
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


#sign up page --> basic information such as name, email
@auth.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        name = request.form.get("name")
        signupas = request.form.get("as")

        #checking if user already exists
        user = User.query.filter_by(email = email).first()

        if user:
            flash("user already exists.", category="error")
        elif len(email) < 4:
            flash("email has to be at least 4 characters!", category="error")
        elif len(password1) < 8:
            flash("password has to be at least 8 characters!", category="error")
        elif password1 != password2:
            flash("passwords do not match!", category="error")
        elif len(name) < 1:
            flash("name has to be at least 1 character")
        else:
            new_user = User(email = email, password = generate_password_hash(password1), name = name, person = signupas)
            db.session.add(new_user)
            db.session.commit()


            if signupas == "user":
                return redirect(url_for("auth.signup2", userid = new_user.userid))
            else:
                login_user(new_user, remember=True)
                return redirect(url_for('views.ehome'))
       
    return render_template("signup.html")


#sign up page --> genres and authors of interest
@auth.route('/signup2', methods=["GET", "POST"])
def signup2():


    if request.method == "POST":
        #from first sign up page
        userid = request.args.get("userid")
        user = User.query.filter_by(userid = userid).first()


       #from second sign up page
        genres = [request.form.get("genre1"), request.form.get("genre2"), request.form.get("genre3")]
        authors = [request.form.get("authors1"), request.form.get("authors2"), request.form.get("authors3")]


        for i, g in enumerate(genres):
            genre = Genre.query.filter_by(genre = g).first()
            if not genre:
                genres[i] = Genre(genre = g)
                db.session.add(genres[i])
                db.session.commit()

        for i, a, in enumerate(authors):
            author = Authors.query.filter_by(name = a).first()
            if not author:
                author = Authors(name = a)
                db.session.add(author)
                db.session.commit()

            alabels = Alabels.query.filter(Alabels.authorid == author.authorid, Alabels.userid == userid).first()
            if not alabels:
                alabels = Alabels(authorid = author.authorid, userid = userid)
                db.session.add(alabels)
                db.session.commit()
            
       
        flash("account created!", category="success")
        login_user(user, remember=True)
        return redirect(url_for("views.home"))
       
       
    return render_template("signup2.html")




