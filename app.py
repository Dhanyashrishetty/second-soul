import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from flask_cors import CORS
from models import db, User, NGO, Volunteer, Donation
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'charity.db')
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads')
app.config['JSON_SORT_KEYS'] = False

CORS(app)
db.init_app(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

with app.app_context():
    db.create_all()
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session and not session.get('guest'):
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/ngo')
def ngo_page():
    if 'user_id' not in session and not session.get('guest'):
        return redirect(url_for('index'))
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('ngo.html', user=user)

@app.route('/volunteer')
def volunteer_page():
    if 'user_id' not in session and not session.get('guest'):
        return redirect(url_for('index'))
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('volunteer.html', user=user)

@app.route('/donate')
def donate_page():
    if 'user_id' not in session and not session.get('guest'):
        return redirect(url_for('index'))
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('donate.html', user=user)

@app.route('/activities')
def activities_page():
    if 'user_id' not in session and not session.get('guest'):
        return redirect(url_for('index'))
    return render_template('activities.html')

@app.route('/admin')
def admin_page():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('admin.html')

# ============ API ROUTES ============

@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        phone = data.get('phone', '').strip()

        if not all([name, email, password, phone]):
            return jsonify({'error': 'All fields required'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400

        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1

        new_user = User(
            username=username,
            email=email,
            password=password,
            full_name=name,
            phone=phone
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'id': new_user.id,
            'name': new_user.full_name,
            'email': new_user.email,
            'phone': new_user.phone
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400

        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            session.pop('guest', None)
            return jsonify({
                'id': user.id,
                'name': user.full_name,
                'email': user.email,
                'phone': user.phone
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('guest', None)
    return jsonify({'success': True}), 200

@app.route('/api/guest', methods=['POST'])
def api_guest():
    session['guest'] = True
    return jsonify({'success': True}), 200

@app.route('/api/ngos', methods=['GET'])
def api_get_ngos():
    try:
        ngos = NGO.query.all()
        return jsonify([{
            'id': ngo.id,
            'name': ngo.name,
            'email': ngo.email,
            'phone': ngo.phone,
            'address': ngo.address,
            'description': ngo.description,
            'registration_number': ngo.registration_number,
            'owner_name': ngo.owner_name,
            'qr_code': f'/static/uploads/{ngo.qr_code_filename}' if ngo.qr_code_filename else None
        } for ngo in ngos]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ngos', methods=['POST'])
def api_create_ngo():
    try:
        if 'user_id' not in session and not session.get('guest'):
            return jsonify({'error': 'Unauthorized'}), 401

        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        description = request.form.get('description', '').strip()
        registration_number = request.form.get('registration_number', '').strip()
        owner_name = request.form.get('owner_name', '').strip()

        if not all([name, email, phone]):
            return jsonify({'error': 'Name, email, and phone required'}), 400

        filename = None
        if 'qr_file' in request.files:
            file = request.files['qr_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = str(uuid.uuid4()) + "_" + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                filename = unique_filename

        new_ngo = NGO(
            name=name,
            email=email,
            phone=phone,
            address=address,
            description=description,
            registration_number=registration_number,
            owner_name=owner_name,
            qr_code_filename=filename
        )
        db.session.add(new_ngo)
        db.session.commit()

        return jsonify({
            'id': new_ngo.id,
            'name': new_ngo.name,
            'email': new_ngo.email,
            'phone': new_ngo.phone,
            'address': new_ngo.address,
            'description': new_ngo.description,
            'registration_number': new_ngo.registration_number,
            'owner_name': new_ngo.owner_name,
            'qr_code': f'/static/uploads/{new_ngo.qr_code_filename}' if new_ngo.qr_code_filename else None
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/volunteers', methods=['GET'])
def api_get_volunteers():
    try:
        volunteers = Volunteer.query.all()
        return jsonify([{
            'id': v.id,
            'name': v.name,
            'email': v.email,
            'phone': v.phone,
            'address': v.address,
            'skills': v.skills,
            'availability': v.availability
        } for v in volunteers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/volunteers', methods=['POST'])
def api_create_volunteer():
    try:
        if 'user_id' not in session and not session.get('guest'):
            return jsonify({'error': 'Unauthorized'}), 401

        data = request.get_json()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        address = data.get('address', '').strip()
        skills = data.get('skills', '').strip()
        availability = data.get('availability', '').strip()

        if not all([name, email]):
            return jsonify({'error': 'Name and email required'}), 400

        new_volunteer = Volunteer(
            name=name,
            email=email,
            phone=phone,
            address=address,
            skills=skills,
            availability=availability
        )
        db.session.add(new_volunteer)
        db.session.commit()

        return jsonify({
            'id': new_volunteer.id,
            'name': new_volunteer.name,
            'email': new_volunteer.email,
            'phone': new_volunteer.phone,
            'address': new_volunteer.address,
            'skills': new_volunteer.skills,
            'availability': new_volunteer.availability
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/donations', methods=['GET'])
def api_get_donations():
    try:
        user_email = request.args.get('user_email')
        donation_type = request.args.get('type')

        query = Donation.query
        if user_email:
            query = query.filter_by(donor_email=user_email)
        if donation_type:
            query = query.filter_by(type=donation_type)

        donations = query.all()
        return jsonify([{
            'id': d.id,
            'type': d.type,
            'amount': d.amount,
            'item_name': d.item_name,
            'item_image': f'/static/uploads/{d.item_image_filename}' if d.item_image_filename else None,
            'ngo_id': d.ngo_id,
            'donor_name': d.donor_name,
            'donor_email': d.donor_email,
            'donor_phone': d.donor_phone,
            'date': d.date_donated.isoformat() if d.date_donated else None
        } for d in donations]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/donations', methods=['POST'])
def api_create_donation():
    try:
        donation_type = request.form.get('type', '').strip()
        ngo_id = request.form.get('ngo_id', type=int)
        donor_name = request.form.get('donor_name', '').strip()
        donor_email = request.form.get('donor_email', '').strip()
        donor_phone = request.form.get('donor_phone', '').strip()

        if not all([donation_type, ngo_id]):
            return jsonify({'error': 'Type and NGO ID required'}), 400

        if donation_type == 'money':
            amount = request.form.get('amount', type=float)
            if not amount or amount <= 0:
                return jsonify({'error': 'Valid amount required'}), 400

            new_donation = Donation(
                type='money',
                amount=amount,
                ngo_id=ngo_id,
                donor_name=donor_name,
                donor_email=donor_email,
                donor_phone=donor_phone
            )
            db.session.add(new_donation)
            db.session.commit()

            voucher_code = "GIFT-" + str(uuid.uuid4())[:8].upper()
            return jsonify({
                'id': new_donation.id,
                'type': 'money',
                'amount': new_donation.amount,
                'ngo_id': new_donation.ngo_id,
                'voucher_code': voucher_code,
                'message': 'Donation successful!'
            }), 201

        elif donation_type == 'item':
            item_name = request.form.get('item_name', '').strip()
            if not item_name:
                return jsonify({'error': 'Item name required'}), 400

            filename = None
            if 'item_file' in request.files:
                file = request.files['item_file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = str(uuid.uuid4()) + "_" + filename
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                    filename = unique_filename

            new_donation = Donation(
                type='item',
                item_name=item_name,
                item_image_filename=filename,
                ngo_id=ngo_id,
                donor_name=donor_name,
                donor_email=donor_email,
                donor_phone=donor_phone
            )
            db.session.add(new_donation)
            db.session.commit()

            return jsonify({
                'id': new_donation.id,
                'type': 'item',
                'item_name': new_donation.item_name,
                'item_image': f'/static/uploads/{new_donation.item_image_filename}' if new_donation.item_image_filename else None,
                'ngo_id': new_donation.ngo_id,
                'message': 'Item donation successful!'
            }), 201
        else:
            return jsonify({'error': 'Invalid donation type'}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/all', methods=['GET'])
def api_admin_all():
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401

        ngos = NGO.query.all()
        volunteers = Volunteer.query.all()
        donations = Donation.query.all()

        return jsonify({
            'ngos': [{
                'id': ngo.id,
                'name': ngo.name,
                'email': ngo.email,
                'phone': ngo.phone,
                'address': ngo.address,
                'description': ngo.description
            } for ngo in ngos],
            'volunteers': [{
                'id': v.id,
                'name': v.name,
                'email': v.email,
                'phone': v.phone,
                'skills': v.skills,
                'availability': v.availability
            } for v in volunteers],
            'donations': [{
                'id': d.id,
                'type': d.type,
                'amount': d.amount,
                'item_name': d.item_name,
                'donor_name': d.donor_name,
                'date': d.date_donated.isoformat() if d.date_donated else None
            } for d in donations]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
