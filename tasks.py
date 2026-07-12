from celery_worker import celery
from datetime import date, datetime
import csv
import os

@celery.task
def export_applications(student_id):

    from app import app
    from models import Application, PlacementDrive, CompanyProfile

    with app.app_context():
        apps = Application.query.filter_by(student_id=student_id).all()

        rows = []
        for a in apps:
            drive   = PlacementDrive.query.get(a.drive_id)
            company = CompanyProfile.query.get(drive.company_id) if drive else None

            rows.append({
                'Application ID':   a.id,
                'Student ID':       a.student_id,
                'Company Name':     company.company_name if company else 'N/A',
                'Drive Title':      drive.job_title if drive else 'N/A',
                'Application Date': a.application_date.strftime('%Y-%m-%d') if a.application_date else '',
                'Status':           a.status
            })


        os.makedirs('exports', exist_ok=True)
        filename = f"exports/applications_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else [
                'Application ID', 'Student ID', 'Company Name',
                'Drive Title', 'Application Date', 'Status'
            ])
            writer.writeheader()
            writer.writerows(rows)

        return filename


@celery.task
def send_daily_reminders():

    from app import app
    from models import PlacementDrive, User, Application

    with app.app_context():
        today = date.today()

        
        drives = PlacementDrive.query.filter_by(status='Approved').all()
        upcoming = [d for d in drives if d.deadline and (d.deadline - today).days == 3]

        if not upcoming:
            print(f"[{datetime.now()}] No upcoming deadlines in 3 days.")
            return

        students = User.query.filter_by(role='student', is_active=True).all()

        for drive in upcoming:
            for student in students:
                already_applied = Application.query.filter_by(
                    student_id=student.id,
                    drive_id=drive.id
                ).first()

                if not already_applied:
                    message = (
                        f"Reminder: The placement drive '{drive.job_title}' "
                        f"deadline is on {drive.deadline}. Apply before it closes!"
                    )

                    mail = app.extensions.get('mail')
                    if mail:
                        try:
                            from flask_mail import Message
                            msg = Message(
                                subject='Placement Drive Deadline Reminder',
                                recipients=[student.email],
                                body=message
                            )
                            mail.send(msg)
                            print(f"Reminder emailed to {student.email}")
                        except Exception as e:
                            print(f"Mail error: {e}")
                    else:
                        print(f"[REMINDER] {student.email}: {message}")



@celery.task
def send_monthly_report():
    
    from app import app
    from models import PlacementDrive, Application, User

    with app.app_context():
        now   = datetime.now()
        month = now.strftime('%B %Y')

        
        total_drives   = PlacementDrive.query.count()
        approved       = PlacementDrive.query.filter_by(status='Approved').count()
        total_students = User.query.filter_by(role='student').count()
        total_apps     = Application.query.count()
        selected       = Application.query.filter_by(status='Selected').count()

        
        html_report = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Monthly Placement Activity Report — {month}</h2>
            <hr/>
            <table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;">
                <tr style="background:#f0f0f0;">
                    <th>Metric</th>
                    <th>Count</th>
                </tr>
                <tr><td>Total Placement Drives</td><td>{total_drives}</td></tr>
                <tr><td>Approved Drives</td><td>{approved}</td></tr>
                <tr><td>Total Registered Students</td><td>{total_students}</td></tr>
                <tr><td>Total Applications</td><td>{total_apps}</td></tr>
                <tr><td>Students Selected</td><td>{selected}</td></tr>
            </table>
            <br/>
            <p style="color:gray;">Generated on: {now.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """

        
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("No admin found for monthly report.")
            return

        
        mail = app.extensions.get('mail')
        if mail:
            try:
                from flask_mail import Message
                msg = Message(
                    subject=f'Monthly Placement Report — {month}',
                    recipients=[admin.email],
                    html=html_report
                )
                mail.send(msg)
                print(f"Monthly report sent to {admin.email}")
            except Exception as e:
                print(f"Mail error: {e}")
        else:
            
            os.makedirs('reports', exist_ok=True)
            fname = f"reports/report_{now.strftime('%Y_%m')}.html"
            with open(fname, 'w') as f:
                f.write(html_report)
            print(f"Monthly report saved to {fname}")
