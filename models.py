from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import zoneinfo

db = SQLAlchemy()

def ist_now():
    return datetime.now(zoneinfo.ZoneInfo('Asia/Kolkata')).replace(tzinfo=None)


class User(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role          = db.Column(db.String(20), nullable=False)   
    is_active     = db.Column(db.Boolean, default=True)

    cgpa          = db.Column(db.Float,   nullable=True)
    branch        = db.Column(db.String(50),  nullable=True)
    year          = db.Column(db.Integer, nullable=True)
    resume        = db.Column(db.String(200), nullable=True)   


class CompanyProfile(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name    = db.Column(db.String(100), nullable=False)
    hr_contact      = db.Column(db.String(100), nullable=False)
    website         = db.Column(db.String(100), nullable=True)
    approval_status = db.Column(db.String(20), default='Pending')  
    is_blacklisted  = db.Column(db.Boolean, default=False)


class PlacementDrive(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    company_id  = db.Column(db.Integer, db.ForeignKey('company_profile.id'), nullable=False)
    job_title   = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    eligibility = db.Column(db.String(200), nullable=True)  
    min_cgpa    = db.Column(db.Float, nullable=True)
    min_year    = db.Column(db.Integer, nullable=True)
    deadline    = db.Column(db.Date, nullable=False)         
    status      = db.Column(db.String(20), default='Pending')  


class Application(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    student_id       = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    drive_id         = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    status           = db.Column(db.String(20), default='Applied')  
    application_date = db.Column(db.DateTime, default=ist_now)
    interview_date   = db.Column(db.DateTime, nullable=True)
