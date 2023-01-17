"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route("/user", methods=["GET"])
def get_users():
    user = User.query.all()
    userList = list(map(lambda obj : obj.serialize(), user ))

    response_body = {
        "msg":"Here's your user list: ",
        "results":  userList
    }

    return jsonify(response_body), 200

@app.route("/user/<int:id>", methods=["GET"])
def user_detail(id):
    user = db.get_or_404(User, id)
    userDetail = user.serialize()
    
    response_body = {
        "msg":"Here's your user: ",
        "results":  userDetail
    }
    
    return jsonify(response_body), 200

@app.route("/planet", methods=["GET"])
def get_planet():
    planet = Planets.query.all()
    planetList = list(map(lambda obj : obj.serialize(), planet ))

    response_body = {
        "msg":"Lots of planets, mate ",
        "results":  planetList
    }

    return jsonify(response_body), 200

# @app.route("/planet/create", methods=["POST"])
# def create_planet():
#     planet = Planets(
#             name=request.form["name"],
#             climate=request.form["climate"]
#         )
#     db.session.add(planet)
#     db.session.commit()
#     response_body = {
#         "msg":"New planet, mate",
#         "results":  planet
#     }

#     return jsonify(response_body), 200

@app.route("/planet/create", methods=["POST"])
def create_planet():
    request_body = request.get_json()
    planet = Planets(
                    name = request_body['name'],
                    climate = request_body['climate']
                )
    db.session.add(planet)
    db.session.commit()
    return request_body, 200
    # return jsonify(request_body), 200

# Endpoint /user
# @app.route('/user', methods=['GET', 'POST'])
# def user():
#     if request.method == 'GET':
#         users = User.query.all()
#         results = [user.serialize() for user in users]
#         response_body = {"message": "ok",
#                          "total_records": len(results),
#                          "results": results}
#         return response_body, 200
#         # return jsonify(response_body), 200
#     if request.method == 'POST':
#         request_body = request.get_json()



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
