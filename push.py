from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from pusher import Pusher
from flask_cors import CORS
from datetime import datetime
import os
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:8002"}})

# SQLite Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'chat.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Pusher Configuration
pusher_client = Pusher(
    app_id='4712912',
    key='iijdsjkanidnasqw9rqw',
    secret='jsnfaoicfoapjfjpqef',
    host="09d1-35-159-107-7.ngrok-free.app",
    port=443,
    ssl=True,
)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    profile_pic = db.Column(db.String(200), nullable=True)
    is_online = db.Column(db.Boolean, default=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('messages', lazy=True))

with app.app_context():
    db.create_all()

@app.route('/pusher/auth', methods=['POST'])
def pusher_auth():
    data = request.form if request.form else request.json
    channel_name = data.get('channel_name')
    socket_id = data.get('socket_id')
    username = data.get('username')

    if not all([channel_name, socket_id, username]):
        return jsonify({"error": "Missing required parameters"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    auth = pusher_client.authenticate(
        channel=channel_name,
        socket_id=socket_id,
        custom_data={
            'user_id': user.id,
            'user_info': {
                'username': user.username,
                'profile_pic': user.profile_pic
            }
        }
    )
    return jsonify(auth)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    profile_pic = data.get('profile_pic', '')
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"status": "error", "message": "Username already exists"}), 400
    
    new_user = User(username=username, profile_pic=profile_pic, is_online=True)
    db.session.add(new_user)
    db.session.commit()
    
    pusher_client.trigger('presence-chat', 'user-joined', {
        'username': username,
        'profile_pic': profile_pic
    })
    
    return jsonify({"status": "success", "message": "User registered successfully"}), 201

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json
    username = data['username']
    content = data['content']
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404
    
    new_message = Message(content=content, user=user)
    db.session.add(new_message)
    db.session.commit()
    
    pusher_client.trigger('presence-chat', 'new-message', {
        'username': username,
        'content': content,
        'timestamp': new_message.timestamp.isoformat()
    })
    
    return jsonify({"status": "Message sent and saved"}), 200

@app.route('/get-messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.timestamp.asc()).all()
    return jsonify([{
        'username': msg.user.username,
        'content': msg.content,
        'timestamp': msg.timestamp.isoformat()
    } for msg in messages]), 200

@app.route('/user-typing', methods=['POST'])
def user_typing():
    data = request.json
    username = data['username']
    is_typing = data['is_typing']
    
    pusher_client.trigger('presence-chat', 'user-typing', {
        'username': username,
        'is_typing': is_typing
    })
    
    return jsonify({"status": "Typing status updated"}), 200

@app.route('/user-status', methods=['POST'])
def user_status():
    data = request.json
    username = data['username']
    is_online = data['is_online']
    
    user = User.query.filter_by(username=username).first()
    if user:
        user.is_online = is_online
        db.session.commit()
        
        pusher_client.trigger('presence-chat', 'user-status', {
            'username': username,
            'is_online': is_online
        })
        
        return jsonify({"status": "User status updated"}), 200
    else:
        return jsonify({"status": "error", "message": "User not found"}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)