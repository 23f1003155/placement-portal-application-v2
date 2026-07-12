from flask import Blueprint, request, jsonify, session
from models import db, CompanyProfile, PlacementDrive, Application, User
from datetime import date

company = Blueprint('company', __name__)


def company_required():
    if 'user_id' not in session:
        return jsonify({"message": "Login required"}), 401
    if session.get('role') != 'company':
        return jsonify({"message": "Company access only"}), 403
    return None


def get_my_company():
    user_id = session.get('user_id')
    return CompanyProfile.query.filter_by(user_id=user_id).first()


@company.route('/create_profile', methods=['POST'])
def create_profile():
    err = company_required()
    if err:
        return err

    user_id = session.get('user_id')

    if CompanyProfile.query.filter_by(user_id=user_id).first():
        return jsonify({"message": "Profile already exists"}), 409

    data = request.json or {}
    if not data.get('company_name') or not data.get('hr_contact'):
        return jsonify({"message": "company_name and hr_contact are required"}), 400

    profile = CompanyProfile(
        user_id      = user_id,
        company_name = data['company_name'],
        hr_contact   = data['hr_contact'],
        website      = data.get('website', '')
    )
    db.session.add(profile)
    db.session.commit()

    return jsonify({"message": "Profile created. Waiting for admin approval"}), 201


@company.route('/profile')
def view_profile():
    err = company_required()
    if err:
        return err

    cp = get_my_company()
    if not cp:
        return jsonify({"message": "Profile not found. Please create one."}), 404

    return jsonify({
        "id":             cp.id,
        "company_name":   cp.company_name,
        "hr_contact":     cp.hr_contact,
        "website":        cp.website,
        "status":         cp.approval_status,
        "is_blacklisted": cp.is_blacklisted
    }), 200


@company.route('/create_drive', methods=['POST'])
def create_drive():
    err = company_required()
    if err:
        return err

    cp = get_my_company()
    if not cp:
        return jsonify({"message": "Create a company profile first"}), 404

    if cp.approval_status != 'Approved':
        return jsonify({"message": "Your company is not approved yet"}), 403

    if cp.is_blacklisted:
        return jsonify({"message": "Your company is blacklisted"}), 403

    data = request.json or {}

    if not data.get('job_title') or not data.get('deadline'):
        return jsonify({"message": "job_title and deadline are required"}), 400

    try:
        deadline = date.fromisoformat(data['deadline'])  
    except ValueError:
        return jsonify({"message": "deadline must be in YYYY-MM-DD format"}), 400

    if deadline < date.today():
        return jsonify({"message": "Deadline must be a future date"}), 400

    drive = PlacementDrive(
        company_id  = cp.id,
        job_title   = data['job_title'],
        description = data.get('description', ''),
        eligibility = data.get('eligibility', ''),   
        min_cgpa    = data.get('min_cgpa'),
        min_year    = data.get('min_year'),
        deadline    = deadline
    )
    db.session.add(drive)
    db.session.commit()

    return jsonify({"message": "Drive created. Waiting for admin approval"}), 201


@company.route('/my_drives')
def my_drives():
    err = company_required()
    if err:
        return err

    cp = get_my_company()
    if not cp:
        return jsonify({"message": "Profile not found"}), 404

    drives = PlacementDrive.query.filter_by(company_id=cp.id).all()
    result = []
    for d in drives:
        applicant_count = Application.query.filter_by(drive_id=d.id).count()
        result.append({
            "id":              d.id,
            "job_title":       d.job_title,
            "status":          d.status,
            "deadline":        str(d.deadline),
            "applicant_count": applicant_count
        })
    return jsonify(result), 200


@company.route('/close_drive/<int:drive_id>', methods=['POST'])
def close_drive(drive_id):
    err = company_required()
    if err:
        return err

    cp = get_my_company()
    if not cp:
        return jsonify({"message": "Profile not found"}), 404

    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        return jsonify({"message": "Drive not found"}), 404

    if drive.company_id != cp.id:
        return jsonify({"message": "Unauthorized"}), 403

    drive.status = 'Closed'
    db.session.commit()
    return jsonify({"message": "Drive closed"}), 200


@company.route('/applications/<int:drive_id>')
def view_applications(drive_id):
    err = company_required()
    if err:
        return err

    cp = get_my_company()
    if not cp:
        return jsonify({"message": "Profile not found"}), 404

    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        return jsonify({"message": "Drive not found"}), 404

    if drive.company_id != cp.id:
        return jsonify({"message": "Unauthorized"}), 403

    apps = Application.query.filter_by(drive_id=drive_id).all()
    result = []
    for a in apps:
        student = User.query.get(a.student_id)
        result.append({
            "application_id": a.id,
            "student_id":     a.student_id,
            "student_name":   student.name if student else 'N/A',
            "student_email":  student.email if student else 'N/A',
            "cgpa":           student.cgpa if student else None,
            "branch":         student.branch if student else None,
            "status":         a.status,
            "interview_date": str(a.interview_date) if a.interview_date else None
        })
    return jsonify(result), 200


@company.route('/update_application/<int:app_id>', methods=['POST'])
def update_application(app_id):
    err = company_required()
    if err:
        return err

    cp = get_my_company()
    if not cp:
        return jsonify({"message": "Profile not found"}), 404

    application = Application.query.get(app_id)
    if not application:
        return jsonify({"message": "Application not found"}), 404

    drive = PlacementDrive.query.get(application.drive_id)
    if not drive or drive.company_id != cp.id:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json or {}
    new_status = data.get('status', '')

    allowed = ('Applied', 'Shortlisted', 'Selected', 'Rejected')
    if new_status not in allowed:
        return jsonify({"message": f"Status must be one of {allowed}"}), 400

    application.status = new_status
    db.session.commit()
    return jsonify({"message": "Application status updated"}), 200


@company.route('/schedule_interview/<int:app_id>', methods=['POST'])
def schedule_interview(app_id):
    err = company_required()
    if err:
        return err

    cp = get_my_company()
    if not cp:
        return jsonify({"message": "Profile not found"}), 404

    application = Application.query.get(app_id)
    if not application:
        return jsonify({"message": "Application not found"}), 404

    drive = PlacementDrive.query.get(application.drive_id)
    if not drive or drive.company_id != cp.id:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json or {}
    if not data.get('interview_date'):
        return jsonify({"message": "interview_date is required (YYYY-MM-DD HH:MM)"}), 400

    from datetime import datetime
    try:
        application.interview_date = datetime.fromisoformat(data['interview_date'])
    except ValueError:
        return jsonify({"message": "interview_date must be in YYYY-MM-DD HH:MM format"}), 400

    application.status = 'Shortlisted'
    db.session.commit()

    return jsonify({"message": "Interview scheduled"}), 200
