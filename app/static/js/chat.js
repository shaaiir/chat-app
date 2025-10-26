// chat.js - Client-side real-time messaging
const socket = io();

// Configuration
const CONFIG = {
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
    timeout: 20000
};

// DOM elements
const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

// Connection status
let isConnected = false;

// Socket event handlers
socket.on('connect', () => {
    console.log('✅ Connected to chat server');
    isConnected = true;
    updateConnectionStatus(true);
});

socket.on('disconnect', () => {
    console.log('❌ Disconnected from chat server');
    isConnected = false;
    updateConnectionStatus(false);
});

socket.on('connect_error', (error) => {
    console.error('Connection error:', error);
    showNotification('Connection error. Please refresh the page.', 'error');
});

socket.on('receive_message', (data) => {
    console.log('📨 Message received:', data);
    appendMessage(data);
    playNotificationSound();
});

socket.on('status', (data) => {
    console.log('Status:', data.msg);
});

// Send message function
function sendMessage() {
    if (!isConnected) {
        showNotification('Not connected to server', 'error');
        return;
    }

    const message = messageInput.value.trim();
    
    if (message === '') {
        return;
    }

    const receiverId = window.FRIEND_ID; // Set by template
    
    socket.emit('send_message', {
        receiver_id: receiverId,
        message: message
    });
    
    messageInput.value = '';
    messageInput.focus();
}

// Append message to chat
function appendMessage(data) {
    const messageDiv = document.createElement('div');
    const userId = window.USER_ID; // Set by template
    
    messageDiv.className = `message ${data.sender_id === userId ? 'sent' : 'received'}`;
    
    messageDiv.innerHTML = `
        <div class="message-bubble">
            <div class="message-content">${escapeHtml(data.content)}</div>
            <div class="message-time">${data.timestamp}</div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Scroll to bottom of messages
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Handle Enter key press
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Update connection status indicator
function updateConnectionStatus(connected) {
    const statusIndicator = document.getElementById('connectionStatus');
    if (statusIndicator) {
        statusIndicator.className = connected ? 'status-connected' : 'status-disconnected';
        statusIndicator.textContent = connected ? 'Connected' : 'Disconnected';
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Play notification sound
function playNotificationSound() {
    // Create a simple beep sound using Web Audio API
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800;
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.1);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (messageInput) {
        messageInput.addEventListener('keypress', handleKeyPress);
        messageInput.focus();
    }
    
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }
    
    // Scroll to bottom on page load
    scrollToBottom();
});

// Auto-reconnect on visibility change
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && !isConnected) {
        socket.connect();
    }
});
