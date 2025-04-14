"""
Module for generating analysis reports
"""
import json
import datetime
import pandas as pd
import io
from collections import defaultdict

def generate_report(collection_analysis, environment_analysis=None):
    """
    Generate a comprehensive report from analysis results
    
    Args:
        collection_analysis (dict): Collection analysis results
        environment_analysis (dict, optional): Environment analysis results
    
    Returns:
        dict: Complete report data
    """
    # Start with collection analysis data
    report = collection_analysis.copy()
    
    # Add timestamp
    report['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Add environment analysis if available
    if environment_analysis:
        report['environment_info'] = environment_analysis['environment_info']
        report['environment_analysis'] = environment_analysis['environment_analysis']
        report['environment_recommendations'] = environment_analysis['environment_recommendations']
    
    # Generate recommendations
    report['recommendations'] = generate_recommendations(report)
    
    return report

def generate_recommendations(report):
    """
    Generate recommendations based on analysis results
    
    Args:
        report (dict): Analysis report
    
    Returns:
        list: List of recommendations
    """
    recommendations = []
    
    # Check for empty or missing tests
    endpoints_without_tests = sum(1 for ep in report['endpoints'] if ep['test_count'] == 0)
    if endpoints_without_tests > 0:
        recommendations.append({
            'title': 'Add Tests for Uncovered Endpoints',
            'description': f'Found {endpoints_without_tests} endpoints without any tests. Add basic status code and response validation tests at minimum.',
            'severity': 'critical',
            'example': 'pm.test("Status code is 200", function () {\n    pm.response.to.have.status(200);\n});'
        })
    
    # Check test coverage by type
    test_coverage = report['test_coverage'].get('by_type', {})
    for test_type, coverage in test_coverage.items():
        if coverage < 40:
            test_type_name = test_type.replace('_', ' ').title()
            description = f'Only {coverage}% of endpoints have {test_type_name} tests.'
            example = get_example_for_test_type(test_type)
            
            recommendations.append({
                'title': f'Increase {test_type_name} Test Coverage',
                'description': description,
                'severity': 'important',
                'example': example
            })
    
    # Check for status code validation
    if test_coverage.get('response_code', 0) < 80:
        recommendations.append({
            'title': 'Add Status Code Validation',
            'description': 'Status code validation is a fundamental test that should be present for nearly all endpoints.',
            'severity': 'critical',
            'example': 'pm.test("Status code is successful", function () {\n    pm.response.to.be.success;\n});'
        })
    
    # Check for error handling
    if report['script_analysis']['error_handling'] < 50:
        recommendations.append({
            'title': 'Improve Error Handling in Tests',
            'description': 'Add error handling to your tests to make them more robust. Use try-catch blocks for parsing and validation.',
            'severity': 'important',
            'example': 'try {\n    const jsonData = pm.response.json();\n    pm.test("Response has expected data", function () {\n        pm.expect(jsonData).to.have.property("id");\n    });\n} catch (e) {\n    pm.test("Response body is valid JSON", function () {\n        pm.expect.fail("Invalid JSON response");\n    });\n}'
        })
    
    # Check for variable usage
    if report['script_analysis']['variable_usage'] < 60:
        recommendations.append({
            'title': 'Use Environment Variables',
            'description': 'Increase the use of environment variables to make tests more maintainable and to run them across different environments.',
            'severity': 'medium',
            'example': 'pm.test("Response matches expected user ID", function () {\n    const jsonData = pm.response.json();\n    pm.expect(jsonData.userId).to.eql(pm.environment.get("user_id"));\n});'
        })
    
    # Check for dynamic data usage
    if report['script_analysis']['dynamic_data_usage'] < 40:
        recommendations.append({
            'title': 'Use Dynamic Data Generation',
            'description': 'Tests that use dynamic data are more robust. Use functions like Math.random() or Date() to generate test data.',
            'severity': 'medium',
            'example': 'const randomName = "User_" + Math.floor(Math.random() * 10000);\npm.environment.set("random_user_name", randomName);\n\npm.test("User created with random name", function () {\n    const jsonData = pm.response.json();\n    pm.expect(jsonData.name).to.eql(randomName);\n});'
        })
    
    # Check for schema validation
    if test_coverage.get('schema_validation', 0) < 30:
        recommendations.append({
            'title': 'Add Schema Validation',
            'description': 'Schema validation helps ensure API responses match expected data structures. Add JSON schema validation to critical endpoints.',
            'severity': 'important',
            'example': 'const schema = {\n    "type": "object",\n    "required": ["id", "name", "email"],\n    "properties": {\n        "id": { "type": "integer" },\n        "name": { "type": "string" },\n        "email": { "type": "string", "format": "email" }\n    }\n};\n\npm.test("Response matches schema", function () {\n    const jsonData = pm.response.json();\n    pm.expect(tv4.validate(jsonData, schema)).to.be.true;\n});'
        })
    
    # Check script complexity
    if report['script_analysis']['avg_complexity'] < 2:
        recommendations.append({
            'title': 'Increase Test Depth',
            'description': 'Your tests have low complexity, suggesting basic validations only. Add more comprehensive tests to validate data format, content, and business rules.',
            'severity': 'medium',
            'example': '// Instead of just testing status code:\npm.test("Status code is 200", function () {\n    pm.response.to.have.status(200);\n});\n\n// Also test response structure and data:\npm.test("Response has expected data structure", function () {\n    const jsonData = pm.response.json();\n    pm.expect(jsonData).to.be.an("object");\n    pm.expect(jsonData).to.have.property("items");\n    pm.expect(jsonData.items).to.be.an("array");\n});\n\npm.test("Response data passes validation", function () {\n    const jsonData = pm.response.json();\n    pm.expect(jsonData.items).to.have.lengthOf.at.least(1);\n    pm.expect(jsonData.items[0]).to.have.property("id");\n    pm.expect(jsonData.items[0].id).to.be.a("number");\n});'
        })
    
    # Add collection-level recommendations
    if report['folder_count'] <= 1 and report['request_count'] > 5:
        recommendations.append({
            'title': 'Organize Requests into Folders',
            'description': 'Group related requests into folders for better organization and easier maintenance.',
            'severity': 'low'
        })
    
    # Add request naming recommendation if needed
    if has_generic_request_names(report):
        recommendations.append({
            'title': 'Use Descriptive Request Names',
            'description': 'Give each request a descriptive name that indicates its purpose and expected outcome. For example, "Get User Profile" is better than "GET /user".',
            'severity': 'low'
        })
    
    # Add recommendation for Authentication tests
    if test_coverage.get('authentication', 0) < 20:
        recommendations.append({
            'title': 'Add Authentication Tests',
            'description': 'Add specific tests for authentication to ensure your API security is working correctly. Test both successful authentication and failure cases.',
            'severity': 'important',
            'example': 'pm.test("Unauthorized access should be rejected", function () {\n    pm.response.to.have.status(401);\n});\n\n// After authentication:\npm.test("Auth token is received", function () {\n    const jsonData = pm.response.json();\n    pm.expect(jsonData).to.have.property("token");\n    pm.environment.set("auth_token", jsonData.token);\n});'
        })
    
    # Add authorization tests recommendation if needed
    if test_coverage.get('authorization', 0) < 20:
        recommendations.append({
            'title': 'Add Authorization Tests',
            'description': 'Test proper authorization by verifying that different user roles can only access appropriate resources.',
            'severity': 'important',
            'example': 'pm.test("Admin resources not accessible by regular user", function () {\n    pm.response.to.have.status(403);\n});\n\n// With admin token:\npm.test("Admin can access all resources", function () {\n    pm.response.to.have.status(200);\n    const jsonData = pm.response.json();\n    pm.expect(jsonData).to.have.property("adminControls");\n});'
        })
    
    # Add response time tests if missing
    if test_coverage.get('response_time', 0) < 30:
        recommendations.append({
            'title': 'Add Performance Validation',
            'description': 'Add response time validation to ensure your API meets performance requirements.',
            'severity': 'medium',
            'example': 'pm.test("Response time is acceptable", function () {\n    pm.expect(pm.response.responseTime).to.be.below(300);\n});'
        })
    
    return sorted(recommendations, key=lambda x: severity_score(x['severity']), reverse=True)

def severity_score(severity):
    """Map severity string to numeric score for sorting"""
    scores = {
        'critical': 4,
        'important': 3,
        'medium': 2,
        'low': 1
    }
    return scores.get(severity, 0)

def get_example_for_test_type(test_type):
    """Get example test code for a given test type"""
    examples = {
        'response_code': 'pm.test("Status code is 200", function () {\n    pm.response.to.have.status(200);\n});',
        
        'response_time': 'pm.test("Response time is acceptable", function () {\n    pm.expect(pm.response.responseTime).to.be.below(300);\n});',
        
        'response_json': 'pm.test("Response is valid JSON", function () {\n    const jsonData = pm.response.json();\n    pm.expect(jsonData).to.be.an("object");\n    pm.expect(jsonData).to.have.property("id");\n});',
        
        'response_header': 'pm.test("Content-Type header is present", function () {\n    pm.response.to.have.header("Content-Type");\n    pm.expect(pm.response.headers.get("Content-Type")).to.include("application/json");\n});',
        
        'schema_validation': 'const schema = {\n    "type": "object",\n    "required": ["id", "name"],\n    "properties": {\n        "id": { "type": "integer" },\n        "name": { "type": "string" }\n    }\n};\n\npm.test("Response matches schema", function () {\n    const jsonData = pm.response.json();\n    pm.expect(tv4.validate(jsonData, schema)).to.be.true;\n});',
        
        'data_validation': 'pm.test("Response data is valid", function () {\n    const jsonData = pm.response.json();\n    pm.expect(jsonData.active).to.be.true;\n    pm.expect(jsonData.items).to.be.an("array").that.is.not.empty;\n    pm.expect(jsonData.count).to.eql(jsonData.items.length);\n});',
        
        'error_handling': 'try {\n    const jsonData = pm.response.json();\n    pm.test("Data is valid", function () {\n        pm.expect(jsonData).to.have.property("result");\n    });\n} catch (e) {\n    pm.test("Response body is valid JSON", function () {\n        pm.expect.fail("Invalid JSON response: " + e.message);\n    });\n}',
        
        'authentication': 'pm.test("Authentication works correctly", function () {\n    const jsonData = pm.response.json();\n    pm.expect(jsonData).to.have.property("token");\n    pm.environment.set("auth_token", jsonData.token);\n});\n\npm.test("Token is valid format", function () {\n    const jsonData = pm.response.json();\n    pm.expect(jsonData.token).to.match(/^[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+\\.[A-Za-z0-9-_.+/=]*$/);\n});',
        
        'authorization': 'pm.test("Authorization restricts access correctly", function () {\n    pm.response.to.have.status(403);\n    const jsonData = pm.response.json();\n    pm.expect(jsonData).to.have.property("error");\n    pm.expect(jsonData.error).to.include("permissions");\n});',
        
        'business_logic': 'pm.test("Business logic is enforced", function () {\n    const jsonData = pm.response.json();\n    pm.expect(jsonData.orderTotal).to.eql(jsonData.items.reduce((sum, item) => sum + item.price * item.quantity, 0));\n    pm.expect(jsonData.status).to.be.oneOf(["pending", "processing", "shipped", "delivered"]);\n});'
    }
    
    return examples.get(test_type, "// Example test for this type not available")

def has_generic_request_names(report):
    """Check if the collection has generic request names"""
    generic_names = ['request', 'api', 'test', 'endpoint', 'http']
    
    for endpoint in report.get('endpoints', []):
        name = endpoint.get('name', '').lower()
        
        # Check if name is very short
        if len(name) < 5:
            return True
        
        # Check if name is just the HTTP method and/or URL
        if endpoint.get('method', '').lower() in name and name.count(' ') <= 1:
            return True
        
        # Check if name uses generic terms only
        if any(generic in name for generic in generic_names) and len(name.split()) <= 2:
            return True
    
    return False

def generate_pdf_report(report):
    """
    Generate a PDF version of the report
    
    Args:
        report (dict): Report data
    
    Returns:
        bytes: PDF file as bytes
    """
    # This would normally use a PDF generation library like ReportLab
    # For this implementation, we'll just return a placeholder
    
    # For a real implementation, this would create a formatted PDF with
    # - Executive summary
    # - Collection overview
    # - Test coverage charts
    # - Endpoint analysis
    # - Recommendations
    
    # Placeholder implementation
    pdf_content = b"PDF report content would be generated here"
    return pdf_content

def generate_excel_report(report):
    """
    Generate an Excel version of the report
    
    Args:
        report (dict): Report data
    
    Returns:
        bytes: Excel file as bytes
    """
    # Create a pandas Excel writer
    output = io.BytesIO()
    
    # Create DataFrames for each sheet
    
    # Summary sheet
    summary_data = {
        'Metric': [
            'Collection Name', 
            'Overall Score', 
            'Test Coverage', 
            'Total Endpoints', 
            'Total Requests',
            'Total Tests',
            'Tests Per Request'
        ],
        'Value': [
            report['collection_info']['name'],
            f"{report['overall_score']}%",
            f"{report['test_coverage']['overall']}%",
            report['endpoint_count'],
            report['request_count'],
            report['test_count'],
            report['tests_per_request']
        ]
    }
    summary_df = pd.DataFrame(summary_data)
    
    # Endpoints sheet
    endpoints_data = []
    for ep in report['endpoints']:
        endpoints_data.append({
            'Endpoint': f"{ep['method']} {ep['url']}",
            'Name': ep['name'],
            'Tests': ep['test_count'],
            'Coverage': f"{ep['coverage']}%",
            'Score': f"{ep['score']}%"
        })
    endpoints_df = pd.DataFrame(endpoints_data)
    
    # Test Coverage sheet
    coverage_data = {
        'Test Type': list(report['test_coverage']['by_type'].keys()),
        'Coverage (%)': list(report['test_coverage']['by_type'].values())
    }
    coverage_df = pd.DataFrame(coverage_data)
    
    # Recommendations sheet
    recommendations_data = []
    for rec in report['recommendations']:
        recommendations_data.append({
            'Title': rec['title'],
            'Description': rec['description'],
            'Severity': rec['severity']
        })
    recommendations_df = pd.DataFrame(recommendations_data)
    
    # Write each DataFrame to a different sheet
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        endpoints_df.to_excel(writer, sheet_name='Endpoints', index=False)
        coverage_df.to_excel(writer, sheet_name='Test Coverage', index=False)
        recommendations_df.to_excel(writer, sheet_name='Recommendations', index=False)
        
        # Add environment sheet if available
        if 'environment_info' in report:
            env_data = {
                'Metric': [
                    'Environment Name',
                    'Variables Count',
                    'Quality Score',
                    'Variables with Initial Value',
                    'Variables with Current Value',
                    'Variables Used in Collection',
                    'Naming Convention Quality'
                ],
                'Value': [
                    report['environment_info']['name'],
                    report['environment_info']['variable_count'],
                    f"{report['environment_info']['quality_score']}%",
                    f"{report['environment_analysis']['variables_with_initial_value']}%",
                    f"{report['environment_analysis']['variables_with_current_value']}%",
                    f"{report['environment_analysis']['variables_used_in_collection']}%",
                    f"{report['environment_analysis']['naming_convention_quality']}%"
                ]
            }
            env_df = pd.DataFrame(env_data)
            env_df.to_excel(writer, sheet_name='Environment', index=False)
            
            # Environment recommendations
            env_rec_data = []
            for rec in report.get('environment_recommendations', []):
                env_rec_data.append({
                    'Title': rec['title'],
                    'Description': rec['description'],
                    'Severity': rec['severity']
                })
            if env_rec_data:
                env_rec_df = pd.DataFrame(env_rec_data)
                env_rec_df.to_excel(writer, sheet_name='Env Recommendations', index=False)
    
    # Get the Excel file as bytes
    output.seek(0)
    return output.getvalue()
