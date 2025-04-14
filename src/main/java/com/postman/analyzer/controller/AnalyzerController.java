package com.postman.analyzer.controller;

import java.io.IOException;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.postman.analyzer.model.AnalysisResult;
import com.postman.analyzer.service.CollectionAnalyzerService;
import com.postman.analyzer.service.EnvironmentAnalyzerService;
import com.postman.analyzer.service.ReportGeneratorService;

/**
 * Controller for the Postman Collection Analyzer web application.
 */
@Controller
public class AnalyzerController {
    
    @Autowired
    private CollectionAnalyzerService collectionAnalyzerService;
    
    @Autowired
    private EnvironmentAnalyzerService environmentAnalyzerService;
    
    @Autowired
    private ReportGeneratorService reportGeneratorService;
    
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    /**
     * Index page controller.
     */
    @GetMapping({"/", "/app", "/index"})
    public String index(Model model) {
        // Add a timestamp to prevent caching issues
        model.addAttribute("timestamp", System.currentTimeMillis());
        return "index";
    }
    
    /**
     * Alternative root mapping for the index page.
     */
    @GetMapping("/app/")
    public String indexSlash(Model model) {
        // Add a timestamp to prevent caching issues
        model.addAttribute("timestamp", System.currentTimeMillis());
        return "index";
    }
    
    /**
     * Analysis controller for file upload.
     */
    @PostMapping("/app/analyze")
    public String analyze(@RequestParam("collectionFile") MultipartFile collectionFile,
                           @RequestParam(value = "environmentFile", required = false) MultipartFile environmentFile,
                           RedirectAttributes redirectAttributes,
                           Model model) {
        
        try {
            // Parse the collection file
            if (collectionFile.isEmpty()) {
                model.addAttribute("error", "Please select a Postman collection file");
                return "index";
            }
            
            String collectionJson = new String(collectionFile.getBytes());
            Map<String, Object> collectionData = objectMapper.readValue(collectionJson, Map.class);
            
            // Parse the environment file if provided
            Map<String, Object> environmentData = null;
            if (environmentFile != null && !environmentFile.isEmpty()) {
                String environmentJson = new String(environmentFile.getBytes());
                environmentData = objectMapper.readValue(environmentJson, Map.class);
            }
            
            // Analyze the collection
            AnalysisResult result = collectionAnalyzerService.analyzeCollection(collectionData);
            
            // Analyze the environment if provided
            if (environmentData != null) {
                result.setEnvironmentInfo(environmentAnalyzerService.analyzeEnvironment(environmentData, result));
            }
            
            // Generate recommendations
            result.setRecommendations(reportGeneratorService.generateRecommendations(result));
            
            // Set the timestamp
            result.setTimestamp(LocalDateTime.now());
            
            // Store the result in the session
            model.addAttribute("result", result);
            
            return "report";
            
        } catch (IOException e) {
            model.addAttribute("error", "Error processing the file: " + e.getMessage());
            return "index";
        } catch (Exception e) {
            model.addAttribute("error", "An error occurred: " + e.getMessage());
            return "index";
        }
    }
    
    /**
     * Export report controller.
     */
    @GetMapping("/app/export")
    public String exportReport(@RequestParam("format") String format, Model model) {
        // Implementation for exporting the report in different formats
        // This would be implemented in a full version
        Map<String, String> exportFormats = new HashMap<>();
        exportFormats.put("pdf", "PDF Report");
        exportFormats.put("excel", "Excel Report");
        exportFormats.put("json", "JSON Data");
        
        model.addAttribute("exportFormats", exportFormats);
        
        return "export";
    }
}