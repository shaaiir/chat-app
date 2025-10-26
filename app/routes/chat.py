from flask import Blueprint, render_template, session, redirect, url_for
from app.models import User, Message, Friendship
from app import db

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat/<int:friend_id>')
def chat(friend_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    friend = User.query.get(friend_id)
    
    if not friend:
        return "Friend not found", 404
    
    # Check if they are friends
    friendship = Friendship.query.filter(
        ((Friendship.user_id == user_id) & (Friendship.friend_id == friend_id)) |
        ((Friendship.user_id == friend_id) & (Friendship.friend_id == user_id)),
        Friendship.status == 'accepted'
    ).first()
    
    if not friendship:
        return "Not friends", 403
    
    # Get chat history
    messages = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == friend_id)) |
        ((Message.sender_id == friend_id) & (Message.receiver_id == user_id))
    ).order_by(Message.timestamp.asc()).all()
    
    return render_template('chat.html', friend=friend, messages=messages)
