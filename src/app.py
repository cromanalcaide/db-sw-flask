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

@app.route("/planet", methods=['POST'])
def create_planet():
    body = json.loads(request.data)
    planet = Planets(name = body["name"], climate = body["climate"])
    db.session.add(planet)
    db.session.commit()

    response_body = {
        "msg": " The new planet has been created correctly "
    }

    return jsonify(response_body), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
