"""
source: https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
"""
from flask import Flask
from flask_restful import Api, Resource, reqparse


users = [
    {
        "name": "Nick",
        "age": 42,
        "occupation": "Engineer"
    },
    {
        "name": "Amber",
        "age": 32,
        "occupation": "Sale"
    },
    {
        "name": "Jess",
        "age": 28,
        "occupation": "Technician"
    }
]

app = Flask(__name__)
api = Api(app)


class User(Resource):
    def get(self, name):
        if name == "all":
            return users, 200
        for user in users:
            if name == user.get('name'):
                return user, 200
        return "User not found", 404

    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("age")
        parser.add_argument("occupation")
        args = parser.parse_args()

        for user in users:
            if name == user.get('name'):
                return f'User with name {name} already exists!', 400

        user = {
            "name": name,
            "age": args['age'],
            "occupation": args['occupation']
        }

        users.append(user)
        return user, 201  # Append the new user into the

    def put(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("age")
        parser.add_argument("occupation")
        args = parser.parse_args()

        for user in users:
            if name == user.get('name'):
                user['age'] = args['age']
                user['occupation'] = args['occupation']
                return user, 200

        user = {
            "name": name,
            "age": args['age'],
            "occupation": args['occupation']
        }

        users.append(user)
        return user, 201

    def delete(self, name):
        global users
        users = [user for user in users if user["name"] != name]
        return f'{name} is delete!', 200


if __name__ == '__main__':

    api.add_resource(User, "/user/<string:name>")
    app.run(debug=True)
