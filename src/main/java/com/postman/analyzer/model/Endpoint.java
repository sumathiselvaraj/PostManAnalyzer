package com.postman.analyzer.model;

import java.util.Map;

/**
 * Represents an API endpoint from a Postman collection.
 */
public class Endpoint {
    
    private String name;
    private String url;
    private String method;
    private int testCount;
    private Map<String, Integer> testTypes;
    private Map<String, String> testExamples;
    private boolean hasErrorHandling;
    private boolean usesDynamicData;
    private boolean usesVariables;
    private double coverage;
    private double score;
    
    // Default constructor
    public Endpoint() {
    }
    
    // Constructor with parameters
    public Endpoint(String name, String url, String method, int testCount,
                   Map<String, Integer> testTypes, Map<String, String> testExamples,
                   boolean hasErrorHandling, boolean usesDynamicData, boolean usesVariables,
                   double coverage, double score) {
        this.name = name;
        this.url = url;
        this.method = method;
        this.testCount = testCount;
        this.testTypes = testTypes;
        this.testExamples = testExamples;
        this.hasErrorHandling = hasErrorHandling;
        this.usesDynamicData = usesDynamicData;
        this.usesVariables = usesVariables;
        this.coverage = coverage;
        this.score = score;
    }
    
    // Getters and setters
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getUrl() {
        return url;
    }
    
    public void setUrl(String url) {
        this.url = url;
    }
    
    public String getMethod() {
        return method;
    }
    
    public void setMethod(String method) {
        this.method = method;
    }
    
    public int getTestCount() {
        return testCount;
    }
    
    public void setTestCount(int testCount) {
        this.testCount = testCount;
    }
    
    public Map<String, Integer> getTestTypes() {
        return testTypes;
    }
    
    public void setTestTypes(Map<String, Integer> testTypes) {
        this.testTypes = testTypes;
    }
    
    public Map<String, String> getTestExamples() {
        return testExamples;
    }
    
    public void setTestExamples(Map<String, String> testExamples) {
        this.testExamples = testExamples;
    }
    
    public boolean isHasErrorHandling() {
        return hasErrorHandling;
    }
    
    public void setHasErrorHandling(boolean hasErrorHandling) {
        this.hasErrorHandling = hasErrorHandling;
    }
    
    public boolean isUsesDynamicData() {
        return usesDynamicData;
    }
    
    public void setUsesDynamicData(boolean usesDynamicData) {
        this.usesDynamicData = usesDynamicData;
    }
    
    public boolean isUsesVariables() {
        return usesVariables;
    }
    
    public void setUsesVariables(boolean usesVariables) {
        this.usesVariables = usesVariables;
    }
    
    public double getCoverage() {
        return coverage;
    }
    
    public void setCoverage(double coverage) {
        this.coverage = coverage;
    }
    
    public double getScore() {
        return score;
    }
    
    public void setScore(double score) {
        this.score = score;
    }
    
    // Builder pattern implementation
    public static EndpointBuilder builder() {
        return new EndpointBuilder();
    }
    
    public static class EndpointBuilder {
        private String name;
        private String url;
        private String method;
        private int testCount;
        private Map<String, Integer> testTypes;
        private Map<String, String> testExamples;
        private boolean hasErrorHandling;
        private boolean usesDynamicData;
        private boolean usesVariables;
        private double coverage;
        private double score;
        
        public EndpointBuilder name(String name) {
            this.name = name;
            return this;
        }
        
        public EndpointBuilder url(String url) {
            this.url = url;
            return this;
        }
        
        public EndpointBuilder method(String method) {
            this.method = method;
            return this;
        }
        
        public EndpointBuilder testCount(int testCount) {
            this.testCount = testCount;
            return this;
        }
        
        public EndpointBuilder testTypes(Map<String, Integer> testTypes) {
            this.testTypes = testTypes;
            return this;
        }
        
        public EndpointBuilder testExamples(Map<String, String> testExamples) {
            this.testExamples = testExamples;
            return this;
        }
        
        public EndpointBuilder hasErrorHandling(boolean hasErrorHandling) {
            this.hasErrorHandling = hasErrorHandling;
            return this;
        }
        
        public EndpointBuilder usesDynamicData(boolean usesDynamicData) {
            this.usesDynamicData = usesDynamicData;
            return this;
        }
        
        public EndpointBuilder usesVariables(boolean usesVariables) {
            this.usesVariables = usesVariables;
            return this;
        }
        
        public EndpointBuilder coverage(double coverage) {
            this.coverage = coverage;
            return this;
        }
        
        public EndpointBuilder score(double score) {
            this.score = score;
            return this;
        }
        
        public Endpoint build() {
            return new Endpoint(name, url, method, testCount, testTypes, testExamples,
                             hasErrorHandling, usesDynamicData, usesVariables, coverage, score);
        }
    }
}