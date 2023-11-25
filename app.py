from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.form:
        amount_in_account = request.form.get("amount_in_account")
    else:
        amount_in_account = 0

    return render_template("index.html", amount_in_account=amount_in_account)
