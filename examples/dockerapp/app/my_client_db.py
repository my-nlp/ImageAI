from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
import os
import logging


app = Flask(__name__)

execution_path = os.getcwd()

v_log = logging.getLogger('VDLOG')
v_log.setLevel(logging.DEBUG)
fh = logging.FileHandler(os.path.join(execution_path, "vapp.log"))
ch = logging.StreamHandler()  
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
v_log.addHandler(ch)
v_log.addHandler(fh)

DATABASE = os.path.join(execution_path, 'detect.db')
dburi = 'sqlite:////{:}'.format(DATABASE)
print("dburi: ", dburi)
app.config['SQLALCHEMY_DATABASE_URI'] = dburi

db = SQLAlchemy(app)

class VideoInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, unique=True, nullable=False)
    detectInfo = db.Column(db.String(256), unique=False, nullable=True)

    def __repr__(self):
        return '<url %r>' % self.url
