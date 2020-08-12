import os
import json
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Enterprise, Schedule, Space, Equipment, Spacetype, Brand
from create_database import init_database
from datetime import datetime, timedelta, date
from date_convert import ConvertDate
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity
)
from sqlalchemy import extract

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_database()
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_BLACKLIST_'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
jwt = JWTManager(app)

blacklist=set()

# login_manager= LoginManager()
# login_manager.init_app(app)
# login_manager.login_view='login'

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist

# @login_manager.user_loader
# def load_user(user_id):
#     return Enterprise.query.filter_by(id=user_id).one()

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = request.json.get('email', None)
    password = request.json.get('password', None)
   
    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    
    enterprise = Enterprise.get_enterprise_with_login_credentials(email,password)

    if enterprise == None:
        return jsonify({"msg": "Bad email or password"}), 400

    access_token = create_access_token(identity=enterprise.email)
    
    ret = {
        'access_token': access_token,
        'refresh_token': create_refresh_token(identity=enterprise.email),
        'is_admin': enterprise.is_admin()
    }
    return jsonify(ret), 200

    # Identity can be any data that is json serializable
    
@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    user_id = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=user_id)
    }
    return jsonify(ret), 200
    
@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as = current_user), 200
    
#@app.route('/logout', methods=['DELETE'])
#@jwt_required
#def logout():
#    jti = get_raw_jwt()['jti']
#    blacklist.add(jti)
#    return jsonify({"msg": "Successfully logged out"}), 200

@app.route('/logout', methods=['DELETE'])
@jwt_required
def logged():
    user_id = get_raw_identity()
    blacklist.add(jti)
    return jsonify(logged_in_as=user_id), 200


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

def toJson(model):
    return jsonify(model.serialize())

def addCommitArray(arrayToSave):
    db.session.bulk_save_objects(arrayToSave)
    db.session.commit()

@app.route('/enterprises', methods=['GET', 'POST'])
def handle_enterprises():
    if request.method == 'GET':
        return jsonify(Enterprise.getAllSerialized()), 200 
    if request.method == 'POST':
        body = request.get_json()       
        newEnterprise = Enterprise.newInstance(body)        
        newEnterprise.addCommit()
        return toJson(newEnterprise), 201

@app.route('/enterprises/<int:id>', methods=['GET', 'PUT'])
def handle_enterprise(id):
    enterprise = Enterprise.getById(id)
    if request.method == 'GET':
        return toJson(enterprise), 200
    if request.method == 'PUT':
        body = request.get_json()
        enterprise.updateModel(body)
        enterprise.store()
        return json.dumps({"message" : "Correctly scheduled"}), 200

@app.route('/brands', methods=['GET', 'POST'])
def handle_brands():
    if request.method == 'GET':
        return jsonify(Brand.getAllSerialized()), 200 
    if request.method == 'POST':
        body = request.get_json()
        newBrand = Brand.newInstance(body)        
        newBrand.addCommit()
        return toJson(newBrand), 201

@app.route('/brands/<int:id>', methods=['GET', 'PUT'])
def handle_brand(id):
    brand = Brand.query.get(id)
    if request.method == 'GET':        
        return toJson(brand), 200
    if request.method == 'PUT':
        body = request.get_json()
        brand.updateModel(body)
        brand.store()
        return json.dumps({"message" : "Correctly scheduled"}), 200

@app.route('/schedules/<date>', methods=['GET'])
def handle_schedule_before_after(date): 
    today = ConvertDate.stringToDate(date)
    start = today - timedelta(days=today.weekday()) - timedelta(days=8)
    end = start + timedelta(days=22)
    schedules = db.session.query(Schedule).filter(start < Schedule.date).filter(Schedule.date < end )
    return jsonify(list(map(lambda y: y.serialize(), schedules))), 200

@app.route('/schedules', methods=['POST'])
def handle_schedules():
    body = request.get_json()
    schedulesToAdd = []
    enterprise = Enterprise.query.get(body[0]['enterprise_id'])        
    if enterprise.userHasNotEnoughHours(len(body)): 
        return json.dumps({"message" : "Enterprise has not enough hours"}), 424
    for schedule in body:
        newSchedule = Schedule.newInstance(schedule)
        if newSchedule.isSpaceReservedThisHour(newSchedule.date, newSchedule.space_id):
            return json.dumps({"message" : "Duplicate entity"}), 409        
        if ConvertDate.stringToDate(newSchedule.date) > ConvertDate.fixedTimeZoneCurrentTime():
            schedulesToAdd.append(newSchedule)
    if len(schedulesToAdd) == len(body):
        enterprise.subtractHours(len(schedulesToAdd))
        addCommitArray(schedulesToAdd)
        return json.dumps({"message" : "Correctly scheduled"}), 201
    return json.dumps({"message" : "Past dates are not selectable"}), 422         

@app.route('/schedules/<int:id>', methods=['GET', 'PUT'])
def handle_schedule(id):
    schedule = Schedule.query.get(id)
    if request.method == 'GET':
        return toJson(schedule), 200
    if request.method == 'PUT':
        body = request.get_json()
        date = schedule.date
        space_id = schedule.space_id
        if body['date']: date = body['date']
        if body['space_id']: space_id = body['space_id']
        if Schedule.isSpaceReservedThisHour(date, space_id ):
            return json.dumps({"message" : "Duplicate entity"}), 409
        schedule.updateModel(body)
        schedule.store()        
        return json.dumps({"message" : "Correctly scheduled"}), 200

@app.route('/spaces', methods=['GET', 'POST'])
def handle_spaces():
    if request.method == 'GET':
        return jsonify(Space.getAllSerialized()), 200
    if request.method == 'POST':
        body = request.get_json()
        newSpace = Space.newInstance(body)
        newSpace.addCommit()
        return toJson(newSpace), 201

@app.route('/spaces/<int:id>', methods=['GET', 'PUT'])
def handle_space(id):
    space = Space.query.get(id)
    if request.method == 'GET':        
        return toJson(space), 200
    if request.method == 'PUT':
        body = request.get_json()
        space.updateModel(body)
        space.store()
        return json.dumps({"message" : "Correctly scheduled"}), 200

@app.route('/spacetypes', methods=['GET', 'POST'])
def handle_spacetypes():
    if request.method == 'GET':
        return jsonify(Spacetype.getAllSerialized()), 200
    if request.method == 'POST':
        body = request.get_json()
        newSpacetype = Spacetype.newInstance(body)
        newSpacetype.addCommit()
        return toJson(newSpacetype), 201

@app.route('/spacetypes/<int:id>', methods=['GET', 'PUT'])
def handle_spacetype(id):
    spacetype = Spacetype.query.get(id)
    if request.method == 'GET':
        return toJson(spacetype), 200
    if request.method == 'PUT':
        body = request.get_json()
        spacetype.updateModel(body)
        spacetype.store()
        return json.dumps({"message" : "Correctly scheduled"}), 200


@app.route('/equipments', methods=['GET', 'POST'])
def handle_equipments():
    if request.method == 'GET':
        return jsonify(Equipment.getAllSerialized()), 200
    if request.method == 'POST':
        body = request.get_json()
        newEquipment = Equipment.newInstance(body)
        newEquipment.addCommit()
        return toJson(newEquipment), 201

@app.route('/equipments/<int:id>', methods=['GET', 'PUT'])
def handle_equipment(id):
    equipment = Equipment.query.get(id)
    if request.method == 'GET':        
        return toJson(equipment), 200
    if request.method == 'PUT':
        body = request.get_json()
        equipment.updateModel(body)
        equipment.store()
        return json.dumps({"message" : "Correctly scheduled"}), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
