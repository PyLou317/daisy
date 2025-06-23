import csv
import pandas as pd
from datetime import datetime
from io import StringIO
from flask import current_app
from werkzeug.utils import secure_filename
from app import db
from models import Contractor, ReviewQueue, UploadHistory

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_date(date_string):
    """Parse date string in various formats."""
    if not date_string or date_string.strip() == '':
        return None
    
    date_formats = ['%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y']
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_string.strip(), fmt).date()
        except ValueError:
            continue
    
    return None

def parse_decimal(value_string):
    """Parse decimal values, handling various formats."""
    if not value_string or value_string.strip() == '':
        return None
    
    try:
        # Remove currency symbols and commas
        cleaned = value_string.replace('$', '').replace(',', '').strip()
        return float(cleaned)
    except (ValueError, AttributeError):
        return None

def process_csv_upload(file, user_id):
    """Process uploaded CSV file and update contractor database."""
    
    # Read the CSV file
    try:
        # Read file content
        file_content = file.read().decode('utf-8')
        file.seek(0)  # Reset file pointer
        
        # Parse CSV
        csv_reader = csv.DictReader(StringIO(file_content))
        
        stats = {
            'processed': 0,
            'added': 0,
            'updated': 0,
            'queued': 0
        }
        
        # Get existing talent IDs for comparison
        existing_talent_ids = set(
            contractor.talent_id for contractor in 
            Contractor.query.filter(Contractor.talent_id.isnot(None)).all()
        )
        
        # Track current upload talent IDs
        current_upload_ids = set()
        
        for row in csv_reader:
            stats['processed'] += 1
            
            # Extract data from CSV row
            talent_id = row.get('Talent ID', '').strip()
            talent_name = row.get('Talent Name', '').strip()
            
            if not talent_name:
                continue  # Skip empty rows
            
            current_upload_ids.add(talent_id)
            
            # Check if contractor exists
            existing_contractor = None
            if talent_id:
                existing_contractor = Contractor.query.filter_by(talent_id=talent_id).first()
            
            if existing_contractor:
                # Update existing contractor
                update_contractor_from_csv(existing_contractor, row)
                stats['updated'] += 1
            else:
                # Create new contractor
                contractor = create_contractor_from_csv(row, user_id)
                if contractor:
                    db.session.add(contractor)
                    stats['added'] += 1
        
        # Find contractors that are no longer in the upload (potential removals)
        missing_contractors = Contractor.query.filter(
            Contractor.talent_id.notin_(current_upload_ids),
            Contractor.candidate_status == 'Current'
        ).all()
        
        # Queue missing contractors for review
        for contractor in missing_contractors:
            existing_review = ReviewQueue.query.filter_by(
                contractor_id=contractor.id,
                reviewed=False
            ).first()
            
            if not existing_review:
                review_item = ReviewQueue(
                    contractor_id=contractor.id,
                    reason='Not found in latest upload - potential removal',
                    added_by=user_id
                )
                db.session.add(review_item)
                stats['queued'] += 1
        
        # Save upload history
        upload_record = UploadHistory(
            filename=secure_filename(file.filename),
            uploaded_by=user_id,
            records_processed=stats['processed'],
            records_added=stats['added'],
            records_updated=stats['updated'],
            records_queued_for_review=stats['queued'],
            status='completed'
        )
        db.session.add(upload_record)
        
        # Commit all changes
        db.session.commit()
        
        return stats
        
    except Exception as e:
        db.session.rollback()
        
        # Log error in upload history
        error_record = UploadHistory(
            filename=secure_filename(file.filename),
            uploaded_by=user_id,
            status='failed',
            error_message=str(e)
        )
        db.session.add(error_record)
        db.session.commit()
        
        raise e

def create_contractor_from_csv(row, user_id):
    """Create a new contractor from CSV row data."""
    try:
        contractor = Contractor(
            talent_name=row.get('Talent Name', '').strip(),
            job_title=row.get('Job Title', '').strip(),
            candidate_status=row.get('Candidate Status', 'Current').strip(),
            talent_start_date=parse_date(row.get('Talent Start Date', '')),
            talent_end_date=parse_date(row.get('Talent End Date', '')),
            mobile=row.get('Mobile', '').strip(),
            talent_id=row.get('Talent ID', '').strip(),
            recruiter=row.get('Recruiter', '').strip(),
            peoplesoft_id=row.get('Peoplesoft ID', '').strip(),
            account_manager=row.get('Account Manager', '').strip(),
            account_name=row.get('Account Name', '').strip(),
            spread_amount=parse_decimal(row.get('Spread Amount', '') or row.get('Weekly Spread', '') or row.get('Spread', '')),
            days_since_service=int(row.get('Days Since Service', 0)) if row.get('Days Since Service', '').strip().isdigit() else 0,
            opt_out_mobile=row.get('PrefCentre_Aerotek_OptOut_Mobile', 'No').strip(),
            created_by=user_id
        )
        return contractor
    except Exception as e:
        current_app.logger.error(f"Error creating contractor from CSV row: {e}")
        return None

def update_contractor_from_csv(contractor, row):
    """Update existing contractor with CSV row data."""
    try:
        contractor.talent_name = row.get('Talent Name', contractor.talent_name).strip()
        contractor.job_title = row.get('Job Title', contractor.job_title).strip()
        contractor.candidate_status = row.get('Candidate Status', contractor.candidate_status).strip()
        contractor.talent_start_date = parse_date(row.get('Talent Start Date', '')) or contractor.talent_start_date
        contractor.talent_end_date = parse_date(row.get('Talent End Date', '')) or contractor.talent_end_date
        contractor.mobile = row.get('Mobile', contractor.mobile).strip()
        contractor.recruiter = row.get('Recruiter', contractor.recruiter).strip()
        contractor.peoplesoft_id = row.get('Peoplesoft ID', contractor.peoplesoft_id).strip()
        contractor.account_manager = row.get('Account Manager', contractor.account_manager).strip()
        contractor.account_name = row.get('Account Name', contractor.account_name).strip()
        contractor.opt_out_mobile = row.get('PrefCentre_Aerotek_OptOut_Mobile', contractor.opt_out_mobile).strip()
        contractor.updated_at = datetime.utcnow()
        
        # Update spread amount if provided
        spread_amount = parse_decimal(row.get('Spread Amount', '') or row.get('Weekly Spread', '') or row.get('Spread', ''))
        if spread_amount is not None:
            contractor.spread_amount = spread_amount
        
        days_since = row.get('Days Since Service', '').strip()
        if days_since.isdigit():
            contractor.days_since_service = int(days_since)
            
    except Exception as e:
        current_app.logger.error(f"Error updating contractor from CSV row: {e}")
