package com.postman.analyzer;

import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.server.handler.ContextHandler;
import org.eclipse.jetty.server.handler.HandlerList;
import org.eclipse.jetty.server.handler.ResourceHandler;
import org.eclipse.jetty.servlet.DefaultServlet;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;
import org.eclipse.jetty.util.resource.Resource;
import org.springframework.web.context.ContextLoaderListener;
import org.springframework.web.context.WebApplicationContext;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;
import org.springframework.web.servlet.DispatcherServlet;

import com.postman.analyzer.config.WebConfig;

/**
 * Main application class for the Postman Collection Analyzer.
 * Sets up an embedded Jetty server with Spring MVC.
 */
public class Application {
    private static final int PORT = 5000;
    
    public static void main(String[] args) throws Exception {
        Server server = new Server(PORT);
        
        // Create static resource handler
        ResourceHandler resourceHandler = new ResourceHandler();
        resourceHandler.setDirectoriesListed(false);
        resourceHandler.setWelcomeFiles(new String[]{"index.html"});
        resourceHandler.setResourceBase("src/main/webapp");
        
        ContextHandler staticContextHandler = new ContextHandler("/static");
        staticContextHandler.setHandler(resourceHandler);
        
        // Create the Spring application context
        WebApplicationContext context = getWebApplicationContext();
        
        // Set up Spring MVC
        ServletContextHandler servletContextHandler = new ServletContextHandler(ServletContextHandler.SESSIONS);
        servletContextHandler.setContextPath("/");
        
        // Spring DispatcherServlet for handling MVC requests
        ServletHolder dispatcherServletHolder = new ServletHolder("dispatcher", new DispatcherServlet(context));
        dispatcherServletHolder.setInitOrder(1);
        servletContextHandler.addServlet(dispatcherServletHolder, "/app/*");
        servletContextHandler.addServlet(dispatcherServletHolder, "/app");
        servletContextHandler.addServlet(dispatcherServletHolder, "/");
        
        // Default servlet for static files
        ServletHolder defaultServletHolder = new ServletHolder("default", DefaultServlet.class);
        defaultServletHolder.setInitParameter("resourceBase", "src/main/webapp");
        defaultServletHolder.setInitParameter("dirAllowed", "false");
        servletContextHandler.addServlet(defaultServletHolder, "/resources/*");
        
        // Add Spring ContextLoaderListener
        servletContextHandler.addEventListener(new ContextLoaderListener(context));
        servletContextHandler.setInitParameter("contextConfigLocation", "com.postman.analyzer.config.WebConfig");
        
        // Combine handlers
        HandlerList handlers = new HandlerList();
        handlers.addHandler(staticContextHandler);
        handlers.addHandler(servletContextHandler);
        
        // Set the handlers on the server
        server.setHandler(handlers);
        
        // Start the server
        try {
            server.start();
            System.out.println("Server started on port " + PORT);
            System.out.println("Visit http://localhost:" + PORT + " to access the application");
            server.join();
        } catch (Exception e) {
            System.err.println("Error starting server: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
    
    private static WebApplicationContext getWebApplicationContext() {
        AnnotationConfigWebApplicationContext context = new AnnotationConfigWebApplicationContext();
        context.register(WebConfig.class);
        context.setConfigLocation("com.postman.analyzer.config");
        return context;
    }
}