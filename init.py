from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired

app = Flask(__name__)
Bootstrap5(app)
app.config['RECAPTCHA_PUBLIC_KEY'] = "6LcLVmEqAAAAAEMAeioWuCCppHqLuMRK4drkcbTx"
app.config['RECAPTCHA_PRIVATE_KEY'] = "6LcLVmEqAAAAAN4gcOy7OFDLJxwdGL8Ge5qTrAIB"
app.config["SECRET_KEY"] = "163*%$uSfJLG^E"

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired("A username is required!")])
    password = PasswordField("Password",validators=[InputRequired("A password is required!")])
    # recaptcha = RecaptchaField()
    
@app.route('/', methods=["POST", "GET"])
def home():
    form = LoginForm()
    
    if form.validate_on_submit():
        return "Hello there"
    return render_template("index.html", form = form)

if __name__ == "__main__":
    app.run(debug=True)