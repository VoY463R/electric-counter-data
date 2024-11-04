from flask import Flask, render_template, url_for, redirect, request, session, jsonify
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired
from werkzeug.security import check_password_hash
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
)
from main_class import FireBase
import csv
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime
from figure_class import Plot
from dotenv import load_dotenv
import os
from models import User, DataSaved, db
from forms import LoginForm, LimForm


app = Flask(__name__)
Bootstrap5(app)
matplotlib.use("Agg")

# Load environment variables from the .env file
load_dotenv()

app.config["RECAPTCHA_PUBLIC_KEY"] = os.getenv("RECAPTCHA_PUBLIC_KEY")
app.config["RECAPTCHA_PRIVATE_KEY"] = os.getenv("RECAPTCHA_PRIVATE_KEY")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Konfiguracja bazy danych
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_BINDS"] = {
    'primary' : os.getenv("SQLALCHEMY_PRIMARY_BIND"),
    'secondary' : os.getenv("SQLALCHEMY_SECONDARY_BIND")
    }

# Database initialization
db.init_app(app)

choiced = FireBase()

login_menager = LoginManager()
login_menager.init_app(app)
login_menager.login_view = "login"

@login_menager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

with app.app_context():
    db.create_all()

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
            return render_template("chart.html",is_lim=True, form = form,  data = data)
        else:
            return render_template("chart.html", is_lim=False, form = form, data = default_usage_data)
    else:
        if my_plot.draving_chart() == False:
            return render_template("dashboard.html", is_chart=False, form = form)
        my_plot.saving()

           
    return render_template("chart.html", form = form, data = default_usage_data)

@app.route('/saving')
@login_required
def saving():
    down_time = datetime.strptime(request.args.get('down_time'), '%Y-%m-%d %H:%M:%S')
    up_time = datetime.strptime(request.args.get('up_time'), '%Y-%m-%d %H:%M:%S')
    used_elec = request.args.get('used_elec')
    with app.app_context():
        try:
            new_event = DataSaved(low_date=down_time, high_date=up_time, used_energy=used_elec)
            db.session.add(new_event)
            db.session.commit()
        except:
            redirect(url_for("figure"))
    return redirect(url_for("figure"))

@app.route('/database')
@login_required
def database():
    usage_saved = DataSaved.query.all()
    return render_template("database.html", usage_saved = usage_saved)

@app.route('/delete')
@login_required
def delete():
    id = request.args.get("id")
    data_to_delete = DataSaved.query.get_or_404(id)
    try:
        db.session.delete(data_to_delete)
        db.session.commit()
        return redirect(url_for('database'))
    except:
        return "There was an issue deleting your data"
    

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
