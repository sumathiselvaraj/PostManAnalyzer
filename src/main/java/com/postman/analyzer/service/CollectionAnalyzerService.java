package com.postman.analyzer.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.postman.analyzer.model.AnalysisResult;
import com.postman.analyzer.model.CollectionInfo;
import com.postman.analyzer.model.Endpoint;
import com.postman.analyzer.model.ScriptAnalysis;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Service for analyzing Postman collections.
 */
@Service
public class CollectionAnalyzerService {

    @Autowired
    private ScoringEngine scoringEngine;

    /**
     * Analyze a Postman collection.
     * 
     * @param collectionData The parsed Postman collection JSON
     * @return Analysis results
     */
    public AnalysisResult analyzeCollection(Map<String, Object> collectionData) {
        // Extract basic collection information
        CollectionInfo collectionInfo = extractCollectionInfo(collectionData);
        
        // Extract and analyze all requests
        int folderCount = 0;
        List<Endpoint> endpoints = new ArrayList<>();
        Map<String, Object> items = getItems(collectionData);
        
        if (items != null) {
            ExtractResult result = extractAllRequests(items, folderCount);
            endpoints = result.getEndpoints();
            folderCount = result.getFolderCount();
        }
        
        // Analyze test scripts in the collection
        ScriptAnalysis scriptAnalysis = analyzeScripts(endpoints);
        
        // Calculate overall scores
        double overallScore = scoringEngine.calculateCollectionScore(endpoints, scriptAnalysis);
        
        // Build the analysis result
        return AnalysisResult.builder()
            .collectionInfo(collectionInfo)
            .requestCount(endpoints.size())
            .folderCount(folderCount)
            .endpointCount(endpoints.size())
            .testCount(countTests(endpoints))
            .testsPerRequest(calculateTestsPerRequest(endpoints))
            .testCoverage(calculateTestCoverage(endpoints))
            .scriptAnalysis(scriptAnalysis)
            .endpoints(endpoints)
            .overallScore(overallScore)
            .build();
    }
    
    /**
     * Extract basic information about the collection.
     */
    private CollectionInfo extractCollectionInfo(Map<String, Object> collectionData) {
        Map<String, Object> info = (Map<String, Object>) collectionData.get("info");
        if (info == null) {
            return CollectionInfo.builder()
                .name("Unknown Collection")
                .description("")
                .schema("")
                .version("")
                .build();
        }
        
        return CollectionInfo.builder()
            .name((String) info.getOrDefault("name", "Unknown Collection"))
            .description((String) info.getOrDefault("description", ""))
            .schema((String) info.getOrDefault("schema", ""))
            .version(extractVersion(info))
            .build();
    }
    
    /**
     * Extract version information from collection info.
     */
    private String extractVersion(Map<String, Object> info) {
        Object version = info.get("version");
        if (version instanceof Map) {
            return (String) ((Map<String, Object>) version).getOrDefault("major", "0") + "." +
                   ((Map<String, Object>) version).getOrDefault("minor", "0");
        }
        return "Unknown";
    }
    
    /**
     * Get the items array from the collection data.
     */
    @SuppressWarnings("unchecked")
    private Map<String, Object> getItems(Map<String, Object> collectionData) {
        if (collectionData.containsKey("item")) {
            return (Map<String, Object>) collectionData.get("item");
        } else if (collectionData.containsKey("items")) {
            return (Map<String, Object>) collectionData.get("items");
        }
        return null;
    }
    
    /**
     * Recursively extract all requests from the collection.
     */
    private ExtractResult extractAllRequests(Map<String, Object> items, int folderCount) {
        List<Endpoint> endpoints = new ArrayList<>();
        
        if (items == null) {
            return new ExtractResult(endpoints, folderCount);
        }
        
        for (Object item : items.values()) {
            if (item instanceof Map) {
                Map<String, Object> itemMap = (Map<String, Object>) item;
                
                // Check if this is a folder (has subitems)
                if (itemMap.containsKey("item")) {
                    folderCount++;
                    ExtractResult subResult = extractAllRequests((Map<String, Object>) itemMap.get("item"), folderCount);
                    endpoints.addAll(subResult.getEndpoints());
                    folderCount = subResult.getFolderCount();
                } else if (itemMap.containsKey("request")) {
                    // This is a request
                    Endpoint endpoint = analyzeRequest(itemMap);
                    endpoints.add(endpoint);
                }
            }
        }
        
        return new ExtractResult(endpoints, folderCount);
    }
    
