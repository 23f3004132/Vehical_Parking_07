from flask import Flask
from models.model import db, User

app = None

def setup_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
    db.init_app(app)
    app.app_context().push()
    app.debug = True
    print("App is setup")

# call the setup
setup_app()

from controllers.controller import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(full_name='admin',email='Satyanshi@gmail.com', password='123',role='admin', address='Delhi', pin_code='110001')
            db.session.add(admin)
            db.session.commit()
    app.run()