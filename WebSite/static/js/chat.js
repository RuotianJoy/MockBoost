document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const sendMessageBtn = document.getElementById('sendMessage');
    const startInterviewBtn = document.getElementById('startInterviewBtn');
    const clearChatBtn = document.getElementById('clearChatBtn');
    const jobInput = document.getElementById('jobInput');
    const userAvatarBtn = document.getElementById('userAvatarBtn');
    const userProfileSidebar = document.getElementById('userProfileSidebar');
    const closeProfileBtn = document.getElementById('closeProfileBtn');
    const overlay = document.getElementById('overlay');
    const logoutBtn = document.getElementById('logoutBtn');
    const historyDialog = document.getElementById('historyDialog');
    const closeHistoryBtn = document.getElementById('closeHistoryBtn');
    const startVoiceBtn = document.getElementById('startVoice');
    const backToHomeBtn = document.getElementById('backToHomeFromConversation');
    
    // Get user ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get('user_id');
    
    if (!userId) {
        // Redirect to auth page if no user ID
        window.location.href = '/auth';
        return;
    }
    
    // Variables to store conversation state
    let conversationId = null;
    let isInterviewStarted = false;
    
    // Check if user is authenticated
    fetch('/verify-auth', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: userId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.authenticated) {
            // Redirect to auth page if not authenticated
            window.location.href = '/auth';
        } else {
            // Load user profile
            loadUserProfile();
            // Load user history
            loadUserHistory();
        }
    })
    .catch(error => {
        console.error('Authentication verification error:', error);
        // Redirect to auth page on error
        window.location.href = '/auth';
    });
    
    // Load user profile
    function loadUserProfile() {
        fetch('/user-profile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const userInfo = data.user_info;
                document.getElementById('profileUsername').textContent = userInfo.Name || 'N/A';
                document.getElementById('profileJob').textContent = userInfo.Job || 'N/A';
                document.getElementById('profileMajor').textContent = userInfo.Major || 'N/A';
                document.getElementById('profileEmail').textContent = userInfo.Email || 'N/A';
                
                // Pre-fill job input if available
                if (userInfo.Job) {
                    jobInput.value = userInfo.Job;
                }
                
                // Store user major for later use
                window.userMajor = userInfo.Major || '';
            } else {
                console.error('Failed to load user profile:', data.message);
            }
        })
        .catch(error => {
            console.error('Error loading user profile:', error);
        });
    }
    
    // Load user history
    function loadUserHistory() {
        fetch('/user-history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const historyList = document.getElementById('historyList');
                historyList.innerHTML = '';
                
                if (data.history && data.history.length > 0) {
                    data.history.forEach(item => {
                        const historyItem = document.createElement('div');
                        historyItem.className = 'history-item';
                        historyItem.innerHTML = `
                            <div class="history-item-content">
                                <div class="history-item-title">${item.mode || 'Interview'}</div>
                                <div class="history-item-id">${item.dialog_id.substring(0, 8)}...</div>
                            </div>
                        `;
                        
                        // Add click event to view history
                        historyItem.addEventListener('click', function() {
                            console.log('History item clicked:', item.dialog_id);
                            viewHistoryDetails(item.dialog_id, item.mode);
                        });
                        
                        historyList.appendChild(historyItem);
                    });
                } else {
                    historyList.innerHTML = '<div class="no-history">No history found</div>';
                }
            } else {
                console.error('Failed to load user history:', data.message);
                document.getElementById('historyList').innerHTML = '<div class="no-history">Failed to load history</div>';
            }
        })
        .catch(error => {
            console.error('Error loading user history:', error);
            document.getElementById('historyList').innerHTML = '<div class="no-history">Error loading history</div>';
        });
    }
    
    // View history details
    function viewHistoryDetails(dialogId, mode) {
        // Set dialog title and info
        document.getElementById('historyDialogTitle').textContent = mode || 'Interview';
        document.getElementById('historyDialogId').textContent = dialogId;
        document.getElementById('historyDialogMode').textContent = mode || 'N/A';
        
        // Clear previous content
        document.getElementById('historyChatContent').innerHTML = '';
        
        // Show history dialog
        historyDialog.style.display = 'flex';
        historyDialog.classList.add('active');
        
        // Load chat history
        fetch('/chat-history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                dialog_id: dialogId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const historyChatContent = document.getElementById('historyChatContent');
                historyChatContent.innerHTML = '';
                
                if (data.messages && data.messages.length > 0) {
                    // Skip system message
                    const messages = data.messages.filter(msg => msg.role !== 'system');
                    
                    messages.forEach(msg => {
                        const messageDiv = document.createElement('div');
                        messageDiv.className = `message ${msg.role === 'user' ? 'user-message' : 'bot-message'}`;
                        messageDiv.textContent = msg.content;
                        historyChatContent.appendChild(messageDiv);
                    });
                } else {
                    historyChatContent.innerHTML = '<div class="no-history">No messages found</div>';
                }
            } else {
                console.error('Failed to load chat history:', data.message);
                document.getElementById('historyChatContent').innerHTML = '<div class="no-history">Failed to load chat history</div>';
            }
        })
        .catch(error => {
            console.error('Error loading chat history:', error);
            document.getElementById('historyChatContent').innerHTML = '<div class="no-history">Error loading chat history</div>';
        });
    }
    
    // Send message function
    function sendMessage() {
        const message = messageInput.value.trim();
        
        if (!message) {
            return;
        }
        
        if (!isInterviewStarted) {
            alert('Please start the interview first');
            return;
        }
        
        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input
        messageInput.value = '';
        
        // Create an AbortController to handle timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
        
        // Send message to server
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                user_id: userId,
                conversation_id: conversationId,
                job: jobInput.value,
                major: window.userMajor || ''
            }),
            signal: controller.signal
        })
        .then(response => {
            clearTimeout(timeoutId);
            return response.json();
        })
        .then(data => {
            // Check if the response contains an error message
            if (data.response && data.response.includes("错误") || data.response === "") {
                // Use fallback response
                addMessage(getFallbackQuestion(jobInput.value.trim()), 'bot');
            } else {
                // Add bot response
                addMessage(data.response, 'bot');
            }
            
            // Update conversation ID
            conversationId = data.conversation_id;
        })
        .catch(error => {
            clearTimeout(timeoutId);
            console.error('Chat error:', error);
            
            // Check if it's a timeout error
            if (error.name === 'AbortError') {
                addMessage('The server is taking too long to respond. Please try again later or check your internet connection.', 'bot');
            } else {
                // Use fallback response for other errors
                addMessage(getFallbackQuestion(jobInput.value.trim()), 'bot');
            }
        });
    }
    
    // Add message to chat
    function addMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender === 'user' ? 'user-message' : 'bot-message'}`;
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 10);
    }
    
    // Start interview
    function startInterview() {
        console.log("Starting interview...");
        const job = jobInput.value.trim();
        
        if (!job) {
            alert('Please enter your intended job');
            return;
        }
        
        console.log("Job:", job);
        
        // Clear previous messages except welcome message
        chatMessages.innerHTML = '<div class="message bot-message">Welcome to Interview!</div>';
        
        // Reset conversation ID to start a new conversation
        conversationId = null;
        
        // Set interview started flag
        isInterviewStarted = true;
        
        // Change button text to "New"
        startInterviewBtn.innerHTML = '<i class="fas fa-play-circle"></i> New';
        
        // Create user introduction message
        const userIntroMessage = `Hello, I'm ${userId}${window.userMajor ? ', my major is ' + window.userMajor : ''} and I'm looking to interview for a career in ${job}.`;
        
        // Add user message to chat immediately
        addMessage(userIntroMessage, 'user');
        
        console.log("Sending request to /chat endpoint...");
        
        // Create an AbortController to handle timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
        
        // Send system message to start interview
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: userIntroMessage,
                user_id: userId,
                conversation_id: null,
                job: job,
                major: window.userMajor || '',
                is_system_message: true
            }),
            signal: controller.signal
        })
        .then(response => {
            console.log("Response received:", response.status);
            clearTimeout(timeoutId);
            return response.json();
        })
        .then(data => {
            console.log("Data received:", data);
            
            // Check if the response contains an error message
            if (data.response && data.response.includes("错误") || data.response === "") {
                // Use fallback response
                addMessage(getFallbackIntroduction(job), 'bot');
            } else {
                // Add bot response
                addMessage(data.response, 'bot');
            }
            
            // Update conversation ID
            conversationId = data.conversation_id;
        })
        .catch(error => {
            clearTimeout(timeoutId);
            console.error('Start interview error:', error);
            
            // Check if it's a timeout error
            if (error.name === 'AbortError') {
                addMessage('The server is taking too long to respond. Please try again later or check your internet connection.', 'bot');
            } else {
                // Use fallback response for other errors
                addMessage(getFallbackIntroduction(job), 'bot');
            }
        });
    }
    
    // Fallback introduction for when the API is not available
    function getFallbackIntroduction(job) {
        return `Hello! I'm your interviewer for the ${job} position. Thank you for joining us today. 
        
