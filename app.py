from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'skilltrack_secret_key_2024'

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            phone TEXT,
            college TEXT,
            department TEXT,
            graduation_year TEXT,
            career_goal TEXT,
            bio TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Skills table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            category TEXT,
            proficiency INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            description TEXT,
            technologies TEXT,
            github_link TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Certifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            certification_name TEXT NOT NULL,
            organization TEXT,
            date_earned TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Internships table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS internships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            company TEXT NOT NULL,
            role TEXT,
            duration TEXT,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Login required decorator
def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not full_name or not email or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (full_name, email, password) VALUES (?, ?, ?)',
                (full_name, email, hashed_password)
            )
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered.', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['user_email'] = user['email']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get counts
    cursor.execute('SELECT COUNT(*) FROM skills WHERE user_id = ?', (user_id,))
    skills_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM projects WHERE user_id = ?', (user_id,))
    projects_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM certifications WHERE user_id = ?', (user_id,))
    certifications_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM internships WHERE user_id = ?', (user_id,))
    internships_count = cursor.fetchone()[0]
    
    # Get career goal
    cursor.execute('SELECT career_goal FROM profiles WHERE user_id = ?', (user_id,))
    profile = cursor.fetchone()
    career_goal = profile['career_goal'] if profile and profile['career_goal'] else 'Not set'
    
    # Get skills for progress
    cursor.execute('SELECT skill_name, proficiency FROM skills WHERE user_id = ? LIMIT 5', (user_id,))
    skills = cursor.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html',
                         skills_count=skills_count,
                         projects_count=projects_count,
                         certifications_count=certifications_count,
                         internships_count=internships_count,
                         career_goal=career_goal,
                         skills=skills)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Update profile
        phone = request.form.get('phone', '').strip()
        college = request.form.get('college', '').strip()
        department = request.form.get('department', '').strip()
        graduation_year = request.form.get('graduation_year', '').strip()
        career_goal = request.form.get('career_goal', '').strip()
        bio = request.form.get('bio', '').strip()
        
        cursor.execute('''
            INSERT OR REPLACE INTO profiles 
            (user_id, phone, college, department, graduation_year, career_goal, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, phone, college, department, graduation_year, career_goal, bio))
        conn.commit()
        flash('Profile updated successfully!', 'success')
    
    # Get profile
    cursor.execute('SELECT * FROM profiles WHERE user_id = ?', (user_id,))
    profile = cursor.fetchone()
    
    # Get all data
    cursor.execute('SELECT * FROM skills WHERE user_id = ?', (user_id,))
    skills = cursor.fetchall()
    
    cursor.execute('SELECT * FROM projects WHERE user_id = ?', (user_id,))
    projects = cursor.fetchall()
    
    cursor.execute('SELECT * FROM certifications WHERE user_id = ?', (user_id,))
    certifications = cursor.fetchall()
    
    cursor.execute('SELECT * FROM internships WHERE user_id = ?', (user_id,))
    internships = cursor.fetchall()
    
    conn.close()
    
    return render_template('profile.html',
                         profile=profile,
                         skills=skills,
                         projects=projects,
                         certifications=certifications,
                         internships=internships)

# Skills routes
@app.route('/add_skill', methods=['POST'])
@login_required
def add_skill():
    skill_name = request.form.get('skill_name', '').strip()
    category = request.form.get('category', '').strip()
    proficiency = request.form.get('proficiency', 50)
    
    if skill_name:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO skills (user_id, skill_name, category, proficiency) VALUES (?, ?, ?, ?)',
            (session['user_id'], skill_name, category, proficiency)
        )
        conn.commit()
        conn.close()
        flash('Skill added successfully!', 'success')
    
    return redirect(url_for('profile'))

@app.route('/edit_skill/<int:skill_id>', methods=['POST'])
@login_required
def edit_skill(skill_id):
    skill_name = request.form.get('skill_name', '').strip()
    category = request.form.get('category', '').strip()
    proficiency = request.form.get('proficiency', 50)
    
    if skill_name:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE skills SET skill_name=?, category=?, proficiency=? WHERE id=? AND user_id=?',
            (skill_name, category, proficiency, skill_id, session['user_id'])
        )
        conn.commit()
        conn.close()
        flash('Skill updated successfully!', 'success')
    
    return redirect(url_for('profile'))

@app.route('/delete_skill/<int:skill_id>')
@login_required
def delete_skill(skill_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM skills WHERE id=? AND user_id=?', (skill_id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Skill deleted successfully!', 'success')
    return redirect(url_for('profile'))

# Projects routes
@app.route('/add_project', methods=['POST'])
@login_required
def add_project():
    project_name = request.form.get('project_name', '').strip()
    description = request.form.get('description', '').strip()
    technologies = request.form.get('technologies', '').strip()
    github_link = request.form.get('github_link', '').strip()
    
    if project_name:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO projects (user_id, project_name, description, technologies, github_link) VALUES (?, ?, ?, ?, ?)',
            (session['user_id'], project_name, description, technologies, github_link)
        )
        conn.commit()
        conn.close()
        flash('Project added successfully!', 'success')
    
    return redirect(url_for('profile'))

@app.route('/edit_project/<int:project_id>', methods=['POST'])
@login_required
def edit_project(project_id):
    project_name = request.form.get('project_name', '').strip()
    description = request.form.get('description', '').strip()
    technologies = request.form.get('technologies', '').strip()
    github_link = request.form.get('github_link', '').strip()
    
    if project_name:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE projects SET project_name=?, description=?, technologies=?, github_link=? WHERE id=? AND user_id=?',
            (project_name, description, technologies, github_link, project_id, session['user_id'])
        )
        conn.commit()
        conn.close()
        flash('Project updated successfully!', 'success')
    
    return redirect(url_for('profile'))

@app.route('/delete_project/<int:project_id>')
@login_required
def delete_project(project_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM projects WHERE id=? AND user_id=?', (project_id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('profile'))

# Certifications routes
@app.route('/add_certification', methods=['POST'])
@login_required
def add_certification():
    certification_name = request.form.get('certification_name', '').strip()
    organization = request.form.get('organization', '').strip()
    date_earned = request.form.get('date_earned', '').strip()
    
    if certification_name:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO certifications (user_id, certification_name, organization, date_earned) VALUES (?, ?, ?, ?)',
            (session['user_id'], certification_name, organization, date_earned)
        )
        conn.commit()
        conn.close()
        flash('Certification added successfully!', 'success')
    
    return redirect(url_for('profile'))

@app.route('/edit_certification/<int:cert_id>', methods=['POST'])
@login_required
def edit_certification(cert_id):
    certification_name = request.form.get('certification_name', '').strip()
    organization = request.form.get('organization', '').strip()
    date_earned = request.form.get('date_earned', '').strip()
    
    if certification_name:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE certifications SET certification_name=?, organization=?, date_earned=? WHERE id=? AND user_id=?',
            (certification_name, organization, date_earned, cert_id, session['user_id'])
        )
        conn.commit()
        conn.close()
        flash('Certification updated successfully!', 'success')
    
    return redirect(url_for('profile'))

@app.route('/delete_certification/<int:cert_id>')
@login_required
def delete_certification(cert_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM certifications WHERE id=? AND user_id=?', (cert_id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Certification deleted successfully!', 'success')
    return redirect(url_for('profile'))

# Internships routes
@app.route('/add_internship', methods=['POST'])
@login_required
def add_internship():
    company = request.form.get('company', '').strip()
    role = request.form.get('role', '').strip()
    duration = request.form.get('duration', '').strip()
    description = request.form.get('description', '').strip()
    
    if company:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO internships (user_id, company, role, duration, description) VALUES (?, ?, ?, ?, ?)',
            (session['user_id'], company, role, duration, description)
        )
        conn.commit()
        conn.close()
        flash('Internship added successfully!', 'success')
    
    return redirect(url_for('profile'))

@app.route('/edit_internship/<int:internship_id>', methods=['POST'])
@login_required
def edit_internship(internship_id):
    company = request.form.get('company', '').strip()
    role = request.form.get('role', '').strip()
    duration = request.form.get('duration', '').strip()
    description = request.form.get('description', '').strip()
    
    if company:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE internships SET company=?, role=?, duration=?, description=? WHERE id=? AND user_id=?',
            (company, role, duration, description, internship_id, session['user_id'])
        )
        conn.commit()
        conn.close()
        flash('Internship updated successfully!', 'success')
    
    return redirect(url_for('profile'))

@app.route('/delete_internship/<int:internship_id>')
@login_required
def delete_internship(internship_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM internships WHERE id=? AND user_id=?', (internship_id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Internship deleted successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/resume')
@login_required
def resume():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user info
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    # Get profile
    cursor.execute('SELECT * FROM profiles WHERE user_id = ?', (user_id,))
    profile = cursor.fetchone()
    
    # Get all data
    cursor.execute('SELECT * FROM skills WHERE user_id = ?', (user_id,))
    skills = cursor.fetchall()
    
    cursor.execute('SELECT * FROM projects WHERE user_id = ?', (user_id,))
    projects = cursor.fetchall()
    
    cursor.execute('SELECT * FROM certifications WHERE user_id = ?', (user_id,))
    certifications = cursor.fetchall()
    
    cursor.execute('SELECT * FROM internships WHERE user_id = ?', (user_id,))
    internships = cursor.fetchall()
    
    conn.close()
    
    return render_template('resume.html',
                         user=user,
                         profile=profile,
                         skills=skills,
                         projects=projects,
                         certifications=certifications,
                         internships=internships)

if __name__ == '__main__':
    app.run(debug=True)