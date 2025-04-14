package com.postman.analyzer.model;

/**
 * Represents a recommendation for improving the Postman collection.
 */
public class Recommendation {
    
    /**
     * Type of recommendation (e.g., "test-coverage", "naming", "structure").
     */
    private String type;
    
    /**
     * Severity level of the recommendation (e.g., "high", "medium", "low").
     */
    private String severity;
    
    /**
     * Description of the recommendation.
     */
    private String description;
    
    /**
     * Additional details or explanation.
     */
    private String details;
    
    /**
     * Example code or implementation suggestion.
     */
    private String example;
    
    // Default constructor
    public Recommendation() {
    }
    
    // Parameterized constructor
    public Recommendation(String type, String severity, String description, String details, String example) {
        this.type = type;
        this.severity = severity;
        this.description = description;
        this.details = details;
        this.example = example;
    }
    
    // Getters and setters
    public String getType() {
        return type;
    }
    
    public void setType(String type) {
        this.type = type;
    }
    
    public String getSeverity() {
        return severity;
    }
    
    public void setSeverity(String severity) {
        this.severity = severity;
    }
    
    public String getDescription() {
        return description;
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public String getDetails() {
        return details;
    }
    
    public void setDetails(String details) {
        this.details = details;
    }
    
    public String getExample() {
        return example;
    }
    
    public void setExample(String example) {
        this.example = example;
    }
    
    // Builder pattern implementation
    public static RecommendationBuilder builder() {
        return new RecommendationBuilder();
    }
    
    public static class RecommendationBuilder {
        private String type;
        private String severity;
        private String description;
        private String details;
        private String example;
        
        public RecommendationBuilder type(String type) {
            this.type = type;
            return this;
        }
        
        public RecommendationBuilder severity(String severity) {
            this.severity = severity;
            return this;
        }
        
        public RecommendationBuilder description(String description) {
            this.description = description;
            return this;
        }
        
        public RecommendationBuilder details(String details) {
            this.details = details;
            return this;
        }
        
        public RecommendationBuilder example(String example) {
            this.example = example;
            return this;
        }
        
        public Recommendation build() {
            return new Recommendation(type, severity, description, details, example);
        }
    }
}