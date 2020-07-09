import os
from flask_admin import Admin
from models import db, Enterprise, Schedule, Space, Equipment, Spacetype, Brand
from flask_admin.contrib.sqla import ModelView

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='Admin', template_mode='bootstrap3')

    admin.add_view(ModelView(Enterprise, db.session))
    admin.add_view(ModelView(Schedule, db.session))
    admin.add_view(ModelView(Space, db.session))
    admin.add_view(ModelView(Equipment, db.session))
    admin.add_view(ModelView(Spacetype, db.session))
    admin.add_view(ModelView(Brand, db.session))