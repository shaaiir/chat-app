from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import User
from app import db

auth_bp = Blueprint('auth', __name__)

# ADD THIS ROOT ROUTE - FIX FOR YOUR 404 ERROR
@auth_bp.route('/')
def home():
    """Root route - redirect based on login status"""
    if 'user_id' in session:
        return redirect(url_for('friends.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new user (plain text password - vulnerable)
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('friends.dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login'))

# ADD PROFILE ROUTE (needed for navigation)
@auth_bp.route('/profile')
def profile():
    """Display user profile"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    
    if not user:
        return redirect(url_for('auth.login'))
    
    from app.models import Message, Friendship
    from sqlalchemy import func
    
    # Get statistics
    friends_count = Friendship.query.filter(
        ((Friendship.user_id == user.id) | (Friendship.friend_id == user.id)),
        Friendship.status == 'accepted'
    ).count()
    
    messages_sent = Message.query.filter_by(sender_id=user.id).count()
    messages_received = Message.query.filter_by(receiver_id=user.id).count()
    
    total_conversations = 0
    
    # Get recent messages
    recent_messages = []
    
    return render_template('profile.html',
                         user=user,
                         friends_count=friends_count,
                         messages_sent=messages_sent,
                         messages_received=messages_received,
                         total_conversations=total_conversations,
                         recent_messages=recent_messages)
