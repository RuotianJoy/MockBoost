document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const loginBox = document.getElementById('loginBox');
    const registerBox = document.getElementById('registerBox');
    const switchToRegister = document.getElementById('switchToRegister');
    const switchToLogin = document.getElementById('switchToLogin');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const sendVerificationBtn = document.getElementById('sendVerificationBtn');
    
    // Fix icon positioning in input groups
    const inputGroups = document.querySelectorAll('.input-group');
    inputGroups.forEach(group => {
        const icon = group.querySelector('i');
        const input = group.querySelector('input');
        
        if (icon && input) {
            // Ensure icon is before input for proper CSS positioning
            if (icon.nextElementSibling !== input) {
                group.insertBefore(icon, input);
            }
        }
    });
    
    // Enhance input groups - add focus effects
    const inputs = document.querySelectorAll('.input-group input');
    inputs.forEach(input => {
        // Add focus event to highlight icon
        input.addEventListener('focus', function() {
            const icon = this.previousElementSibling;
            if (icon && icon.tagName === 'I') {
                icon.style.color = '#4a6cf7';
            }
        });
        
        // Add blur event to reset icon color
        input.addEventListener('blur', function() {
            const icon = this.previousElementSibling;
            if (icon && icon.tagName === 'I') {
                icon.style.color = '';
            }
        });
    });
    
    // Check URL parameters to see if we should show register form
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('register') === 'true') {
        loginBox.classList.add('hidden');
        registerBox.classList.remove('hidden');
    }
    
    // Switch between login and register forms
    if (switchToRegister) {
        switchToRegister.addEventListener('click', function(e) {
            e.preventDefault();
            loginBox.classList.add('hidden');
            registerBox.classList.remove('hidden');
        });
    }
    
    if (switchToLogin) {
        switchToLogin.addEventListener('click', function(e) {
            e.preventDefault();
            registerBox.classList.add('hidden');
            loginBox.classList.remove('hidden');
        });
    }
    
    // Handle login form submission
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            
            // Validate inputs
            if (!username || !password) {
                alert('Please fill in all fields');
                return;
            }
            
            // Send login request
            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Redirect to chat page with user ID
                    window.location.href = `/chat?user_id=${data.user_id}`;
                } else {
                    alert(data.message || 'Login failed. Please check your credentials.');
                }
            })
            .catch(error => {
                console.error('Login error:', error);
                alert('An error occurred during login. Please try again.');
            });
        });
    }
    
    // Handle register form submission
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('registerUsername').value;
            const password = document.getElementById('registerPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const job = document.getElementById('registerJob').value;
            const major = document.getElementById('registerMajor').value;
            const email = document.getElementById('registerEmail').value;
            const verificationCode = document.getElementById('verificationCode').value;
            
            // Validate inputs
            if (!username || !password || !confirmPassword || !job || !major || !email || !verificationCode) {
                alert('Please fill in all fields');
                return;
            }
            
            if (password !== confirmPassword) {
                alert('Passwords do not match');
                return;
            }
            
            // Get stored verification code
            const storedCode = localStorage.getItem('verification_code');
            
            // Send register request
            fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    password: password,
                    job: job,
                    major: major,
                    email: email,
                    verification_code: verificationCode,
                    stored_code: storedCode
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Registration successful! Please login.');
                    // Switch to login form
                    registerBox.classList.add('hidden');
                    loginBox.classList.remove('hidden');
                } else {
                    alert(data.message || 'Registration failed. Please try again.');
                }
            })
            .catch(error => {
                console.error('Registration error:', error);
                alert('An error occurred during registration. Please try again.');
            });
        });
    }
    
    // Handle send verification code
    if (sendVerificationBtn) {
        sendVerificationBtn.addEventListener('click', function() {
            const email = document.getElementById('registerEmail').value;
            
            if (!email) {
                alert('Please enter your email address');
                return;
            }
            
            // Disable button during request
            sendVerificationBtn.disabled = true;
            sendVerificationBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            // Send verification code request
            fetch('/send-verification', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Verification code sent to your email');
                    // Store verification code in localStorage
                    localStorage.setItem('verification_code', data.code);
                    
                    // Start countdown for button re-enable
                    let countdown = 60;
                    const countdownInterval = setInterval(function() {
                        countdown--;
                        sendVerificationBtn.innerHTML = `<i class="fas fa-clock"></i> ${countdown}s`;
                        
                        if (countdown <= 0) {
                            clearInterval(countdownInterval);
                            sendVerificationBtn.disabled = false;
                            sendVerificationBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send';
                        }
                    }, 1000);
                } else {
                    alert(data.message || 'Failed to send verification code');
                    sendVerificationBtn.disabled = false;
                    sendVerificationBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send';
                }
            })
            .catch(error => {
                console.error('Verification code error:', error);
                alert('An error occurred while sending verification code');
                sendVerificationBtn.disabled = false;
                sendVerificationBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send';
            });
        });
    }
}); 