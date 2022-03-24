from dataclasses import dataclass
from datetime import datetime


from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_cors import CORS
from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SelectField, SubmitField
from wtforms.validators import DataRequired


IN_MEMORY_STORAGE = []
SUPPORTED_CURRENCIES = ['USD', 'HUF']

SORTED_BY_OPTIONS = ["amount", "spent_at",]
SORTING_OPTION_LABELS = ["Sort_by_Amount", "Sort_by_Time"]

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'filesystem'


class ExpenseForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired()],
                          render_kw={"placeholder": 0})
    currency = SelectField('Currency', choices=[SUPPORTED_CURRENCIES],
                           validate_choice=False)
    description = StringField('Description', validators=[DataRequired()],
                              render_kw={"placeholder": "Description"})
    submit = SubmitField('SAVE')


@dataclass
class Spending:
    amount : float
    currency: str
    description: str
    spent_at: datetime


def persist_spending(spending: Spending):
    IN_MEMORY_STORAGE.append(spending)


@app.route("/spendings", methods=["GET"])
def get_spendings():
    return jsonify(IN_MEMORY_STORAGE)

@app.route("/add_spending", methods=["POST"])
def add_spending():
    new_spending= request.get_json()
    persist_spending(Spending(**new_spending))
    return jsonify({"Response": 200})

@app.route("/switch_sorting", methods=["GET"])
def switch_sorting():
    session['sorted_by_index'] = (session.get('sorted_by_index', 0) + 1) % len(SORTED_BY_OPTIONS)
    return redirect(url_for('index'))

@app.route('/switch_listed_currency/', defaults={'curr': None})
@app.route("/switch_listed_currency/<curr>", methods=["GET"])
def switch_listed_currency(curr):
    if not curr:
        session['listed_currency'] = None
    else:
        session['listed_currency'] = curr
    return redirect(url_for('index'))


@app.route("/", methods=["GET", "POST"])
def index():
    form = ExpenseForm()
    if request.method == 'POST':
        if form.validate_on_submit():

            persist_spending(Spending(
                amount=form.amount.data,
                currency=form.currency.data,
                description=form.description.data,
                spent_at=datetime.utcnow()
            ))
            return redirect(url_for('index'))
        else:
            print(f"Invalid form submitted: {form.errors}")
    if SORTED_BY_OPTIONS[session.get('sorted_by_index',0)] == 'spent_at':
        sorting_key = lambda spending: spending.spent_at
    else:
        sorting_key = lambda spending: spending.amount
    if session.get('listed_currency'):
        filtered_data = [e for e in IN_MEMORY_STORAGE if e.currency == session['listed_currency']]
    else:
        filtered_data = IN_MEMORY_STORAGE
    sorted_data = sorted(filtered_data, key=sorting_key)
    return render_template('index.html', form=form,
                           exps=sorted_data,
                           currencies=SUPPORTED_CURRENCIES,
                           sorting_button_label=SORTING_OPTION_LABELS[session.get('sorted_by_index', 0)])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
