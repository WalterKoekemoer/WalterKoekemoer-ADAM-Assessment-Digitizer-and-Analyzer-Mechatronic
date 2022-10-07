from argparse import ArgumentError
from mimetypes import init
import os
from flask import Flask, render_template,url_for,request,redirect
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import base64,cv2
import numpy as np
import io
from PIL import Image
# import tensorflow as tf

app = Flask(__name__, instance_relative_config=True)
socketio = SocketIO(app) 
app.config['SECRET_KEY'] = 'k10wl3oa0dc@kv(#0@0('
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///adam.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



IMG_FOLDER = os.path.join('static', 'images')

app.config['UPLOAD_FOLDER'] = IMG_FOLDER

# _____________________________________HOME__________________________________________
@app.route('/')
def home():
    ADAM_Logo = os.path.join(app.config['UPLOAD_FOLDER'], 'NWU-Logo-SW.png')
    return render_template('Welcome.html',user_image=ADAM_Logo)
# _____________________________________HOME__________________________________________


# ____________________________________SIGN-UP________________________________________
@app.route('/Signup', methods=['GET'])
def Signup():
    ADAM_Logo = os.path.join(app.config['UPLOAD_FOLDER'], 'NWU-Logo-SW.png')
    return render_template('Sign-up.html',user_image=ADAM_Logo)
# ____________________________________SIGN-UP________________________________________

# ____________________________________SIGN-IN________________________________________
@app.route('/Signin', methods=['GET'])
def Signin():
    ADAM_Logo = os.path.join(app.config['UPLOAD_FOLDER'], 'NWU-Logo-SW.png')
    return render_template('Sign-in.html',user_image=ADAM_Logo)
# ____________________________________SIGN-IN________________________________________

# ___________________________________database_______________________________________

class Lecturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(22), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    type = db.Column(db.String(9), nullable=False)
    
    events = db.relationship("Event")

    def __repr__(self):
        return '<id %r>' % self.id

class Event(db.Model):
    eve_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, db.ForeignKey("lecturer.id"))
    date_create = db.Column(db.DateTime,default=datetime.utcnow)
    active = db.Column(db.Boolean, unique=False, default=True)
    modulename = db.Column(db.String(10), nullable=False)
    
    tests = db.relationship("Test", uselist=False)

    def __repr__(self):
        return '<id %r>' % self.id

class Test(db.Model):
    test_id = db.Column(db.Integer, primary_key=True)
    eve_id = db.Column(db.Integer, db.ForeignKey("event.eve_id"))

    std_num = db.Column(db.Integer, unique=True, nullable=False)
    
    sections = db.relationship("Section")

    def __repr__(self):
        return '<id %r>' % self.id

class Section(db.Model):
    sec_id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey("test.test_id"))
    std_num = db.Column(db.Integer, unique=True, nullable=False)
    ass_num = db.Column(db.Integer, unique=False, nullable=False)
    sec_name = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return '<id %r>' % self.id

class Assessor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.String(1), unique=False, nullable=True)
    password = db.Column(db.String(22), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    type = db.Column(db.String(9), nullable=False)
    
    modules = db.relationship("Module")

    def __repr__(self):
        return '<id %r>' % self.id

class Module(db.Model):
    ass_id = db.Column(db.Integer, db.ForeignKey("assessor.id"))
    id = db.Column(db.Integer, primary_key=True)
    modulename = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return '<id %r>' % self.id

# ___________________________________database_______________________________________


# ___________________________________dashboard_______________________________________

@app.route('/dashboard', methods=['POST'])
def dashboard():
    ADAM_Logo = os.path.join(app.config['UPLOAD_FOLDER'], 'NWU-Logo-SW.png')
    if request.referrer[-6:] == 'Signup':
        type = request.form.get('type')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if type and username and email and password:
            if type == "Assessor":
                assessor = Assessor(type = type, password = password, email = email, username = username)
                db.session.add(assessor)
                db.session.commit()
                return render_template(assessor.type + '.html',user_image=ADAM_Logo , assessor = assessor)
            if type == "Lecturer":
                lecturer = Lecturer(type = type, password = password, email = email, username = username)
                db.session.add(lecturer)
                db.session.add(lecturer)
                db.session.commit()
                assessors = Assessor.query.order_by(Assessor.rating)
                return render_template(lecturer.type + '.html',user_image=ADAM_Logo , lecturer = lecturer, assessors = assessors)
            # except:
            #     return "Please contact the NWU's IT department*"

        else:
            return redirect(request.referrer)
    elif request.referrer[-6:] == 'Signin':
        email = request.form.get('email')
        password = request.form.get('password')
        if email and password:
            assessor = Assessor.query.filter_by(email=email,password=password).first()
            if assessor:
                return render_template(assessor.type + '.html',user_image=ADAM_Logo , assessor = assessor)
            else:
                lecturer = Lecturer.query.filter_by(email=email,password=password).first()
                if lecturer:
                    assessors = Assessor.query.order_by(Assessor.rating)
                    return render_template(lecturer.type + '.html',user_image=ADAM_Logo , lecturer = lecturer, assessors = assessors)
                else:
                    return redirect(request.referrer)

        
# ___________________________________dashboard_______________________________________



# ____________________________________SOCKET_________________________________________
def readb64(base64_string):
    idx = base64_string.find('base64,')
    base64_string  = base64_string[idx+7:]

    sbuf = io.BytesIO()

    sbuf.write(base64.b64decode(base64_string, ' /'))
    pimg = Image.open(sbuf)

    return pimg

@socketio.on('image')
def image(data_image):
    img = (readb64(data_image))

    frame = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

    imgencode = cv2.imencode('.jpg', frame,[cv2.IMWRITE_JPEG_QUALITY,95])[1]

    # base64 encode
    stringData = base64.b64encode(imgencode).decode('utf-8')
    b64_src = 'data:image/jpg;base64,'
    stringData = b64_src + stringData
    
    emit('response_back', stringData)
# _____________________________________HOME__________________________________________


# _______________________________QUICK REFRESH_______________________________________
def before_request():
    app.jinja_env.cache = {}

# _______________________________QUICK REFRESH_______________________________________


if __name__ == '__main__':
    # model = tf.keras.models.load_model('saved_model/my_model')
    socketio.run(app, host='0.0.0.0', port=5000)