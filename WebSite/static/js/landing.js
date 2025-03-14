document.addEventListener('DOMContentLoaded', function() {
    // How It Works modal functionality
    const howItWorksLink = document.querySelector('.how-it-works-link');
    const howItWorksModal = document.getElementById('howItWorksModal');
    const closeHowItWorksBtn = document.getElementById('closeHowItWorksBtn');
    
    if (howItWorksLink) {
        howItWorksLink.addEventListener('click', (e) => {
            e.preventDefault();
            howItWorksModal.classList.add('active');
        });
    }

    if (closeHowItWorksBtn) {
        closeModalBtn.addEventListener('click', () => {
            howItWorksModal.classList.remove('active');
        });
    }

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === howItWorksModal) {
            howItWorksModal.classList.remove('active');
        }
    });
    
    // Get Started and Start Now buttons redirect to auth page
    const getStartedBtn = document.getElementById('getStartedBtn');
    const startNowBtn = document.getElementById('startNowBtn');
    
    if (getStartedBtn) {
        getStartedBtn.addEventListener('click', function() {
            window.location.href = '/auth';
        });
    }
    
    if (startNowBtn) {
        startNowBtn.addEventListener('click', function() {
            window.location.href = '/auth';
        });
    }
}); 