// Frontend JavaScript for AI Chatbot Leads

let currentSessionId = null;
let messageCount = 0;
let leadsCount = 0;

// DOM elements
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');
const loading = document.getElementById('loading');
const sessionIdSpan = document.getElementById('sessionId');
const messageCountSpan = document.getElementById('messageCount');
const leadsCountSpan = document.getElementById('leadsCount');
const leadsList = document.getElementById('leadsList');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    loadLeads();
});

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Disable input while processing
    sendButton.disabled = true;
    messageInput.disabled = true;
    loading.style.display = 'block';
    
    // Add user message to chat
    addMessage(message, 'user');
    messageInput.value = '';
    messageCount++;
    updateStatus();
    
    try {
        const response = await fetch('/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                message: message
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update session ID
        currentSessionId = data.session_id;
        sessionIdSpan.textContent = currentSessionId.substring(0, 8) + '...';
        
        // Add AI response
        addMessage(data.reply, 'assistant');
        
        // Check if lead was qualified
        if (data.lead_qualified) {
            leadsCount++;
            updateStatus();
            showLeadNotification(data.lead_data);
            loadLeads(); // Refresh leads list
        }
        
    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, there was an error processing your message. Please try again.', 'assistant');
        showError('Failed to send message. Please try again.');
    } finally {
        // Re-enable input
        sendButton.disabled = false;
        messageInput.disabled = false;
        loading.style.display = 'none';
    }
}

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateStatus() {
    messageCountSpan.textContent = messageCount;
    leadsCountSpan.textContent = leadsCount;
}

async function loadLeads() {
    try {
        const response = await fetch('/api/leads/');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const leads = await response.json();
        displayLeads(leads);
        
    } catch (error) {
        console.error('Error loading leads:', error);
    }
}

function displayLeads(leads) {
    if (leads.length === 0) {
        leadsList.innerHTML = '<p style="color: #6b7280; text-align: center;">No leads yet</p>';
        return;
    }
    
    leadsList.innerHTML = leads.map(lead => `
        <div class="lead-item">
            <div class="lead-name">${lead.name || 'Unknown'}</div>
            <div class="lead-email">${lead.email || 'No email'}</div>
            <div class="lead-score">Interest: ${(lead.interest_score * 100).toFixed(1)}%</div>
        </div>
    `).join('');
}

function showLeadNotification(leadData) {
    const notification = document.createElement('div');
    notification.className = 'success';
    notification.innerHTML = `
        <strong>New Lead Qualified!</strong><br>
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

function getCsrfToken() {
    // Get CSRF token from cookies
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
}
