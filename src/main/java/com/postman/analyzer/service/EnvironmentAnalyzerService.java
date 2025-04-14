package com.postman.analyzer.service;

import org.springframework.stereotype.Service;

import com.postman.analyzer.model.AnalysisResult;
import com.postman.analyzer.model.Endpoint;
import com.postman.analyzer.model.EnvironmentInfo;
import com.postman.analyzer.model.Recommendation;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Service for analyzing Postman environment files.
 */
@Service
public class EnvironmentAnalyzerService {

    /**
     * Analyze a Postman environment.
     * 
     * @param environmentData The parsed Postman environment JSON
     * @param collectionResult The analysis results for the associated collection
     * @return Environment analysis results
     */
    public EnvironmentInfo analyzeEnvironment(Map<String, Object> environmentData, AnalysisResult collectionResult) {
        // Extract basic environment information
        String name = (String) environmentData.getOrDefault("name", "Unknown Environment");
        String postmanVariableScope = (String) environmentData.getOrDefault("_postman_variable_scope", "");
        
        // Extract and analyze variables
        List<Map<String, Object>> variables = extractVariables(environmentData);
        int variableCount = variables.size();
        
        // Analyze naming conventions
        double namingConventionScore = analyzeNamingConventions(variables);
        
        // Categorize variables
        Map<String, Integer> variableCategories = categorizeVariables(variables);
        
        // Check usage in collection
        Set<String> collectionVariables = extractVariablesFromCollection(collectionResult);
        int usedInCollectionCount = 0;
        double usedInCollectionPercent = 0.0;
        
        if (variableCount > 0) {
            for (Map<String, Object> variable : variables) {
                String key = (String) variable.get("key");
                if (collectionVariables.contains(key)) {
                    usedInCollectionCount++;
                }
            }
            
            usedInCollectionPercent = (double) usedInCollectionCount / variableCount * 100.0;
        }
        
        // Generate recommendations
        List<Recommendation> recommendations = generateEnvironmentRecommendations(
                variables, variableCategories, namingConventionScore, usedInCollectionPercent);
        
        // Calculate quality score
        double qualityScore = calculateEnvironmentQualityScore(
                variableCount, namingConventionScore, usedInCollectionPercent);
        
        return EnvironmentInfo.builder()
                .name(name)
                .postmanVariableScope(postmanVariableScope)
                .variableCount(variableCount)
                .variableCategories(variableCategories)
                .namingConventionScore(namingConventionScore)
                .qualityScore(qualityScore)
                .usedInCollectionCount(usedInCollectionCount)
                .usedInCollectionPercent(usedInCollectionPercent)
                .recommendations(recommendations)
                .build();
    }
    
    /**
     * Extract variables from the environment data.
     */
    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> extractVariables(Map<String, Object> environmentData) {
        List<Map<String, Object>> variables = new ArrayList<>();
        
        if (environmentData.containsKey("values")) {
            Object valuesObj = environmentData.get("values");
            if (valuesObj instanceof List) {
                variables = (List<Map<String, Object>>) valuesObj;
            }
        }
        
        return variables;
    }
    
    /**
     * Analyze variable naming conventions.
     */
    private double analyzeNamingConventions(List<Map<String, Object>> variables) {
        if (variables.isEmpty()) {
            return 0.0;
        }
        
        // Count of variables following good naming conventions
        int goodNamingCount = 0;
        
        // Check each variable for good naming practices
        for (Map<String, Object> variable : variables) {
            String key = (String) variable.get("key");
            
            if (key != null && !key.isEmpty()) {
                // Check for consistent casing (snake_case, camelCase, or kebab-case)
                boolean hasConsistentCase = hasConsistentCase(key);
                
                // Check for meaningful name (not single letter or very short)
                boolean hasMeaningfulName = key.length() > 2;
                
                // Check for good prefix or namespace
                boolean hasGoodPrefix = key.contains("_") || key.contains(".");
                
                // Increment good naming count if most criteria are met
                int score = (hasConsistentCase ? 1 : 0) + (hasMeaningfulName ? 1 : 0) + (hasGoodPrefix ? 1 : 0);
                if (score >= 2) {
                    goodNamingCount++;
                }
            }
        }
        
        // Calculate score (percentage of variables with good naming)
        return (double) goodNamingCount / variables.size() * 100.0;
    }
    
    /**
     * Check if a variable name has consistent case style.
     */
    private boolean hasConsistentCase(String name) {
        // Check for snake_case
        if (name.matches("^[a-z][a-z0-9]*(_[a-z0-9]+)*$")) {
            return true;
        }
        
        // Check for camelCase
        if (name.matches("^[a-z][a-zA-Z0-9]*$") && name.matches(".*[A-Z].*")) {
            return true;
        }
        
        // Check for kebab-case
        if (name.matches("^[a-z][a-z0-9]*(-[a-z0-9]+)*$")) {
            return true;
        }
        
        // Check for UPPER_SNAKE_CASE
        if (name.matches("^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$")) {
            return true;
        }
        
        return false;
    }
    
