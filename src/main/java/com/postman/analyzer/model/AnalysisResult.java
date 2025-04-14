package com.postman.analyzer.model;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * Represents the complete analysis result of a Postman collection.
 */
public class AnalysisResult {
    
    /**
     * Basic information about the collection.
     */
    private CollectionInfo collectionInfo;
    
    /**
     * Environment information (if available).
     */
    private EnvironmentInfo environmentInfo;
    
    /**
     * Number of requests in the collection.
     */
    private int requestCount;
    
    /**
     * Number of folders in the collection.
     */
    private int folderCount;
    
    /**
     * Number of unique endpoints in the collection.
     */
    private int endpointCount;
    
    /**
     * Total number of tests in the collection.
     */
    private int testCount;
    
    /**
     * Average number of tests per request.
     */
    private double testsPerRequest;
    
    /**
     * Test coverage by test type.
     */
    private Map<String, Double> testCoverage;
    
    /**
     * Analysis of test scripts.
     */
    private ScriptAnalysis scriptAnalysis;
    
    /**
     * List of analyzed endpoints.
     */
    private List<Endpoint> endpoints;
    
    /**
     * Overall quality score.
     */
    private double overallScore;
    
    /**
     * List of recommendations for improvement.
     */
    private List<Recommendation> recommendations;
    
    /**
     * Timestamp of the analysis.
     */
    private LocalDateTime timestamp;
    
    // Default constructor
    public AnalysisResult() {
    }
    
    // Parameterized constructor
    public AnalysisResult(CollectionInfo collectionInfo, EnvironmentInfo environmentInfo, int requestCount,
                         int folderCount, int endpointCount, int testCount, double testsPerRequest,
                         Map<String, Double> testCoverage, ScriptAnalysis scriptAnalysis,
                         List<Endpoint> endpoints, double overallScore, List<Recommendation> recommendations,
                         LocalDateTime timestamp) {
        this.collectionInfo = collectionInfo;
        this.environmentInfo = environmentInfo;
        this.requestCount = requestCount;
        this.folderCount = folderCount;
        this.endpointCount = endpointCount;
        this.testCount = testCount;
        this.testsPerRequest = testsPerRequest;
        this.testCoverage = testCoverage;
        this.scriptAnalysis = scriptAnalysis;
        this.endpoints = endpoints;
        this.overallScore = overallScore;
        this.recommendations = recommendations;
        this.timestamp = timestamp;
    }
    
    // Getters and setters
    public CollectionInfo getCollectionInfo() {
        return collectionInfo;
    }
    
    public void setCollectionInfo(CollectionInfo collectionInfo) {
        this.collectionInfo = collectionInfo;
    }
    
    public EnvironmentInfo getEnvironmentInfo() {
        return environmentInfo;
    }
    
    public void setEnvironmentInfo(EnvironmentInfo environmentInfo) {
        this.environmentInfo = environmentInfo;
    }
    
    public int getRequestCount() {
        return requestCount;
    }
    
    public void setRequestCount(int requestCount) {
        this.requestCount = requestCount;
    }
    
    public int getFolderCount() {
        return folderCount;
    }
    
    public void setFolderCount(int folderCount) {
        this.folderCount = folderCount;
    }
    
    public int getEndpointCount() {
        return endpointCount;
    }
    
    public void setEndpointCount(int endpointCount) {
        this.endpointCount = endpointCount;
    }
    
    public int getTestCount() {
        return testCount;
    }
    
    public void setTestCount(int testCount) {
        this.testCount = testCount;
    }
    
    public double getTestsPerRequest() {
        return testsPerRequest;
    }
    
    public void setTestsPerRequest(double testsPerRequest) {
        this.testsPerRequest = testsPerRequest;
    }
    
    public Map<String, Double> getTestCoverage() {
        return testCoverage;
    }
    
    public void setTestCoverage(Map<String, Double> testCoverage) {
        this.testCoverage = testCoverage;
    }
    
    public ScriptAnalysis getScriptAnalysis() {
        return scriptAnalysis;
    }
    
    public void setScriptAnalysis(ScriptAnalysis scriptAnalysis) {
        this.scriptAnalysis = scriptAnalysis;
    }
    
    public List<Endpoint> getEndpoints() {
        return endpoints;
    }
    
    public void setEndpoints(List<Endpoint> endpoints) {
        this.endpoints = endpoints;
    }
    
    public double getOverallScore() {
        return overallScore;
    }
    
    public void setOverallScore(double overallScore) {
        this.overallScore = overallScore;
    }
    
    public List<Recommendation> getRecommendations() {
        return recommendations;
    }
    
    public void setRecommendations(List<Recommendation> recommendations) {
        this.recommendations = recommendations;
    }
    
    public LocalDateTime getTimestamp() {
        return timestamp;
    }
    
    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }
    
    // Builder pattern implementation
    public static AnalysisResultBuilder builder() {
        return new AnalysisResultBuilder();
    }
    
    public static class AnalysisResultBuilder {
        private CollectionInfo collectionInfo;
        private EnvironmentInfo environmentInfo;
        private int requestCount;
        private int folderCount;
        private int endpointCount;
        private int testCount;
        private double testsPerRequest;
        private Map<String, Double> testCoverage;
        private ScriptAnalysis scriptAnalysis;
        private List<Endpoint> endpoints;
        private double overallScore;
        private List<Recommendation> recommendations;
        private LocalDateTime timestamp;
        
        public AnalysisResultBuilder collectionInfo(CollectionInfo collectionInfo) {
            this.collectionInfo = collectionInfo;
            return this;
        }
        
        public AnalysisResultBuilder environmentInfo(EnvironmentInfo environmentInfo) {
            this.environmentInfo = environmentInfo;
            return this;
        }
        
        public AnalysisResultBuilder requestCount(int requestCount) {
            this.requestCount = requestCount;
            return this;
        }
        
        public AnalysisResultBuilder folderCount(int folderCount) {
            this.folderCount = folderCount;
            return this;
        }
        
        public AnalysisResultBuilder endpointCount(int endpointCount) {
            this.endpointCount = endpointCount;
            return this;
        }
        
        public AnalysisResultBuilder testCount(int testCount) {
            this.testCount = testCount;
            return this;
        }
        
        public AnalysisResultBuilder testsPerRequest(double testsPerRequest) {
            this.testsPerRequest = testsPerRequest;
            return this;
        }
        
        public AnalysisResultBuilder testCoverage(Map<String, Double> testCoverage) {
            this.testCoverage = testCoverage;
            return this;
        }
        
        public AnalysisResultBuilder scriptAnalysis(ScriptAnalysis scriptAnalysis) {
            this.scriptAnalysis = scriptAnalysis;
            return this;
        }
        
        public AnalysisResultBuilder endpoints(List<Endpoint> endpoints) {
            this.endpoints = endpoints;
            return this;
        }
        
        public AnalysisResultBuilder overallScore(double overallScore) {
            this.overallScore = overallScore;
            return this;
        }
        
        public AnalysisResultBuilder recommendations(List<Recommendation> recommendations) {
            this.recommendations = recommendations;
            return this;
        }
        
        public AnalysisResultBuilder timestamp(LocalDateTime timestamp) {
            this.timestamp = timestamp;
            return this;
        }
        
        public AnalysisResult build() {
            return new AnalysisResult(collectionInfo, environmentInfo, requestCount, folderCount,
                                    endpointCount, testCount, testsPerRequest, testCoverage,
                                    scriptAnalysis, endpoints, overallScore, recommendations, timestamp);
        }
    }
}