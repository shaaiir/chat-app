from flask import Blueprint, request, jsonify, session
from app.models import User, Message, Friendship
from app import db
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

# ==========================================
# User API Endpoints
# ==========================================

@api_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users (vulnerable - no authentication required)"""
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'created_at': user.created_at.isoformat()
    } for user in users])

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get specific user info (vulnerable - exposes data)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'password': user.password,  # Vulnerable: exposes plain text password
        'created_at': user.created_at.isoformat()
    })

@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user (vulnerable - no authorization check)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Delete all related data
    Message.query.filter(
        (Message.sender_id == user_id) | (Message.receiver_id == user_id)
    ).delete()
    Friendship.query.filter(
        (Friendship.user_id == user_id) | (Friendship.friend_id == user_id)
    ).delete()
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'User deleted'})

# ==========================================
# Messages API Endpoints
# ==========================================

@api_bp.route('/messages', methods=['GET'])
def get_all_messages():
    """Get all messages (vulnerable - no authentication)"""
    messages = Message.query.order_by(Message.timestamp.desc()).limit(100).all()
    return jsonify([{
        'id': msg.id,
        'sender_id': msg.sender_id,
        'receiver_id': msg.receiver_id,
        'content': msg.content,
        'timestamp': msg.timestamp.isoformat()
    } for msg in messages])

@api_bp.route('/messages/<int:user1_id>/<int:user2_id>', methods=['GET'])
def get_conversation(user1_id, user2_id):
    """Get messages between two users (vulnerable - no auth check)"""
    messages = Message.query.filter(
        ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
        ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
    ).order_by(Message.timestamp.asc()).all()
    
    return jsonify([{
        'id': msg.id,
        'sender_id': msg.sender_id,
        'receiver_id': msg.receiver_id,
        'content': msg.content,
        'timestamp': msg.timestamp.isoformat()
    } for msg in messages])

@api_bp.route('/messages', methods=['POST'])
def send_message_api():
    """Send a message via API (vulnerable - weak validation)"""
    data = request.get_json()
    
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    
    if not all([sender_id, receiver_id, content]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # No authentication check - anyone can impersonate any user
    message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message_id': message.id,
        'timestamp': message.timestamp.isoformat()
    }), 201

@api_bp.route('/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """Delete a message (vulnerable - no ownership check)"""
    message = Message.query.get(message_id)
    
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    db.session.delete(message)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Message deleted'})

# ==========================================
# Friendship API Endpoints
# ==========================================

@api_bp.route('/friendships', methods=['GET'])
def get_all_friendships():
    """Get all friendships (vulnerable - exposes all relationships)"""
    friendships = Friendship.query.all()
    return jsonify([{
        'id': f.id,
        'user_id': f.user_id,
        'friend_id': f.friend_id,
        'status': f.status,
        'created_at': f.created_at.isoformat()
    } for f in friendships])

@api_bp.route('/friendships/<int:user_id>', methods=['GET'])
def get_user_friends(user_id):
    """Get friends of a specific user (vulnerable - no auth)"""
    friendships = Friendship.query.filter(
        ((Friendship.user_id == user_id) | (Friendship.friend_id == user_id)),
        Friendship.status == 'accepted'
    ).all()
    
    friends = []
    for f in friendships:
        friend_id = f.friend_id if f.user_id == user_id else f.user_id
        friend = User.query.get(friend_id)
        if friend:
            friends.append({
                'id': friend.id,
                'username': friend.username
            })
    
    return jsonify(friends)

@api_bp.route('/friendships', methods=['POST'])
def create_friendship_api():
    """Create friend request via API (vulnerable - no validation)"""
    data = request.get_json()
    
    user_id = data.get('user_id')
    friend_id = data.get('friend_id')
    
    if not user_id or not friend_id:
        return jsonify({'error': 'Missing user_id or friend_id'}), 400
    
    # Check if already exists
    existing = Friendship.query.filter(
        ((Friendship.user_id == user_id) & (Friendship.friend_id == friend_id)) |
        ((Friendship.user_id == friend_id) & (Friendship.friend_id == user_id))
    ).first()
    
    if existing:
        return jsonify({'error': 'Friendship already exists'}), 400
    
    friendship = Friendship(user_id=user_id, friend_id=friend_id, status='pending')
    db.session.add(friendship)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'friendship_id': friendship.id
    }), 201

@api_bp.route('/friendships/<int:friendship_id>/accept', methods=['PUT'])
def accept_friendship_api(friendship_id):
    """Accept friendship (vulnerable - no ownership validation)"""
    friendship = Friendship.query.get(friendship_id)
    
    if not friendship:
        return jsonify({'error': 'Friendship not found'}), 404
    
    friendship.status = 'accepted'
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Friendship accepted'})

@api_bp.route('/friendships/<int:friendship_id>', methods=['DELETE'])
def delete_friendship(friendship_id):
    """Delete friendship (vulnerable - no auth check)"""
    friendship = Friendship.query.get(friendship_id)
    
    if not friendship:
        return jsonify({'error': 'Friendship not found'}), 404
    
    db.session.delete(friendship)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Friendship deleted'})

# ==========================================
# Statistics & Analytics (Data Leakage)
# ==========================================

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get application statistics (vulnerable - information disclosure)"""
    total_users = User.query.count()
    total_messages = Message.query.count()
    total_friendships = Friendship.query.filter_by(status='accepted').count()
    
    # Most active users (data leakage)
    from sqlalchemy import func
    active_users = db.session.query(
        User.username,
        func.count(Message.id).label('message_count')
    ).join(Message, Message.sender_id == User.id)\
     .group_by(User.id)\
     .order_by(func.count(Message.id).desc())\
     .limit(10).all()
    
    return jsonify({
        'total_users': total_users,
        'total_messages': total_messages,
        'total_friendships': total_friendships,
        'most_active_users': [{
            'username': username,
            'message_count': count
        } for username, count in active_users]
    })

# ==========================================
# Debug Endpoints (Extremely Vulnerable)
# ==========================================

@api_bp.route('/debug/database', methods=['GET'])
def debug_database():
    """Debug endpoint exposing entire database (CRITICAL vulnerability)"""
    return jsonify({
        'users': [{
            'id': u.id,
            'username': u.username,
            'password': u.password  # Plain text!
        } for u in User.query.all()],
        'messages': [{
            'id': m.id,
            'sender': m.sender_id,
            'receiver': m.receiver_id,
            'content': m.content
        } for m in Message.query.all()],
        'friendships': [{
            'id': f.id,
            'user': f.user_id,
            'friend': f.friend_id,
            'status': f.status
        } for f in Friendship.query.all()]
    })

@api_bp.route('/debug/session', methods=['GET'])
def debug_session():
    """Debug endpoint exposing session data (vulnerable)"""
    return jsonify({
        'session': dict(session),
        'cookies': dict(request.cookies)
    })

# ==========================================
# SQL Injection Vulnerable Endpoint
# ==========================================

@api_bp.route('/search', methods=['GET'])
def search_users():
    """Search users (VULNERABLE to SQL Injection)"""
    query = request.args.get('q', '')
    
    # Intentionally vulnerable SQL query
    sql = f"SELECT id, username FROM user WHERE username LIKE '%{query}%'"
    
    try:
        result = db.session.execute(sql)
        users = [{'id': row[0], 'username': row[1]} for row in result]
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
