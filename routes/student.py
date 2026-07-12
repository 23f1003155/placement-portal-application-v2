from flask import Blueprint, request, jsonify, session, send_file
from werkzeug.utils import secure_filename
from models import db, User, PlacementDrive, Application, CompanyProfile
from extensions import cache
from celery.result import AsyncResult
from celery_worker import celery
from datetime import date
import os

student = Blueprint('student', __name__)

UPLOAD_FOLDER = 'resumes'    
ALLOWED_EXTENSIONS = {'pdf'}

def student_required():
    if 'user_id' not in session:
        return jsonify({"message": "Login required"}), 401
    if session.get('role') != 'student':
        return jsonify({"message": "Student access only"}), 403
    return None


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@student.route('/profile')
def profile():
    err = student_required()
    if err:
        return err

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id":     user.id,
        "name":   user.name,
        "email":  user.email,
        "cgpa":   user.cgpa,
        "branch": user.branch,
        "year":   user.year,
        "resume": user.resume
    }), 200


@student.route('/update_profile', methods=['POST'])
def update_profile():
    err = student_required()
    if err:
        return err

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.json or {}

    if data.get('cgpa') is not None:
        try:
            cgpa = float(data['cgpa'])
            if not (0 <= cgpa <= 10):
                return jsonify({"message": "CGPA must be between 0 and 10"}), 400
            user.cgpa = cgpa
        except (ValueError, TypeError):
            return jsonify({"message": "Invalid CGPA"}), 400

    if data.get('branch') is not None:
        user.branch = data['branch']

    if data.get('year') is not None:
        user.year = int(data['year'])

    db.session.commit()
    return jsonify({"message": "Profile updated"}), 200


@student.route('/upload_resume', methods=['POST'])
def upload_resume():
    err = student_required()
    if err:
        return err

    if 'resume' not in request.files:
        return jsonify({"message": "No file provided"}), 400

    file = request.files['resume']

    if file.filename == '':
        return jsonify({"message": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"message": "Only PDF files allowed"}), 400

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    filename = f"{session['user_id']}_resume.pdf"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    user = User.query.get(session['user_id'])
    user.resume = filename
    db.session.commit()

    return jsonify({"message": "Resume uploaded", "filename": filename}), 200


@student.route('/drives')
def view_drives():
    err = student_required()
    if err:
        return err

    user_id = session['user_id']

    cache_key = f"drives_{user_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return jsonify(cached), 200

    drives = PlacementDrive.query.filter_by(status='Approved').all()
    result = []
    for d in drives:
        company = CompanyProfile.query.get(d.company_id)
        result.append({
            "id":          d.id,
            "job_title":   d.job_title,
            "description": d.description,
            "eligibility": d.eligibility,
            "min_cgpa":    d.min_cgpa,
            "min_year":    d.min_year,
            "deadline":    str(d.deadline),
            "company":     company.company_name if company else 'N/A'
        })

    cache.set(cache_key, result, timeout=60)   
    return jsonify(result), 200


@student.route('/search_drives')
def search_drives():
    err = student_required()
    if err:
        return err

    title = request.args.get('title', '')
    drives = PlacementDrive.query.filter(
        PlacementDrive.job_title.ilike(f'%{title}%'),
        PlacementDrive.status == 'Approved'
    ).all()

    result = []
    for d in drives:
        company = CompanyProfile.query.get(d.company_id)
        result.append({
            "id":          d.id,
            "job_title":   d.job_title,
            "description": d.description,
            "eligibility": d.eligibility,
            "min_cgpa":    d.min_cgpa,
            "min_year":    d.min_year,
            "deadline":    str(d.deadline),
            "company":     company.company_name if company else 'N/A'
        })

    return jsonify(result), 200


@student.route('/search_companies')
def search_companies():
    err = student_required()
    if err:
        return err

    name = request.args.get('name', '')
    companies = CompanyProfile.query.filter(
        CompanyProfile.company_name.ilike(f'%{name}%'),
        CompanyProfile.approval_status == 'Approved'
    ).all()

    return jsonify([
        {"id": c.id, "company_name": c.company_name, "website": c.website}
        for c in companies
    ]), 200



