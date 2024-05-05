from flask import Flask
from flask import redirect
from flask import request

app = Flask(__name__)


# Basic Route
@app.route("/")
def hello():
    return "Hello World!"


# Different Route
@app.route("/test")
def test():
    return "Test different route"


# Route with parameter in route
# Variable must be passed to method
@app.route("/test/<param>")
def param_test(param):
    return "Received: {}".format(param)


# Route with parameters passed as args
# Example: /test/args?name=<name>&age=<age>
@app.route("/test/args")
def arg_test():
    name = request.args.get('name')
    age = request.args.get('age')
    return "Name is {}\nAge is {}".format(name, age)


# Route with HTTP method constraints
@app.route("/methods", methods=['GET', 'POST'])
def default():
    if request.method == 'POST':
        return "Received POST Request"
    else:
        return "Received GET Request"


# Route with type constraint on parameter
@app.route("/test/square/<int:param>")
def int_test(param):
    return "Square of {} is {}".format(param, param * param)


# Route to three amigos
@app.route("/three-amigos")
def three_amigos():
    return redirect(
        "https://www.denverpost.com/2013/09/04/broncos-original-three-amigos-ride-again-living-on-in-nfl-history/",
        code=302)
