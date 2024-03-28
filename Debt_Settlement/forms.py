from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


# class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')  # submit button to submit to our route


class UpdateProfileForm(FlaskForm):
    user_name = StringField('Name', validators=[DataRequired()])
    # Add more fields as needed
    submit = SubmitField('Save Changes')