    /**
     * Analyze a single request from the collection.
     */
    private Endpoint analyzeRequest(Map<String, Object> request) {
        Map<String, Object> requestData = (Map<String, Object>) request.get("request");
        String name = (String) request.getOrDefault("name", "Unnamed Request");
        
        String url = extractUrl(requestData);
        String method = extractMethod(requestData);
        
        // Analyze test scripts
        Map<String, Object> events = (Map<String, Object>) request.get("event");
        int testCount = 0;
        Map<String, Integer> testTypes = new HashMap<>();
        Map<String, String> testExamples = new HashMap<>();
        boolean hasErrorHandling = false;
        boolean usesDynamicData = false;
        boolean usesVariables = false;
        
        if (events != null) {
            for (Object event : events.values()) {
                if (event instanceof Map) {
                    Map<String, Object> eventMap = (Map<String, Object>) event;
                    String listen = (String) eventMap.get("listen");
                    
                    if ("test".equals(listen)) {
                        Map<String, Object> script = (Map<String, Object>) eventMap.get("script");
                        if (script != null) {
                            Object exec = script.get("exec");
                            if (exec instanceof List) {
                                String testScript = String.join("\n", (List<String>) exec);
                                
                                // Analyze test script
                                testCount = countTestsInScript(testScript);
                                testTypes = identifyTestTypes(testScript);
                                testExamples = extractTestExamples(testScript, testTypes);
                                hasErrorHandling = testScript.contains("catch") || testScript.contains("try");
                                usesDynamicData = testScript.contains("pm.variables") || testScript.contains("pm.environment");
                                usesVariables = testScript.contains("pm.variables") || testScript.contains("pm.globals");
                            }
                        }
                    }
                }
            }
        }
        
        // Calculate score for this endpoint
        double coverage = calculateCoverageScore(name, url, method, testCount, testTypes);
        double score = scoringEngine.calculateEndpointScore(name, url, method, testCount, 
                                                           testTypes, hasErrorHandling, usesDynamicData);
        
        return Endpoint.builder()
            .name(name)
            .url(url)
            .method(method)
            .testCount(testCount)
            .testTypes(testTypes)
            .testExamples(testExamples)
            .hasErrorHandling(hasErrorHandling)
            .usesDynamicData(usesDynamicData)
            .usesVariables(usesVariables)
            .coverage(coverage)
            .score(score)
            .build();
    }
    
    /**
     * Extract URL from request object.
     */
    private String extractUrl(Map<String, Object> request) {
        if (request == null) {
            return "";
        }
        
        Object url = request.get("url");
        
        if (url instanceof String) {
            return (String) url;
        } else if (url instanceof Map) {
            Map<String, Object> urlMap = (Map<String, Object>) url;
            return (String) urlMap.getOrDefault("raw", "");
        }
        
        return "";
    }
    
    /**
     * Extract HTTP method from request object.
     */
    private String extractMethod(Map<String, Object> request) {
        if (request == null) {
            return "GET";
        }
        
        return (String) request.getOrDefault("method", "GET");
    }
    
    /**
     * Count tests in a test script.
     */
    private int countTestsInScript(String testScript) {
        if (testScript == null || testScript.isEmpty()) {
            return 0;
        }
        
        int count = 0;
        // Count pm.test calls
        int index = testScript.indexOf("pm.test(");
        while (index >= 0) {
            count++;
            index = testScript.indexOf("pm.test(", index + 1);
        }
        
        // Count tests.* calls
        index = testScript.indexOf("tests[");
        while (index >= 0) {
            count++;
            index = testScript.indexOf("tests[", index + 1);
        }
        
        return count;
    }
    
