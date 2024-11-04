from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired

class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired("A username is required!")]
    )
    password = PasswordField(
        "Password", validators=[InputRequired("A password is required!")]
    )
    submit = SubmitField("Submit")
    
class LimForm(FlaskForm):
    xlim_first = StringField("Xlim_first", render_kw={"placeholder": "np. 22-10-2024"})
    xlim_end = StringField("Xlim_end", render_kw={"placeholder": "np. 22-10-2024"})
    ylim_first = StringField("Ylim_first", render_kw={"placeholder": "np. 4000"})
    ylim_end = StringField("Ylim_end")
    generate = SubmitField("Generuj")
