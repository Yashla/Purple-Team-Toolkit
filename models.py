from flask_sqlalchemy import SQLAlchemy
from extensions import db
from flask_login import UserMixin




device_info = db.relationship('DeviceInfo', backref='device', uselist=False)

class Device(db.Model):
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(15), nullable=False)
    device_type = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    device_info = db.relationship('DeviceInfo', backref='device', uselist=False, lazy=True)

    def __repr__(self):
        return f'<Device {self.ip_address}>'
    
class DeviceInfo(db.Model):
    __tablename__ = 'devices_information'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), unique=True)
    ip_address = db.Column(db.String(255), nullable=False)
    device_type = db.Column(db.Text, nullable=False)
    Vendor = db.Column(db.String(255), nullable=False)
    Product = db.Column(db.String(255), nullable=False)
    Version = db.Column(db.String(255), nullable=False)
    
    
class CVE(db.Model):
    __tablename__ = 'cves'
    cve_id = db.Column(db.String(64), primary_key=True)
    summary = db.Column(db.Text)
    cvss_v3_score = db.Column(db.Text)
    cvss_v3_label= db.Column(db.Text)
    
class DeviceCVE(db.Model):
    __tablename__ = 'device_cves'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    cve_id = db.Column(db.String(64), db.ForeignKey('cves.cve_id'))

    device = db.relationship('Device', backref=db.backref('device_cves', lazy=True))
    cve = db.relationship('CVE', backref=db.backref('device_cves', lazy=True))


class SSDPOutput(db.Model):
    __tablename__ = 'ssdp_outputs'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)  
    output_blob = db.Column(db.LargeBinary, nullable=False)  
    
class SNMP_Output(db.Model):
    __tablename__ = 'snmp_outputs'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)  


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)  # This is the expected field

    def __repr__(self):
        return '<User {}>'.format(self.username)