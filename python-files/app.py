import os
import io
import re
import qrcode
import logging
import zipfile
import shutil
import subprocess  # Add at top with other imports
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import desc

app = Flask(__name__)
# Add pagination helpers to Jinja2's global context
app.jinja_env.globals.update(max=max, min=min)
app.jinja_env.filters['format_number'] = lambda n: '{:,}'.format(n)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads/profile_pics'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class Pagination:
    def __init__(self, items, page, per_page, total):
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = max(1, (total + per_page - 1) // per_page)
        self.showing_from = (page - 1) * per_page + 1
        self.showing_to = min(page * per_page, total)
        
    @property
    def has_prev(self):
        return self.page > 1
        
    @property
    def has_next(self):
        return self.page < self.pages
        
    def iter_pages(self, left_edge=2, right_edge=2, left_current=2, right_current=3):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num

def get_paginated_records(query, page, per_page=5):
    if page < 1:
        page = 1
    
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return Pagination(items, page, per_page, total)

# Create upload folder if it doesn't exist
os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), exist_ok=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_secure_password_hash(password):
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

def verify_password(hash_value, password):
    try:
        return check_password_hash(hash_value, password)
    except Exception:
        return False

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100))
    profile_image = db.Column(db.String(200), default='default.jpg')
    assigned_computer = db.relationship('Computer', backref='assigned_user', lazy=True)

    @property
    def image_url(self):
        return url_for('static', filename=f'uploads/profile_pics/{self.profile_image}')

