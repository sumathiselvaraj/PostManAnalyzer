package com.postman.analyzer.model;

import java.util.List;
import java.util.Map;

/**
 * Represents basic information about a Postman environment.
 */
public class EnvironmentInfo {
    
    private String name;
    private String postmanVariableScope;
    private int variableCount;
    private Map<String, Integer> variableCategories;
    private double namingConventionScore;
    private double qualityScore;
    private int usedInCollectionCount;
    private double usedInCollectionPercent;
    private List<Recommendation> recommendations;
    
    // Default constructor
    public EnvironmentInfo() {
    }
    
    // Parameterized constructor
    public EnvironmentInfo(String name, String postmanVariableScope, int variableCount,
                         Map<String, Integer> variableCategories, double namingConventionScore,
                         double qualityScore, int usedInCollectionCount,
                         double usedInCollectionPercent, List<Recommendation> recommendations) {
        this.name = name;
        this.postmanVariableScope = postmanVariableScope;
        this.variableCount = variableCount;
        this.variableCategories = variableCategories;
        this.namingConventionScore = namingConventionScore;
        this.qualityScore = qualityScore;
        this.usedInCollectionCount = usedInCollectionCount;
        this.usedInCollectionPercent = usedInCollectionPercent;
        this.recommendations = recommendations;
    }
    
    // Getters and setters
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getPostmanVariableScope() {
        return postmanVariableScope;
    }
    
    public void setPostmanVariableScope(String postmanVariableScope) {
        this.postmanVariableScope = postmanVariableScope;
    }
    
    public int getVariableCount() {
        return variableCount;
    }
    
    public void setVariableCount(int variableCount) {
        this.variableCount = variableCount;
    }
    
    public Map<String, Integer> getVariableCategories() {
        return variableCategories;
    }
    
    public void setVariableCategories(Map<String, Integer> variableCategories) {
        this.variableCategories = variableCategories;
    }
    
    public double getNamingConventionScore() {
        return namingConventionScore;
    }
    
    public void setNamingConventionScore(double namingConventionScore) {
        this.namingConventionScore = namingConventionScore;
    }
    
    public double getQualityScore() {
        return qualityScore;
    }
    
    public void setQualityScore(double qualityScore) {
        this.qualityScore = qualityScore;
    }
    
    public int getUsedInCollectionCount() {
        return usedInCollectionCount;
    }
    
    public void setUsedInCollectionCount(int usedInCollectionCount) {
        this.usedInCollectionCount = usedInCollectionCount;
    }
    
    public double getUsedInCollectionPercent() {
        return usedInCollectionPercent;
    }
    
    public void setUsedInCollectionPercent(double usedInCollectionPercent) {
        this.usedInCollectionPercent = usedInCollectionPercent;
    }
    
    public List<Recommendation> getRecommendations() {
        return recommendations;
    }
    
    public void setRecommendations(List<Recommendation> recommendations) {
        this.recommendations = recommendations;
    }
    
    // Builder pattern implementation
    public static EnvironmentInfoBuilder builder() {
        return new EnvironmentInfoBuilder();
    }
    
    public static class EnvironmentInfoBuilder {
        private String name;
        private String postmanVariableScope;
        private int variableCount;
        private Map<String, Integer> variableCategories;
        private double namingConventionScore;
        private double qualityScore;
        private int usedInCollectionCount;
        private double usedInCollectionPercent;
        private List<Recommendation> recommendations;
        
        public EnvironmentInfoBuilder name(String name) {
            this.name = name;
            return this;
        }
        
        public EnvironmentInfoBuilder postmanVariableScope(String postmanVariableScope) {
            this.postmanVariableScope = postmanVariableScope;
            return this;
        }
        
        public EnvironmentInfoBuilder variableCount(int variableCount) {
            this.variableCount = variableCount;
            return this;
        }
        
        public EnvironmentInfoBuilder variableCategories(Map<String, Integer> variableCategories) {
            this.variableCategories = variableCategories;
            return this;
        }
        
        public EnvironmentInfoBuilder namingConventionScore(double namingConventionScore) {
            this.namingConventionScore = namingConventionScore;
            return this;
        }
        
        public EnvironmentInfoBuilder qualityScore(double qualityScore) {
            this.qualityScore = qualityScore;
            return this;
        }
        
        public EnvironmentInfoBuilder usedInCollectionCount(int usedInCollectionCount) {
            this.usedInCollectionCount = usedInCollectionCount;
            return this;
        }
        
        public EnvironmentInfoBuilder usedInCollectionPercent(double usedInCollectionPercent) {
            this.usedInCollectionPercent = usedInCollectionPercent;
            return this;
        }
        
        public EnvironmentInfoBuilder recommendations(List<Recommendation> recommendations) {
            this.recommendations = recommendations;
            return this;
        }
        
        public EnvironmentInfo build() {
            return new EnvironmentInfo(name, postmanVariableScope, variableCount, variableCategories,
                                     namingConventionScore, qualityScore, usedInCollectionCount,
                                     usedInCollectionPercent, recommendations);
        }
    }
}