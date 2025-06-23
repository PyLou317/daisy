import os
import csv
import pandas as pd
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import func
from app import db, login_manager
from models import User, Contractor, ReviewQueue, UploadHistory
from forms import LoginForm, RegisterForm, ContractorForm, UploadForm
from utils import parse_date, allowed_file, process_csv_upload

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Main Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('auth/login.html', form=LoginForm())
    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get dashboard statistics
    total_contractors = Contractor.query.count()
    active_contractors = Contractor.query.filter_by(candidate_status='Current').count()
    pending_reviews = ReviewQueue.query.filter_by(reviewed=False).count()
    
    # Recent uploads
    recent_uploads = UploadHistory.query.order_by(UploadHistory.uploaded_at.desc()).limit(5).all()
    
    # Active contractors with highest spreads
    top_contractors = Contractor.query.filter_by(candidate_status='Current')\
        .filter(Contractor.spread_amount.isnot(None))\
        .order_by(Contractor.spread_amount.desc()).limit(10).all()
    
    # Monthly statistics
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_revenue = db.session.query(func.sum(Contractor.spread_amount))\
        .filter(func.extract('month', Contractor.created_at) == current_month)\
        .filter(func.extract('year', Contractor.created_at) == current_year)\
        .scalar() or 0
    
    return render_template('dashboard.html',
                         total_contractors=total_contractors,
                         active_contractors=active_contractors,
                         pending_reviews=pending_reviews,
                         recent_uploads=recent_uploads,
                         top_contractors=top_contractors,
                         monthly_revenue=monthly_revenue)

@main_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_csv():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            try:
                # Process the CSV upload
                result = process_csv_upload(file, current_user.id)
                
                flash(f'CSV processed successfully! {result["added"]} contractors added, '
                      f'{result["updated"]} updated, {result["queued"]} queued for review.',
                      'success')
                
                return redirect(url_for('main.dashboard'))
            except Exception as e:
                flash(f'Error processing CSV: {str(e)}', 'error')
        else:
            flash('Invalid file format. Please upload a CSV file.', 'error')
    
    return render_template('upload.html', form=form)

@main_bp.route('/review-queue')
@login_required
def review_queue():
    pending_reviews = ReviewQueue.query.filter_by(reviewed=False)\
        .join(Contractor).order_by(ReviewQueue.added_at.desc()).all()
    
    return render_template('review_queue.html', pending_reviews=pending_reviews)

@main_bp.route('/review-queue/<int:review_id>/action/<action>')
@login_required
def review_action(review_id, action):
    review_item = ReviewQueue.query.get_or_404(review_id)
    
    if action == 'remove':
        # Mark contractor as inactive
        review_item.contractor.candidate_status = 'Inactive'
        review_item.action_taken = 'removed'
    elif action == 'keep':
        # Keep contractor active
        review_item.action_taken = 'kept'
    
    review_item.reviewed = True
    review_item.reviewed_at = datetime.utcnow()
    review_item.reviewed_by = current_user.id
    
    db.session.commit()
    flash(f'Review item {action}d successfully.', 'success')
    
    return redirect(url_for('main.review_queue'))

# Authentication Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            return redirect(next_page)
        flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

# Contractors Blueprint
contractors_bp = Blueprint('contractors', __name__)

@contractors_bp.route('/')
@login_required
def list_contractors():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    
    query = Contractor.query
    
    if search:
        query = query.filter(
            (Contractor.talent_name.ilike(f'%{search}%')) |
            (Contractor.account_name.ilike(f'%{search}%')) |
            (Contractor.job_title.ilike(f'%{search}%'))
        )
    
    if status:
        query = query.filter_by(candidate_status=status)
    
    contractors = query.order_by(Contractor.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('contractors/list.html', 
                         contractors=contractors,
                         search=search,
                         status=status)

@contractors_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_contractor():
    form = ContractorForm()
    if form.validate_on_submit():
        contractor = Contractor(
            talent_name=form.talent_name.data,
            job_title=form.job_title.data,
            candidate_status=form.candidate_status.data,
            talent_start_date=form.talent_start_date.data,
            talent_end_date=form.talent_end_date.data,
            mobile=form.mobile.data,
            talent_id=form.talent_id.data,
            recruiter=form.recruiter.data,
            account_manager=form.account_manager.data,
            account_name=form.account_name.data,
            spread_amount=form.spread_amount.data,
            created_by=current_user.id
        )
        db.session.add(contractor)
        db.session.commit()
        
        flash('Contractor added successfully!', 'success')
        return redirect(url_for('contractors.list_contractors'))
    
    return render_template('contractors/add.html', form=form)

@contractors_bp.route('/<int:id>')
@login_required
def view_contractor(id):
    contractor = Contractor.query.get_or_404(id)
    return render_template('contractors/view.html', contractor=contractor)

@contractors_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_contractor(id):
    contractor = Contractor.query.get_or_404(id)
    form = ContractorForm(obj=contractor)
    
    if form.validate_on_submit():
        form.populate_obj(contractor)
        contractor.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Contractor updated successfully!', 'success')
        return redirect(url_for('contractors.view_contractor', id=id))
    
    return render_template('contractors/edit.html', form=form, contractor=contractor)

@contractors_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_contractor(id):
    contractor = Contractor.query.get_or_404(id)
    
    # Add to review queue instead of deleting immediately
    review_item = ReviewQueue(
        contractor_id=id,
        reason='Manual deletion request',
        added_by=current_user.id
    )
    db.session.add(review_item)
    db.session.commit()
    
    flash('Contractor has been queued for review.', 'info')
    return redirect(url_for('contractors.list_contractors'))
