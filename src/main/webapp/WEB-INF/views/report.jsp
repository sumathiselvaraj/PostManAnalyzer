<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis Report - Postman Collection Analyzer</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" 
          rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.3/font/bootstrap-icons.css">
    <link href="${pageContext.request.contextPath}/resources/css/styles.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="row align-items-center">
                <div class="col">
                    <h1>Postman Collection Analysis Report</h1>
                    <p class="lead mb-0">
                        <c:out value="${result.collectionInfo.name}"/>
                        <small class="text-muted">
                            (Analyzed <fmt:formatDate value="${result.timestamp}" pattern="MMM d, yyyy h:mm a"/>)
                        </small>
                    </p>
                </div>
                <div class="col-auto">
                    <a href="/app" class="btn btn-outline-primary">
                        <i class="bi bi-arrow-left"></i> New Analysis
                    </a>
                    <a href="/app/export?format=pdf" class="btn btn-outline-secondary">
                        <i class="bi bi-file-earmark-pdf"></i> Export PDF
                    </a>
                </div>
            </div>
        </div>
        
        <!-- Overview Section -->
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <h5 class="card-title">Overall Quality Score</h5>
                        <div class="score-circle 
                            <c:choose>
                                <c:when test="${result.overallScore < 21}">score-0-20</c:when>
                                <c:when test="${result.overallScore < 41}">score-21-40</c:when>
                                <c:when test="${result.overallScore < 61}">score-41-60</c:when>
                                <c:when test="${result.overallScore < 81}">score-61-80</c:when>
                                <c:otherwise>score-81-100</c:otherwise>
                            </c:choose>">
                            <fmt:formatNumber value="${result.overallScore}" pattern="#,##0" />
                        </div>
                        <div class="score-label">
                            <c:choose>
                                <c:when test="${result.overallScore < 21}">Poor</c:when>
                                <c:when test="${result.overallScore < 41}">Needs Improvement</c:when>
                                <c:when test="${result.overallScore < 61}">Average</c:when>
                                <c:when test="${result.overallScore < 81}">Good</c:when>
                                <c:otherwise>Excellent</c:otherwise>
                            </c:choose>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">Collection Summary</h5>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                Requests
                                <span class="badge bg-primary rounded-pill">${result.requestCount}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                Folders
                                <span class="badge bg-primary rounded-pill">${result.folderCount}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                Tests
                                <span class="badge bg-primary rounded-pill">${result.testCount}</span>
                            </li>
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                Tests Per Request
                                <span class="badge bg-primary rounded-pill">
                                    <fmt:formatNumber value="${result.testsPerRequest}" pattern="#,##0.0" />
                                </span>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">Top Recommendations</h5>
                        <div class="recommendations-list">
                            <c:forEach var="recommendation" items="${result.recommendations}" end="2">
                                <div class="recommendation ${recommendation.severity}">
                                    <strong>${recommendation.description}</strong>
                                </div>
                            </c:forEach>
                            <c:if test="${empty result.recommendations}">
                                <p class="text-muted">No recommendations available.</p>
                            </c:if>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Test Coverage Section -->
        <div class="card mb-4">
            <div class="card-header">
                Test Coverage
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <div class="test-coverage-chart">
                            <canvas id="testCoverageChart"></canvas>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h5>Test Types Distribution</h5>
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Test Type</th>
                                    <th>Coverage</th>
                                </tr>
                            </thead>
                            <tbody>
                                <c:forEach var="coverage" items="${result.testCoverage}">
                                    <tr>
                                        <td>${coverage.key}</td>
                                        <td>
                                            <div class="progress">
                                                <div class="progress-bar" role="progressbar" 
                                                     style="width: ${coverage.value}%" 
                                                     aria-valuenow="${coverage.value}" 
                                                     aria-valuemin="0" aria-valuemax="100">
                                                    <fmt:formatNumber value="${coverage.value}" pattern="#,##0.0" />%
                                                </div>
                                            </div>
                                        </td>
                                    </tr>
                                </c:forEach>
                                <c:if test="${empty result.testCoverage}">
                                    <tr>
                                        <td colspan="2" class="text-center text-muted">No test coverage data available</td>
                                    </tr>
                                </c:if>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Recommendations Section -->
        <div class="card mb-4">
            <div class="card-header">
                Recommendations
            </div>
            <div class="card-body">
                <c:forEach var="recommendation" items="${result.recommendations}">
                    <div class="recommendation ${recommendation.severity}">
                        <h5>${recommendation.description}</h5>
                        <p>${recommendation.details}</p>
                        <pre>${recommendation.example}</pre>
                    </div>
                </c:forEach>
                <c:if test="${empty result.recommendations}">
                    <p class="text-center text-muted">No recommendations available. Your collection looks great!</p>
                </c:if>
            </div>
        </div>
        
        <!-- Endpoint Details Section -->
        <div class="card mb-4">
            <div class="card-header">
                Endpoint Details
            </div>
            <div class="card-body">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Method</th>
                            <th>Tests</th>
                            <th>Coverage</th>
                            <th>Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        <c:forEach var="endpoint" items="${result.endpoints}" varStatus="status">
                            <tr class="endpoint-row" data-bs-toggle="collapse" data-bs-target="#endpoint-${status.index}">
                                <td>${endpoint.name}</td>
                                <td><span class="badge bg-secondary">${endpoint.method}</span></td>
                                <td>${endpoint.testCount}</td>
                                <td>
                                    <div class="progress">
                                        <div class="progress-bar" role="progressbar" 
                                             style="width: ${endpoint.coverage}%" 
                                             aria-valuenow="${endpoint.coverage}" 
                                             aria-valuemin="0" aria-valuemax="100">
                                            <fmt:formatNumber value="${endpoint.coverage}" pattern="#,##0.0" />%
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <span class="badge
                                        <c:choose>
                                            <c:when test="${endpoint.score < 21}">bg-danger</c:when>
                                            <c:when test="${endpoint.score < 41}">bg-warning text-dark</c:when>
                                            <c:when test="${endpoint.score < 61}">bg-info text-dark</c:when>
                                            <c:when test="${endpoint.score < 81}">bg-primary</c:when>
                                            <c:otherwise>bg-success</c:otherwise>
                                        </c:choose>">
                                        <fmt:formatNumber value="${endpoint.score}" pattern="#,##0" />
                                    </span>
                                </td>
                            </tr>
                            <tr class="collapse" id="endpoint-${status.index}">
                                <td colspan="5">
                                    <div class="endpoint-details">
                                        <h6>URL: ${endpoint.url}</h6>
                                        
                                        <h6 class="mt-3">Test Types:</h6>
                                        <ul>
                                            <c:forEach var="testType" items="${endpoint.testTypes}">
                                                <li>${testType.key}: ${testType.value}</li>
                                            </c:forEach>
                                            <c:if test="${empty endpoint.testTypes}">
                                                <li class="text-muted">No tests found</li>
                                            </c:if>
                                        </ul>
                                        
                                        <h6 class="mt-3">Features:</h6>
                                        <ul>
                                            <li>Error Handling: <span class="badge ${endpoint.hasErrorHandling ? 'bg-success' : 'bg-secondary'}">
                                                ${endpoint.hasErrorHandling ? 'Yes' : 'No'}
                                            </span></li>
                                            <li>Dynamic Data: <span class="badge ${endpoint.usesDynamicData ? 'bg-success' : 'bg-secondary'}">
                                                ${endpoint.usesDynamicData ? 'Yes' : 'No'}
                                            </span></li>
                                            <li>Variables: <span class="badge ${endpoint.usesVariables ? 'bg-success' : 'bg-secondary'}">
                                                ${endpoint.usesVariables ? 'Yes' : 'No'}
                                            </span></li>
                                        </ul>
                                        
                                        <c:if test="${not empty endpoint.testExamples}">
                                            <h6 class="mt-3">Test Examples:</h6>
                                            <c:forEach var="example" items="${endpoint.testExamples}">
                                                <p><strong>${example.key}:</strong></p>
                                                <pre>${example.value}</pre>
                                            </c:forEach>
                                        </c:if>
                                    </div>
                                </td>
                            </tr>
                        </c:forEach>
                        <c:if test="${empty result.endpoints}">
                            <tr>
                                <td colspan="5" class="text-center text-muted">No endpoints found in collection</td>
                            </tr>
                        </c:if>
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Environment Section (if available) -->
        <c:if test="${not empty result.environmentInfo}">
            <div class="card mb-4">
                <div class="card-header">
                    Environment Analysis: ${result.environmentInfo.name}
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h5>Overview</h5>
                            <ul class="list-group list-group-flush mb-3">
                                <li class="list-group-item d-flex justify-content-between align-items-center">
                                    Variable Count
                                    <span class="badge bg-primary rounded-pill">${result.environmentInfo.variableCount}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between align-items-center">
                                    Used in Collection
                                    <span class="badge bg-primary rounded-pill">
                                        ${result.environmentInfo.usedInCollectionCount} 
                                        (<fmt:formatNumber value="${result.environmentInfo.usedInCollectionPercent}" pattern="#,##0.0" />%)
                                    </span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between align-items-center">
                                    Naming Convention Score
                                    <span class="badge bg-primary rounded-pill">
                                        <fmt:formatNumber value="${result.environmentInfo.namingConventionScore}" pattern="#,##0.0" />%
                                    </span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between align-items-center">
                                    Quality Score
                                    <span class="badge
                                        <c:choose>
                                            <c:when test="${result.environmentInfo.qualityScore < 21}">bg-danger</c:when>
                                            <c:when test="${result.environmentInfo.qualityScore < 41}">bg-warning text-dark</c:when>
                                            <c:when test="${result.environmentInfo.qualityScore < 61}">bg-info text-dark</c:when>
                                            <c:when test="${result.environmentInfo.qualityScore < 81}">bg-primary</c:when>
                                            <c:otherwise>bg-success</c:otherwise>
                                        </c:choose>">
                                        <fmt:formatNumber value="${result.environmentInfo.qualityScore}" pattern="#,##0" />
                                    </span>
                                </li>
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h5>Variable Categories</h5>
                            <div class="mt-3">
                                <canvas id="variableCategoriesChart"></canvas>
                            </div>
                        </div>
                    </div>
                    
                    <c:if test="${not empty result.environmentInfo.recommendations}">
                        <h5 class="mt-4">Environment Recommendations</h5>
                        <c:forEach var="recommendation" items="${result.environmentInfo.recommendations}">
                            <div class="recommendation ${recommendation.severity}">
                                <h5>${recommendation.description}</h5>
                                <p>${recommendation.details}</p>
                                <pre>${recommendation.example}</pre>
                            </div>
                        </c:forEach>
                    </c:if>
                </div>
            </div>
        </c:if>
        
        <div class="footer">
            <p>Postman Collection Analyzer</p>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Test Coverage Chart
            const testCoverageLabels = [];
            const testCoverageData = [];
            
            <c:forEach var="coverage" items="${result.testCoverage}">
                testCoverageLabels.push('${coverage.key}');
                testCoverageData.push(${coverage.value});
            </c:forEach>
            
            if (testCoverageLabels.length > 0) {
                new Chart(document.getElementById('testCoverageChart'), {
                    type: 'bar',
                    data: {
                        labels: testCoverageLabels,
                        datasets: [{
                            label: 'Test Coverage (%)',
                            data: testCoverageData,
                            backgroundColor: 'rgba(54, 162, 235, 0.6)',
                            borderColor: 'rgba(54, 162, 235, 1)',
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
            
            // Variable Categories Chart (if environment info is available)
            <c:if test="${not empty result.environmentInfo and not empty result.environmentInfo.variableCategories}">
                const variableCategoryLabels = [];
                const variableCategoryData = [];
                
                <c:forEach var="category" items="${result.environmentInfo.variableCategories}">
                    variableCategoryLabels.push('${category.key}');
                    variableCategoryData.push(${category.value});
                </c:forEach>
                
                if (variableCategoryLabels.length > 0) {
                    new Chart(document.getElementById('variableCategoriesChart'), {
                        type: 'pie',
                        data: {
                            labels: variableCategoryLabels,
                            datasets: [{
                                label: 'Variable Categories',
                                data: variableCategoryData,
                                backgroundColor: [
                                    'rgba(255, 99, 132, 0.6)',
                                    'rgba(54, 162, 235, 0.6)',
                                    'rgba(255, 206, 86, 0.6)',
                                    'rgba(75, 192, 192, 0.6)',
                                    'rgba(153, 102, 255, 0.6)',
                                    'rgba(255, 159, 64, 0.6)'
                                ],
                                borderColor: [
                                    'rgba(255, 99, 132, 1)',
                                    'rgba(54, 162, 235, 1)',
                                    'rgba(255, 206, 86, 1)',
                                    'rgba(75, 192, 192, 1)',
                                    'rgba(153, 102, 255, 1)',
                                    'rgba(255, 159, 64, 1)'
                                ],
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false
                        }
                    });
                }
            </c:if>
            
            // Toggle endpoint details
            document.querySelectorAll('.endpoint-row').forEach(row => {
                row.addEventListener('click', function() {
                    const targetId = this.getAttribute('data-bs-target');
                    document.querySelector(targetId).classList.toggle('show');
                });
            });
        });
    </script>
</body>
</html>