    /**
     * Categorize environment variables by their likely purpose.
     */
    private Map<String, Integer> categorizeVariables(List<Map<String, Object>> variables) {
        Map<String, Integer> categories = new HashMap<>();
        
        categories.put("URL", 0);
        categories.put("API Key", 0);
        categories.put("Credential", 0);
        categories.put("ID", 0);
        categories.put("Configuration", 0);
        categories.put("Other", 0);
        
        for (Map<String, Object> variable : variables) {
            String key = (String) variable.get("key");
            String value = (String) variable.get("value");
            
            if (key == null || key.isEmpty()) {
                continue;
            }
            
            String lowerKey = key.toLowerCase();
            
            if (lowerKey.contains("url") || lowerKey.contains("host") || lowerKey.contains("endpoint") || 
                (value != null && (value.startsWith("http://") || value.startsWith("https://")))) {
                categories.put("URL", categories.get("URL") + 1);
            } else if (lowerKey.contains("key") || lowerKey.contains("token") || lowerKey.contains("api")) {
                categories.put("API Key", categories.get("API Key") + 1);
            } else if (lowerKey.contains("user") || lowerKey.contains("pass") || lowerKey.contains("auth") || 
                      lowerKey.contains("login") || lowerKey.contains("secret")) {
                categories.put("Credential", categories.get("Credential") + 1);
            } else if (lowerKey.contains("id") || lowerKey.endsWith("_id") || lowerKey.startsWith("id_")) {
                categories.put("ID", categories.get("ID") + 1);
            } else if (lowerKey.contains("config") || lowerKey.contains("setting") || lowerKey.contains("env") || 
                      lowerKey.contains("mode") || lowerKey.contains("enable")) {
                categories.put("Configuration", categories.get("Configuration") + 1);
            } else {
                categories.put("Other", categories.get("Other") + 1);
            }
        }
        
        return categories;
    }
    
    /**
     * Extract environment variables from the collection analysis.
     */
    private Set<String> extractVariablesFromCollection(AnalysisResult collectionResult) {
        Set<String> variables = new HashSet<>();
        
        // Regular expression to find {{variable}} patterns
        Pattern pattern = Pattern.compile("\\{\\{([^\\}]+)\\}\\}");
        
        // Check URLs for variables
        for (Endpoint endpoint : collectionResult.getEndpoints()) {
            String url = endpoint.getUrl();
            if (url != null && !url.isEmpty()) {
                Matcher matcher = pattern.matcher(url);
                while (matcher.find()) {
                    variables.add(matcher.group(1));
                }
            }
            
            // Check test examples for variables
            Map<String, String> examples = endpoint.getTestExamples();
            if (examples != null) {
                for (String example : examples.values()) {
                    if (example != null) {
                        Matcher matcher = pattern.matcher(example);
                        while (matcher.find()) {
                            variables.add(matcher.group(1));
                        }
                    }
                }
            }
        }
        
        return variables;
    }
    
    /**
     * Generate recommendations for environment improvements.
     */
    private List<Recommendation> generateEnvironmentRecommendations(
            List<Map<String, Object>> variables, 
            Map<String, Integer> categories, 
            double namingScore,
            double usagePercent) {
        
        List<Recommendation> recommendations = new ArrayList<>();
        
        // Check naming conventions
        if (namingScore < 70.0 && !variables.isEmpty()) {
            recommendations.add(Recommendation.builder()
                    .type("naming-convention")
                    .severity("medium")
                    .description("Improve variable naming conventions")
                    .details("Consistent naming conventions make your environment more maintainable. " +
                             "Consider using snake_case or camelCase consistently.")
                    .example("Good: api_base_url, authToken, user_id\nAvoid: URL, a1, x")
                    .build());
        }
        
        // Check for unused variables
        if (usagePercent < 50.0 && !variables.isEmpty()) {
            recommendations.add(Recommendation.builder()
                    .type("unused-variables")
                    .severity("low")
                    .description("Remove unused environment variables")
                    .details(String.format("Only %.1f%% of your environment variables are used in the collection. " +
                                         "Consider removing unused variables.", usagePercent))
                    .example("// In collection requests, reference variables using double curly braces:\n{{base_url}}/api/users")
                    .build());
        }
        
        // Check for missing essential variables
        boolean hasUrl = categories.getOrDefault("URL", 0) > 0;
        if (!hasUrl) {
            recommendations.add(Recommendation.builder()
                    .type("missing-essential")
                    .severity("medium")
                    .description("Add base URL variable to environment")
                    .details("A base URL variable makes it easier to switch between different environments " +
                            "(e.g., dev, staging, production).")
                    .example("Variable name: base_url\nValue: https://api.example.com")
                    .build());
        }
        
        return recommendations;
    }
    
    /**
     * Calculate environment quality score.
     */
    private double calculateEnvironmentQualityScore(int variableCount, double namingScore, double usagePercent) {
        if (variableCount == 0) {
            return 0.0;
        }
        
        // Base score for having variables
        double score = 20.0;
        
        // Add points for good naming conventions
        score += namingScore * 0.4;
        
        // Add points for variables being used in the collection
        score += usagePercent * 0.4;
        
        return Math.min(100.0, score);
    }
}