from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Enterprise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False) 
    cif = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    tot_hours = db.Column(db.Integer, nullable=False)
    brands = db.relationship('Brand', backref='enterprise', lazy=True)
    schedules = db.relationship('Schedule', backref='enterprise', lazy=True)
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "last_name": self.last_name,
            "email": self.email,
            "password": self.password,
            "cif": self.cif,
            "phone": self.phone,
            "tot_hours": self.tot_hours, 
            "brands": list(map(lambda x: x.serialize(), self.brands)),
            "schedules": list(map(lambda x: x.serialize(), self.schedules)) 
        }
        
class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    logo = db.Column(db.String(250), nullable=False)
    enterprise_id = db.Column(db.Integer, db.ForeignKey('enterprise.id'),
        nullable=False)
    
    def serialize(self):
        return {
            "id": self.id,            
            "name": self.name,
            "description": self.description,
            "logo": self.logo,
            "enterpriseID": self.enterprise_id
        }


class Spacetype(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    description = db.Column(db.String(250), nullable=False)
    spaces = db.relationship('Space', backref='spacetype', lazy=True)
    
    def serialize(self):
        return {
            "id": self.id,           
            "description": self.description,
            "spaces": list(map(lambda x: x.serialize(), self.spaces))
        }

class Space(db.Model):
    id = db.Column(db.Integer, primary_key=True)   
    name = db.Column(db.String(250), nullable=False) 
    equipments = db.relationship('Equipment', backref='space', lazy=True)
    schedules = db.relationship('Schedule', backref='space', lazy=True)
    spacetype_id = db.Column(db.Integer, db.ForeignKey('spacetype.id'),
        nullable=False)
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "spacetypeID": self.spacetype_id,
            "equipments": list(map(lambda x: x.serialize(), self.equipments)),
            "schedules": list(map(lambda x: x.serialize(), self.schedules))
        }

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Integer, nullable=False)
    hour_start = db.Column(db.Integer, nullable=False)
    hour_end = db.Column(db.Integer, nullable=False)
    enterprise_id = db.Column(db.Integer, db.ForeignKey('enterprise.id'),
        nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('space.id'), 
        nullable=False)
    
    def serialize(self):
        return {
            "id": self.id,
            "date": self.date,
            "hour_start": self.hour_start,
            "hour_end": self.hour_end,
            "enterpriseID": self.enterprise_id,
            "spaceID": self.space_id
        }

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('space.id'),
        nullable=False)
    
    def serialize(self):
        return {
            "id": self.id,            
            "quantity": self.quantity,
            "name": self.name,
            "description": self.description,
            "spaceID": self.space_id
        }
