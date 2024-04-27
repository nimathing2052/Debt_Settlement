from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class SendMoneyForm(FlaskForm):
    recipient = SelectField('Select Recipient:', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Enter Amount:', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    submit = SubmitField('Send')
