document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const chatMessages = document.getElementById('chatMessages');
    let messageInput = document.getElementById('messageInput');
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
    
    // Import PCMAudioPlayer from audio_player.js
    let audioPlayer;
    import('/static/js/audio_player.js')
        .then(module => {
            const PCMAudioPlayer = module.default;
            audioPlayer = new PCMAudioPlayer(24000); // 24000 Hz sample rate
            console.log('PCMAudioPlayer loaded successfully');
        })
        .catch(error => {
            console.error('Failed to load PCMAudioPlayer:', error);
        });
    
    // Aliyun TTS WebSocket variables
    let ttsToken = null;
    let ttsAppKey = null;
    let ttsWebSocket = null;
    let isPlayingAudio = false;
    let audioQueue = [];
    let currentTaskId = null;
    let isSynthesisStarted = false;
    let processedMessages = new Set(); // Track messages that have already been processed for TTS
    
    // Initialize TTS
    initTTS();
    
    /**
     * 生成32位随机字符串
     */
    function generateUUID() {
        let d = new Date().getTime();
        let d2 = (performance && performance.now && (performance.now()*1000)) || 0;
        return 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            let r = Math.random() * 16;
            if(d > 0){
                r = (d + r)%16 | 0;
                d = Math.floor(d/16);
            } else {
                r = (d2 + r)%16 | 0;
                d2 = Math.floor(d2/16);
            }
            return (c == 'x' ? r :(r&0x3|0x8)).toString(16);
        });
    }
    
    /**
     * 生成 WebSocket 消息的头部信息
     */
    function getHeader(name) {
        return {
            message_id: generateUUID(),
            task_id: currentTaskId,
            namespace: 'FlowingSpeechSynthesizer',
            name: name,
            appkey: ttsAppKey
        };
    }
    
    // Initialize TTS functionality by getting token
    async function initTTS() {
        try {
            console.log('===== TTS API Initialization =====');
            console.log('Requesting new TTS token from server...');
            // Get TTS token from server
            const response = await fetch('/get-tts-token', {
                method: 'GET'
            });
            
            const data = await response.json();
            if (data.success && data.token) {
                ttsToken = data.token;
                ttsAppKey = data.appkey || "LRPVa0X9S1KqjOK3"; // Use provided appkey or fallback
                console.log(`TTS Token obtained successfully: ${ttsToken.substring(0, 8)}...`);
                console.log(`TTS AppKey: ${ttsAppKey}`);
                console.log('===================================');
                return true;
            } else {
                console.error('===== TTS API Initialization Error =====');
                console.error('Failed to get TTS token:', data.message);
                if (data.response) {
                    console.error('Server response:', data.response);
                }
                console.error('=======================================');
                return false;
            }
        } catch (error) {
            console.error('===== TTS API Initialization Error =====');
            console.error('Error initializing TTS:', error);
            console.error('=======================================');
            return false;
        }
    }
    
    // Function to play text using TTS
    function playTTS(text, messageId) {
        // If this message has already been processed, skip it
        if (processedMessages.has(messageId)) {
            console.log('Message already processed for TTS, skipping:', messageId);
            return;
        }
        
        // Mark this message as processed
        processedMessages.add(messageId);
        
        if (!ttsToken) {
            console.error('TTS not initialized properly');
            // Try to re-initialize TTS
            initTTS().then(() => {
                if (ttsToken && audioPlayer) {
                    // If initialization was successful, add to queue
                    audioQueue.push({text, messageId});
                    if (!isPlayingAudio) {
                        processAudioQueue();
                    }
                }
            });
            return;
        }
        
        // Add to queue with messageId
        audioQueue.push({text, messageId});
        
        // If not currently playing, start playing
        if (!isPlayingAudio) {
            processAudioQueue();
        }
    }
    
    // Process and play audio queue
    function processAudioQueue() {
        if (audioQueue.length === 0) {
            isPlayingAudio = false;
            return;
        }
        
        isPlayingAudio = true;
        const {text, messageId} = audioQueue.shift();
        
        // Connect the audio player
        if (audioPlayer) {
            audioPlayer.connect();
            //setTimeout(5000);
            audioPlayer.stop(); // Stop any current playback
        } else {
            console.error('Audio player not available');
            isPlayingAudio = false;
            return;
        }
        
        startSynthesis(text);
    }
    
    // Start a new synthesis session
    function startSynthesis(text) {
        // Clean text for better handling
        const cleanedText = text.replace(/[\r\n]+/g, ' ').replace(/\s+/g, ' ').trim();
        
        // Close any existing connection
        if (ttsWebSocket && ttsWebSocket.readyState === WebSocket.OPEN) {
            console.log('Closing existing WebSocket connection');
            ttsWebSocket.close();
        }
        
        // Create a new connection
        const url = `wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1?token=${ttsToken}`;
        console.log("======= TTS API Connection Info =======");
        console.log("Connecting to TTS API URL:", url);
        console.log("AppKey:", ttsAppKey);
        console.log("Text to synthesize:", cleanedText.substring(0, 50) + (cleanedText.length > 50 ? '...' : ''));
        console.log("Original text length:", text.length, "characters");
        console.log("Cleaned text length:", cleanedText.length, "characters");
        console.log("=======================================");
        
        ttsWebSocket = new WebSocket(url);
        ttsWebSocket.binaryType = "arraybuffer";
        
        // Generate a new task ID for this session
        currentTaskId = generateUUID();
        console.log('Generated taskId:', currentTaskId);
        isSynthesisStarted = false;
        
        ttsWebSocket.onopen = function() {
            console.log('TTS WebSocket connected, sending StartSynthesis');
            
            const params = {
                header: getHeader('StartSynthesis'),
                payload: {
                    voice: 'zhixiaoxia',
                    format: 'wav',
                    sample_rate: 24000,
                    volume: 100,
                    speech_rate: 0,
                    pitch_rate: 0,
                    enable_subtitle: false,
                    platform: 'javascript'
                }
            };
            
            console.log('===== TTS API Request: StartSynthesis =====');
            console.log(JSON.stringify(params, null, 2));
            console.log('===========================================');
            
            ttsWebSocket.send(JSON.stringify(params));
        };
        
        ttsWebSocket.onmessage = function(event) {
            const data = event.data;
            
            // Handle binary audio data
            if (data instanceof ArrayBuffer) {
                console.log(`Received binary audio data: ${data.byteLength} bytes`);
                if (audioPlayer) {
                    audioPlayer.pushPCM(data);
                }
            } 
            // Handle text messages
            else {
                try {
                    const body = JSON.parse(data);
                    
                    console.log('===== TTS API Response =====');
                    console.log('Header:', body.header);
                    if (body.payload) {
                        console.log('Payload:', body.payload);
                    }
                    console.log('=============================');
                    
                    // Handle SynthesisStarted
                    if (body.header.name === 'SynthesisStarted' && body.header.status === 20000000) {
                        console.log('TTS synthesis started successfully, sending text to synthesize');
                        isSynthesisStarted = true;
                        // Send the text to synthesize - already cleaned in startSynthesis
                        sendRunSynthesis(text);
                    }
                    
                    // Handle SynthesisCompleted
                    if (body.header.name === 'SynthesisCompleted' && body.header.status === 20000000) {
                        console.log('TTS synthesis completed successfully');
                        
                        // Close the WebSocket
                        if (ttsWebSocket) {
                            ttsWebSocket.close();
                            ttsWebSocket = null;
                        }
                        
                        // Reset state and process next in queue
                        isSynthesisStarted = false;
                        
                        // Wait for audio to finish playing before processing next item
                        setTimeout(() => {
                            isPlayingAudio = false;
                            processAudioQueue();
                        }, 1000);
                    }
                    
                    // Handle any errors
                    if (body.header.status && body.header.status !== 20000000) {
                        console.error('TTS error:', body);
                        
                        // Clean up and move on to next item
                        if (ttsWebSocket) {
                            ttsWebSocket.close();
                            ttsWebSocket = null;
                        }
                        
                        // Reset state and process next in queue
                        isSynthesisStarted = false;
                        setTimeout(() => {
                            isPlayingAudio = false;
                            processAudioQueue();
                        }, 500);
                    }
                } catch (error) {
                    console.error('Error parsing TTS message:', error);
                }
            }
        };
        
        ttsWebSocket.onerror = function(error) {
            console.error('TTS WebSocket error:', error);
            
            // Clean up and try again
            if (ttsWebSocket) {
                ttsWebSocket.close();
                ttsWebSocket = null;
            }
            
            // Try to refresh token and retry
            initTTS().then(() => {
                // Re-add current text to the queue with a new ID (since the original failed)
                if (text) {
                    // Use a temporary ID for retry purposes
                    const retryId = generateUUID();
                    audioQueue.unshift({text, messageId: retryId});
                }
                
                setTimeout(() => {
                    isPlayingAudio = false;
                    processAudioQueue();
                }, 2000);
            });
        };
        
        ttsWebSocket.onclose = function(event) {
            console.log(`TTS WebSocket closed with code: ${event.code}, reason: ${event.reason}`);
        };
    }
    
    // Send RunSynthesis command to synthesize text
    function sendRunSynthesis(text) {
        if (ttsWebSocket && isSynthesisStarted) {
            // Remove all newlines/carriage returns and normalize whitespace
            const cleanedText = text.replace(/[\r\n]+/g, ' ').replace(/\s+/g, ' ').trim();
            
            console.log('Sending RunSynthesis with text:', cleanedText);
            
            const params = {
                header: getHeader('RunSynthesis'),
                payload: {
                    text: cleanedText
                }
            };
            
            console.log('===== TTS API Request: RunSynthesis =====');
            console.log(JSON.stringify(params, null, 2));
            console.log('Original text length:', text.length, 'characters');
            console.log('Cleaned text length:', cleanedText.length, 'characters');
            console.log('===========================================');
            
            ttsWebSocket.send(JSON.stringify(params));
            
            // Immediately send StopSynthesis to indicate end of text stream
            setTimeout(() => {
                sendStopSynthesis();
            }, 100); // Small delay to ensure RunSynthesis is processed first
        } else {
            console.error('Cannot send RunSynthesis: WebSocket not ready or synthesis not started');
        }
    }
    
    // Send StopSynthesis command
    function sendStopSynthesis() {
        if (ttsWebSocket && isSynthesisStarted) {
            console.log('Sending StopSynthesis command to indicate end of text stream');
            
            const params = {
                header: getHeader('StopSynthesis')
            };
            
            console.log('===== TTS API Request: StopSynthesis =====');
            console.log(JSON.stringify(params, null, 2));
            console.log('============================================');
            
            ttsWebSocket.send(JSON.stringify(params));
            
            // Log completion
            console.log('Text stream ended, waiting for synthesis to complete...');
        } else {
            console.warn('Cannot send StopSynthesis: WebSocket not ready or synthesis not started');
        }
    }
    
    // Add message to chat
    function addMessage(message, sender) {
        const messageId = generateUUID(); // Generate a unique ID for this message
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender === 'user' ? 'user-message' : 'bot-message'}`;
        messageDiv.textContent = message;
        messageDiv.dataset.messageId = messageId; // Store the message ID in the DOM element
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 10);
        
        // Play TTS for bot messages
        if (sender === 'bot') {
            playTTS(message, messageId);
        }
    }
    
    // Configure the message input to support multi-line text
    if (messageInput) {
        // Check if the input is a textarea
        if (messageInput.tagName.toLowerCase() === 'textarea') {
            // Already a textarea, ensure it has auto-height behavior
            messageInput.style.resize = 'none'; // Disable manual resize
            messageInput.style.overflowY = 'hidden'; // Hide vertical scrollbar
            
            // Function to adjust height based on content
            const adjustHeight = () => {
                messageInput.style.height = 'auto';
                messageInput.style.height = messageInput.scrollHeight + 'px';
                
                // Ensure full width
                messageInput.style.width = '100%';
                messageInput.style.boxSizing = 'border-box';
                
                // Force recalculation if needed
                const parentWidth = messageInput.parentNode.clientWidth;
                if (parentWidth > 0) {
                    messageInput.style.maxWidth = (parentWidth - 10) + 'px';
                }
            };
            
            // Add event listeners for auto-height
            messageInput.addEventListener('input', adjustHeight);
            messageInput.addEventListener('change', adjustHeight);
            
            // Initial height adjustment
            setTimeout(adjustHeight, 0);
        } else {
            // If it's an input element, replace it with a textarea
            const parent = messageInput.parentNode;
            const newTextarea = document.createElement('textarea');
            
            // Copy attributes
            Array.from(messageInput.attributes).forEach(attr => {
                newTextarea.setAttribute(attr.name, attr.value);
            });
            
            // Set additional styles for textarea
            newTextarea.style.resize = 'none';
            newTextarea.style.overflowY = 'hidden';
            newTextarea.style.height = messageInput.offsetHeight + 'px';
            newTextarea.style.width = '100%'; // Make the textarea take full width
            newTextarea.style.boxSizing = 'border-box'; // Include padding in width calculation
            newTextarea.style.padding = '8px 12px'; // Add some padding
            newTextarea.style.borderRadius = '4px'; // Round corners
            newTextarea.rows = 1;
            
            // Replace input with textarea
            parent.replaceChild(newTextarea, messageInput);
            messageInput = newTextarea;
            
            // Add auto-resize capability
            messageInput.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = this.scrollHeight + 'px';
                
                // Force recalculation of parent container if needed
                const parentWidth = this.parentNode.clientWidth;
                if (parentWidth > 0) {
                    this.style.maxWidth = (parentWidth - 10) + 'px'; // Small buffer for margins
                }
            });
            
            // Handle Enter key for sending message
            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
        }
    }
    
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
                        messageDiv.dataset.messageId = generateUUID(); // Add ID but don't trigger TTS for history
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
        
        // Reset textarea height to default
        messageInput.style.height = 'auto';
        
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
    
    // Voice input implementation
    let mediaRecorder = null;
    let audioContext = null;
    let audioProcessor = null;
    let audioStream = null;
    let isRecording = false;
    let ws = null;
    // Track voice recognition state
    let priorInputText = '';
    let currentPartialText = '';
    let voiceReconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 3;

    // Constants for Baidu ASR API
    const APPID = 118057093;
    const API_KEY = "8GKydTmb9V6iVlyMGk3BEmym";
    const DEV_PID = 17372; 
    const CUID = "cuid-" + userId;
    const FORMAT = "pcm";
    const SAMPLE_RATE = 16000;

    // Start/Stop voice recording
    if (startVoiceBtn) {
        startVoiceBtn.addEventListener('click', async function() {
            if (!isRecording) {
                try {
                    // Request microphone access
                    audioStream = await navigator.mediaDevices.getUserMedia({ 
                        audio: {
                            echoCancellation: true,
                            noiseSuppression: true,
                            autoGainControl: true
                        } 
                    });
                    
                    // Reset reconnect attempts when starting a new recording
                    voiceReconnectAttempts = 0;
                    
                    // Initialize WebSocket connection
                    initializeVoiceRecognition();
                    
                    // Store the current input text before we start appending voice results
                    priorInputText = messageInput.value;
                    currentPartialText = '';
                    
                    isRecording = true;
                    startVoiceBtn.innerHTML = '<i class="fas fa-stop-circle"></i>';
                    startVoiceBtn.classList.add('recording');
                    
                } catch (error) {
                    console.error('Error starting voice input:', error);
                    alert('Failed to start voice input. Please check your microphone permissions.');
                }
            } else {
                // Stop recording and clean up
                stopVoiceRecording();
            }
        });
    }
    
    // Initialize WebSocket connection for voice recognition
    function initializeVoiceRecognition() {
        try {
            // Create WebSocket connection
            const sn = crypto.randomUUID();
            ws = new WebSocket(`wss://vop.baidu.com/realtime_asr?sn=${sn}`);
            
            // Initialize audio context
            audioContext = new (window.AudioContext || window.webkitAudioContext)({
                sampleRate: SAMPLE_RATE
            });
            
            // Create source from the microphone stream
            const source = audioContext.createMediaStreamSource(audioStream);
            
            // Create script processor for audio processing
            audioProcessor = audioContext.createScriptProcessor(4096, 1, 1);
            
            // Connect the audio processing pipeline
            source.connect(audioProcessor);
            audioProcessor.connect(audioContext.destination);
            
            // Set up WebSocket handlers
            ws.onopen = function() {
                console.log('WebSocket connected');
                // Send start parameters
                const startData = {
                    "type": "START",
                    "data": {
                        "appid": APPID,
                        "appkey": API_KEY,
                        "dev_pid": DEV_PID,
                        "cuid": CUID,
                        "format": FORMAT,
                        "sample": SAMPLE_RATE
                    }
                };
                ws.send(JSON.stringify(startData));
            };
            
            ws.onmessage = function(event) {
                try {
                    const result = JSON.parse(event.data);
                    
                    if (result.type === "MID_TEXT") {
                        // Real-time recognition result
                        currentPartialText = result.result || '';
                        // Update input field with original text + current recognition
                        messageInput.value = priorInputText + currentPartialText;
                    } 
                    else if (result.type === "FIN_TEXT") {
                        // Final recognition result
                        const finalText = result.result || '';
                        
                        // Handle error message
                        if (result.err_msg && result.err_msg.includes("find effective speech")) {
                            console.log("ASR server didn't find effective speech, error:", result.err_msg);
                            
                            // Don't add error messages to the input field
                            if (finalText === '') {
                                // Try to reconnect if we haven't exceeded max attempts
                                if (isRecording && voiceReconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                                    voiceReconnectAttempts++;
                                    console.log(`Reconnecting ASR (attempt ${voiceReconnectAttempts})...`);
                                    
                                    // Clean up existing connection
                                    cleanupVoiceConnection();
                                    
                                    // Re-initialize after a short delay
                                    setTimeout(() => {
                                        if (isRecording) {
                                            initializeVoiceRecognition();
                                        }
                                    }, 500);
                                    
                                    return;
                                }
                            }
                        } else {
                            // Reset reconnection counter on successful speech recognition
                            voiceReconnectAttempts = 0;
                        }
                        
                        // Replace the partial text with the final result (only if it's not an error)
                        if (finalText && !finalText.includes("[info:-4]")) {
                            messageInput.value = priorInputText + finalText;
                            
                            // Update priorInputText to include this final result for next voice segment
                            priorInputText = messageInput.value;
                            currentPartialText = '';
                        }
                    }
                } catch (e) {
                    console.error('Error parsing message:', e);
                }
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                
                // Try to reconnect on error if still recording
                if (isRecording && voiceReconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                    voiceReconnectAttempts++;
                    console.log(`WebSocket error occurred. Reconnecting (attempt ${voiceReconnectAttempts})...`);
                    
                    // Clean up existing connection
                    cleanupVoiceConnection();
                    
                    // Re-initialize after a short delay
                    setTimeout(() => {
                        if (isRecording) {
                            initializeVoiceRecognition();
                        }
                    }, 1000);
                } else if (voiceReconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
                    alert('Voice recognition encountered too many errors. Please try again later.');
                    stopVoiceRecording();
                }
            };
            
            ws.onclose = function() {
                console.log('WebSocket closed');
            };
            
            // Process and send audio data
            audioProcessor.onaudioprocess = function(e) {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    // Get audio data from the input channel
                    const inputData = e.inputBuffer.getChannelData(0);
                    
                    // Convert Float32Array to Int16Array for PCM
                    const pcmData = new Int16Array(inputData.length);
                    for (let i = 0; i < inputData.length; i++) {
                        // Convert float audio data (-1.0 to 1.0) to int16 (-32768 to 32767)
                        pcmData[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7FFF;
                    }
                    
                    // Send the PCM data to the WebSocket
                    ws.send(pcmData.buffer);
                }
            };
        } catch (error) {
            console.error('Error initializing voice recognition:', error);
            
            if (isRecording) {
                stopVoiceRecording();
                alert('Failed to initialize voice recognition. Please try again.');
            }
        }
    }
    
    // Clean up WebSocket and audio processing resources
    function cleanupVoiceConnection() {
        if (ws) {
            try {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.close();
                }
            } catch (e) {
                console.error('Error closing WebSocket:', e);
            }
            ws = null;
        }
        
        if (audioProcessor) {
            try {
                audioProcessor.disconnect();
            } catch (e) {
                console.error('Error disconnecting audio processor:', e);
            }
            audioProcessor = null;
        }
        
        if (audioContext) {
            try {
                audioContext.close();
            } catch (e) {
                console.error('Error closing audio context:', e);
            }
            audioContext = null;
        }
    }
    
    // Function to stop voice recording and clean up resources
    function stopVoiceRecording() {
        // Send end frame if WebSocket is open
        if (ws && ws.readyState === WebSocket.OPEN) {
            try {
                const endData = { "type": "END" };
                ws.send(JSON.stringify(endData));
                
                // Update the prior text to include whatever is currently in the input box
                priorInputText = messageInput.value;
                currentPartialText = '';
            } catch (e) {
                console.error('Error sending END message:', e);
            }
        }
        
        // Clean up all resources
        cleanupVoiceConnection();
        
        // Stop all audio tracks
        if (audioStream) {
            try {
                audioStream.getTracks().forEach(track => track.stop());
            } catch (e) {
                console.error('Error stopping audio tracks:', e);
            }
            audioStream = null;
        }
        
        // Reset state
        isRecording = false;
        voiceReconnectAttempts = 0;
        startVoiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        startVoiceBtn.classList.remove('recording');
    }

    // Clean up on page unload
    window.addEventListener('beforeunload', function() {
        stopVoiceRecording();
    });
});