class Computer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    computer_id = db.Column(db.String(20), unique=True, nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    model = db.Column(db.String(100), nullable=False)
    computer_type = db.Column(db.String(50))
    purchase_date = db.Column(db.DateTime, nullable=False)
    purchase_price = db.Column(db.Float)
    warranty = db.Column(db.Integer)
    status = db.Column(db.String(50), nullable=False, default='Available')
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assignment_notes = db.Column(db.Text)
    assignment_date = db.Column(db.DateTime)
    maintenance_records = db.relationship('Maintenance', backref='computer', lazy=True)

    @classmethod
    def generate_next_id(cls):
        last_computer = cls.query.filter(
            cls.computer_id.like('HfCCF-%')
        ).order_by(cls.computer_id.desc()).first()
        
        if last_computer:
            try:
                last_num = int(last_computer.computer_id.split('-')[1])
                next_num = last_num + 1
            except (IndexError, ValueError):
                next_num = 1
        else:
            next_num = 1
            
        return f'HfCCF-{next_num:04d}'

    @classmethod
    def get_last_id(cls):
        last_computer = cls.query.filter(
            cls.computer_id.like('HfCCF-%')
        ).order_by(cls.computer_id.desc()).first()
        return last_computer.computer_id if last_computer else 'No computers yet'
        
    def __init__(self, **kwargs):
        if 'computer_id' not in kwargs:
            kwargs['computer_id'] = self.generate_next_id()
        super(Computer, self).__init__(**kwargs)

    @property
    def assigned_to(self):
        if self.assigned_user_id:
            user = User.query.get(self.assigned_user_id)
            return user.name if user else 'None'
        return 'None'

    def update_status(self):
        self.status = 'In Use' if self.assigned_user_id else 'Available'

class Maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    computer_id = db.Column(db.Integer, db.ForeignKey('computer.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    technician_name = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Float, nullable=False, default=0.0)
    materials_used = db.Column(db.Text)
    payment_status = db.Column(db.String(50), default='Pending')  # Pending, Paid, Cancelled

class MaintenanceSchedule(db.Model):
    __tablename__ = 'maintenance_schedule'
    id = db.Column(db.Integer, primary_key=True)
    computer_id = db.Column(db.Integer, db.ForeignKey('computer.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=True)  # Make nullable
    department = db.Column(db.String(100), nullable=True)  # Make nullable
    schedule_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    computer = db.relationship('Computer')  # Simplified relationship

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_admin_email = db.Column(db.String(200), nullable=False, default='support@hccf.com')
    contact_admin_phone = db.Column(db.String(50), nullable=False, default='+1234567890')
    company_address = db.Column(db.String(200), nullable=False, default='HCCF Main Office')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def get_settings():
        settings = Settings.query.first()
        if not settings:
            settings = Settings()
            db.session.add(settings)
            db.session.commit()
        return settings

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_settings():
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
        db.session.add(settings)
        db.session.commit()
    return settings

# Routes
@app.route('/')
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()
    
    query = Computer.query
    if search_query:
        query = query.filter(
            db.or_(
                Computer.serial_number.ilike(f'%{search_query}%'),
                Computer.model.ilike(f'%{search_query}%'),
                Computer.status.ilike(f'%{search_query}%')
            )
        )
    
    pagination = get_paginated_records(query, page)
    users = User.query.all()
    
    return render_template('home.html', 
                         computers=pagination,
                         users=users,
                         search_query=search_query,
                         page=page)

@app.route('/computers')
@login_required
def computers():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    
    query = Computer.query.order_by(Computer.id)
    pagination = get_paginated_records(query, page, per_page)
    
    return render_template('computers.html', 
                         computers=pagination,
                         today=datetime.utcnow())

@app.route('/assigned_computers')
@login_required
def assigned_computers():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()
    
    query = Computer.query.filter(Computer.assigned_user_id.isnot(None))
    if search_query:
        query = query.filter(
            db.or_(
                Computer.computer_id.ilike(f'%{search_query}%'),
                Computer.serial_number.ilike(f'%{search_query}%'),
                Computer.model.ilike(f'%{search_query}%')
            )
        )
    
    pagination = get_paginated_records(query, page)
    return render_template('assigned_computers.html', 
                         computers=pagination,
                         search_query=search_query)

@app.route('/available_computers')
@login_required
def available_computers():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()
    
    query = Computer.query.filter(Computer.assigned_user_id.is_(None))
    if search_query:
        query = query.filter(
            db.or_(
                Computer.computer_id.ilike(f'%{search_query}%'),
                Computer.serial_number.ilike(f'%{search_query}%'),
                Computer.model.ilike(f'%{search_query}%')
            )
        )
    
    pagination = get_paginated_records(query, page)
    return render_template('available_computers.html', 
                         computers=pagination,
                         search_query=search_query)

@app.route('/maintenance_computers')
@login_required
def maintenance_computers():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()
    
    query = Computer.query.join(Maintenance).distinct()
    if search_query:
        query = query.filter(
            db.or_(
                Computer.computer_id.ilike(f'%{search_query}%'),
                Computer.serial_number.ilike(f'%{search_query}%'),
                Computer.model.ilike(f'%{search_query}%')
            )
        )
    
    pagination = get_paginated_records(query, page)
    return render_template('maintenance_computers.html', 
                         computers=pagination,
                         search_query=search_query)

@app.route('/computer/view/<int:computer_id>')
@login_required
def view_computer(computer_id):
    computer = Computer.query.get_or_404(computer_id)
    maintenance_records = Maintenance.query.filter_by(computer_id=computer_id)\
        .order_by(Maintenance.date.desc())\
        .all()
    
    return render_template('view_computer.html',
                         computer=computer,
                         maintenance_records=maintenance_records)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and verify_password(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/reset_admin', methods=['GET', 'POST'])
def reset_admin():
    if request.method == 'POST':
        admin_user = User.query.filter_by(email='admin@example.com').first()
        if not admin_user:
            # Create admin user if it doesn't exist
            admin_user = User(
                name='Admin User',
                email='admin@example.com',
                password=generate_secure_password_hash('admin'),
                department='IT'
            )
            db.session.add(admin_user)
        else:
            # Reset existing admin's password
            admin_user.password = generate_secure_password_hash('admin')
        
        db.session.commit()
        flash('Admin password has been reset to: admin')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/computer/add', methods=['GET', 'POST'])
@login_required
def add_computer():
    if request.method == 'POST':
        serial_number = request.form.get('serial_number')
        formatted_computer_id = request.form.get('formatted_computer_id')
        
        # Check if computer ID or serial number already exists
        if Computer.query.filter_by(computer_id=formatted_computer_id).first():
            flash('A computer with this ID already exists', 'error')
            return redirect(url_for('add_computer'))
            
        if Computer.query.filter_by(serial_number=serial_number).first():
            flash('A computer with this serial number already exists', 'error')
            return redirect(url_for('add_computer'))
            
        computer = Computer(
            computer_id=formatted_computer_id,
            serial_number=serial_number,
            computer_type=request.form.get('computer_type'),
            model=request.form.get('model'),
            purchase_price=float(request.form.get('purchase_price', 0)),
            purchase_date=datetime.strptime(request.form.get('purchase_date'), '%Y-%m-%d'),
            warranty=int(request.form.get('warranty', 0)),
            status='Available'
        )
        db.session.add(computer)
        try:
            db.session.commit()
            flash('Computer added successfully', 'success')
            return redirect(url_for('computers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding computer: {str(e)}', 'error')
            return redirect(url_for('add_computer'))
    return render_template('add_computer.html')

@app.route('/maintenance/add/<int:computer_id>', methods=['GET', 'POST'])
@login_required
def add_maintenance(computer_id):
    if request.method == 'POST':
        maintenance = Maintenance(
            computer_id=computer_id,
            description=request.form.get('description'),
            technician_name=request.form.get('technician_name'),
            cost=float(request.form.get('cost', 0)),
            materials_used=request.form.get('materials_used'),
            payment_status=request.form.get('payment_status', 'Pending')
        )
        db.session.add(maintenance)
        db.session.commit()
        flash('Maintenance record added successfully')
        return redirect(url_for('home'))
    computer = Computer.query.get_or_404(computer_id)
    return render_template('add_maintenance.html', computer=computer)

@app.route('/maintenance')
@login_required
def maintenance_list():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()
    
    query = Maintenance.query.order_by(desc(Maintenance.date))
    if search_query:
        query = query.filter(
            db.or_(
                Maintenance.technician_name.ilike(f'%{search_query}%'),
                Maintenance.description.ilike(f'%{search_query}%'),
                Maintenance.materials_used.ilike(f'%{search_query}%'),
                Maintenance.payment_status.ilike(f'%{search_query}%')
            )
        )
    
    pagination = get_paginated_records(query, page)
    return render_template('maintenance_list.html', 
                         maintenance_records=pagination,
                         search_query=search_query)

@app.route('/maintenance/edit/<int:maintenance_id>', methods=['GET', 'POST'])
@login_required
def edit_maintenance(maintenance_id):
    maintenance = Maintenance.query.get_or_404(maintenance_id)
    if request.method == 'POST':
        maintenance.description = request.form.get('description')
        maintenance.technician_name = request.form.get('technician_name')
        maintenance.cost = float(request.form.get('cost', 0))
        maintenance.materials_used = request.form.get('materials_used')
        maintenance.payment_status = request.form.get('payment_status')
        db.session.commit()
        flash('Maintenance record updated successfully')
        return redirect(url_for('maintenance_list'))
    return render_template('edit_maintenance.html', maintenance=maintenance)

@app.route('/maintenance/delete/<int:maintenance_id>', methods=['POST'])
@login_required
def delete_maintenance(maintenance_id):
    maintenance = Maintenance.query.get_or_404(maintenance_id)
    db.session.delete(maintenance)
    db.session.commit()
    flash('Maintenance record deleted successfully')
    return redirect(url_for('maintenance_list'))

@app.route('/maintenance/schedule') 
@login_required
def maintenance_schedule():
    computers = Computer.query.all()
    users = User.query.all()
    
    # Get active schedules grouped by department
    active_schedules = MaintenanceSchedule.query.join(Computer).filter(
        MaintenanceSchedule.status != 'Completed'
    ).order_by(
        MaintenanceSchedule.department,
        MaintenanceSchedule.schedule_date
    ).all()
    
    # Get completed schedules separately
    completed_schedules = MaintenanceSchedule.query.join(Computer).filter(
        MaintenanceSchedule.status == 'Completed'
    ).order_by(MaintenanceSchedule.schedule_date.desc()).all()
    
    # Add metadata for auto-refresh on completion
    for schedule in active_schedules:
        schedule.complete_url = url_for('complete_maintenance_schedule', schedule_id=schedule.id)
        schedule.refresh_url = url_for('maintenance_schedule')

    # Add completed items metadata
    for schedule in completed_schedules:
        schedule.original_department = schedule.department
        schedule.department = 'Completed Maintenance'
        schedule.can_edit = True
        schedule.can_undo = True
        
    # Combine schedules
    grouped_schedules = active_schedules + completed_schedules
    
    # Update overdue status
    current_date = datetime.now()
    for schedule in active_schedules:
        if schedule.status == 'Pending' and schedule.schedule_date < current_date:
            schedule.status = 'Overdue'
    db.session.commit()
    
    return render_template('maintenance_schedule.html',
                         computers=computers,
                         users=users,
                         schedules=grouped_schedules)

@app.route('/maintenance/schedule/add', methods=['POST'])
@login_required
def add_maintenance_schedule():
    computer_id = request.form.get('computer_id')
    user_id = request.form.get('user_id')
    user = User.query.get_or_404(user_id)
    
    schedule = MaintenanceSchedule(
        computer_id=computer_id,
        user_name=user.name,
        department=user.department,
        schedule_date=datetime.strptime(request.form.get('schedule_date'), '%Y-%m-%d'),
        description=request.form.get('description')
    )
    db.session.add(schedule)
    db.session.commit()
    
    flash('Maintenance schedule added successfully')
    return redirect(url_for('maintenance_schedule'))

@app.route('/maintenance/schedule/complete/<int:schedule_id>', methods=['POST'])
@login_required
def complete_maintenance_schedule(schedule_id):
    try:
        schedule = MaintenanceSchedule.query.get_or_404(schedule_id)
        
        # Store info before update
        old_department = schedule.department
        
        # Update status and move to completed group
        schedule.status = 'Completed'
        schedule.department = 'Completed Maintenance'
        db.session.commit()
        
        # Get updated counts
        old_dept_count = MaintenanceSchedule.query.filter_by(
            department=old_department
        ).filter(MaintenanceSchedule.status != 'Completed').count()
        completed_count = MaintenanceSchedule.query.filter_by(status='Completed').count()
        
        return jsonify({
            'success': True,
            'id': schedule_id,
            'old_department': old_department,
            'old_dept_count': old_dept_count,
            'completed_count': completed_count,
            'new_department': 'Completed Maintenance',
            'refresh': True,  # Signal frontend to refresh
            'refresh_url': url_for('maintenance_schedule')
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error completing schedule {schedule_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/maintenance/schedule/undo/<int:schedule_id>', methods=['POST'])
@login_required 
def undo_maintenance_schedule(schedule_id):
    try:
        schedule = MaintenanceSchedule.query.get_or_404(schedule_id)
        if schedule.status != 'Completed':
            return jsonify({'success': False, 'error': 'Schedule is not completed'}), 400
            
        # Store original info
        old_status = schedule.status
        original_department = schedule.original_department
        
        # Restore to original state
        schedule.status = 'Pending'
        schedule.department = original_department
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': schedule_id,
            'status': 'Pending',
            'old_status': old_status,
            'department': original_department
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/maintenance/schedule/edit/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
def edit_maintenance_schedule(schedule_id):
    schedule = MaintenanceSchedule.query.get_or_404(schedule_id)
    if request.method == 'POST':
        schedule.schedule_date = datetime.strptime(request.form.get('schedule_date'), '%Y-%m-%d')
        schedule.description = request.form.get('description')
        schedule.status = request.form.get('status', 'Pending')  # Update status
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({
        'schedule_date': schedule.schedule_date.strftime('%Y-%m-%d'),
        'description': schedule.description
    })

@app.route('/maintenance/schedule/delete/<int:schedule_id>', methods=['POST'])
@login_required
def delete_maintenance_schedule(schedule_id):
    try:
        schedule = MaintenanceSchedule.query.get_or_404(schedule_id)
        department = schedule.department
        
        # Delete the schedule regardless of status
        db.session.delete(schedule)
        db.session.commit()
        
        # Get remaining count for the department
        remaining_count = MaintenanceSchedule.query.filter_by(
            department=department
        ).filter(MaintenanceSchedule.status != 'Completed').count()
        
        # Get completed count if needed
        completed_count = MaintenanceSchedule.query.filter_by(
            status='Completed'
        ).count()
        
        return jsonify({
            'success': True,
            'message': 'Schedule deleted successfully',
            'id': schedule_id,
            'department': department,
            'remaining_count': remaining_count,
            'completed_count': completed_count,
            'refresh': True
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting schedule {schedule_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/users')
@login_required
def users():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()
    
    query = User.query
    if search_query:
        query = query.filter(
            db.or_(
                User.name.ilike(f'%{search_query}%'),
                User.email.ilike(f'%{search_query}%'),
                User.department.ilike(f'%{search_query}%')
            )
        )
    
    pagination = get_paginated_records(query, page)
    return render_template('users.html',
                         users=pagination,
                         search_query=search_query)

@app.route('/user/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        department = request.form.get('department')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('add_user'))

        profile_image = request.files.get('profile_image')
        image_filename = 'default.jpg'
        
        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            image_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            profile_image.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], image_filename))

        hashed_password = generate_secure_password_hash(password)
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            department=department,
            profile_image=image_filename
        )
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully')
        return redirect(url_for('users'))
    return render_template('add_user.html')

@app.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        email = request.form.get('email')
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user and existing_user.id != user_id:
            flash('Email already registered')
            return redirect(url_for('edit_user', user_id=user_id))

        profile_image = request.files.get('profile_image')
        if profile_image and allowed_file(profile_image.filename):
            # Delete old image if it exists and is not the default
            if user.profile_image and user.profile_image != 'default.jpg':
                old_image_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], user.profile_image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            # Save new image
            filename = secure_filename(profile_image.filename)
            image_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            profile_image.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], image_filename))
            user.profile_image = image_filename

        user.name = request.form.get('name')
        user.email = email
        user.department = request.form.get('department')
        
        if request.form.get('password'):
            user.password = generate_secure_password_hash(request.form.get('password'))
        
        db.session.commit()
        flash('User updated successfully')
        return redirect(url_for('users'))
    return render_template('edit_user.html', user=user)

@app.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.assigned_computer:
        flash('Cannot delete user with assigned computer')
        return redirect(url_for('users'))
        
    try:
        # Delete profile image if it exists and is not the default
        if user.profile_image and user.profile_image != 'default.jpg':
            image_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], user.profile_image)
            if os.path.exists(image_path):
                os.remove(image_path)
                
        db.session.delete(user)
        db.session.commit()
        flash('User and profile image deleted successfully')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}')
        
    return redirect(url_for('users'))

@app.route('/computer/assign/<int:computer_id>', methods=['POST'])
@login_required
def assign_computer(computer_id):
    computer = Computer.query.get_or_404(computer_id)
    user_id = request.form.get('user_id')
    user = User.query.get_or_404(user_id)
    
    computer.assigned_user_id = user.id
    computer.update_status()
    db.session.commit()
    flash(f'Computer assigned to {user.name}')
    return redirect(url_for('home'))

@app.route('/computer/unassign/<int:computer_id>', methods=['POST'])
@login_required
def unassign_computer(computer_id):
    computer = Computer.query.get_or_404(computer_id)
    computer.assigned_user_id = None
    computer.update_status()
    db.session.commit()
    flash('Computer unassigned successfully')
    return redirect(url_for('home'))

@app.route('/computer/edit/<int:computer_id>', methods=['GET', 'POST'])
@login_required
def edit_computer(computer_id):
    computer = Computer.query.get_or_404(computer_id)
    if request.method == 'POST':
        # Check if serial number already exists for another computer
        existing = Computer.query.filter_by(serial_number=request.form.get('serial_number')).first()
        if existing and existing.id != computer_id:
            flash('Serial number already exists')
            return redirect(url_for('edit_computer', computer_id=computer_id))
            
        computer.serial_number = request.form.get('serial_number')
        computer.model = request.form.get('model')
        computer.purchase_date = datetime.strptime(request.form.get('purchase_date'), '%Y-%m-%d')
        db.session.commit()
        flash('Computer updated successfully')
        return redirect(url_for('home'))
    return render_template('edit_computer.html', computer=computer)

@app.route('/computer/delete/<int:computer_id>', methods=['POST'])
@login_required
def delete_computer(computer_id):
    computer = Computer.query.get_or_404(computer_id)
    
    # Cannot delete if computer is assigned
    if computer.assigned_user_id:
        flash('Cannot delete computer while it is assigned to a user')
        return redirect(url_for('home'))
        
    # Delete associated maintenance records first
    Maintenance.query.filter_by(computer_id=computer_id).delete()
    
    db.session.delete(computer)
    db.session.commit()
    flash('Computer deleted successfully')
    return redirect(url_for('home'))

@app.route('/print_preview')
@login_required
def print_preview():
    search_query = request.args.get('search', '').strip()
    date_range = request.args.get('date_range', '')
    
    query = Computer.query
    if search_query:
        query = query.filter(
            db.or_(
                Computer.serial_number.ilike(f'%{search_query}%'),
                Computer.model.ilike(f'%{search_query}%'),
                Computer.status.ilike(f'%{search_query}%')
            )
        )
    
    # Apply date range filter if specified
    if date_range:
        today = datetime.now()
        if date_range == 'day':
            query = query.filter(db.func.date(Computer.purchase_date) == today.date())
        elif date_range == 'week':
            week_ago = today - timedelta(days=7)
            query = query.filter(Computer.purchase_date >= week_ago)
        elif date_range == 'month':
            month_ago = today - timedelta(days=30)
            query = query.filter(Computer.purchase_date >= month_ago)
        elif date_range == 'year':
            year_ago = today - timedelta(days=365)
            query = query.filter(Computer.purchase_date >= year_ago)
    
    computers = query.all()
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('print_preview.html',
                         computers=computers,
                         current_date=current_date,
                         search_query=search_query,
                         date_range=date_range)

def get_inventory_stats():
    total = Computer.query.count()
    available = Computer.query.filter_by(status='Available').count()
    in_use = total - available
    
    # Get department distribution
    dept_counts = db.session.query(
        User.department,
        db.func.count(Computer.id)
    ).join(Computer, User.id == Computer.assigned_user_id
    ).group_by(User.department).all()
    
    # Handle unassigned computers
    unassigned_count = Computer.query.filter_by(assigned_user_id=None).count()
    if unassigned_count:
        dept_counts.append(('Unassigned', unassigned_count))
    
    return {
        'total': total,
        'available': available,
        'in_use': in_use,
        'by_department': dept_counts
    }

@app.route('/print_summary')
@login_required
def print_summary():
    report_type = request.args.get('type', 'Computers')
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if report_type == 'Users':
        stats = get_users_stats()
    elif report_type == 'Maintenance':
        stats = get_maintenance_stats()
    else:  # Computers is default
        stats = get_inventory_stats()
        report_type = 'Computers'
    
    return render_template('print_summary.html',
                         stats=stats,
                         current_date=current_date,
                         report_type=report_type)

def get_users_stats():
    total = User.query.count()
    with_computers = User.query.filter(User.assigned_computer.any()).count()
    
    # Get department distribution
    dept_counts = db.session.query(
        User.department,
        db.func.count(User.id)
    ).group_by(User.department).all()
    
    return {
        'total': total,
        'with_computers': with_computers,
        'without_computers': total - with_computers,
        'by_department': dept_counts
    }

def get_maintenance_stats():
    records = Maintenance.query.all()
    total = len(records)
    total_cost = sum(record.cost for record in records)
    avg_cost = total_cost / total if total > 0 else 0
    
    # Get status distribution
    status_counts = db.session.query(
        Maintenance.payment_status,
        db.func.count(Maintenance.id)
    ).group_by(Maintenance.payment_status).all()
    
    # Get top technicians
    tech_counts = db.session.query(
        Maintenance.technician_name,
        db.func.count(Maintenance.id).label('count')
    ).group_by(Maintenance.technician_name
    ).order_by(db.func.count(Maintenance.id).desc()
    ).limit(5).all()
    
    top_technicians = [{'name': tech[0], 'count': tech[1]} for tech in tech_counts]
    
    return {
        'total': total,
        'total_cost': total_cost,
        'avg_cost': avg_cost,
        'by_status': status_counts,
        'top_technicians': top_technicians
    }

@app.route('/users/print')
@login_required
def print_users():
    search_query = request.args.get('search', '').strip()
    summary = request.args.get('summary', '0') == '1'
    
    query = User.query
    if search_query:
        query = query.filter(
            db.or_(
                User.name.ilike(f'%{search_query}%'),
                User.email.ilike(f'%{search_query}%'),
                User.department.ilike(f'%{search_query}%')
            )
        )
    
    users = query.all()
    stats = get_users_stats()
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if summary:
        return render_template('print_summary.html',
                             stats=stats,
                             current_date=current_date,
                             search_query=search_query,
                             report_type=request.args.get('type', 'Users'))
    return render_template('print_users.html',
                         users=users,
                         stats=stats,
                         current_date=current_date,
                         search_query=search_query)

@app.route('/maintenance/print')
@login_required
def print_maintenance():
    search_query = request.args.get('search', '').strip()
    summary = request.args.get('summary', '0') == '1'
    
    query = Maintenance.query.order_by(desc(Maintenance.date))
    if search_query:
        query = query.filter(
            db.or_(
                Maintenance.technician_name.ilike(f'%{search_query}%'),
                Maintenance.description.ilike(f'%{search_query}%'),
                Maintenance.materials_used.ilike(f'%{search_query}%'),
                Maintenance.payment_status.ilike(f'%{search_query}%')
            )
        )
    maintenance_records = query.all()
    stats = get_maintenance_stats()
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if summary:
        return render_template('print_summary.html',
                             stats=stats,
                             current_date=current_date,
                             search_query=search_query,
                             report_type=request.args.get('type', 'Maintenance'))
    return render_template('print_maintenance.html',
                         maintenance_records=maintenance_records,
                         stats=stats,
                         current_date=current_date,
                         search_query=search_query)

@app.route('/generate_qr', methods=['POST'])
@login_required
def generate_qr():
    try:
        qr_type = request.form.get('qr_type')
        if not qr_type:
            app.logger.error('QR code type not provided')
            return jsonify({'error': 'Missing QR code type'}), 400

        # Get required parameters based on QR type
        required_params = {
            'computer': ['computer_id'],
            'user': ['user_id'],
            'maintenance': ['maintenance_id']
        }
        
        if qr_type in required_params:
            missing_params = [param for param in required_params[qr_type] 
                            if not request.form.get(param)]
            if missing_params:
                error_msg = f"Missing required parameters: {', '.join(missing_params)}"
                app.logger.error(error_msg)
                return jsonify({'error': error_msg}), 400
        else:
            app.logger.error(f'Invalid QR type: {qr_type}')
            return jsonify({'error': 'Invalid QR code type'}), 400

        # Import qrcode here to ensure it's available
        import qrcode
        import io
        
        settings = get_settings()
        show_save_dialog = request.form.get('showSaveDialog', 'true') == 'true'
        
        app.logger.info(f"Generating QR code with type: {qr_type}, showSaveDialog: {show_save_dialog}")
        
        # Initialize QR data dictionary with contact info
        data = {
            'Type': qr_type.title(),
            'Contact Email': request.form.get('contact_admin_email', settings.contact_admin_email),
            'Contact Phone': request.form.get('contact_admin_phone', settings.contact_admin_phone),
            'Location': request.form.get('company_address', settings.company_address)
        }

        # Add specific data based on QR type
        if qr_type == 'computer':
            try:
                computer_id = request.form.get('computer_id')
                computer = Computer.query.get_or_404(computer_id)
                
                # Get user name if computer is assigned
                user_name = computer.assigned_user.name if computer.assigned_user else 'Unassigned'
                # Make the name safe for filenames
                safe_name = ''.join(c for c in user_name if c.isalnum() or c in ' -_').strip().replace(' ', '_')
                safe_serial = ''.join(c for c in computer.serial_number if c.isalnum() or c in '-_')
                
                data.update({
                    'Serial Number': computer.serial_number,
                    'Model': computer.model,
                    'Purchase Date': computer.purchase_date.strftime('%Y-%m-%d'),
                    'Status': computer.status,
                    'Assigned To': user_name
                })
                filename = f'QR_Code_{safe_name}_{safe_serial}.png'
                
            except Exception as e:
                error_msg = f"Error processing computer data: {str(e)}"
                app.logger.error(error_msg)
                return jsonify({'error': error_msg}), 400
                
        elif qr_type == 'user':
            try:
                user_id = request.form.get('user_id')
                user = User.query.get_or_404(user_id)
                assigned_computers = [f"{c.model} ({c.serial_number})" for c in user.assigned_computer]
                
                data.update({
                    'Name': user.name,
                    'Email': user.email,
                    'Department': user.department,
                    'Assigned Computers': ', '.join(assigned_computers) if assigned_computers else 'None'
                })
                safe_email = ''.join(c for c in user.email if c.isalnum() or c in '._-').strip()
                filename = f'QR_Code_{safe_email}.png'
                
            except Exception as e:
                error_msg = f"Error processing user data: {str(e)}"
                app.logger.error(error_msg)
                return jsonify({'error': error_msg}), 400
                
        elif qr_type == 'maintenance':
            try:
                maintenance_id = request.form.get('maintenance_id')
                maintenance = Maintenance.query.get_or_404(maintenance_id)
                
                data.update({
                    'Computer': f"{maintenance.computer.model} ({maintenance.computer.serial_number})",
                    'Date': maintenance.date.strftime('%Y-%m-%d'),
                    'Technician': maintenance.technician_name,
                    'Description': maintenance.description,
                    'Cost': f"${maintenance.cost:.2f}",
                    'Payment Status': maintenance.payment_status
                })
                filename = f'QR_Code_Maintenance_{maintenance_id}.png'
                
            except Exception as e:
                error_msg = f"Error processing maintenance data: {str(e)}"
                app.logger.error(error_msg)
                return jsonify({'error': error_msg}), 400
        
        try:
            # Create QR code instance with higher error correction
            qr = qrcode.QRCode(
                version=None,  # Auto-determine version
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            
            # Add data and format it nicely
            qr_data = '\n'.join([f'{k}: {v}' for k, v in data.items() if v])
            qr.add_data(qr_data)
            qr.make(fit=True)

            # Create an image from the QR Code
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save it to a bytes buffer
            img_buffer = io.BytesIO()
            img.save(img_buffer, 'PNG')
            img_buffer.seek(0)

            return send_file(
                img_buffer,
                mimetype='image/png',
                as_attachment=show_save_dialog,  # This controls whether to show save dialog or display inline
                download_name=filename
            )
            
        except Exception as e:
            error_msg = f"Error generating QR code image: {str(e)}"
            app.logger.error(error_msg)
            return jsonify({'error': error_msg}), 500
            
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        app.logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/generate_qr_form')
@login_required
def generate_qr_form():
    computers = Computer.query.all()
    # Serialize computers to dict before sending to template
    computers_data = [{
        'id': c.id,
        'serial_number': c.serial_number,
        'model': c.model,
        'purchase_date': c.purchase_date.strftime('%Y-%m-%d') if c.purchase_date else None
    } for c in computers]
    
    users = User.query.all()
    # You can customize these values based on your application's needs
    admin_email = 'support@hccf.com'
    company_address = 'HCCF Main Office'
    return render_template('generate_qr.html', 
                         computers=computers_data, 
                         users=users,
                         admin_email=admin_email,
                         company_address=company_address)

@app.route('/api/maintenance/<int:computer_id>')
@login_required
def get_maintenance_records(computer_id):
    records = Maintenance.query.filter_by(computer_id=computer_id)\
        .order_by(Maintenance.date.desc())\
        .all()
    return jsonify([{
        'id': record.id,
        'date': record.date.strftime('%Y-%m-%d'),
        'description': record.description[:50] + '...' if len(record.description) > 50 else record.description
    } for record in records])

@app.route('/computer/assign-form', methods=['GET', 'POST'])
@login_required
def assign_computer_form():
    selected_computer_id = request.args.get('computer_id', type=int)
    selected_user_id = request.args.get('user_id', type=int)
    
    if request.method == 'POST':
        computer_id = request.form.get('computer_id')
        user_id = request.form.get('user_id')
        notes = request.form.get('assignment_notes')
        
        computer = Computer.query.get_or_404(computer_id)
        user = User.query.get_or_404(user_id)
        
        # Update computer assignment
        computer.assigned_user_id = user.id
        computer.assignment_notes = notes
        computer.assignment_date = datetime.utcnow()
        computer.update_status()
        
        db.session.commit()
        flash(f'Computer {computer.serial_number} successfully assigned to {user.name}')
        return redirect(url_for('home'))
    
    # Get all computers for the selection
    computers = Computer.query.all()
    users = User.query.all()
    
    return render_template('assign_computer.html',
                         available_computers=computers,
                         users=users,
                         selected_computer_id=selected_computer_id,
                         selected_user_id=selected_user_id)

@app.route('/api/assignments')
@login_required
def get_assignments():
    # Query joining User and Computer tables
    assignments = db.session.query(
        User.name, 
        User.email,
        User.department,
        Computer.serial_number,
        Computer.model,
        Computer.purchase_date,
        Computer.status,
        Computer.assignment_date
    ).join(
        Computer, 
        User.id == Computer.assigned_user_id,
        isouter=True  # This makes it a LEFT OUTER JOIN
    ).all()
    
    # Format the results
    result = [{
        'user_name': row[0],
        'email': row[1],
        'department': row[2],
        'serial_number': row[3],
        'model': row[4],
        'purchase_date': row[5].strftime('%Y-%m-%d') if row[5] else None,
        'status': row[6],
        'assignment_date': row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else None
    } for row in assignments]
    
    return jsonify(result)

@app.route('/api/users/names')
@login_required
def get_user_names():    # Query user information including profile image
    users = User.query.with_entities(
        User.id,
        User.name,
        User.email,
        User.department,
        User.profile_image
    ).order_by(User.name).all()
    
    # Format the results with profile image URL
    result = [{
        'id': user[0],
        'name': user[1],
        'email': user[2],
        'department': user[3],
        'profile_image_url': url_for('static', filename=f'uploads/profile_pics/{user[4]}', _external=True)
    } for user in users]
    
    return jsonify(result)

@app.route('/qrcode_lookup')
@login_required
def qrcode_lookup():
    # Get filter and sort parameters
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')
    department_filter = request.args.get('department', '')
    page = request.args.get('page', 1, type=int)
    per_page = 3  # Show 3 items per page

    # Build the base query
    query = db.session.query(
        User.name,
        User.email,
        User.department,
        User.profile_image,
        Computer.serial_number,
        Computer.model,
        Computer.purchase_date,
        Computer.assignment_date,
        Computer.id.label('computer_id')
    ).join(
        Computer,
        User.id == Computer.assigned_user_id
    )

    # Apply filters and get total count before pagination
    if search:
        query = query.filter(
            db.or_(
                User.name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                Computer.serial_number.ilike(f'%{search}%'),
                Computer.model.ilike(f'%{search}%')
            )
        )
    
    if department_filter:
        query = query.filter(User.department == department_filter)

    # Apply sorting
    sort_column = {
        'name': User.name,
        'email': User.email,
        'department': User.department,
        'serial_number': Computer.serial_number,
        'model': Computer.model,
        'purchase_date': Computer.purchase_date,
        'assignment_date': Computer.assignment_date
    }.get(sort_by, User.name)

    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Create pagination object
    pagination = Pagination(
        query.offset((page - 1) * per_page).limit(per_page).all(),
        page,
        per_page,
        query.count()
    )

    # Get departments for filter dropdown
    departments = db.session.query(User.department).distinct().all()
    departments = [dept[0] for dept in departments if dept[0]]

    # Format results
    assignments = [{
        'name': row[0],
        'email': row[1],
        'department': row[2],
        'profile_image': url_for('static', filename=f'uploads/profile_pics/{row[3]}'),
        'serial_number': row[4],
        'model': row[5],
        'purchase_date': row[6].strftime('%Y-%m-%d') if row[6] else None,
        'assignment_date': row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else None,
        'computer_id': row[8]
    } for row in pagination.items]

    return render_template('qrcode_lookup.html',
                         assignments=assignments,
                         settings=get_settings(),
                         departments=departments,
                         search=search,
                         sort_by=sort_by,
                         sort_order=sort_order,
                         department_filter=department_filter,
                         pagination=pagination,
                         page=page)

@app.route('/settings/contact', methods=['GET', 'POST'])
@login_required
def edit_contact_settings():
    settings = get_settings()
    if request.method == 'POST':
        settings.contact_admin_email = request.form.get('contact_admin_email')
        settings.contact_admin_phone = request.form.get('contact_admin_phone')
        settings.company_address = request.form.get('company_address')
        settings.last_updated = datetime.utcnow()
        db.session.commit()
        flash('Contact settings updated successfully')
        return redirect(url_for('qrcode_lookup'))
    return render_template('edit_contact_settings.html', settings=settings)

@app.route('/temp_qr/<string:serial_number>', methods=['GET'])
@login_required
def temp_qr(serial_number):
    try:
        # Find the computer by serial number
        computer = Computer.query.filter_by(serial_number=serial_number).first_or_404()
        settings = get_settings()
        
        # Get all related assignment info
        assigned_details = db.session.query(
            Computer, User
        ).outerjoin(
            User, Computer.assigned_user_id == User.id
        ).filter(
            Computer.serial_number == serial_number
        ).first()
        
        if not assigned_details:
            flash('Computer not found', 'error')
            return redirect(url_for('qrcode_lookup'))
            
        return render_template('temp_qr.html', computer=assigned_details[0], settings=settings)
    except Exception as e:
        flash(f'Error viewing QR details: {str(e)}', 'error')
        return redirect(url_for('qrcode_lookup'))

@app.route('/unified_report')
@login_required
def unified_report():
    from datetime import datetime
    current_date = datetime.now()
    current_month = current_date.strftime('%m')  # Default to current month if not 'all'
    current_year = current_date.year

    # Get parameters with 'all' as an option
    month = request.args.get('months', 'all')  # Default to 'all'
    year = request.args.get('years', str(current_year))
    report_type = request.args.get('type', 'all')
    department = request.args.get('department', '')

    # Build base queries
    computers_query = Computer.query
    users_query = User.query
    maintenance_query = Maintenance.query.order_by(desc(Maintenance.date))

    # Apply month filter only if specific month selected
    if month != 'all':
        computers_query = computers_query.filter(db.extract('month', Computer.purchase_date) == month)
        maintenance_query = maintenance_query.filter(db.extract('month', Maintenance.date) == month)

    if year != 'all':
        computers_query = computers_query.filter(db.extract('year', Computer.purchase_date) == year)
        maintenance_query = maintenance_query.filter(db.extract('year', Maintenance.date) == year)

    # Apply department filter
    if department:
        computers_query = computers_query.join(User).filter(User.department == department)
        users_query = users_query.filter(User.department == department)
        maintenance_query = maintenance_query.join(Computer).join(User).filter(User.department == department)

    # Get data based on report type
    data = {}
    if report_type in ['all', 'computers']:
        data['computers'] = computers_query.all()
    if report_type in ['all', 'users']:
        data['users'] = users_query.all()
    if report_type in ['all', 'maintenance']:
        data['maintenance'] = maintenance_query.all()

    # Get statistics
    stats = {
        'computers': get_inventory_stats() if report_type in ['all', 'computers'] else None,
        'users': get_users_stats() if report_type in ['all', 'users'] else None,
        'maintenance': get_maintenance_stats() if report_type in ['all', 'maintenance'] else None
    }

    # Get departments for filter
    departments = db.session.query(User.department).distinct().all()
    departments = [dept[0] for dept in departments if dept[0]]

    return render_template('unified_report.html',
                         data=data,
                         stats=stats,
                         date_range=request.args.get('date_range', 'month'),
                         report_type=report_type,
                         department=department,
                         departments=departments,
                         current_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                         current_month=current_month,
                         current_year=current_year)

@app.route('/api/computer/next')
@login_required
def get_next_computer_id():
    # Get highest computer ID
    latest_computer = Computer.query\
        .filter(Computer.computer_id.like('HfCCF-%'))\
        .order_by(Computer.computer_id.desc())\
        .first()
    
    if latest_computer:
        # Extract number from ID and increment
        current_id = int(latest_computer.computer_id.split('-')[1])
        next_id = current_id + 1
    else:
        next_id = 1
        
    return jsonify({
        'success': True,
        'next_id': next_id
    })

@app.route('/computer/update_id/<int:computer_id>', methods=['POST'])
@login_required
def update_computer_id(computer_id):
    try:
        data = request.get_json()
        computer = Computer.query.get_or_404(computer_id)
        new_id = data.get('computer_id')
        
        # Validate new ID format
        if not new_id or not re.match(r'^HfCCF-\d{4}$', new_id):
            return jsonify({'error': 'Invalid computer ID format'}), 400
            
        # Check if ID already exists
        if Computer.query.filter(Computer.computer_id == new_id, Computer.id != computer_id).first():
            return jsonify({'error': 'Computer ID already exists'}), 400
            
        computer.computer_id = new_id
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def create_backup():
    try:
        # Setup paths
        backup_path = os.path.join(app.root_path, 'backups')
        db_path = os.path.join(app.root_path, 'inventory.db')
        profiles_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
        
        # Create backup directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(backup_path, f'backup_{timestamp}')
        os.makedirs(backup_dir, exist_ok=True)

        # 1. Copy database file
        db_backup = os.path.join(backup_dir, 'inventory.db')
        shutil.copy2(db_path, db_backup)

        # 2. Copy profile images
        profiles_backup = os.path.join(backup_dir, 'profile_pics')
        if os.path.exists(profiles_path):
            shutil.copytree(profiles_path, profiles_backup, dirs_exist_ok=True)

        # 3. Create zip archive
        backup_filename = f'backup_{timestamp}.zip'
        backup_zip = os.path.join(backup_path, backup_filename)
        
        with zipfile.ZipFile(backup_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add database
            zipf.write(db_backup, 'inventory.db')
            
            # Add profile images
            for root, dirs, files in os.walk(profiles_backup):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, backup_dir)
                    zipf.write(full_path, rel_path)

        # Cleanup temporary backup directory
        shutil.rmtree(backup_dir)
        
        return backup_filename

    except Exception as e:
        app.logger.error(f"Backup error: {str(e)}")
        if 'backup_dir' in locals() and os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
        raise

@app.route('/restore', methods=['GET', 'POST'])
@app.route('/restore/<filename>', methods=['POST'])
@login_required
def restore_database(filename=None):
    try:
        if request.method == 'POST':
            backup_path = os.path.join(app.root_path, 'backups')
            temp_dir = os.path.join(backup_path, 'temp_restore')
            
            try:
                # Create temp directory
                os.makedirs(temp_dir, exist_ok=True)

                if filename:
                    # Handle existing backup
                    file_path = os.path.join(backup_path, filename)
                    if not os.path.exists(file_path):
                        return jsonify({'success': False, 'error': 'Backup file not found'})
                        
                    # Copy to temp dir
                    temp_file = os.path.join(temp_dir, filename)
                    shutil.copy2(file_path, temp_file)
                else:
                    # Handle upload
                    if 'backup_file' not in request.files:
                        return jsonify({'success': False, 'error': 'No file uploaded'})
                    
                    file = request.files['backup_file']
                    extension = os.path.splitext(file.filename)[1].lower()
                    
                    if extension not in ['.db', '.zip']:
                        return jsonify({'success': False, 'error': 'Invalid file format. Only .db or .zip files allowed'})
                    
                    temp_file = os.path.join(temp_dir, file.filename)
                    file.save(temp_file)

                # Process based on file type
                if temp_file.endswith('.zip'):
                    try:
                        # Extract database file from zip
                        with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                            db_files = [f for f in zip_ref.namelist() if f.endswith('.db')]
                            if not db_files:
                                return jsonify({'success': False, 'error': 'No database file found in zip'})
                            
                            # Extract the first database file found
                            zip_ref.extract(db_files[0], temp_dir)
                            db_path = os.path.join(temp_dir, db_files[0])
                    except zipfile.BadZipFile:
                        return jsonify({'success': False, 'error': 'Invalid zip file format'})
                else:
                    db_path = temp_file

                # Backup current admin user if preserve_admin flag is set
                preserve_admin = request.form.get('preserve_admin') == 'true'
                admin_data = None
                if preserve_admin:
                    admin = User.query.filter_by(email='admin@example.com').first()
                    if admin:
                        admin_data = {
                            'name': admin.name,
                            'email': admin.email,
                            'password': admin.password,
                            'department': admin.department
                        }

                # Restore database
                try:
                    shutil.copy2(db_path, os.path.join(app.root_path, 'instance/inventory.db'))
                    
                    # Restore admin if needed
                    if preserve_admin and admin_data:
                        db.session.remove()  # Close current session
                        with app.app_context():
                            admin = User.query.filter_by(email='admin@example.com').first()
                            if not admin:
                                admin = User(**admin_data)
                                db.session.add(admin)
                            else:
                                for key, value in admin_data.items():
                                    setattr(admin, key, value)
                            db.session.commit()

                    return jsonify({
                        'success': True,
                        'message': 'Database restored successfully'
                    })

                except Exception as e:
                    app.logger.error(f"Error restoring database: {str(e)}")
                    return jsonify({'success': False, 'error': f'Error restoring database: {str(e)}'})

            finally:
                # Cleanup
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    
    except Exception as e:
        app.logger.error(f"Restore error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/backup', methods=['GET', 'POST'])
@app.route('/backup_database', methods=['POST'])
@login_required
def backup_database():
    """Handle database backup operations"""
    # Initialize paths
    backup_path = os.path.join(app.root_path, 'backups')
    db_path = os.path.join(app.root_path, 'instance', 'inventory.db')  # Fix: Add 'instance' to path
    
    # Create backup directory if needed
    os.makedirs(backup_path, exist_ok=True)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Create instance directory if needed
    
    if request.method == 'POST':
        try:
            # Check if source database exists
            if not os.path.exists(db_path):
                with app.app_context():
                    db.create_all()
                    app.logger.info("Created new database file")
            
            # Create backup with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'backup_{timestamp}.db'
            backup_file = os.path.join(backup_path, backup_filename)
            
            # Copy database with error handling
            try:
                shutil.copy2(db_path, backup_file)
                if request.headers.get('Accept') == 'application/json':
                    return jsonify({
                        'success': True,
                        'message': 'Backup created successfully'
                    })
                flash('Backup created successfully', 'success')
            except IOError as e:
                app.logger.error(f"Backup error: {str(e)}")
                if request.headers.get('Accept') == 'application/json':
                    return jsonify({
                        'success': False,
                        'error': str(e)
                    }), 500
                flash('Error: Could not create backup file. Check permissions.', 'error')
                
        except Exception as e:
            app.logger.error(f"Backup error: {str(e)}")
            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
            flash(f'Backup failed: {str(e)}', 'error')
        return redirect(url_for('backup_list'))  # Fix: Change redirect to 'backup' instead of 'backup_database')

    # Handle GET request for listing backups
    backup_list = []
    if os.path.exists(backup_path):
        for file in os.listdir(backup_path):
            if file.endswith('.db'):
                file_path = os.path.join(backup_path, file)
                try:
                    backup_list.append({
                        'name': file,
                        'date': datetime.fromtimestamp(os.path.getctime(file_path)),
                        'size': os.path.getsize(file_path) / 1024
                    })
                except OSError:
                    continue
    
    # Sort and paginate backups
    page = request.args.get('page', 1, type=int)
    per_page = 5
    backup_list.sort(key=lambda x: x['date'], reverse=True)
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, len(backup_list))
    backups = backup_list[start_idx:end_idx]
    
    pagination = Pagination(backups, page, per_page, len(backup_list))
    return render_template('backup.html', 
                         backups=backups,
                         pagination=pagination,
                         page=page)

@app.route('/download_backup/<filename>')
@login_required
def download_backup(filename):
    backup_path = os.path.join(app.root_path, 'backups')
    return send_from_directory(
        backup_path, 
        filename,
        as_attachment=True,
        download_name=filename
    )

@app.route('/delete_backup/<filename>', methods=['POST'])
@login_required
def delete_backup(filename):
    try:
        backup_path = os.path.join(app.root_path, 'backups')
        file_path = os.path.join(backup_path, filename)
        
        # Verify file exists and is within backups directory
        if not os.path.exists(file_path) or not file_path.startswith(backup_path):
            flash('Backup file not found', 'error')
            return redirect(url_for('backup_list'))
            
        # Delete the backup file
        os.remove(file_path)
        flash('Backup deleted successfully', 'success')
        
    except Exception as e:
        app.logger.error(f'Error deleting backup: {str(e)}')
        flash(f'Error deleting backup: {str(e)}', 'error')
        
    return redirect(url_for('backup_list'))

@app.route('/open_backup_folder')
@login_required
def open_backup_folder():
    backup_path = os.path.join(app.root_path, 'backups')
    try:
        os.makedirs(backup_path, exist_ok=True)
        if os.name == 'nt':  # Windows
            subprocess.run(['explorer', backup_path])
        elif os.name == 'posix':  # macOS/Linux
            subprocess.run(['open', backup_path])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/backup_list')
@login_required
def backup_list():
    # Initialize paths
    backup_path = os.path.join(app.root_path, 'backups')
    db_path = os.path.join(app.root_path, 'instance', 'inventory.db')
    
    # Create backup directory if needed
    os.makedirs(backup_path, exist_ok=True)
    
    # Get backups list
    backup_list = []
    if os.path.exists(backup_path):
        for file in os.listdir(backup_path):
            if file.endswith('.db'):
                file_path = os.path.join(backup_path, file)
                try:
                    backup_list.append({
                        'name': file,
                        'date': datetime.fromtimestamp(os.path.getctime(file_path)),
                        'size': os.path.getsize(file_path) / 1024
                    })
                except OSError:
                    continue
    
    # Sort and paginate backups
    page = request.args.get('page', 1, type=int)
    per_page = 5
    backup_list.sort(key=lambda x: x['date'], reverse=True)
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, len(backup_list))
    backups = backup_list[start_idx:end_idx]
    
    pagination = Pagination(backups, page, per_page, len(backup_list))
    return render_template('backup_list.html', 
                         backups=backups,
                         pagination=pagination,
                         page=page)

def create_test_user():
    # Create a test user if it doesn't exist
    if not User.query.filter_by(email='admin@example.com').first():
        test_user = User(
            name='Admin User',
            email='admin@example.com',
            password=generate_secure_password_hash('admin'),
            department='IT'
        )
        db.session.add(test_user)
        db.session.commit()
        print('Test user created. Email: admin@example.com, Password: admin')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_test_user()
    app.run(debug=True)
    if not User.query.filter_by(email='admin@example.com').first():
        test_user = User(
            name='Admin User',
            email='admin@example.com',
            password=generate_secure_password_hash('admin'),
            department='IT'
        )
        db.session.add(test_user)
        db.session.commit()
        print('Test user created. Email: admin@example.com, Password: admin')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_test_user()
    app.run(debug=True)
