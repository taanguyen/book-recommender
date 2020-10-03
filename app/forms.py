from wtforms import Form, StringField, SubmitField
from wtforms.validators import DataRequired

class InputLeadersForm(Form):
    leaders = StringField('Leaders', validators=[DataRequired()])
    submit = SubmitField('Submit')
