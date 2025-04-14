package com.postman.analyzer.model;

/**
 * Represents basic information about a Postman collection.
 */
public class CollectionInfo {
    
    private String name;
    private String description;
    private String schema;
    private String version;
    
    // Default constructor
    public CollectionInfo() {
    }
    
    // Parameterized constructor
    public CollectionInfo(String name, String description, String schema, String version) {
        this.name = name;
        this.description = description;
        this.schema = schema;
        this.version = version;
    }
    
    // Getters and setters
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getDescription() {
        return description;
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public String getSchema() {
        return schema;
    }
    
    public void setSchema(String schema) {
        this.schema = schema;
    }
    
    public String getVersion() {
        return version;
    }
    
    public void setVersion(String version) {
        this.version = version;
    }
    
    // Builder pattern implementation
    public static CollectionInfoBuilder builder() {
        return new CollectionInfoBuilder();
    }
    
    public static class CollectionInfoBuilder {
        private String name;
        private String description;
        private String schema;
        private String version;
        
        public CollectionInfoBuilder name(String name) {
            this.name = name;
            return this;
        }
        
        public CollectionInfoBuilder description(String description) {
            this.description = description;
            return this;
        }
        
        public CollectionInfoBuilder schema(String schema) {
            this.schema = schema;
            return this;
        }
        
        public CollectionInfoBuilder version(String version) {
            this.version = version;
            return this;
        }
        
        public CollectionInfo build() {
            return new CollectionInfo(name, description, schema, version);
        }
    }
}