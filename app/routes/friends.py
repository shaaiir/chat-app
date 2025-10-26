from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.models import User, Friendship
from app import db

friends_bp = Blueprint('friends', __name__)

@friends_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    # Get accepted friends
    friends = db.session.query(User).join(
        Friendship, 
        (Friendship.friend_id == User.id) | (Friendship.user_id == User.id)
    ).filter(
        ((Friendship.user_id == user_id) | (Friendship.friend_id == user_id)),
        Friendship.status == 'accepted',
        User.id != user_id
    ).all()
    
    # Get pending requests received
    pending_requests = db.session.query(User, Friendship).join(
        Friendship, Friendship.user_id == User.id
    ).filter(
        Friendship.friend_id == user_id,
        Friendship.status == 'pending'
    ).all()
    
    # Get all users for adding friends
    all_users = User.query.filter(User.id != user_id).all()
    
    return render_template('dashboard.html', 
                         friends=friends, 
                         pending_requests=pending_requests,
                         all_users=all_users)

@friends_bp.route('/add_friend/<int:friend_id>', methods=['POST'])
def add_friend(friend_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    # Check if friendship already exists
    existing = Friendship.query.filter(
        ((Friendship.user_id == user_id) & (Friendship.friend_id == friend_id)) |
        ((Friendship.user_id == friend_id) & (Friendship.friend_id == user_id))
    ).first()
    
    if existing:
        return jsonify({'error': 'Request already exists'}), 400
    
    # Create friend request
    friendship = Friendship(user_id=user_id, friend_id=friend_id, status='pending')
    db.session.add(friendship)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Friend request sent!'})

@friends_bp.route('/accept_friend/<int:friendship_id>', methods=['POST'])
def accept_friend(friendship_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    friendship = Friendship.query.get(friendship_id)
    
    if friendship and friendship.friend_id == session['user_id']:
        friendship.status = 'accepted'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Friend request accepted!'})
    
    return jsonify({'error': 'Invalid request'}), 400
