from flask import Flask, render_template, url_for, redirect, request, session
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from main_class import FireBase
from random import randrange
import csv
import pandas as pd
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from datetime import datetime
from figure_class import Plot


app = Flask(__name__)
Bootstrap5(app)
app.config["RECAPTCHA_PUBLIC_KEY"] = "6LcLVmEqAAAAAEMAeioWuCCppHqLuMRK4drkcbTx"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6LcLVmEqAAAAAN4gcOy7OFDLJxwdGL8Ge5qTrAIB"
app.config["SECRET_KEY"] = "163*%$uSfJLG^E"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///login_data.db"

db = SQLAlchemy(app)

login_menager = LoginManager()
login_menager.init_app(app)
login_menager.login_view = "login"

choiced = FireBase()


# Definicja modelu
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)


@login_menager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


# Konfiguracja bazy danych
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///login_data.db"


class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired("A username is required!")]
    )
    password = PasswordField(
        "Password", validators=[InputRequired("A password is required!")]
    )
    submit = SubmitField("Submit")
    # recaptcha = RecaptchaField()
    
class LimForm(FlaskForm):
    xlim_first = StringField("Xlim_first", render_kw={"placeholder": "np. 22-10-2024"})
    xlim_end = StringField("Xlim_end", render_kw={"placeholder": "np. 22-10-2024"})
    ylim_first = StringField("Ylim_first", render_kw={"placeholder": "np. 4000"})
    ylim_end = StringField("Ylim_end")
    generate = SubmitField("Generuj")
    # recaptcha = RecaptchaField()

@app.route("/", methods=["POST", "GET"])
def login():
    session['data_saved'] = False
    form = LoginForm()
    not_validate = False
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            not_validate = True
    return render_template("index.html", form=form, validate=not_validate)


@app.route("/dashboard", methods=["POST", "GET"])
@login_required
def dashboard():
    data_saved = session['data_saved']
    if data_saved:
        session['data_saved'] = False
    return render_template("dashboard.html", saved=data_saved)


@app.route("/firebase")
@login_required
def firebase():
    dane = choiced.getting_data_firebase()
    with open("dane.csv", "w", newline="", encoding="utf-8") as plik_csv:
        fieldnames = dane[0].keys()  # Nagłówki oparte na kluczach pierwszego słownika
        writer = csv.DictWriter(plik_csv, fieldnames=fieldnames)

        # Zapisanie nagłówków
        writer.writeheader()

        # Zapisanie wierszy (każdy słownik to jeden wiersz)
        writer.writerows(dane)

    session['data_saved'] = True
    return redirect(url_for("dashboard"))


@app.route("/figure", methods=["POST", "GET"])
@login_required
def figure():
    form = LimForm()
    try:
        data = pd.read_csv("dane.csv")
    except:
        return render_template("dashboard.html", is_chart=False, form = form)
    df = pd.DataFrame(data)
    my_plot = Plot(df)
    default_usage_data = my_plot.default_result
    if form.validate_on_submit():
        xlim = (my_plot.conv_time(form.xlim_first.data, form.xlim_end.data))
        ylim = (my_plot.convert_to_int(form.ylim_first.data, form.ylim_end.data))
        if xlim and ylim:
            my_plot.limiation()
            my_plot.saving()
            data = my_plot.limitation_values()
            print('tutaj jesetm')
            return render_template("chart.html",is_lim=True, form = form,  data = data)
        else:
            print(default_usage_data)
            return render_template("chart.html", is_lim=False, form = form, data = default_usage_data)
    else:
        if my_plot.draving_chart() == False:
            return render_template("dashboard.html", is_chart=False, form = form)
        my_plot.saving()

           
    return render_template("chart.html", form = form, data = default_usage_data)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
