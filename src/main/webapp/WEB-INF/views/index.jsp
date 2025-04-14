<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Postman Collection Analyzer</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" 
          rel="stylesheet">
    <style>
        /* Main Styles for Postman Collection Analyzer */
        body {
            padding-top: 20px;
            padding-bottom: 40px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }
        
        .jumbotron {
            background-color: #f8f9fa;
            padding: 2rem 1rem;
            margin-bottom: 2rem;
            border-radius: 0.3rem;
        }
        
        .form-container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .drop-zone {
            border: 2px dashed #0d6efd;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin-bottom: 20px;
            background-color: #f8f9fa;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        
        .drop-zone:hover {
            background-color: #e9ecef;
        }
        
        .drop-zone p {
            margin-bottom: 0;
        }
        
        .file-info {
            margin-top: 10px;
            font-size: 0.9rem;
        }
        
        .footer {
            margin-top: 50px;
            color: #6c757d;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="jumbotron">
            <div class="container">
                <h1 class="display-4">Postman Collection Analyzer</h1>
                <p class="lead">Upload your Postman collection to analyze and improve your API tests</p>
            </div>
        </div>
        
        <div class="form-container">
            <!-- Error message will be displayed here if present -->
            <% if (request.getAttribute("error") != null) { %>
                <div class="alert alert-danger" role="alert">
                    <%= request.getAttribute("error") %>
                </div>
            <% } %>
            
            <form action="/app/analyze" method="post" enctype="multipart/form-data">
                <div class="mb-4">
                    <label class="form-label"><strong>Upload Postman Collection File</strong></label>
                    <div id="collectionDropZone" class="drop-zone">
                        <p>Drag & drop your Postman collection file here or click to browse</p>
                        <p class="text-muted">(.json format)</p>
                        <input type="file" name="collectionFile" id="collectionFile" class="d-none" accept=".json,application/json">
                        <div id="collectionFileInfo" class="file-info"></div>
                    </div>
                </div>
                
                <div class="mb-4">
                    <label class="form-label"><strong>Upload Environment File (Optional)</strong></label>
                    <div id="environmentDropZone" class="drop-zone">
                        <p>Drag & drop your Postman environment file here or click to browse</p>
                        <p class="text-muted">(.json format)</p>
                        <input type="file" name="environmentFile" id="environmentFile" class="d-none" accept=".json,application/json">
                        <div id="environmentFileInfo" class="file-info"></div>
                    </div>
                </div>
                
                <div class="text-center">
                    <button type="submit" class="btn btn-primary btn-lg" id="analyzeBtn" disabled>Analyze Collection</button>
                </div>
            </form>
        </div>
        
        <div class="footer">
            <p>Postman Collection Analyzer</p>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        /**
         * Main JavaScript for Postman Collection Analyzer
         */
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize file upload functionality
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
                if (collectionFile.files.length > 0) {
                    analyzeBtn.disabled = false;
                } else {
                    analyzeBtn.disabled = true;
                }
            }
        });
    </script>
</body>
</html>