I'd like to start by asking you about your background and experience in this field. Could you tell me about your relevant experience and why you're interested in this position?`;
    }
    
    // Fallback question for when the API is not available
    function getFallbackQuestion(job) {
        const questions = [
            `Could you describe a challenging project you worked on as a ${job} and how you overcame the obstacles?`,
            `What specific skills do you think are most important for a ${job} role, and how have you developed these skills?`,
            `How do you stay updated with the latest trends and developments in the ${job} field?`,
            `Can you walk me through your problem-solving approach when faced with a complex issue?`,
            `How do you handle feedback and criticism in your work?`
        ];
        
        return questions[Math.floor(Math.random() * questions.length)];
    }
    
    // Clear chat
    function clearChat() {
        // Confirm before clearing
        if (!confirm('Are you sure you want to clear the chat and start a new interview?')) {
            return;
        }
        
        // Reset interview started flag
        isInterviewStarted = false;
        
        // Reset button text to "Start"
        startInterviewBtn.innerHTML = '<i class="fas fa-play-circle"></i> Start';
        
        // Clear chat messages except welcome message
        chatMessages.innerHTML = '<div class="message bot-message">Welcome to Interview!</div>';
        
        // Send clear chat request to server
        fetch('/clear-chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update conversation ID
                conversationId = data.conversation_id;
                console.log('Chat cleared successfully');
            } else {
                console.error('Failed to clear chat:', data.message);
            }
        })
        .catch(error => {
            console.error('Clear chat error:', error);
        });
    }
    
    // Event listeners
    if (sendMessageBtn) {
        sendMessageBtn.addEventListener('click', sendMessage);
    }
    
    if (messageInput) {
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    if (startInterviewBtn) {
        startInterviewBtn.addEventListener('click', startInterview);
    }
    
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', clearChat);
    }
    
    if (userAvatarBtn) {
        userAvatarBtn.addEventListener('click', function() {
            userProfileSidebar.classList.add('active');
            overlay.style.display = 'block';
        });
    }
    
    if (closeProfileBtn) {
        closeProfileBtn.addEventListener('click', function() {
            userProfileSidebar.classList.remove('active');
            overlay.style.display = 'none';
        });
    }
    
    if (overlay) {
        overlay.addEventListener('click', function() {
            userProfileSidebar.classList.remove('active');
            overlay.style.display = 'none';
            
            if (historyDialog.style.display === 'flex') {
                historyDialog.style.display = 'none';
                historyDialog.classList.remove('active');
            }
        });
    }
    
    if (closeHistoryBtn) {
        closeHistoryBtn.addEventListener('click', function() {
            historyDialog.style.display = 'none';
            historyDialog.classList.remove('active');
        });
    }
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            // Redirect to home page
            window.location.href = '/';
        });
    }
    
    // Back to Home button event listener
    if (backToHomeBtn) {
        backToHomeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = '/';
        });
    }
    
    // Voice input (placeholder - actual implementation would require additional setup)
    if (startVoiceBtn) {
        startVoiceBtn.addEventListener('click', function() {
            alert('Voice input feature is not implemented in this version.');
        });
    }
}); 