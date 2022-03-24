"""
This is the central application implementation of the Expense Tracker Service.
The service supports registration of new expenses as well as queries of the
expenses in the given currencies, sorted by multiple parameters.
"""

# Standard Library Imports
import logging
from datetime import datetime

# Third Party Imports
import click
from flask import (Flask, jsonify, redirect, render_template,
                   request, session, url_for)
from flask_cors import CORS
from gevent.pywsgi import WSGIServer

# Application Imports
from constants import (APP_KEY, SORTED_BY_OPTIONS,
                       SORTING_OPTION_LABELS, SUPPORTED_CURRENCIES)
from data_persistence import IN_MEMORY_STORAGE, persist_spending
from schemas import ExpenseForm,  Spending

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(format="%(process)d-%(levelname)s-%(message)s")

app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = APP_KEY


# Operative Endpoints
@app.route("/switch_sorting", methods=["GET"])
def switch_sorting():
    session["sorted_by_index"] =\
        (session.get("sorted_by_index", 0) + 1) % len(SORTED_BY_OPTIONS)
    return redirect(url_for("index"))


@app.route("/switch_listed_currency/", defaults={"curr": None})
@app.route("/switch_listed_currency/<curr>", methods=["GET"])
def switch_listed_currency(curr):
    if not curr:
        session["listed_currency"] = None
    else:
        session["listed_currency"] = curr
    return redirect(url_for("index"))


# User-facing Endpoints
@app.route("/spendings/", defaults={"curr": None, "by_what": "amount"})
@app.route("/spendings/<curr>/<by_what>", methods=["GET"])
def get_spendings(curr, by_what):
    if not curr:
        curr = "ALL"
    return jsonify(list(IN_MEMORY_STORAGE[f"{curr}_by_{by_what}"]))


@app.route("/add_spending", methods=["POST"])
def add_spending():
    new_spending = request.get_json()
    new_spending["spent_at"] = datetime.utcnow()
    persist_spending(Spending(**new_spending))
    return jsonify({"Response": 200})


@app.route("/", methods=["GET", "POST"])
def index():
    form = ExpenseForm()
    if request.method == "POST":
        if not form.validate_on_submit():
            logging.error("Invalid form submitted: %s", form.errors)
        else:
            try:
                persist_spending(Spending(
                    amount=form.amount.data,
                    currency=form.currency.data,
                    description=form.description.data,
                    spent_at=datetime.utcnow()
                ))
                return redirect(url_for("index"))
            except Exception as exc:
                # Do not raise the exception, allow presentation of
                # past expenses even if the persistance fails.
                logging.error("Exception occured while persisting data: %d",
                              str(exc))

    # Select the relevant container to display
    if SORTED_BY_OPTIONS[session.get("sorted_by_index", 0)] == "spent_at":
        key_postfix = "by_time"
    else:
        key_postfix = "by_amount"
    currency = session.get("listed_currency")
    if currency:
        filtered_data = IN_MEMORY_STORAGE[f"{currency}_{key_postfix}"]
    else:
        filtered_data = IN_MEMORY_STORAGE[f"ALL_{key_postfix}"]

    return render_template(
        "index.html", form=form,
        exps=filtered_data,
        currencies=SUPPORTED_CURRENCIES,
        sorting_button_label=SORTING_OPTION_LABELS[
            session.get("sorted_by_index", 0)],
        listed_currency=session.get("listed_currency"))


@click.command()
@click.option("--host", type=str, default="localhost")
@click.option("--port", type=int, default=5000)
def main(host, port):
    http_server = WSGIServer((host, port), app)
    logging.info("Starting WSGI server on host %s, port %s", host, port)
    http_server.serve_forever()


if __name__ == "__main__":
    main()
