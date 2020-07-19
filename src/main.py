import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Enterprise, Schedule, Space, Equipment, Spacetype, Brand
from create_database import init_database
from datetime import datetime, timedelta
from date_convert import ConvertDate

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_database()
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

def toJson(model):
    return jsonify(model.serialize())

@app.route('/enterprises', methods=['GET', 'POST'])
def handle_enterprises():
    if request.method == 'GET':
        return jsonify(Enterprise.getAll()), 200 
    if request.method == 'POST':
        body = request.get_json()       
        newEnterprise = Enterprise.newInstance(body)        
        newEnterprise.addCommit()
        return toJson(newEnterprise), 201

@app.route('/enterprises/<int:id>', methods=['GET', 'PUT'])
def handle_enterprise(id):
    if request.method == 'GET':
        enterprise = Enterprise.query.get(id)
        return toJson(enterprise), 200
    if request.method == 'PUT':
        body = request.get_json()
        update = Enterprise.query.get(id)
        if update is None:
            raise APIException('Enterprise not found', status_code=404)
        if "name" in body:
            update.name = body["name"]
        if "last_name" in body:
            update.last_name = body["last_name"]
        if "email" in body:
            update.email = body["email"]
        if "password" in body:
            update.password = body["password"]
        if "cif" in body:
            update.cif = body["cif"]
        if "phone" in body:
            update.phone = body["phone"]
        if "tot_hours" in body:
            update.tot_hours = body["tot_hours"]
        db.session.commit()
        return "Enterprise correctly edited", 200

@app.route('/brands', methods=['GET', 'POST'])
def handle_brands():
    if request.method == 'GET':
        return jsonify(Brand.getAll()), 200 
    if request.method == 'POST':
        body = request.get_json()
        newBrand = Brand.newInstance(body)        
        newBrand.addCommit()
        return toJson(newBrand), 201

@app.route('/brands/<int:id>', methods=['GET', 'PUT'])
def handle_brand(id):
    if request.method == 'GET':
        brand = Brand.query.get(id)
        return toJson(brand), 200
    if request.method == 'PUT':
        body = request.get_json()
        update = Brand.query.get(id)
        if update is None:
            raise APIException('Brand not found', status_code=404)
        if "name" in body:
            update.name = body["name"]
        if "description" in body:
            update.description = body["description"]
        if "logo" in body:
            update.logo = body["logo"]      
        db.session.commit()
        return "Brand correctly edited", 200

@app.route('/schedules', methods=['GET', 'POST'])
def handle_schedules():
    if request.method == 'GET':
        return jsonify(Schedule.getAll()), 200
    if request.method == 'POST':
        body = request.get_json()
        schedulesToAdd = []
        for obj in body:
            schedule = Schedule.newInstance(obj)    
            if ConvertDate.stringToDate(schedule.date) > ConvertDate.fixedTimeZoneCurrentTime():
                schedulesToAdd.append(schedule)
        if len(schedulesToAdd) == len(body):
            db.session.bulk_save_objects(schedulesToAdd)
            db.session.commit()
            return jsonify(list(map(lambda x: x.serialize(), schedulesToAdd))), 201
        return {"Message" : "One or more dates are not selectable"}, 422         

@app.route('/schedules/<int:id>', methods=['GET', 'PUT'])
def handle_schedule(id):
    if request.method == 'GET':
        schedule = Schedule.query.get(id)
        return toJson(schedule), 200
    if request.method == 'PUT':
        body = request.get_json()
        update = Schedule.query.get(id)
        if update is None:
            raise APIException('Enterprise not found', status_code=404)
        if "name" in body:
            update.name = body["name"]        
        db.session.commit()
        return "Schedule correctly edited", 200

@app.route('/spaces', methods=['GET', 'POST'])
def handle_spaces():
    if request.method == 'GET':
        return jsonify(Space.getAll()), 200
    if request.method == 'POST':
        body = request.get_json()
        newSpace = Space.newInstance(body)
        newSpace.addCommit()
        return toJson(newSpace), 201

@app.route('/spaces/<int:id>', methods=['GET', 'PUT'])
def handle_space(id):
    if request.method == 'GET':
        space = Space.query.get(id)
        return toJson(space), 200
    if request.method == 'PUT':
        body = request.get_json()
        update = Space.query.get(id)
        if update is None:
            raise APIException('Space not found', status_code=404)
        if "name" in body:
            update.name = body["name"]
        if "spacetype_id" in body:
            update.spacetype_id = body["spacetype_id"]
        db.session.commit()
        return "Space correctly edited", 200

@app.route('/spacetypes', methods=['GET', 'POST'])
def handle_spacetypes():
    if request.method == 'GET':
        return jsonify(Spacetype.getAll()), 200
    if request.method == 'POST':
        body = request.get_json()
        newSpacetype = Spacetype.newInstance(body)
        newSpacetype.addCommit()
        return toJson(newSpacetype), 201

@app.route('/spacetypes/<int:id>', methods=['GET', 'PUT'])
def handle_spacetype(id):
    if request.method == 'GET':
        spacetype = Spacetype.query.get(id)
        return toJson(spacetype), 200
    if request.method == 'PUT':
        body = request.get_json()
        update = Spacetype.query.get(id)
        if update is None:
            raise APIException('Spacetype not found', status_code=404)
        if "description" in body:
            update.description = body["description"]
        db.session.commit()
        return "Spacetype correctly edited", 200

@app.route('/equipments', methods=['GET', 'POST'])
def handle_equipments():
    if request.method == 'GET':
        return jsonify(Equipment.getAll()), 200
    if request.method == 'POST':
        body = request.get_json()
        newEquipment = Equipment.newInstance(body)
        newEquipment.addCommit()
        return toJson(newEquipment), 201

@app.route('/equipments/<int:id>', methods=['GET', 'PUT'])
def handle_equipment(id):
    if request.method == 'GET':
        equipment = Equipment.query.get(id)
        return toJson(equipment), 200
    if request.method == 'PUT':
        body = request.get_json()
        update = Equipment.query.get(id)
        if update is None:
            raise APIException('Equipment not found', status_code=404)
        if "description" in body:
            update.description = body["description"]
        if "name" in body:
            update.name = body["name"]
        if "quantity" in body:
            update.quantity = body["quantity"]
        db.session.commit()
        return "Equipments correctly edited", 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
