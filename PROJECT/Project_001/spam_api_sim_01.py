from flask import Flask
from flask import redirect
from flask import request

app = Flask(__name__)

"""
check hwinfo (get): http://10.1.1.2:80/api/v1.0/spam/trace/hwinfo'
check swinfo (get): http://10.1.1.2:80/api/v1.0/swupdate/sw-versions/rootfs'
check cpuinfo (get): http://10.1.1.2:80/api/v1.0//spam/cpu_check/lscpu'

solenoid on (post): http://10.1.1.2:80/api/v1.0/spam/solenoid_on/<port>; port = 0-7
solenoid off (post): http://10.1.1.2:80/api/v1.0/spam/solenoid_off/<port>; port = 0-7

fan on (post): http://10.1.1.2:80/api/v1.0/spam/fan_on
fan off (post): http://10.1.1.2:80/api/v1.0/spam/fan_off

Set fan duty cycle (post): http://10.1.1.2:80/api/v1.0/spam/fan_speed/set/<percent>; percent = 0-100
Get fan duty cycle (get): http://10.1.1.2:80/api/v1.0/spam/fan_speed/get/<fan>; fan = 0 or 1 for fan number
{
    "api": "api/v1.0/spam/fan_speed/get",
    "status": "success",
    "RPM": <fan_rpm>
}

Check temperature (get): http://10.1.1.2:80/api/v1.0/spam/check/temp
{
    "api": "api/v1.0/spam/check/temp",
    "status": "success",
    "data": "{'unit': 'C', 'reading': <temp_value>}"
}
Check humidity (get): http://10.1.1.2:80/api/v1.0/spam/check/humidity
{
    "api": "api/v1.0/spam/check/humidity",
    "status": "success",
    "data": "{'unit': '%HR', 'reading': <humidity_value>}"
}
"""


# Basic Route
@app.route("/")
def spam_sim():
    return "This is SPAM simulated API"


# Different Route
@app.route("/test")
def test():
    return "Test different route"


# Route with parameter in route
# Variable must be passed to method
@app.route("/api/v1.0/spam/solenoid_on/<port>")
def solenoid_on_api_sim(port):
    solenoid_on_json = {'api': f'api/v1.0/spam/solenoid_on/{port}',
                        'status': 'success'}
    return solenoid_on_json


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
