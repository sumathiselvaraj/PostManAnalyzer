package com.postman.analyzer.util;

import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.stereotype.Component;

import java.util.HashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Component
public class JsonValidator {

    /**
     * Validate if the JSON data is a valid Postman collection
     * 
     * @param data The parsed JSON data
     * @return True if valid, False otherwise
     */
    public boolean isValidPostmanCollection(JsonNode data) {
        // Check for required keys that indicate this is a Postman collection
        if (data == null || !data.isObject()) {
            return false;
        }
        
        // Check for info section
        if (!data.has("info")) {
            return false;
        }
        
        JsonNode info = data.get("info");
        
        // Check for name in info
        if (!info.has("name")) {
            return false;
        }
        
        // Check for schema in info (should be a Postman schema URL)
        if (!info.has("schema")) {
            return false;
        }
        
        String schema = info.get("schema").asText();
        if (!schema.startsWith("https://schema.getpostman.com/")) {
            return false;
        }
        
        // Check for item array (contains requests or folders)
        if (!data.has("item") || !data.get("item").isArray()) {
            return false;
        }
        
        return true;
    }

    /**
     * Validate if the JSON data is a valid Postman environment
     * 
     * @param data The parsed JSON data
     * @return True if valid, False otherwise
     */
    public boolean isValidPostmanEnvironment(JsonNode data) {
        // Check for required keys that indicate this is a Postman environment
        if (data == null || !data.isObject()) {
            return false;
        }
        
        // Check for name
        if (!data.has("name")) {
            return false;
        }
        
        // Check for values array
        if (!data.has("values") || !data.get("values").isArray()) {
            return false;
        }
        
        // Check if values have the right structure
        JsonNode values = data.get("values");
        for (JsonNode value : values) {
            if (!value.isObject()) {
                return false;
            }
            
            // Each environment variable should have a key
            if (!value.has("key") || value.get("key").asText().isEmpty()) {
                return false;
            }
        }
        
        return true;
    }

    /**
     * Extract all variable references from a Postman collection
     * 
     * @param collectionStr The collection JSON as string
     * @return Set of variable names referenced in the collection
     */
    public Set<String> extractVariablesFromCollection(String collectionStr) {
        Pattern variablePattern = Pattern.compile("\\{\\{\\s*([\\w\\-\\.]+)\\s*\\}\\}");
        Matcher matcher = variablePattern.matcher(collectionStr);
        
        Set<String> referencedVariables = new HashSet<>();
        while (matcher.find()) {
            referencedVariables.add(matcher.group(1));
        }
        
        return referencedVariables;
    }

    /**
     * Extract the Postman collection format version
     * 
     * @param collectionData The parsed Postman collection JSON
     * @return Version (v1, v2, v2.1)
     */
    public String extractCollectionVersion(JsonNode collectionData) {
        if (collectionData.has("info") && collectionData.get("info").has("schema")) {
            String schema = collectionData.get("info").get("schema").asText();
            
            if (schema.contains("schema.getpostman.com/json/collection/v2.1.0")) {
                return "v2.1";
            } else if (schema.contains("schema.getpostman.com/json/collection/v2.0.0")) {
                return "v2.0";
            } else if (schema.contains("schema.getpostman.com/json/collection/v1.0.0")) {
                return "v1.0";
            }
        }
        
        return "unknown";
    }
}