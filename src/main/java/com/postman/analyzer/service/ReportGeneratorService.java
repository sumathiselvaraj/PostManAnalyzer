package com.postman.analyzer.service;

import org.springframework.stereotype.Service;

import com.postman.analyzer.model.AnalysisResult;
import com.postman.analyzer.model.Endpoint;
import com.postman.analyzer.model.Recommendation;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;

/**
 * Service for generating analysis reports.
 */
@Service
public class ReportGeneratorService {

    /**
     * Generate recommendations based on analysis results.
     * 
     * @param analysisResult The analysis results
     * @return List of recommendations
     */
    public List<Recommendation> generateRecommendations(AnalysisResult analysisResult) {
        List<Recommendation> recommendations = new ArrayList<>();
        
        // Check for overall test coverage issues
        if (analysisResult.getTestCount() == 0) {
            recommendations.add(createRecommendation(
                "test-coverage",
                "high",
                "Add tests to your API requests",
                "Your collection doesn't have any tests. Tests help ensure your API works correctly and catches regressions.",
                "pm.test(\"Status code is 200\", function() {\n    pm.response.to.have.status(200);\n});"
            ));
        } else if (analysisResult.getTestsPerRequest() < 1.0) {
            recommendations.add(createRecommendation(
                "test-coverage",
                "medium",
                "Increase test coverage across requests",
                "Your collection has low test coverage with an average of " + 
                String.format("%.1f", analysisResult.getTestsPerRequest()) + " tests per request.",
                "pm.test(\"Response is valid JSON\", function() {\n    pm.response.to.be.json;\n});"
            ));
        }
        
        // Check for missing test types
        Map<String, Double> testCoverage = analysisResult.getTestCoverage();
        if (testCoverage != null) {
            // Check for status code tests
            if (!testCoverage.containsKey("Status Code") || testCoverage.get("Status Code") < 80.0) {
                recommendations.add(createRecommendation(
                    "test-variety",
                    "high",
                    "Add status code validation tests",
                    "Status code validation is a fundamental API test that verifies the expected response code.",
                    "pm.test(\"Status code is 200\", function() {\n    pm.response.to.have.status(200);\n});"
                ));
            }
            
            // Check for JSON validation tests
            if (!testCoverage.containsKey("JSON Validation") || testCoverage.get("JSON Validation") < 60.0) {
                recommendations.add(createRecommendation(
                    "test-variety",
                    "medium",
                    "Add JSON response validation tests",
                    "JSON validation tests ensure the API response contains the expected data structure and values.",
                    "pm.test(\"Response has expected property\", function() {\n    var jsonData = pm.response.json();\n    pm.expect(jsonData).to.have.property('id');\n});"
                ));
            }
            
            // Check for schema validation tests
            if (!testCoverage.containsKey("Schema Validation") || testCoverage.get("Schema Validation") < 40.0) {
                recommendations.add(createRecommendation(
                    "test-variety",
                    "medium",
                    "Add schema validation tests",
                    "Schema validation ensures API responses conform to a defined data structure.",
                    "pm.test(\"Response matches schema\", function() {\n    var schema = { ... };\n    pm.expect(tv4.validate(pm.response.json(), schema)).to.be.true;\n});"
                ));
            }
        }
        
        // Check for error handling
        boolean hasErrorHandling = false;
        for (Endpoint endpoint : analysisResult.getEndpoints()) {
            if (endpoint.isHasErrorHandling()) {
                hasErrorHandling = true;
                break;
            }
        }
        
        if (!hasErrorHandling && !analysisResult.getEndpoints().isEmpty()) {
            recommendations.add(createRecommendation(
                "error-handling",
                "medium",
                "Add error handling in test scripts",
                "Error handling in tests makes them more robust and prevents test failures from unexpected responses.",
                "try {\n    var jsonData = pm.response.json();\n    pm.test(\"Valid data\", function() {\n        pm.expect(jsonData.id).to.exist;\n    });\n} catch (e) {\n    pm.test(\"Response parsing failed\", function() {\n        pm.expect.fail(\"Failed to parse response: \" + e.message);\n    });\n}"
            ));
        }
        
        // Check for dynamic data usage
        boolean usesDynamicData = false;
        for (Endpoint endpoint : analysisResult.getEndpoints()) {
            if (endpoint.isUsesDynamicData()) {
                usesDynamicData = true;
                break;
            }
        }
        
        if (!usesDynamicData && !analysisResult.getEndpoints().isEmpty()) {
            recommendations.add(createRecommendation(
                "data-driven",
                "medium",
                "Use environment variables for configurable tests",
                "Environment variables make your tests more flexible and easier to run in different environments.",
                "pm.test(\"Check expected value\", function() {\n    var expected = pm.environment.get(\"expectedValue\");\n    pm.expect(pm.response.json().value).to.equal(expected);\n});"
            ));
        }
        
        return recommendations;
    }
    
    /**
     * Create a recommendation object.
     */
    private Recommendation createRecommendation(String type, String severity, 
                                               String description, String details, String example) {
        return Recommendation.builder()
            .type(type)
            .severity(severity)
            .description(description)
            .details(details)
            .example(example)
            .build();
    }
}