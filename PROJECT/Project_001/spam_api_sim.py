"""
source: https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
code: https://gist.github.com/leon-sleepinglion/97bfd34132394e23ca5905ec730f776a

To run the app: python app.py
This will start the Flask web server. To access the user data on the web browser:
http://127.0.0.1:5000/user/Elvin

This will display Elvin's user data

Also, curl the same web address will have the same result

https://github.robot.car/cruise/embedded-linux/blob/develop/apps/cruise-websrv/cruise_websrv/modules/spam/spam.md
"""
from flask import Flask
from flask_restful import Api, Resource, reqparse
import re


__AUTHOR__ = 'Ray Lai'
app = Flask(__name__)
api = Api(app)

sim_api = [
    {
        'type': 'solenoid_on',
        'output': {'api': '/api/v1.0/spam/solenoid/set',
                   'test_mode': 'Simulation',
                   'status': 'success'},
        'Method': 'post',
        'desc': 'Set fan speed to 100%'
    },
    {
        'type': 'solenoid_off',
        'output': {'api': '/api/v1.0/spam/solenoid/set',
                   'test_mode': 'Simulation',
                   'status': 'success'},
        'Method': 'post',
        'desc': 'Set fan speed to 0%'
    },
    {
        'type': 'fan_on',
        'output': {'api': '/api/v1.0/spam/fan_on',
                   'test_mode': 'Simulation',
                   'status': 'success'},
        'Method': 'post',
        'desc': 'Set fan speed to 100%'
    },
    {
        'type': 'fan_off',
        'output': {'api': '/api/v1.0/spam/fan_off',
                   'test_mode': 'Simulation',
                   'status': 'success'},
        'Method': 'post',
        'desc': 'Set fan speed to 0%'
    },
    {
        'type': 'fan_speed/set',
        'output': {'api': '/api/v1.0/spam/fan_speed/set/{percent}',
                   'test_mode': 'Simulation',
                   'status': 'success'},
        'Method': 'post',
        'desc': 'Set fan speed percent; can be a value from 0-100 to set speed to {percent}%'
    },
    {
        'type': 'fan_speed/get',
        'output': {'api': '/api/v1.0/spam/fan_speed/get',
                   'test_mode': 'Simulation',
                   'status': 'success',
                   'RPM' : '<Fan RPM>'},
        'Method': 'post',
        'desc': '{fan} can be either 0 or 1 return a JSON message containing the RPM of the Fan requested'
    },
]

failed_msg = {
    "api": "invalid port",
    "test_mode": "Simulation",
    "status": "failed"
}


class sim_interface(Resource):

    def get(self, name: str) -> (str, int):
        for user in users:
            if name == user["name"]:
                return user, 200
        return "User not found", 404

    def post(self, name: str) -> (dict, int):
        # parser = reqparse.RequestParser()
        # parser.add_argument("age")
        # parser.add_argument("occupation")
        # args = parser.parse_args()
        port = int(re.search(r'\d+', name).group(0))
        feature_type = name.split('/')[0]  # solenoid, fan, CPU, etc
        print(f'{port = }, {feature_type = }')
        if 0 <= port <= 7:
            for api_dict in sim_api:
                if feature_type == api_dict['type']:
                    return api_dict.get('output'), 200
        else:
            return failed_msg, 404

    def put(self, name: str) -> (str, int):
        parser = reqparse.RequestParser()
        parser.add_argument("age")
        parser.add_argument("occupation")
        args = parser.parse_args()

        for user in users:
            if name == user["name"]:
                user["age"] = args["age"]
                user["occupation"] = args["occupation"]
                return user, 200

        user = {
            "name": name,
            "age": args["age"],
            "occupation": args["occupation"]
        }
        users.append(user)
        return user, 201

    def delete(self, name: str) -> (str, int):
        global users
        users = [user for user in users if user["name"] != name]
        return f"{name} is deleted.", 200


api.add_resource(sim_interface, "/api/v1.0/spam/<string:name>")

app.run(debug=True)

# if __name__ == '__main__':
#     s = sim_interface()
#     print(s.post('solenoid_on/1'))
"""

Solenoid Control
Attribute	Value
URI	/api/v1.0/spam/solenoid_on/{solenoid}
Method	POST
# curl -X POST http://<url>:<port>/api/v1.0/spam/solenoid_on/{solenoid}
solenoid can be a value from 0-7 Set Solenoid current to 100%

Attribute	Value
URI	/api/v1.0/spam/solenoid_off/{solenoid}
Method	POST
# curl -X POST http://<url>:<port>/api/v1.0/spam/solenoid_off/{solenoid}
solenoid can be a value from 0-7 Set Solenoid current to 0%

Get Sensor Value
Attribute	Value
URI	/api/v1.0/spam/check/
Method	GET
# curl http://<url>:<port>/api/v1.0/spam/check/temp
# curl http://<url>:<port>/api/v1.0/spam/check/humidity
Returns a JSON message containing data from onboard sensor(temperature and humidity).

{
    "api": "/api/v1.0/spam/check/temp",
    "status": "success",
    "data": "{'unit': <'C'>,  'reading': '<temperature_value>'}"
}
{
    "api": "/api/v1.0/spam/check/humidity",
    "status": "success",
    "data": "{'unit': <'%HR'>,  'reading': '<humidity_value>'}"
"""