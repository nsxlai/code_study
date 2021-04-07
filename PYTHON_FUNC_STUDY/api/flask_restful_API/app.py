"""
source: https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
code: https://gist.github.com/leon-sleepinglion/97bfd34132394e23ca5905ec730f776a

To run the app: python app.py
This will start the Flask web server. To access the user data on the web browser:
http://127.0.0.1:5000/user/Elvin

This will display Elvin's user data

Also, curl the same web address will have the same result
"""
from flask import Flask
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

users = [
    {
        "name": "Nicholas",
        "age": 42,
        "occupation": "Network Engineer"
    },
    {
        "name": "Elvin",
        "age": 32,
        "occupation": "Doctor"
    },
    {
        "name": "Jass",
        "age": 22,
        "occupation": "Web Developer"
    },
]


class User(Resource):

    def get(self, name: str) -> (str, int):
        for user in users:
            if name == user["name"]:
                return user, 200
        return "User not found", 404

    def post(self, name: str) -> (str, int):
        parser = reqparse.RequestParser()
        parser.add_argument("age")
        parser.add_argument("occupation")
        args = parser.parse_args()

        for user in users:
            if name == user["name"]:
                return f"User with name {name} already exists", 400

        user = {
            "name": name,
            "age": args["age"],
            "occupation": args["occupation"]
        }
        users.append(user)
        return user, 201

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
        global user
        users = [user for users in users if user["name"] != name]
        return f"{name} is deleted.", 200


api.add_resource(User, "/user/<string:name>")

app.run(debug=True)

