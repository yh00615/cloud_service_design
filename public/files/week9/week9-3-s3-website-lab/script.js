// AWS CI/CD Demo - Week 9-3
// Simple JavaScript for interactive features

document.addEventListener('DOMContentLoaded', function () {
    console.log('AWS CI/CD Demo Website Loaded');
    console.log('Deployed via CodePipeline + CodeBuild + S3');

    // Add animation to feature items
    const featureItems = document.querySelectorAll('.feature-item');
    featureItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px)';

        setTimeout(() => {
            item.style.transition = 'opacity 0.5s, transform 0.5s';
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Add click event to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function (e) {
            console.log('Navigation button clicked:', this.href);
        });
    });

    // Display deployment info
    const deploymentInfo = {
        timestamp: new Date().toISOString(),
        service: 'Amazon S3',
        pipeline: 'AWS CodePipeline',
        build: 'AWS CodeBuild'
    };

    console.log('Deployment Info:', deploymentInfo);

    // Add version info to console
    const versionElement = document.querySelector('.version');
    if (versionElement) {
        console.log('Current Version:', versionElement.textContent);
    }
});

// Function to simulate real-time updates
function checkForUpdates() {
    console.log('Checking for updates...');
    // In a real scenario, this could poll an API or use WebSockets
}

// Check for updates every 30 seconds
setInterval(checkForUpdates, 30000);
