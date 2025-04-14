/**
 * Postman Collection Analyzer - Frontend JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // File upload handling
    const collectionFileInput = document.getElementById('collection-file');
    const environmentFileInput = document.getElementById('environment-file');
    const collectionFileLabel = document.querySelector('label[for="collection-file"]');
    const environmentFileLabel = document.querySelector('label[for="environment-file"]');
    const analyzeForm = document.getElementById('analyze-form');
    const loadingSpinner = document.getElementById('loading-spinner');
    
    // Update file input labels with selected filename
    collectionFileInput?.addEventListener('change', function() {
        const fileName = this.files[0]?.name || 'Choose Postman collection file';
        collectionFileLabel.textContent = fileName;
        collectionFileLabel.title = fileName;
    });
    
    environmentFileInput?.addEventListener('change', function() {
        const fileName = this.files[0]?.name || 'Choose Postman environment file (optional)';
        environmentFileLabel.textContent = fileName;
        environmentFileLabel.title = fileName;
    });
    
    // Show loading spinner on form submission
    analyzeForm?.addEventListener('submit', function() {
        loadingSpinner.style.display = 'flex';
    });
    
    // Report page functionality
    if (window.location.pathname.includes('/report')) {
        initReportPage();
    }
});

function initReportPage() {
    // Initialize tabs functionality
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            
            // Hide all tab contents
            tabContents.forEach(content => {
                content.style.display = 'none';
            });
            
            // Deactivate all tab buttons
            tabButtons.forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected tab content and activate button
            document.getElementById(tabId).style.display = 'block';
            button.classList.add('active');
        });
    });
    
    // Show first tab by default
    if (tabButtons.length > 0) {
        tabButtons[0].click();
    }
    
    // Export buttons functionality
    const exportButtons = document.querySelectorAll('.export-button');
    exportButtons.forEach(button => {
        button.addEventListener('click', () => {
            const format = button.getAttribute('data-format');
            window.location.href = `/export/${format}`;
        });
    });
    
    // Initialize collapsible sections
    const collapsibleHeaders = document.querySelectorAll('.collapsible-header');
    collapsibleHeaders.forEach(header => {
        header.addEventListener('click', () => {
            header.classList.toggle('active');
            const content = header.nextElementSibling;
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
            } else {
                content.style.maxHeight = content.scrollHeight + "px";
            }
        });
    });
    
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', (e) => {
            const tooltipText = e.target.getAttribute('data-tooltip');
            
            const tooltipElement = document.createElement('div');
            tooltipElement.className = 'tooltip';
            tooltipElement.textContent = tooltipText;
            
            document.body.appendChild(tooltipElement);
            
            const rect = e.target.getBoundingClientRect();
            tooltipElement.style.top = rect.bottom + 5 + 'px';
            tooltipElement.style.left = rect.left + (rect.width / 2) - (tooltipElement.offsetWidth / 2) + 'px';
        });
        
        tooltip.addEventListener('mouseleave', () => {
            const tooltipElement = document.querySelector('.tooltip');
            if (tooltipElement) {
                tooltipElement.remove();
            }
        });
    });
    
    // Initialize charts if any
    if (typeof initCharts === 'function') {
        initCharts();
    }
}

// Charts initialization for report page
function initCharts() {
    // Get the canvas elements
    const scoreChartCanvas = document.getElementById('score-chart');
    const coverageChartCanvas = document.getElementById('coverage-chart');
    const endpointChartCanvas = document.getElementById('endpoint-chart');
    
    if (!scoreChartCanvas || !coverageChartCanvas || !endpointChartCanvas) {
        return;
    }
    
    // Extract data from HTML data attributes
    const overallScore = parseFloat(scoreChartCanvas.getAttribute('data-score'));
    const endpointScores = JSON.parse(endpointChartCanvas.getAttribute('data-scores'));
    const coverageData = JSON.parse(coverageChartCanvas.getAttribute('data-coverage'));
    
    // Create overall score chart (gauge)
    new Chart(scoreChartCanvas, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [overallScore, 100 - overallScore],
                backgroundColor: [
                    getScoreColor(overallScore),
                    '#f0f0f0'
                ],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '80%',
            responsive: true,
            maintainAspectRatio: false,
            circumference: 180,
            rotation: 270,
            plugins: {
                tooltip: {
                    enabled: false
                },
                legend: {
                    display: false
                }
            }
        }
    });
    
    // Add score text in the middle of the doughnut
    const scoreText = document.createElement('div');
    scoreText.style.position = 'absolute';
    scoreText.style.top = '75%';
    scoreText.style.left = '50%';
    scoreText.style.transform = 'translate(-50%, -50%)';
    scoreText.style.fontSize = '24px';
    scoreText.style.fontWeight = 'bold';
    scoreText.style.color = getScoreColor(overallScore);
    scoreText.innerHTML = `${overallScore.toFixed(1)}<span style="font-size:14px;">%</span>`;
    scoreChartCanvas.parentNode.style.position = 'relative';
    scoreChartCanvas.parentNode.appendChild(scoreText);
    
    // Create test coverage chart (bar)
    new Chart(coverageChartCanvas, {
        type: 'bar',
        data: {
            labels: Object.keys(coverageData),
            datasets: [{
                label: 'Test Coverage (%)',
                data: Object.values(coverageData),
                backgroundColor: Object.values(coverageData).map(value => getScoreColor(value)),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Coverage (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Test Type'
                    }
                }
            }
        }
    });
    
    // Create endpoint scores chart (horizontal bar)
    new Chart(endpointChartCanvas, {
        type: 'bar',
        data: {
            labels: Object.keys(endpointScores),
            datasets: [{
                label: 'Endpoint Score (%)',
                data: Object.values(endpointScores),
                backgroundColor: Object.values(endpointScores).map(value => getScoreColor(value)),
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Score (%)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'API Endpoint'
                    }
                }
            }
        }
    });
}

// Helper function to get color based on score
function getScoreColor(score) {
    if (score >= 80) {
        return '#4CAF50'; // Green
    } else if (score >= 60) {
        return '#FFC107'; // Yellow
    } else if (score >= 40) {
        return '#FF9800'; // Orange
    } else {
        return '#F44336'; // Red
    }
}
