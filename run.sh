#!/bin/bash

# Postman Collection Analyzer - Build and Run Script

echo "Building and running Postman Collection Analyzer..."

# Build with Maven
echo "Building with Maven..."
mvn clean package -DskipTests

if [ $? -ne 0 ]; then
    echo "Maven build failed!"
    exit 1
fi

# Run the application using embedded Jetty server
echo "Starting application on port 5000..."
java -cp "target/classes:target/dependency/*" com.postman.analyzer.Application

# Alternative: Run with Spring Boot
# java -jar target/postman-analyzer.jar