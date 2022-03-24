# Standard Library Imports
from dataclasses import dataclass
from datetime import datetime

# Third Party Imports
from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

# Application Imports
from constants import SUPPORTED_CURRENCIES


@dataclass
class Spending:
    amount : float
    currency: str
    description: str
    spent_at: datetime


class ExpenseForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired()],
                          render_kw={"placeholder": 0})
    currency = SelectField('Currency', choices=[SUPPORTED_CURRENCIES],
                           validate_choice=False)
    description = StringField('Description', validators=[DataRequired()],
                              render_kw={"placeholder": "Description"})
    submit = SubmitField('SAVE')
