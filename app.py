from flask import Flask, render_template
from werkzeug.security import generate_password_hash

from models import db, User
from extensions import cache
from routes.auth import auth
from routes.admin import admin
from routes.company import company
from routes.student import student


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY']                = 'ppa_secret_key_2024'
    app.config['SQLALCHEMY_DATABASE_URI']   = 'sqlite:///placement.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['CACHE_TYPE']      = 'RedisCache'
    app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/1'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 60    

    app.config['MAIL_ENABLED']  = True              
    app.config['MAIL_SERVER']   = 'localhost'
    app.config['MAIL_PORT']     = 1025
    app.config['MAIL_USE_TLS']  = False
    app.config['MAIL_USERNAME'] = ''   
    app.config['MAIL_PASSWORD'] = ''   
    app.config['MAIL_DEFAULT_SENDER'] = 'placement-portal@ppa.com'

    db.init_app(app)
    cache.init_app(app)

    if app.config['MAIL_ENABLED']:
        from flask_mail import Mail
        mail = Mail(app)

    app.register_blueprint(auth,    url_prefix='/auth')
    app.register_blueprint(admin,   url_prefix='/admin')
    app.register_blueprint(company, url_prefix='/company')
    app.register_blueprint(student, url_prefix='/student')

    @app.route('/')
    def index():
        return render_template('index.html')


    with app.app_context():
        db.create_all()

        if not User.query.filter_by(role='admin').first():
            admin_user = User(
                name          = 'Admin',
                email         = 'admin@ppa.com',
                password_hash = generate_password_hash('admin123'),
                role          = 'admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: admin@ppa.com / admin123")

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