    /**
     * Identify types of tests in the test script.
     */
    private Map<String, Integer> identifyTestTypes(String testScript) {
        Map<String, Integer> testTypes = new HashMap<>();
        
        if (testScript == null || testScript.isEmpty()) {
            return testTypes;
        }
        
        // Status code tests
        int statusCount = countOccurrences(testScript, "pm.response.code");
        if (statusCount > 0) {
            testTypes.put("Status Code", statusCount);
        }
        
        // Response time tests
        int responseTimeCount = countOccurrences(testScript, "pm.response.responseTime");
        if (responseTimeCount > 0) {
            testTypes.put("Response Time", responseTimeCount);
        }
        
        // JSON validation tests
        int jsonCount = countOccurrences(testScript, "pm.response.json");
        if (jsonCount > 0) {
            testTypes.put("JSON Validation", jsonCount);
        }
        
        // Header validation tests
        int headerCount = countOccurrences(testScript, "pm.response.headers");
        if (headerCount > 0) {
            testTypes.put("Header Validation", headerCount);
        }
        
        // Schema validation tests
        int schemaCount = countOccurrences(testScript, "tv4.validate") + 
                          countOccurrences(testScript, "ajv.validate");
        if (schemaCount > 0) {
            testTypes.put("Schema Validation", schemaCount);
        }
        
        // Error handling tests
        int errorCount = countOccurrences(testScript, "catch") + 
                         countOccurrences(testScript, "try");
        if (errorCount > 0) {
            testTypes.put("Error Handling", errorCount);
        }
        
        return testTypes;
    }
    
    /**
     * Extract examples of each test type from the test script.
     */
    private Map<String, String> extractTestExamples(String testScript, Map<String, Integer> testTypes) {
        Map<String, String> examples = new HashMap<>();
        
        if (testScript == null || testScript.isEmpty()) {
            return examples;
        }
        
        // For each test type, extract an example
        for (String testType : testTypes.keySet()) {
            String searchString;
            
            switch (testType) {
                case "Status Code":
                    searchString = "pm.response.code";
                    break;
                case "Response Time":
                    searchString = "pm.response.responseTime";
                    break;
                case "JSON Validation":
                    searchString = "pm.response.json";
                    break;
                case "Header Validation":
                    searchString = "pm.response.headers";
                    break;
                case "Schema Validation":
                    searchString = "tv4.validate";
                    if (!testScript.contains(searchString)) {
                        searchString = "ajv.validate";
                    }
                    break;
                case "Error Handling":
                    searchString = "try";
                    if (!testScript.contains(searchString)) {
                        searchString = "catch";
                    }
                    break;
                default:
                    searchString = "";
            }
            
            if (!searchString.isEmpty()) {
                int index = testScript.indexOf(searchString);
                if (index >= 0) {
                    // Find the surrounding test block (typically a line or a simple statement)
                    int lineStart = Math.max(0, testScript.lastIndexOf("\n", index));
                    int lineEnd = testScript.indexOf("\n", index);
                    if (lineEnd < 0) {
                        lineEnd = testScript.length();
                    }
                    
                    // Extract the example line
                    String example = testScript.substring(lineStart, lineEnd).trim();
                    examples.put(testType, example);
                }
            }
        }
        
        return examples;
    }
    
    /**
     * Count occurrences of a substring in a string.
     */
    private int countOccurrences(String text, String searchString) {
        if (text == null || text.isEmpty() || searchString == null || searchString.isEmpty()) {
            return 0;
        }
        
        int count = 0;
        int index = text.indexOf(searchString);
        while (index >= 0) {
            count++;
            index = text.indexOf(searchString, index + 1);
        }
        
        return count;
    }
    
    /**
     * Calculate coverage score for an endpoint.
     */
    private double calculateCoverageScore(String name, String url, String method, int testCount, Map<String, Integer> testTypes) {
        // Simple coverage score based on test count and variety
        double baseScore = 0;
        
        if (testCount > 0) {
            baseScore = 30.0; // Base score for having any tests
            
            // More tests = better score, up to a point
            baseScore += Math.min(testCount * 5, 20.0);
            
            // Variety of test types
            baseScore += Math.min(testTypes.size() * 10, 30.0);
        }
        
        // Make sure score is between 0 and 100
        return Math.min(100.0, baseScore);
    }
    
    /**
     * Count the total number of tests in all endpoints.
     */
    private int countTests(List<Endpoint> endpoints) {
        int total = 0;
        for (Endpoint endpoint : endpoints) {
            total += endpoint.getTestCount();
        }
        return total;
    }
    
    /**
     * Calculate average tests per request.
     */
    private double calculateTestsPerRequest(List<Endpoint> endpoints) {
        if (endpoints.isEmpty()) {
            return 0.0;
        }
        
        return (double) countTests(endpoints) / endpoints.size();
    }
    
