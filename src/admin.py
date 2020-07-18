import os
from flask_admin import Admin, BaseView, expose
from models import db, Enterprise, Schedule, Space, Equipment, Spacetype, Brand
from flask_admin.contrib.sqla import ModelView

class MyView(BaseView):
    @expose('/')
    def index(self):
        import time
        current_time = time.strftime("%d/%m/%Y")
        return self.render('index.html', schedule=list(map(lambda x: x.serialize(), Schedule.query.all())), data = current_time)       

class MyModelView(ModelView):
    column_display_pk = True

class MyModelViewActive(MyModelView):
    def get_query(self):
        return self.session.query(self.model).filter(self.model.is_active==True)

    def delete_model(self, model):
        try:
            self.on_model_delete(model)            
            model.is_active = False         
            db.session.commit()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(gettext('Failed to delete record. %(error)s', error=str(ex)), 'error')
                log.exception('Failed to delete record.')
            self.session.rollback()
            return False
        else:
            self.after_model_delete(model)
        return True

class MyModelViewNotActive(MyModelView):
    def get_query(self):        
        return self.session.query(self.model).filter(self.model.is_active==False)

class MyModelViewBrands(MyModelView):
    def get_query(self):
        return self.session.query(self.model).join(Enterprise).filter(Enterprise.is_active==True)
        
def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'    
    admin = Admin(app, name='Admin', template_mode='bootstrap3')

    admin.add_view(MyModelViewActive(Enterprise, db.session, endpoint='enterprises', menu_icon_type='glyph', menu_icon_value='glyphicon-user'))
    admin.add_view(MyModelViewBrands(Brand, db.session, endpoint='brands', menu_icon_type='glyph', menu_icon_value='glyphicon-briefcase'))
    admin.add_view(MyModelView(Schedule, db.session, endpoint='schedules', menu_icon_type='glyph', menu_icon_value='glyphicon-list-alt'))
    admin.add_view(MyModelView(Equipment, db.session, endpoint='equipments', menu_icon_type='glyph', menu_icon_value='glyphicon-wrench'))
    admin.add_view(MyModelView(Space, db.session, endpoint='spaces'))       
    admin.add_view(MyModelView(Spacetype, db.session, endpoint='spacetypes', ))    
    admin.add_view(MyModelViewNotActive(Enterprise, db.session, "Inactive Enterprise", endpoint='inactive-enterprises', menu_icon_type='glyph', menu_icon_value='glyphicon-alert'))
