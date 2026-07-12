from flask import Blueprint, request, jsonify, session
from models import db, User, CompanyProfile, PlacementDrive, Application
from extensions import cache

admin = Blueprint('admin', __name__)


def admin_required():
    if 'user_id' not in session:
        return jsonify({"message": "Login required"}), 401
    if session.get('role') != 'admin':
        return jsonify({"message": "Admin access only"}), 403
    return None


@admin.route('/dashboard')
def dashboard():
    err = admin_required()
    if err:
        return err

    return jsonify({
        "total_students":      User.query.filter_by(role='student').count(),
        "total_companies":     User.query.filter_by(role='company').count(),
        "total_drives":        PlacementDrive.query.count(),
        "pending_companies":   CompanyProfile.query.filter_by(approval_status='Pending').count(),
        "pending_drives":      PlacementDrive.query.filter_by(status='Pending').count(),
        "total_applications":  Application.query.count(),
        "total_selected":      Application.query.filter_by(status='Selected').count()
    }), 200


@admin.route('/companies')
def view_companies():
    err = admin_required()
    if err:
        return err

    companies = CompanyProfile.query.all()
    result = []
    for c in companies:
        result.append({
            "id":             c.id,
            "company_name":   c.company_name,
            "hr_contact":     c.hr_contact,
            "website":        c.website,
            "status":         c.approval_status,
            "is_blacklisted": c.is_blacklisted
        })
    return jsonify(result), 200


@admin.route('/approve_company/<int:id>', methods=['POST'])
def approve_company(id):
    err = admin_required()
    if err:
        return err

    company = CompanyProfile.query.get(id)
    if not company:
        return jsonify({"message": "Company not found"}), 404

    company.approval_status = 'Approved'
    db.session.commit()
    return jsonify({"message": "Company approved"}), 200


@admin.route('/reject_company/<int:id>', methods=['POST'])
def reject_company(id):
    err = admin_required()
    if err:
        return err

    company = CompanyProfile.query.get(id)
    if not company:
        return jsonify({"message": "Company not found"}), 404

    company.approval_status = 'Rejected'
    db.session.commit()
    return jsonify({"message": "Company rejected"}), 200


@admin.route('/blacklist_company/<int:id>', methods=['POST'])
def blacklist_company(id):
    err = admin_required()
    if err:
        return err

    company = CompanyProfile.query.get(id)
    if not company:
        return jsonify({"message": "Company not found"}), 404

    company.is_blacklisted  = True
    company.approval_status = 'Rejected'
    db.session.commit()
    return jsonify({"message": "Company blacklisted"}), 200


@admin.route('/drives')
def view_drives():
    err = admin_required()
    if err:
        return err

    drives = PlacementDrive.query.all()
    result = []
    for d in drives:
        result.append({
            "id":         d.id,
            "job_title":  d.job_title,
            "status":     d.status,
            "deadline":   str(d.deadline),
            "company_id": d.company_id
        })
    return jsonify(result), 200


@admin.route('/approve_drive/<int:id>', methods=['POST'])
def approve_drive(id):
    err = admin_required()
    if err:
        return err

    drive = PlacementDrive.query.get(id)
    if not drive:
        return jsonify({"message": "Drive not found"}), 404

    drive.status = 'Approved'
    db.session.commit()

    cache.clear()

    return jsonify({"message": "Drive approved"}), 200


@admin.route('/reject_drive/<int:id>', methods=['POST'])
def reject_drive(id):
    err = admin_required()
    if err:
        return err

    drive = PlacementDrive.query.get(id)
    if not drive:
        return jsonify({"message": "Drive not found"}), 404

    drive.status = 'Rejected'
    db.session.commit()
    return jsonify({"message": "Drive rejected"}), 200


@admin.route('/students')
def view_students():
    err = admin_required()
    if err:
        return err

    students = User.query.filter_by(role='student').all()
    result = []
    for s in students:
        result.append({
            "id":        s.id,
            "name":      s.name,
            "email":     s.email,
            "cgpa":      s.cgpa,
            "branch":    s.branch,
            "year":      s.year,
            "is_active": s.is_active
        })
    return jsonify(result), 200


@admin.route('/deactivate_user/<int:id>', methods=['POST'])
def deactivate_user(id):
    err = admin_required()
    if err:
        return err

    user = User.query.get(id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    user.is_active = False
    db.session.commit()
    return jsonify({"message": f"{user.role.capitalize()} deactivated"}), 200


@admin.route('/activate_user/<int:id>', methods=['POST'])
def activate_user(id):
    err = admin_required()
    if err:
        return err

    user = User.query.get(id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    user.is_active = True
    db.session.commit()
    return jsonify({"message": f"{user.role.capitalize()} activated"}), 200


@admin.route('/search_companies')
def search_companies():
    err = admin_required()
    if err:
        return err

    name = request.args.get('name', '')
    companies = CompanyProfile.query.filter(
        CompanyProfile.company_name.ilike(f'%{name}%')
    ).all()

    result = []
    for c in companies:
        result.append({
            "id":             c.id,
            "company_name":   c.company_name,
            "hr_contact":     c.hr_contact,
            "website":        c.website,
            "status":         c.approval_status,
            "is_blacklisted": c.is_blacklisted
        })
    return jsonify(result), 200


@admin.route('/search_students')
def search_students():
    err = admin_required()
    if err:
        return err

    name = request.args.get('name', '')
    students = User.query.filter(
        User.role == 'student',
        User.name.ilike(f'%{name}%')
    ).all()

    result = []
    for s in students:
        result.append({
            "id":        s.id,
            "name":      s.name,
            "email":     s.email,
            "cgpa":      s.cgpa,
            "branch":    s.branch,
            "year":      s.year,
            "is_active": s.is_active
        })
    return jsonify(result), 200


@admin.route('/search_drives')
def search_drives():
    err = admin_required()
    if err:
        return err

    title = request.args.get('title', '')
    drives = PlacementDrive.query.filter(
        PlacementDrive.job_title.ilike(f'%{title}%')
    ).all()

    result = []
    for d in drives:
        result.append({
            "id":         d.id,
            "job_title":  d.job_title,
            "status":     d.status,
            "deadline":   str(d.deadline),
            "company_id": d.company_id
        })
    return jsonify(result), 200


@admin.route('/applications')
def view_applications():
    err = admin_required()
    if err:
        return err

    apps = Application.query.all()
    result = []
    for a in apps:
        student = User.query.get(a.student_id)
        drive = PlacementDrive.query.get(a.drive_id)
        result.append({
            "id":               a.id,
            "student_id":       a.student_id,
            "student_name":     student.name if student else 'N/A',
            "drive_id":         a.drive_id,
            "job_title":        drive.job_title if drive else 'N/A',
            "status":           a.status,
            "application_date": str(a.application_date)
        })
    return jsonify(result), 200


@admin.route('/statistics')
def statistics():
    err = admin_required()
    if err:
        return err

    return jsonify({
        "total_drives":        PlacementDrive.query.count(),
        "approved_drives":     PlacementDrive.query.filter_by(status='Approved').count(),
        "closed_drives":       PlacementDrive.query.filter_by(status='Closed').count(),
        "total_applications":  Application.query.count(),
        "applied":             Application.query.filter_by(status='Applied').count(),
        "shortlisted":         Application.query.filter_by(status='Shortlisted').count(),
        "selected":            Application.query.filter_by(status='Selected').count(),
        "rejected":            Application.query.filter_by(status='Rejected').count()
    }), 200
