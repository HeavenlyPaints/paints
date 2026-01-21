from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, FileField, HiddenField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional

class AdminLoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class ProductForm(FlaskForm):
    name = StringField("Product name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Optional()])
    price = IntegerField("Price (smallest unit)", validators=[DataRequired(), NumberRange(min=0)])
    image = FileField("Image (optional)")
    submit = SubmitField("Save")

class RefererApplyForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    phone = StringField("Phone", validators=[DataRequired()])
    email = StringField("Email", validators=[Optional(), Email()])
    whatsapp = StringField("WhatsApp", validators=[Optional()])
    submit = SubmitField("Apply")

class CheckoutForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone", validators=[DataRequired()])
    submit = SubmitField("Proceed to Pay")

class WithdrawalForm(FlaskForm):
    amount = IntegerField("Amount (smallest unit)", validators=[DataRequired(), NumberRange(min=1)])
    account_details = TextAreaField("Account Details", validators=[DataRequired()])
    submit = SubmitField("Request Withdrawal")

class ChangeAdminForm(FlaskForm):
    username = StringField("New Username", validators=[DataRequired()])
    password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Change")
