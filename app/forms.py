from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class InputLeadersForm(FlaskForm):
    leaders = StringField('Leaders', validators=[DataRequired()],  \
        render_kw={"placeholder": "mark manson; elizabeth gilbert"})
