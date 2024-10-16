from flask import Flask, render_template, url_for, redirect
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
Bootstrap5(app)
app.config['RECAPTCHA_PUBLIC_KEY'] = "6LcLVmEqAAAAAEMAeioWuCCppHqLuMRK4drkcbTx"
app.config['RECAPTCHA_PRIVATE_KEY'] = "6LcLVmEqAAAAAN4gcOy7OFDLJxwdGL8Ge5qTrAIB"
app.config["SECRET_KEY"] = "163*%$uSfJLG^E"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login_data.db'

db = SQLAlchemy(app)

login_menager = LoginManager()
login_menager.init_app(app)
login_menager.login_view = "login"


# Definicja modelu
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)

@login_menager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

# Konfiguracja bazy danych
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login_data.db'

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired("A username is required!")])
    password = PasswordField("Password",validators=[InputRequired("A password is required!")])
    submit = SubmitField("Submit")
    # recaptcha = RecaptchaField()

@app.route('/', methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else: return "<h1>Błędne dane logowania</h1><a href = '/'>Wróć do strony logowania</a>", 401
    return render_template("index.html", form = form)

@app.route('/dashboard', methods=["POST", "GET"])
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)