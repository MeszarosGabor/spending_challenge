# Standard Library Imports
from dataclasses import dataclass
from datetime import datetime

# Third Party Imports
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_cors import CORS

# Application Imports
from constants import APP_KEY, SORTED_BY_OPTIONS, SORTING_OPTION_LABELS, SUPPORTED_CURRENCIES
from data_persistence import IN_MEMORY_STORAGE, persist_spending
from schemas import ExpenseForm,  Spending


app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = APP_KEY


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


@app.route("/spendings", methods=["GET"])
def get_spendings():
    return jsonify(IN_MEMORY_STORAGE)


@app.route("/add_spending", methods=["POST"])
def add_spending():
    new_spending= request.get_json()
    new_spending['spent_at']=datetime.utcnow()
    persist_spending(Spending(**new_spending))
    return jsonify({"Response": 200})


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

    # Apply the filtering and sorting criteria present.
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
