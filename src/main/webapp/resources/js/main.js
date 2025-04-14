/**
 * Main JavaScript for Postman Collection Analyzer
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize file upload functionality
    initFileUpload();
    
    // Initialize charts if on report page
    if (document.getElementById('testCoverageChart')) {
        initCharts();
    }
    
    // Initialize expandable endpoint details
    initEndpointDetails();
});

/**
 * Initialize file upload functionality
 */
function initFileUpload() {
    const collectionDropZone = document.getElementById('collectionDropZone');
    const environmentDropZone = document.getElementById('environmentDropZone');
    const collectionFile = document.getElementById('collectionFile');
    const environmentFile = document.getElementById('environmentFile');
    const collectionFileInfo = document.getElementById('collectionFileInfo');
    const environmentFileInfo = document.getElementById('environmentFileInfo');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    // Return if not on upload page
    if (!collectionDropZone) return;
    
    // Set up drag and drop for collection files
    collectionDropZone.addEventListener('click', function() {
        collectionFile.click();
    });
    
    collectionDropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        collectionDropZone.classList.add('bg-light');
    });
    
    collectionDropZone.addEventListener('dragleave', function() {
        collectionDropZone.classList.remove('bg-light');
    });
    
    collectionDropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        collectionDropZone.classList.remove('bg-light');
        
        if (e.dataTransfer.files.length) {
            collectionFile.files = e.dataTransfer.files;
            updateFileInfo(collectionFile, collectionFileInfo);
            validateForm();
        }
    });
    
    // Set up drag and drop for environment files
    environmentDropZone.addEventListener('click', function() {
        environmentFile.click();
    });
    
    environmentDropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        environmentDropZone.classList.add('bg-light');
    });
    
    environmentDropZone.addEventListener('dragleave', function() {
        environmentDropZone.classList.remove('bg-light');
    });
    
    environmentDropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        environmentDropZone.classList.remove('bg-light');
        
        if (e.dataTransfer.files.length) {
            environmentFile.files = e.dataTransfer.files;
            updateFileInfo(environmentFile, environmentFileInfo);
        }
    });
    
    // Update file info when files are selected
    collectionFile.addEventListener('change', function() {
        updateFileInfo(collectionFile, collectionFileInfo);
        validateForm();
    });
    
    environmentFile.addEventListener('change', function() {
        updateFileInfo(environmentFile, environmentFileInfo);
    });
}

/**
 * Update file info display
 */
function updateFileInfo(fileInput, fileInfoElement) {
    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        const fileSize = (file.size / 1024).toFixed(2);
        fileInfoElement.innerHTML = `<strong>${file.name}</strong> (${fileSize} KB)`;
    } else {
        fileInfoElement.innerHTML = '';
    }
}

/**
 * Validate form before submission
 */
function validateForm() {
    const collectionFile = document.getElementById('collectionFile');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (!collectionFile || !analyzeBtn) return;
    
    if (collectionFile.files.length > 0) {
        analyzeBtn.disabled = false;
    } else {
        analyzeBtn.disabled = true;
    }
}

/**
 * Initialize charts on the report page
 */
function initCharts() {
    const testCoverageCtx = document.getElementById('testCoverageChart');
    
    // Return if not on report page or no chart canvas
    if (!testCoverageCtx) return;
    
    // Get test coverage data from the page
    const coverageData = {};
    const coverageRows = document.querySelectorAll('table tr td:first-child');
    const coverageValues = document.querySelectorAll('.progress-bar');
    
    for (let i = 0; i < Math.min(coverageRows.length, coverageValues.length); i++) {
        const label = coverageRows[i].textContent.trim();
        const value = parseFloat(coverageValues[i].textContent);
        if (!isNaN(value)) {
            coverageData[label] = value;
        }
    }
    
    // Create chart
    new Chart(testCoverageCtx, {
        type: 'bar',
        data: {
            labels: Object.keys(coverageData),
            datasets: [{
                label: 'Test Coverage (%)',
                data: Object.values(coverageData),
                backgroundColor: [
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(153, 102, 255, 0.6)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(153, 102, 255, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

/**
 * Initialize expandable endpoint details
 */
function initEndpointDetails() {
    // Toggle endpoint details visibility
    document.querySelectorAll('.endpoint-row').forEach(row => {
        row.addEventListener('click', function() {
            const targetId = this.getAttribute('data-bs-target');
            const detailsRow = document.querySelector(targetId);
            
            if (detailsRow) {
                detailsRow.classList.toggle('show');
            }
        });
    });
}