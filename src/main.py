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
from models import db, Enterprise, Schedule, Space, Equipment, Spacetype, Brand
from create_database import init_database

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_database()
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/enterprise', methods=['GET', 'POST'])
def handle_enterprise():

    if request.method == 'GET':
        all_people = Enterprise.query.all()
        all_people = list(map(lambda x: x.serialize(), all_people))
        return jsonify(all_people), 200
    
    if request.method == 'POST':
        body = request.get_json()
        enterprise = Enterprise(
            name=body['name'], 
            last_name=body['last_name'], 
            email=body['email'], 
            password=body['password'],
            cif=body['cif'],
            phone=body['phone'], 
            tot_hours=body['tot_hours'], 
            is_admin=False
        )
        db.session.add(enterprise)
        db.session.commit()
        return "ok", 200

    return "Invalid Method", 404

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
