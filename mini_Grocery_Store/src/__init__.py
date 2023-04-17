from flask import Flask
from .models import db, UserModel
from flask_bcrypt import Bcrypt
from flask_uploads import IMAGES, UploadSet, configure_uploads
import os
from flask_msearch import Search
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_moment import Moment

basedir = os.path.abspath(os.path.dirname(__file__))

# initializing all the installed packages here.

search = Search()
bcrypt = Bcrypt()
login_manager = LoginManager()
moment = Moment()
photos = UploadSet('photos', IMAGES)


def create_app():
    app = Flask(__name__)
    # database name and path to save mentioned here.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # all the uploaded images like product images will be saved in this directory
    app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')

    # connecting all the installed packages with the app
    configure_uploads(app, photos)
    Bootstrap(app)
    db.init_app(app)
    bcrypt.init_app(app)
    search.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)

    # flask_login package setting.
    login_manager.login_view = 'customer_bp.login'
    login_manager.needs_refresh_message_category = 'danger'
    login_manager.login_message = u"Please login first"

    @login_manager.user_loader
    def user_loader(user_id):
        return UserModel.query.get(int(user_id))

    # all the blueprint registered with app here
    from src.admin.routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/")
    from src.customers.routes import customer_bp
    app.register_blueprint(customer_bp, url_prefix="/")
    from src.carts.carts import cart_bp
    app.register_blueprint(cart_bp, url_prefix="/")
    from src.products.routes import products_bp
    app.register_blueprint(products_bp, url_prefix="/")

    @app.before_first_request
    def create_table():
        db.create_all()

        if not UserModel.query.filter_by(username='admin').first():

            user = UserModel(name='admin', username='admin',
                             email='admin@email.com',
                             password=bcrypt.generate_password_hash('12345678'),
                             is_admin=True)
            db.session.add(user)
            db.session.commit()
            print('admin user created')

    return app
