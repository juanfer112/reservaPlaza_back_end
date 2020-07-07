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
def handle_enterprises():
    if request.method == 'GET':
        enterprises = Enterprise.query.all()
        enterprises = list(map(lambda x: x.serialize(), enterprises))
        return jsonify(enterprises), 200    
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
            is_admin=body['is_admin']
            )
        db.session.add(enterprise)
        db.session.commit()
        return "ok", 200
    return "Invalid Method", 404

@app.route('/enterprise/<int:id>')
def handle_enterprise(id):
    enterprise = Enterprise.query.filter_by(id=id)
    enterprise = list(map(lambda x: x.serialize(), enterprise))
    return jsonify(enterprise), 200
 
@app.route('/brand')
def handle_brands():
    brands = Brand.query.all()
    brands = list(map(lambda x: x.serialize(), brands))
    return jsonify(brands), 200  

@app.route('/brand/<int:id>', methods=['GET', 'POST'])
def handle_brand(id):
    if request.method == 'GET':
        brand = Brand.query.filter_by(enterprise_id=id)
        brand = list(map(lambda x: x.serialize(), brand))
        return jsonify(brand), 200    
    if request.method == 'POST':
        body = request.get_json()
        brand = Brand(
            name=body['name'], 
            description=body['description'],             
            logo=body['logo'],
            enterprise_id=id
            )
        db.session.add(brand)
        db.session.commit()
        return "ok", 200
    return "Invalid Method", 404

@app.route('/schedule')
def handle_schedules():
    schedules = Schedule.query.all()
    schedules = list(map(lambda x: x.serialize(), schedules))
    return jsonify(schedules), 200

@app.route('/schedule/<int:id>', methods=['GET', 'POST'])
def handle_schedule(id):
    if request.method == 'GET':
        schedule = Schedule.query.filter_by(enterprise_id=id)
        schedule = list(map(lambda x: x.serialize(), schedule))
        return jsonify(schedule), 200    
    if request.method == 'POST':
        body = request.get_json()
        schedule = Schedule(
            date=body['date'], 
            hour_start=body['hour_start'],             
            hour_end=body['hour_end'],
            enterprise_id=id,
            space_id=body['space_id']
            )
        db.session.add(schedule)
        db.session.commit()
        return "ok", 200
    return "Invalid Method", 404  

@app.route('/space')
def handle_spaces():
    schedules = Space.query.all()
    schedules = list(map(lambda x: x.serialize(), schedules))
    return jsonify(schedules), 200

@app.route('/space/<int:id>', methods=['POST'])
def handle_space(id):
    space = Space(
        spacetype_id=id
    )
    db.session.add(space)
    db.session.commit()
    return "ok", 200

@app.route('/spacetype')
def handle_spacetypes():
    spacetype = Spacetype.query.all()
    spacetype = list(map(lambda x: x.serialize(), spacetype))
    return jsonify(spacetype), 200

@app.route('/spacetype', methods=['POST'])
def handle_spacetype():
    body = request.get_json()
    spacetype = Spacetype(
        name=body['name'],
        description=body['description']
    )
    db.session.add(spacetype)
    db.session.commit()
    return "ok", 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
