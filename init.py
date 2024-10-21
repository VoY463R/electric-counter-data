from flask import Flask, render_template, url_for, redirect, request
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
import matplotlib.pyplot as plt

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


def create_plot():
    try:
        df = pd.read_csv("dane.csv")
    except:
        return False
    df["Czas"] = pd.to_datetime(df["Czas"], format="%y-%m-%d %H:%M:%S")
    df.sort_values("Czas", inplace=True)
    print(df)
    time = df["Czas"]
    value = df["Odczytana wartosc"]
    plt.figure(figsize=(10, 5))
    plt.plot(time, value, marker="o")
    plt.title("Wykres wartości w czasie (posortowane)")
    plt.xlabel("Data i czas")
    plt.ylabel("Wartość")
    plt.xticks(rotation=45)
    plt.grid(True)

    # Zapisane wykresu jako obrazek
    plt.savefig("static/chart.png", bbox_inches="tight")
    plt.close()


@app.route("/", methods=["POST", "GET"])
def login():
    form = LoginForm()
    not_validate = False
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            not_validate = True
    return render_template("index.html", form=form, validate = not_validate)


@app.route("/dashboard", methods=["POST", "GET"])
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/firebase")
@login_required
def firebase():
    dane = choiced.getting_data_firebase()
    print(dane)
    with open("dane.csv", "w", newline="", encoding="utf-8") as plik_csv:
        fieldnames = dane[0].keys()  # Nagłówki oparte na kluczach pierwszego słownika
        writer = csv.DictWriter(plik_csv, fieldnames=fieldnames)

        # Zapisanie nagłówków
        writer.writeheader()

        # Zapisanie wierszy (każdy słownik to jeden wiersz)
        writer.writerows(dane)

    print("Dane zostały zapisane do pliku CSV.")
    return redirect(url_for("dashboard"))


@app.route("/figure")
@login_required
def figure():
    chart = create_plot()
    if chart == False:
        return "<h1>Błąd przy odczycie pliku</h1><a href = '/dashboard'>Wróć do poprzedniej strony</a>"
    return render_template("chart.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
