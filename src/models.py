from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import force_instant_defaults

db = SQLAlchemy()
force_instant_defaults()

class Mix():
    @classmethod
    def getAllSerialized(cls):
        models = cls.query.all()
        models = list(map(lambda x: x.serialize(), models))
        return models

    @classmethod
    def getById(cls, id):
        model = cls.query.get(id)
        return model

    @classmethod
    def newInstance(cls, body):
        model = cls()               
        for attribute in body:
            setattr(model, attribute, body[attribute])
        return model

    def updateModel(self, body):        
        for attribute in body:
            if hasattr(self, attribute):
                setattr(self, attribute, body[attribute])
                db.session.commit()                
        return self

    def addCommit(self):
        db.session.add(self)
        self.store()

    def store(self):
        db.session.commit()   
        
class Enterprise(db.Model, Mix):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    cif = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    tot_hours = db.Column(db.Integer, default=0, nullable=False)
    current_hours = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    brands = db.relationship('Brand', cascade="all,delete", backref='enterprise', lazy=True)
    schedules = db.relationship('Schedule', cascade="all,delete", backref='enterprise', lazy=True)
    
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
            "current_hours": self.current_hours, 
            "is_active": self.is_active,
            "brands": list(map(lambda x: x.serialize(), self.brands)),
            "schedules": list(map(lambda x: x.serialize(), self.schedules)) 
        }

class Brand(db.Model, Mix):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    logo = db.Column(db.String(250), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    enterprise_id = db.Column(db.Integer, db.ForeignKey('enterprise.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False)
    
    def serialize(self):
        return {
            "id": self.id,            
            "name": self.name,
            "description": self.description,
            "logo": self.logo,
            "is_active": self.is_active,
            "enterprise_id": self.enterprise_id
        }

class Spacetype(db.Model, Mix):
    id = db.Column(db.Integer, primary_key=True)  
    description = db.Column(db.String(250), nullable=False)
    spaces = db.relationship('Space', cascade="all,delete", backref='spacetype', lazy=True)
    
    def serialize(self):
        return {
            "id": self.id,           
            "description": self.description,
            "spaces": list(map(lambda x: x.serialize(), self.spaces))
        }

class Space(db.Model, Mix):
    id = db.Column(db.Integer, primary_key=True)   
    name = db.Column(db.String(250), nullable=False) 
    equipments = db.relationship('Equipment', cascade="all,delete", backref='space', lazy=True)
    schedules = db.relationship('Schedule', cascade="all,delete", backref='space', lazy=True)
    spacetype_id = db.Column(db.Integer, db.ForeignKey('spacetype.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False)
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "spacetype_id": self.spacetype_id,
            "equipments": list(map(lambda x: x.serialize(), self.equipments)),
            "schedules": list(map(lambda x: x.serialize(), self.schedules))
        }

class Schedule(db.Model, Mix):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    enterprise_id = db.Column(db.Integer, db.ForeignKey('enterprise.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('space.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    __table_args__ = (db.UniqueConstraint('space_id', 'date'),)
    
    def serialize(self):
        return {
            "id": self.id,
            "date": self.date,
            "enterprise_id": self.enterprise_id,
            "space_id": self.space_id
        }

    def isSpaceReservedThisHour(self):
        sched = self        
        sched = self.query.filter_by(date=sched.date, space_id=sched.space_id)
        return db.session.query(sched.exists()).scalar()

    @classmethod
    def userHasNotEnoughHours(cls, body):
        id = body[0]['enterprise_id']
        enterprise = Enterprise.query.get(id)
        if enterprise.current_hours < len(body):            
            return True
    
    @classmethod
    def subtractHours(cls, schedulesArray):
        id = schedulesArray[0].enterprise_id
        enterprise = Enterprise.query.get(id)
        enterprise.current_hours = enterprise.current_hours - len(schedulesArray)

class Equipment(db.Model, Mix):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(250), nullable=False)    
    description = db.Column(db.String(250), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('space.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False)
    
    def serialize(self):
        return {
            "id": self.id,            
            "quantity": self.quantity,
            "name": self.name,
            "description": self.description,
            "space_id": self.space_id
        }
