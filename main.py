from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

db = {
    'users': {'ceo@inswa.tech': {'password': 'zambia2026', 'name': 'OLLEN'}},
    'farms': [],
    'drone_data': []
}

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in db['users'] and db['users'][email]['password'] == password:
            session['user'] = email
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('splash'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html', user=db['users'][session['user']])

@app.route('/api/farms', methods=['GET', 'POST'])
@login_required
def farms():
    if request.method == 'POST':
        farm = request.get_json()
        farm['id'] = len(db['farms']) + 1
        farm['owner'] = session['user']
        farm['created'] = datetime.now().isoformat()
        db['farms'].append(farm)
        return jsonify(farm)
    user_farms = [f for f in db['farms'] if f['owner'] == session['user']]
    return jsonify(user_farms)

@app.route('/api/drone/upload', methods=['POST'])
@login_required
def drone_upload():
    data = request.get_json()
    if not data or 'drone_id' not in data:
        return jsonify({"error": "Missing drone_id"}), 400
    data['timestamp'] = datetime.now().isoformat()
    data['user'] = session['user']
    db['drone_data'].append(data)
    db['drone_data'] = db['drone_data'][-500:]
    return jsonify({"success": True, "total_pings": len(db['drone_data'])})

@app.route('/api/drone/latest')
@login_required
def drone_latest():
    user_drones = [d for d in db['drone_data'] if d['user'] == session['user']]
    return jsonify(user_drones[-1] if user_drones else {})

@app.route('/api/drone/history')
@login_required
def drone_history():
    limit = int(request.args.get('limit', 100))
    user_drones = [d for d in db['drone_data'] if d['user'] == session['user']]
    return jsonify(user_drones[-limit:])

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
