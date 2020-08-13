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
    
    @classmethod
    def isSpaceReservedThisHour(cls, date, space_id):
        sched = cls.query.filter_by(date=date, space_id=space_id)
        return db.session.query(sched.exists()).scalar() 

    @classmethod
    def get_enterprise_with_login_credentials(cls,email,password):
        return db.session.query(cls).filter(Enterprise.email==email).filter(Enterprise.password==password).one_or_none()
    
    def is_admin(self):     #esta funcion retorna una respuesta de true o false, indicando si es administrador o no. 
        return self.is_admin 

    def updateModel(self, body):           
        for attribute in body:
            if hasattr(self, attribute):
                setattr(self, attribute, body[attribute])            
        return True
       
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
    is_admin = db.Column(db.Boolean, default=False)
    brands = db.relationship('Brand', cascade="all,delete", backref='enterprise', lazy=True)
    schedules = db.relationship("Schedule", back_populates="enterprise")
    
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
    
    # def get_enterprise_with_login_credentials(self,email,password):
        #return db.session.query().filter(self.email==email).filter(self.password==password).one_or_none()
                                         


    def userHasNotEnoughHours(self, length):
        if self.current_hours < length:            
            return True
        else: False

    def subtractHours(self, length):
        self.current_hours = self.current_hours - length

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
    description = db.Column(db.String(250), nullable=False)
    spacetype_id = db.Column(db.Integer, db.ForeignKey('spacetype.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False)
    schedules = db.relationship("Schedule", back_populates="space")
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "spacetype_id": self.spacetype_id,
            "description": self.description,
            "equipments": list(map(lambda x: x.serialize(), self.equipments)),
            "schedules": list(map(lambda x: x.serialize(), self.schedules))
        }

class Schedule(db.Model, Mix):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('space.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    enterprise_id = db.Column(db.Integer, db.ForeignKey('enterprise.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    enterprise = db.relationship("Enterprise", back_populates="schedules")
    space = db.relationship("Space", back_populates="schedules")
    __table_args__ = (db.UniqueConstraint('space_id', 'date'),)
    
    def serialize(self):
        return {
            "id": self.id,
            "date": self.date,
            "space_id": self.space_id,
            "enterprise_id": self.enterprise_id,
            "enterprise_name": self.enterprise.name,
            "space_name": self.space.name
        }

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