    /**
     * Calculate test coverage by test type.
     */
    private Map<String, Double> calculateTestCoverage(List<Endpoint> endpoints) {
        Map<String, Double> coverage = new HashMap<>();
        
        if (endpoints.isEmpty()) {
            return coverage;
        }
        
        // Count each test type
        Map<String, Integer> testTypeCounts = new HashMap<>();
        for (Endpoint endpoint : endpoints) {
            Map<String, Integer> types = endpoint.getTestTypes();
            for (Map.Entry<String, Integer> entry : types.entrySet()) {
                String type = entry.getKey();
                Integer count = entry.getValue();
                
                testTypeCounts.put(type, testTypeCounts.getOrDefault(type, 0) + count);
            }
        }
        
        // Calculate percentage of endpoints with each test type
        int totalEndpoints = endpoints.size();
        for (Map.Entry<String, Integer> entry : testTypeCounts.entrySet()) {
            String type = entry.getKey();
            Integer count = entry.getValue();
            
            int endpointsWithType = 0;
            for (Endpoint endpoint : endpoints) {
                if (endpoint.getTestTypes().containsKey(type)) {
                    endpointsWithType++;
                }
            }
            
            double percentage = (double) endpointsWithType / totalEndpoints * 100.0;
            coverage.put(type, percentage);
        }
        
        return coverage;
    }
    
    /**
     * Analyze test scripts in the collection.
     */
    private ScriptAnalysis analyzeScripts(List<Endpoint> endpoints) {
        int scriptCount = 0;
        int totalLinesOfCode = 0;
        int scriptsWithAssertions = 0;
        int scriptsUsingVariables = 0;
        int scriptsUsingEnvironmentVariables = 0;
        Map<String, Integer> complexityDistribution = new HashMap<>();
        Map<String, Integer> functionalityTypes = new HashMap<>();
        
        complexityDistribution.put("Low", 0);
        complexityDistribution.put("Medium", 0);
        complexityDistribution.put("High", 0);
        
        for (Endpoint endpoint : endpoints) {
            if (endpoint.getTestCount() > 0) {
                scriptCount++;
                
                // Assume average lines per test
                int linesOfCode = endpoint.getTestCount() * 5; // Rough estimate
                totalLinesOfCode += linesOfCode;
                
                if (endpoint.getTestCount() > 0) {
                    scriptsWithAssertions++;
                }
                
                if (endpoint.isUsesVariables()) {
                    scriptsUsingVariables++;
                }
                
                if (endpoint.isUsesDynamicData()) {
                    scriptsUsingEnvironmentVariables++;
                }
                
                // Simple complexity heuristic
                if (endpoint.getTestCount() <= 2) {
                    complexityDistribution.put("Low", complexityDistribution.get("Low") + 1);
                } else if (endpoint.getTestCount() <= 5) {
                    complexityDistribution.put("Medium", complexityDistribution.get("Medium") + 1);
                } else {
                    complexityDistribution.put("High", complexityDistribution.get("High") + 1);
                }
                
                // Aggregate test types into functionality types
                for (String testType : endpoint.getTestTypes().keySet()) {
                    String functionType;
                    
                    switch (testType) {
                        case "Status Code":
                        case "Response Time":
                            functionType = "Basic Validation";
                            break;
                        case "JSON Validation":
                        case "Schema Validation":
                            functionType = "Data Validation";
                            break;
                        case "Header Validation":
                            functionType = "Header Validation";
                            break;
                        case "Error Handling":
                            functionType = "Error Handling";
                            break;
                        default:
                            functionType = "Other";
                    }
                    
                    functionalityTypes.put(functionType, functionalityTypes.getOrDefault(functionType, 0) + 1);
                }
            }
        }
        
        double avgLinesPerScript = scriptCount > 0 ? (double) totalLinesOfCode / scriptCount : 0;
        
        return ScriptAnalysis.builder()
            .scriptCount(scriptCount)
            .totalLinesOfCode(totalLinesOfCode)
            .avgLinesPerScript(avgLinesPerScript)
            .scriptsWithAssertions(scriptsWithAssertions)
            .scriptsUsingVariables(scriptsUsingVariables)
            .scriptsUsingEnvironmentVariables(scriptsUsingEnvironmentVariables)
            .complexityDistribution(complexityDistribution)
            .functionalityTypes(functionalityTypes)
            .build();
    }
    
    /**
     * Helper class for managing the recursive extraction of requests.
     */
    private static class ExtractResult {
        private final List<Endpoint> endpoints;
        private final int folderCount;
        
        public ExtractResult(List<Endpoint> endpoints, int folderCount) {
            this.endpoints = endpoints;
            this.folderCount = folderCount;
        }
        
        public List<Endpoint> getEndpoints() {
            return endpoints;
        }
        
        public int getFolderCount() {
            return folderCount;
        }
    }
}