@student.route('/apply', methods=['POST'])
def apply():
    err = student_required()
    if err:
        return err

    data       = request.json or {}
    drive_id   = data.get('drive_id')
    student_id = session['user_id']

    if not drive_id:
        return jsonify({"message": "drive_id is required"}), 400

    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        return jsonify({"message": "Drive not found"}), 404

    if drive.status != 'Approved':
        return jsonify({"message": "Drive is not open for applications"}), 400

    
    if drive.deadline < date.today():
        return jsonify({"message": "Application deadline has passed"}), 400

    user = User.query.get(student_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    
    if drive.min_cgpa is not None:
        if user.cgpa is None or user.cgpa < drive.min_cgpa:
            return jsonify({"message": f"Minimum CGPA required: {drive.min_cgpa}"}), 403

    
    if drive.eligibility:
        allowed_branches = [b.strip().lower() for b in drive.eligibility.split(',')]
        if user.branch is None or user.branch.lower() not in allowed_branches:
            return jsonify({"message": f"Your branch is not eligible. Allowed: {drive.eligibility}"}), 403

    
    if drive.min_year is not None:
        if user.year is None or user.year < drive.min_year:
            return jsonify({"message": f"Minimum year required: {drive.min_year}"}), 403

    
    existing = Application.query.filter_by(
        student_id=student_id,
        drive_id=drive_id
    ).first()
    if existing:
        return jsonify({"message": "You have already applied for this drive"}), 400

    
    application = Application(student_id=student_id, drive_id=drive_id)
    db.session.add(application)
    db.session.commit()

    return jsonify({"message": "Applied successfully"}), 201


@student.route('/my_applications')
def my_applications():
    err = student_required()
    if err:
        return err

    apps = Application.query.filter_by(student_id=session['user_id']).all()
    result = []
    for a in apps:
        drive   = PlacementDrive.query.get(a.drive_id)
        company = CompanyProfile.query.get(drive.company_id) if drive else None
        result.append({
            "application_id":   a.id,
            "drive_id":         a.drive_id,
            "job_title":        drive.job_title if drive else 'N/A',
            "company":          company.company_name if company else 'N/A',
            "status":           a.status,
            "application_date": str(a.application_date),
            "interview_date":   str(a.interview_date) if a.interview_date else None
        })
    return jsonify(result), 200


@student.route('/placement_history')
def placement_history():
    err = student_required()
    if err:
        return err

    apps = Application.query.filter(
        Application.student_id == session['user_id'],
        Application.status.in_(['Selected', 'Rejected'])
    ).all()

    result = []
    for a in apps:
        drive   = PlacementDrive.query.get(a.drive_id)
        company = CompanyProfile.query.get(drive.company_id) if drive else None
        result.append({
            "job_title":  drive.job_title if drive else 'N/A',
            "company":    company.company_name if company else 'N/A',
            "status":     a.status,
            "applied_on": str(a.application_date)
        })
    return jsonify(result), 200


@student.route('/export')
def export_csv():
    err = student_required()
    if err:
        return err

    from tasks import export_applications
    task = export_applications.delay(session['user_id'])

    return jsonify({
        "message": "Export started. Use task_id to check status.",
        "task_id": task.id
    }), 202


@student.route('/export_status/<task_id>')
def export_status(task_id):
    err = student_required()
    if err:
        return err

    task = AsyncResult(task_id, app=celery)

    return jsonify({
        "status": task.status,   
        "result": task.result if task.successful() else None
    }), 200



@student.route('/download_csv/<path:filename>')
def download_csv(filename):
    err = student_required()
    if err:
        return err

    
    safe_name = secure_filename(os.path.basename(filename))
    filepath  = os.path.join('exports', safe_name)

    if not os.path.exists(filepath):
        return jsonify({"message": "File not found"}), 404

    
    if str(session['user_id']) not in safe_name:
        return jsonify({"message": "Unauthorized"}), 403

    return send_file(filepath, as_attachment=True), 200
