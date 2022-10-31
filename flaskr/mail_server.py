from mimetypes import init
from flask_mail import Mail,Message

class mail_server(Mail):
    def __init__(self, app=None):
        super().__init__(app)
        app.config['MAIL_SERVER']='smtp.gmail.com'
        app.config['MAIL_PORT'] = 465
        app.config['MAIL_USERNAME'] = 'yourId@gmail.com'
        app.config['MAIL_PASSWORD'] = 'L3@ndriKo3k3mo3r'
        app.config['MAIL_USE_TLS'] = False
        app.config['MAIL_USE_SSL'] = True