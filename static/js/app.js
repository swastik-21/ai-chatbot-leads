// Frontend JavaScript for AI Chatbot Leads

let currentSessionId = null;
let messageCount = 0;
let leadsCount = 0;

// DOM elements
let messageInput, sendButton, chatMessages, loading;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    messageInput = document.getElementById('messageInput');
    sendButton = document.getElementById('sendButton');
    chatMessages = document.getElementById('chatMessages');
    loading = document.getElementById('loading');
    
    // Add event listeners
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }
    
    if (messageInput) {
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
});

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Disable input while processing
    sendButton.disabled = true;
    messageInput.disabled = true;
    if (loading) loading.style.display = 'block';
    
    // Add user message to chat
    addMessage(message, 'user');
    messageInput.value = '';
    messageCount++;
    
    try {
        const requestBody = {
            message: message
        };
        
        // Only include session_id if it exists
        if (currentSessionId) {
            requestBody.session_id = currentSessionId;
        }
        
        const response = await fetch('/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update session ID
        currentSessionId = data.session_id;
        
        // Add AI response
        addMessage(data.reply, 'assistant');
        
        // Check if lead was qualified
        if (data.lead_qualified) {
            leadsCount++;
            showLeadNotification(data.lead_data);
        }
        
    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, there was an error processing your message. Please try again.', 'assistant');
        showError('Failed to send message. Please try again.');
    } finally {
        // Re-enable input
        sendButton.disabled = false;
        messageInput.disabled = false;
        if (loading) loading.style.display = 'none';
    }
}

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    // Add avatar for assistant messages
    if (sender === 'assistant') {
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.textContent = 'AI';
        messageDiv.appendChild(avatarDiv);
    } else if (sender === 'user') {
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.textContent = 'You';
        messageDiv.appendChild(avatarDiv);
    }
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showLeadNotification(leadData) {
    const notification = document.createElement('div');
    notification.className = 'success';
    notification.innerHTML = `
        <strong>New Potential Client!</strong><br>
        Name: ${leadData.name || 'Unknown'}<br>
        Email: ${leadData.email || 'No email'}<br>
        Interest Score: ${(leadData.interest_score * 100).toFixed(1)}%
    `;
    
    chatMessages.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = message;
    
    chatMessages.appendChild(errorDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
