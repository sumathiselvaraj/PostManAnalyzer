package com.postman.analyzer.service;

import org.springframework.stereotype.Service;

import com.postman.analyzer.model.Endpoint;
import com.postman.analyzer.model.ScriptAnalysis;

import java.util.List;
import java.util.Map;

/**
 * Service for scoring and evaluating Postman collections.
 */
@Service
public class ScoringEngine {
    
    /**
     * Calculate overall collection quality score.
     * 
     * @param endpoints List of analyzed endpoints
     * @param scriptAnalysis Script analysis results
     * @return Quality score (0-100)
     */
    public double calculateCollectionScore(List<Endpoint> endpoints, ScriptAnalysis scriptAnalysis) {
        if (endpoints == null || endpoints.isEmpty()) {
            return 0.0;
        }
        
        // Calculate the average endpoint score
        double totalScore = 0.0;
        for (Endpoint endpoint : endpoints) {
            totalScore += endpoint.getScore();
        }
        
        double avgEndpointScore = totalScore / endpoints.size();
        
        // Calculate the script complexity factor
        double scriptComplexityFactor = calculateScriptComplexityFactor(scriptAnalysis);
        
        // Calculate the test variety factor
        double testVarietyFactor = calculateTestVarietyFactor(endpoints);
        
        // Calculate the overall score as a weighted average
        double weightedScore = (avgEndpointScore * 0.6) + 
                              (scriptComplexityFactor * 0.2) + 
                              (testVarietyFactor * 0.2);
        
        // Make sure score is between 0 and 100
        return Math.min(100.0, Math.max(0.0, weightedScore));
    }
    
    /**
     * Calculate quality score for an endpoint.
     * 
     * @param name Endpoint name
     * @param url Endpoint URL
     * @param method HTTP method
     * @param testCount Number of tests
     * @param testTypes Map of test types and their counts
     * @param hasErrorHandling Whether the endpoint has error handling tests
     * @param usesDynamicData Whether the endpoint tests use dynamic data
     * @return Quality score (0-100)
     */
    public double calculateEndpointScore(String name, String url, String method, int testCount, 
                                         Map<String, Integer> testTypes, boolean hasErrorHandling, 
                                         boolean usesDynamicData) {
        double score = 0.0;
        
        // Base score for having tests
        if (testCount > 0) {
            score = 30.0;
            
            // Add points for each test, up to a maximum
            score += Math.min(testCount * 2, 20.0);
            
            // Add points for test variety
            score += Math.min(testTypes.size() * 5, 20.0);
            
            // Add points for important test types
            if (testTypes.containsKey("Status Code")) {
                score += 5.0;
            }
            
            if (testTypes.containsKey("JSON Validation")) {
                score += 5.0;
            }
            
            if (testTypes.containsKey("Schema Validation")) {
                score += 10.0;
            }
            
            // Add points for error handling
            if (hasErrorHandling) {
                score += 5.0;
            }
            
            // Add points for dynamic data usage
            if (usesDynamicData) {
                score += 5.0;
            }
        }
        
        // Make sure score is between 0 and 100
        return Math.min(100.0, score);
    }
    
    /**
     * Calculate a factor based on script complexity.
     */
    private double calculateScriptComplexityFactor(ScriptAnalysis scriptAnalysis) {
        if (scriptAnalysis == null) {
            return 0.0;
        }
        
        double factor = 0.0;
        
        // Factor based on scripts with assertions
        if (scriptAnalysis.getScriptCount() > 0) {
            double assertionRatio = (double) scriptAnalysis.getScriptsWithAssertions() / scriptAnalysis.getScriptCount();
            factor += assertionRatio * 40.0;
        }
        
        // Factor based on scripts using variables
        if (scriptAnalysis.getScriptCount() > 0) {
            double variableRatio = (double) scriptAnalysis.getScriptsUsingVariables() / scriptAnalysis.getScriptCount();
            factor += variableRatio * 20.0;
        }
        
        // Factor based on scripts using environment variables
        if (scriptAnalysis.getScriptCount() > 0) {
            double envVarRatio = (double) scriptAnalysis.getScriptsUsingEnvironmentVariables() / scriptAnalysis.getScriptCount();
            factor += envVarRatio * 20.0;
        }
        
        // Factor based on complexity distribution (more points for medium/high complexity)
        Map<String, Integer> complexityDist = scriptAnalysis.getComplexityDistribution();
        if (complexityDist != null && scriptAnalysis.getScriptCount() > 0) {
            int mediumCount = complexityDist.getOrDefault("Medium", 0);
            int highCount = complexityDist.getOrDefault("High", 0);
            
            double complexityRatio = (double) (mediumCount + highCount * 2) / (scriptAnalysis.getScriptCount() * 2);
            factor += complexityRatio * 20.0;
        }
        
        return Math.min(100.0, factor);
    }
    
    /**
     * Calculate a factor based on test variety.
     */
    private double calculateTestVarietyFactor(List<Endpoint> endpoints) {
        if (endpoints == null || endpoints.isEmpty()) {
            return 0.0;
        }
        
        // Count the total unique test types across all endpoints
        int totalUniqueTestTypes = countTotalUniqueTestTypes(endpoints);
        
        // Calculate the factor based on unique test types (more is better)
        double varietyFactor = Math.min(totalUniqueTestTypes * 20, 100.0);
        
        return varietyFactor;
    }
    
    /**
     * Count the total unique test types across all endpoints.
     */
    private int countTotalUniqueTestTypes(List<Endpoint> endpoints) {
        java.util.Set<String> uniqueTestTypes = new java.util.HashSet<>();
        
        for (Endpoint endpoint : endpoints) {
            Map<String, Integer> testTypes = endpoint.getTestTypes();
            if (testTypes != null) {
                uniqueTestTypes.addAll(testTypes.keySet());
            }
        }
        
        return uniqueTestTypes.size();
    }
}