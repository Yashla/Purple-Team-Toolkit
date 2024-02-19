from flask_sqlalchemy import SQLAlchemy
from extensions import db

device_info = db.relationship('DeviceInfo', backref='device', uselist=False)

class Device(db.Model):
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(15), nullable=False)
    device_type = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Device {self.ip_address}>'
    
class DeviceInfo(db.Model):
    __tablename__ = 'devices_information'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), unique=True)
    ip_address = db.Column(db.String(255), nullable=False)
    device_type = db.Column(db.Text, nullable=False)
    os_version = db.Column(db.String(255), nullable=False)
    open_ports = db.Column(db.String(255), nullable=False)
    apps = db.Column(db.String(255), nullable=False)