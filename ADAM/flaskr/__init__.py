import os

from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # add database
    from . import db
    db.init_app(app)

    # add mail server
    from .compo.mail_server import mail
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'walterkoekemoer97@gmail.com'
    app.config['MAIL_PASSWORD'] = 'L3@ndriKo3k3mo3r'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail.__init__(app)

    # add blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    from .compo import assessor
    app.register_blueprint(assessor.bp)

    from .compo import lecturer
    app.register_blueprint(lecturer.bp)

    from .compo import student
    app.register_blueprint(student.bp)

    from .compo import adam
    app.register_blueprint(adam.bp)

    from .compo import room
    app.register_blueprint(room.bp)

    return app