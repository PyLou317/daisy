from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Numeric
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

class Contractor(db.Model):
    __tablename__ = 'contractors'
    
    id = db.Column(db.Integer, primary_key=True)
    talent_name = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(100))
    candidate_status = db.Column(db.String(50), default='Current')
    talent_start_date = db.Column(db.Date)
    talent_end_date = db.Column(db.Date)
    mobile = db.Column(db.String(20))
    talent_id = db.Column(db.String(50), unique=True)
    recruiter = db.Column(db.String(100))
    peoplesoft_id = db.Column(db.String(50))
    account_manager = db.Column(db.String(100))
    account_name = db.Column(db.String(200))
    spread_amount = db.Column(Numeric(10, 2))
    days_since_service = db.Column(db.Integer)
    opt_out_mobile = db.Column(db.String(10), default='No')
    
    # Tracking fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    creator = db.relationship('User', backref='contractors_created')
    
    def __repr__(self):
        return f'<Contractor {self.talent_name}>'
    
    @property
    def contract_duration_days(self):
        if self.talent_start_date and self.talent_end_date:
            return (self.talent_end_date - self.talent_start_date).days
        return None
    
    @property
    def is_active(self):
        return self.candidate_status == 'Current'

class ReviewQueue(db.Model):
    __tablename__ = 'review_queue'
    
    id = db.Column(db.Integer, primary_key=True)
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractors.id'), nullable=False)
    reason = db.Column(db.String(200))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed = db.Column(db.Boolean, default=False)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    action_taken = db.Column(db.String(50))  # 'removed', 'kept', 'modified'
    
    # Relationships
    contractor = db.relationship('Contractor', backref='review_entries')
    added_by_user = db.relationship('User', foreign_keys=[added_by], backref='review_items_added')
    reviewed_by_user = db.relationship('User', foreign_keys=[reviewed_by], backref='review_items_reviewed')
    
    def __repr__(self):
        return f'<ReviewQueue {self.contractor.talent_name}>'

class UploadHistory(db.Model):
    __tablename__ = 'upload_history'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    records_processed = db.Column(db.Integer)
    records_added = db.Column(db.Integer)
    records_updated = db.Column(db.Integer)
    records_queued_for_review = db.Column(db.Integer)
    status = db.Column(db.String(50), default='completed')
    error_message = db.Column(db.Text)
    
    # Relationships
    uploader = db.relationship('User', backref='uploads')
    
    def __repr__(self):
        return f'<UploadHistory {self.filename}>'
