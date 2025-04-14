package com.postman.analyzer.model;

import java.util.Map;

/**
 * Analysis results for test scripts in the Postman collection.
 */
public class ScriptAnalysis {
    
    private int scriptCount;
    private int totalLinesOfCode;
    private double avgLinesPerScript;
    private int scriptsWithAssertions;
    private int scriptsUsingVariables;
    private int scriptsUsingEnvironmentVariables;
    private Map<String, Integer> complexityDistribution;
    private Map<String, Integer> functionalityTypes;
    
    // Default constructor
    public ScriptAnalysis() {
    }
    
    // Parameterized constructor
    public ScriptAnalysis(int scriptCount, int totalLinesOfCode, double avgLinesPerScript,
                        int scriptsWithAssertions, int scriptsUsingVariables,
                        int scriptsUsingEnvironmentVariables,
                        Map<String, Integer> complexityDistribution,
                        Map<String, Integer> functionalityTypes) {
        this.scriptCount = scriptCount;
        this.totalLinesOfCode = totalLinesOfCode;
        this.avgLinesPerScript = avgLinesPerScript;
        this.scriptsWithAssertions = scriptsWithAssertions;
        this.scriptsUsingVariables = scriptsUsingVariables;
        this.scriptsUsingEnvironmentVariables = scriptsUsingEnvironmentVariables;
        this.complexityDistribution = complexityDistribution;
        this.functionalityTypes = functionalityTypes;
    }
    
    // Getters and setters
    public int getScriptCount() {
        return scriptCount;
    }
    
    public void setScriptCount(int scriptCount) {
        this.scriptCount = scriptCount;
    }
    
    public int getTotalLinesOfCode() {
        return totalLinesOfCode;
    }
    
    public void setTotalLinesOfCode(int totalLinesOfCode) {
        this.totalLinesOfCode = totalLinesOfCode;
    }
    
    public double getAvgLinesPerScript() {
        return avgLinesPerScript;
    }
    
    public void setAvgLinesPerScript(double avgLinesPerScript) {
        this.avgLinesPerScript = avgLinesPerScript;
    }
    
    public int getScriptsWithAssertions() {
        return scriptsWithAssertions;
    }
    
    public void setScriptsWithAssertions(int scriptsWithAssertions) {
        this.scriptsWithAssertions = scriptsWithAssertions;
    }
    
    public int getScriptsUsingVariables() {
        return scriptsUsingVariables;
    }
    
    public void setScriptsUsingVariables(int scriptsUsingVariables) {
        this.scriptsUsingVariables = scriptsUsingVariables;
    }
    
    public int getScriptsUsingEnvironmentVariables() {
        return scriptsUsingEnvironmentVariables;
    }
    
    public void setScriptsUsingEnvironmentVariables(int scriptsUsingEnvironmentVariables) {
        this.scriptsUsingEnvironmentVariables = scriptsUsingEnvironmentVariables;
    }
    
    public Map<String, Integer> getComplexityDistribution() {
        return complexityDistribution;
    }
    
    public void setComplexityDistribution(Map<String, Integer> complexityDistribution) {
        this.complexityDistribution = complexityDistribution;
    }
    
    public Map<String, Integer> getFunctionalityTypes() {
        return functionalityTypes;
    }
    
    public void setFunctionalityTypes(Map<String, Integer> functionalityTypes) {
        this.functionalityTypes = functionalityTypes;
    }
    
    // Builder pattern implementation
    public static ScriptAnalysisBuilder builder() {
        return new ScriptAnalysisBuilder();
    }
    
    public static class ScriptAnalysisBuilder {
        private int scriptCount;
        private int totalLinesOfCode;
        private double avgLinesPerScript;
        private int scriptsWithAssertions;
        private int scriptsUsingVariables;
        private int scriptsUsingEnvironmentVariables;
        private Map<String, Integer> complexityDistribution;
        private Map<String, Integer> functionalityTypes;
        
        public ScriptAnalysisBuilder scriptCount(int scriptCount) {
            this.scriptCount = scriptCount;
            return this;
        }
        
        public ScriptAnalysisBuilder totalLinesOfCode(int totalLinesOfCode) {
            this.totalLinesOfCode = totalLinesOfCode;
            return this;
        }
        
        public ScriptAnalysisBuilder avgLinesPerScript(double avgLinesPerScript) {
            this.avgLinesPerScript = avgLinesPerScript;
            return this;
        }
        
        public ScriptAnalysisBuilder scriptsWithAssertions(int scriptsWithAssertions) {
            this.scriptsWithAssertions = scriptsWithAssertions;
            return this;
        }
        
        public ScriptAnalysisBuilder scriptsUsingVariables(int scriptsUsingVariables) {
            this.scriptsUsingVariables = scriptsUsingVariables;
            return this;
        }
        
        public ScriptAnalysisBuilder scriptsUsingEnvironmentVariables(int scriptsUsingEnvironmentVariables) {
            this.scriptsUsingEnvironmentVariables = scriptsUsingEnvironmentVariables;
            return this;
        }
        
        public ScriptAnalysisBuilder complexityDistribution(Map<String, Integer> complexityDistribution) {
            this.complexityDistribution = complexityDistribution;
            return this;
        }
        
        public ScriptAnalysisBuilder functionalityTypes(Map<String, Integer> functionalityTypes) {
            this.functionalityTypes = functionalityTypes;
            return this;
        }
        
        public ScriptAnalysis build() {
            return new ScriptAnalysis(scriptCount, totalLinesOfCode, avgLinesPerScript,
                                    scriptsWithAssertions, scriptsUsingVariables,
                                    scriptsUsingEnvironmentVariables, complexityDistribution,
                                    functionalityTypes);
        }
    }
}