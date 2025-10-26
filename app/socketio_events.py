from flask_socketio import emit, join_room, leave_room
from flask import session
from app import socketio, db
from app.models import Message, User

@socketio.on('connect')
def handle_connect():
    if 'user_id' in session:
        user_id = session['user_id']
        join_room(f'user_{user_id}')
        emit('status', {'msg': 'Connected to chat server'})

@socketio.on('send_message')
def handle_message(data):
    if 'user_id' not in session:
        return
    
    sender_id = session['user_id']
    receiver_id = data.get('receiver_id')
    content = data.get('message')
    
    # Save message to database
    message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.session.add(message)
    db.session.commit()
    
    sender = User.query.get(sender_id)
    
    # Emit to sender
    emit('receive_message', {
        'message_id': message.id,
        'sender': sender.username,
        'sender_id': sender_id,
        'content': content,
        'timestamp': message.timestamp.strftime('%H:%M')
    }, room=f'user_{sender_id}')
    
    # Emit to receiver
    emit('receive_message', {
        'message_id': message.id,
        'sender': sender.username,
        'sender_id': sender_id,
        'content': content,
        'timestamp': message.timestamp.strftime('%H:%M')
    }, room=f'user_{receiver_id}')

@socketio.on('disconnect')
def handle_disconnect():
    if 'user_id' in session:
        leave_room(f'user_{session["user_id"]}')
