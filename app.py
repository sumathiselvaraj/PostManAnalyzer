"""
Flask application for Postman Collection Analyzer demonstration.
This is a proxy to showcase the functionality that would be implemented in the Java application.
"""

import os
import json
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
import pandas as pd

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# Helper functions to analyze Postman collections
def is_valid_postman_collection(data):
    """Validate if the JSON data is a valid Postman collection"""
    if not isinstance(data, dict):
        return False
    
    if 'info' not in data:
        return False
    
    info = data.get('info', {})
    if 'name' not in info:
        return False
    
    if 'schema' not in info:
        return False
    
    schema = info.get('schema', '')
    if not schema.startswith('https://schema.getpostman.com/'):
        return False
    
    if 'item' not in data or not isinstance(data['item'], list):
        return False
    
    return True

def is_valid_postman_environment(data):
    """Validate if the JSON data is a valid Postman environment"""
    if not isinstance(data, dict):
        return False
    
    if 'name' not in data:
        return False
    
    if 'values' not in data or not isinstance(data['values'], list):
        return False
    
    for value in data.get('values', []):
        if not isinstance(value, dict):
            return False
        
        if 'key' not in value or not value['key']:
            return False
    
    return True

def extract_variables_from_collection(collection_str):
    """Extract all variable references from a Postman collection"""
    pattern = r'\{\{\s*([\w\-\.]+)\s*\}\}'
    matches = re.findall(pattern, collection_str)
    return set(matches)

def extract_collection_info(collection_data):
    """Extract basic information about the collection"""
    info = collection_data.get('info', {})
    name = info.get('name', 'Unnamed Collection')
    description = info.get('description', '')
    schema = info.get('schema', '')
    version = extract_collection_version(collection_data)
    
    return {
        'name': name,
        'description': description,
        'schema': schema,
        'version': version
    }

def extract_collection_version(collection_data):
    """Extract the Postman collection format version"""
    schema = collection_data.get('info', {}).get('schema', '')
    
    if 'schema.getpostman.com/json/collection/v2.1.0' in schema:
        return 'v2.1'
    elif 'schema.getpostman.com/json/collection/v2.0.0' in schema:
        return 'v2.0'
    elif 'schema.getpostman.com/json/collection/v1.0.0' in schema:
        return 'v1.0'
    
    return 'unknown'

def extract_all_requests(collection_data, folder_count=0):
    """Recursively extract all requests from the collection"""
    all_requests = []
    
    items = collection_data.get('item', [])
    if not items:
        return {'requests': all_requests, 'folderCount': folder_count}
    
    for item in items:
        if 'request' in item:
            # This is a request
            request_data = {
                'name': item.get('name', ''),
                'request': item.get('request', {})
            }
            
            # Extract test scripts if present
            if 'event' in item and isinstance(item['event'], list):
                for event in item['event']:
                    if event.get('listen') == 'test' and 'script' in event and 'exec' in event['script']:
                        exec_data = event['script']['exec']
                        test_script = ''
                        
                        if isinstance(exec_data, list):
                            test_script = '\n'.join(exec_data)
                        elif isinstance(exec_data, str):
                            test_script = exec_data
                        
                        request_data['test_script'] = test_script
                        break
            
            all_requests.append(request_data)
        elif 'item' in item:
            # This is a folder, recurse
            folder_count += 1
            folder_results = extract_all_requests(item, folder_count)
            all_requests.extend(folder_results['requests'])
            folder_count = folder_results['folderCount']
    
    return {'requests': all_requests, 'folderCount': folder_count}

def analyze_request(request):
    """Analyze a single request from the collection"""
    name = request.get('name', '')
    request_data = request.get('request', {})
    
    # Extract URL and method
    url = extract_url(request_data)
    method = extract_method(request_data)
    
    # Analyze test script if present
    test_count = 0
    test_types = {}
    test_examples = {}
    uses_dynamic_data = False
    uses_variables = False
    has_error_handling = False
    coverage = 0.0
    
    if 'test_script' in request:
        test_script = request['test_script']
        
        # Count tests with pm.test()
        test_count = len(re.findall(r'pm\.test\(', test_script))
        
        # Identify test types
        test_types = identify_test_types(test_script)
        
        # Check for variable usage
        uses_variables = any(term in test_script for term in ['pm.environment', 'pm.globals', 'pm.variables'])
        
        # Check for dynamic data
        uses_dynamic_data = any(term in test_script for term in ['Math.random', 'new Date', 'moment(', 'faker'])
        
        # Check for error handling
        has_error_handling = 'try' in test_script and 'catch' in test_script
        
        # Extract example tests for each type
        test_examples = extract_test_examples(test_script, test_types)
        
        # Calculate coverage
        coverage = calculate_coverage_score(name, url, method, test_count, test_types)
    
    return {
        'name': name,
        'url': url,
        'method': method,
        'testCount': test_count,
        'testTypes': test_types,
        'testExamples': test_examples,
        'usesDynamicData': uses_dynamic_data,
        'usesVariables': uses_variables,
        'hasErrorHandling': has_error_handling,
        'coverage': coverage,
        'score': 0  # Will be calculated later
    }

def extract_url(request):
    """Extract URL from request object"""
    if 'url' in request:
        url_data = request['url']
        
        # Handle URL as string
        if isinstance(url_data, str):
            return url_data
        
        # Handle URL as object
        if isinstance(url_data, dict):
            if 'raw' in url_data:
                return url_data['raw']
            
            # Try to reconstruct from components
            if 'protocol' in url_data and 'host' in url_data and 'path' in url_data:
                url_parts = []
                
                # Protocol
                url_parts.append(f"{url_data['protocol']}://")
                
                # Host
                host = url_data['host']
                if isinstance(host, list):
                    url_parts.append('.'.join(host))
                elif isinstance(host, str):
                    url_parts.append(host)
                
                # Path
                path = url_data['path']
                if isinstance(path, list):
                    url_parts.append('/' + '/'.join(path))
                elif isinstance(path, str):
                    if not path.startswith('/'):
                        url_parts.append('/')
                    url_parts.append(path)
                
                return ''.join(url_parts)
    
    return "Unknown URL"

def extract_method(request):
    """Extract HTTP method from request object"""
    if 'method' in request:
        return request['method']
    return "GET"  # Default

def identify_test_types(test_script):
    """Identify the types of tests in the test script"""
    test_types = {}
    
    # Check for status code tests
    if any(term in test_script for term in ['status', 'pm.response.to.have.status', 'statusCode']):
        test_types['response_code'] = 1
    
    # Check for response time tests
    if any(term in test_script for term in ['responseTime', 'pm.response.responseTime']):
        test_types['response_time'] = 1
    
    # Check for JSON validation
    if any(term in test_script for term in ['pm.response.json', 'json()']):
        test_types['response_json'] = 1
    
    # Check for header validation
    if any(term in test_script for term in ['header', 'pm.response.headers']):
        test_types['response_header'] = 1
    
    # Check for schema validation
    if any(term in test_script for term in ['schema', 'tv4.validate', 'ajv']):
        test_types['schema_validation'] = 1
    
    # Check for data validation
    if any(term in test_script for term in ['pm.expect', 'to.eql', 'to.equal', 'to.deep.equal']):
        test_types['data_validation'] = 1
    
    # Check for authentication tests
    if any(term in test_script for term in ['token', 'auth', 'jwt', 'bearer']):
        test_types['authentication'] = 1
    
    # Check for authorization tests
    if any(term in test_script for term in ['permissions', 'authorize', 'role', 'access']):
        test_types['authorization'] = 1
    
    # Check for business logic tests
    if any(term in test_script for term in ['business', 'rules', 'logic', 'calculation']):
        test_types['business_logic'] = 1
    
    return test_types

def extract_test_examples(test_script, test_types):
    """Extract examples of each test type"""
    examples = {}
    
    for test_type in test_types:
        # Find example for this test type using regex patterns
        pattern = None
        
        if test_type == 'response_code':
            pattern = r'pm\.test\(.*?status.*?\{[\s\S]*?pm\.response\.to\.have\.status\([^;]*\)[\s\S]*?\}\)'
        elif test_type == 'response_time':
            pattern = r'pm\.test\(.*?time.*?\{[\s\S]*?responseTime[\s\S]*?\}\)'
        elif test_type == 'response_json':
            pattern = r'pm\.test\(.*?\{[\s\S]*?json\(\)[\s\S]*?\}\)'
        elif test_type == 'response_header':
            pattern = r'pm\.test\(.*?\{[\s\S]*?headers[\s\S]*?\}\)'
        elif test_type == 'schema_validation':
            pattern = r'pm\.test\(.*?schema.*?\{[\s\S]*?\}\)'
        elif test_type == 'data_validation':
            pattern = r'pm\.test\(.*?\{[\s\S]*?pm\.expect[\s\S]*?\}\)'
        # Add more patterns for other test types
        
        if pattern:
            match = re.search(pattern, test_script)
            if match:
                examples[test_type] = match.group(0)
    
    return examples

def calculate_coverage_score(name, url, method, test_count, test_types):
    """Calculate coverage score for an endpoint"""
    if test_count == 0:
        return 0.0
    
    # Calculate base coverage: 30% for having any tests
    coverage = 30.0
    
    # Add score for multiple test types
    test_type_count = len(test_types)
    coverage += test_type_count * 10  # 10% per test type
    
    # Cap at 100%
    return min(100.0, coverage)

def calculate_endpoint_score(endpoint):
    """Calculate quality score for an endpoint"""
    if endpoint['testCount'] == 0:
        return 0
    
    # Calculate test type coverage score
    test_types = endpoint['testTypes']
    test_type_weights = {
        'response_code': 0.15,      # Status code validation
        'response_json': 0.15,      # JSON structure validation
        'data_validation': 0.15,    # Specific data validation
        'schema_validation': 0.15,  # Schema validation
        'error_handling': 0.10,     # Error scenarios
        'authentication': 0.10,     # Authentication testing
        'authorization': 0.10,      # Authorization testing
        'response_header': 0.05,    # Header validation
        'response_time': 0.05,      # Performance validation
        'business_logic': 0.10,     # Business rules validation
    }
    
    total_weight = 0
    weighted_sum = 0
    
    for test_type in test_types:
        weight = test_type_weights.get(test_type, 0.05)
        weighted_sum += weight
        total_weight += weight
    
    test_type_score = (weighted_sum * 100 / total_weight) if total_weight > 0 else 0
    
    # Calculate implementation quality score
    implementation_quality = 50  # Default baseline
    
    # Adjust for various quality factors
    if endpoint['usesVariables']:
        implementation_quality += 10
    
    if endpoint['usesDynamicData']:
        implementation_quality += 15
    
    if endpoint['hasErrorHandling']:
        implementation_quality += 15
    
    # Adjust based on test count
    test_count_factor = min(1.0, endpoint['testCount'] / 5.0)  # Cap at 5 tests
    implementation_quality = implementation_quality * test_count_factor
    
    # Calculate final score (50% test types, 50% implementation)
    final_score = (test_type_score * 0.5) + (implementation_quality * 0.5)
    
    return min(100, max(0, round(final_score * 10) / 10))

def calculate_collection_score(analysis_result):
    """Calculate overall collection quality score"""
    # Score weights for different aspects of API tests
    score_weights = {
        'test_coverage': 0.3,       # How many endpoints have tests
        'test_depth': 0.2,          # How many different types of tests
        'test_quality': 0.2,        # Quality of test implementations
        'environment_usage': 0.1,   # Use of environment variables
        'documentation': 0.1,       # Documentation in tests
        'error_handling': 0.1,      # Error handling in tests
    }
    
    # Calculate test coverage score
    coverage_score = analysis_result['testCoverage'].get('overall', 0.0)
    
    # Calculate test depth score
    test_types = analysis_result['testCoverage']
    
    test_depth_score = 0
    if test_types:
        # Test type weights
        test_type_weights = {
            'response_code': 0.15,
            'response_json': 0.15,
            'data_validation': 0.15,
            'schema_validation': 0.15,
            'error_handling': 0.10,
            'authentication': 0.10,
            'authorization': 0.10,
            'response_header': 0.05,
            'response_time': 0.05,
            'business_logic': 0.10,
        }
        
        # Calculate weighted score based on coverage of each test type
        weighted_sum = 0
        total_weight = 0
        
        for test_type, coverage in test_types.items():
            # Skip the overall entry
            if test_type == 'overall':
                continue
            
            weight = test_type_weights.get(test_type, 0.05)
            weighted_sum += weight * coverage
            total_weight += weight
        
        test_depth_score = (weighted_sum * 100 / total_weight) if total_weight > 0 else 0
    
    # Calculate test quality score
    test_quality_score = min(100, analysis_result['scriptAnalysis']['avgComplexity'] * 25)
    
    # Calculate environment usage score
    environment_score = analysis_result['scriptAnalysis']['variableUsage']
    
    # Calculate documentation score (placeholder - would need more analysis)
    documentation_score = 50  # Default middle value
    
    # Calculate error handling score
    error_handling_score = analysis_result['scriptAnalysis']['errorHandling']
    
    # Calculate weighted total score
    total_score = (
        coverage_score * score_weights['test_coverage'] +
        test_depth_score * score_weights['test_depth'] +
        test_quality_score * score_weights['test_quality'] +
        environment_score * score_weights['environment_usage'] +
        documentation_score * score_weights['documentation'] +
        error_handling_score * score_weights['error_handling']
    )
    
    return round(total_score * 10) / 10

def generate_recommendations(analysis_result):
    """Generate recommendations based on analysis results"""
    recommendations = []
    
    # Check for empty or missing tests
    endpoints_without_tests = sum(1 for ep in analysis_result['endpoints'] if ep['testCount'] == 0)
    
    if endpoints_without_tests > 0:
        recommendations.append({
            'title': 'Add Tests for Uncovered Endpoints',
            'description': f"Found {endpoints_without_tests} endpoints without any tests. Add basic status code and response validation tests at minimum.",
            'severity': 'critical',
            'example': 'pm.test("Status code is 200", function () {\n    pm.response.to.have.status(200);\n});'
        })
    
    # Check test coverage by type
    test_coverage = analysis_result['testCoverage']
    for test_type, coverage in test_coverage.items():
        if test_type == 'overall':
            continue
        
        if coverage < 40:
            test_type_name = test_type.replace('_', ' ')
            test_type_name = test_type_name[0].upper() + test_type_name[1:]
            
            description = f"Only {round(coverage)}% of endpoints have {test_type_name} tests."
            example = get_example_for_test_type(test_type)
            
            recommendations.append({
                'title': f"Increase {test_type_name} Test Coverage",
                'description': description,
                'severity': 'important',
                'example': example
            })
    
    # Check for status code validation
    if test_coverage.get('response_code', 0.0) < 80:
        recommendations.append({
            'title': 'Add Status Code Validation',
            'description': 'Status code validation is a fundamental test that should be present for nearly all endpoints.',
            'severity': 'critical',
            'example': 'pm.test("Status code is successful", function () {\n    pm.response.to.be.success;\n});'
        })
    
    # Check for error handling
    if analysis_result['scriptAnalysis']['errorHandling'] < 50:
        recommendations.append({
            'title': 'Improve Error Handling in Tests',
            'description': 'Add error handling to your tests to make them more robust. Use try-catch blocks for parsing and validation.',
            'severity': 'important',
            'example': 'try {\n    const jsonData = pm.response.json();\n    pm.test("Response has expected data", function () {\n        pm.expect(jsonData).to.have.property("id");\n    });\n} catch (e) {\n    pm.test("Response body is valid JSON", function () {\n        pm.expect.fail("Invalid JSON response");\n    });\n}'
        })
    
    # Check for variable usage
    if analysis_result['scriptAnalysis']['variableUsage'] < 60:
        recommendations.append({
            'title': 'Use Environment Variables',
            'description': 'Increase the use of environment variables to make tests more maintainable and to run them across different environments.',
            'severity': 'medium',
            'example': 'pm.test("Response matches expected user ID", function () {\n    const jsonData = pm.response.json();\n    pm.expect(jsonData.userId).to.eql(pm.environment.get("user_id"));\n});'
        })
    
    # Add more recommendations as needed
    
    # Sort recommendations by severity
    severity_order = {'critical': 4, 'important': 3, 'medium': 2, 'low': 1}
    recommendations.sort(key=lambda x: severity_order.get(x['severity'], 0), reverse=True)
    
    return recommendations

def get_example_for_test_type(test_type):
    """Get example test code for a given test type"""
    examples = {
        'response_code': 'pm.test("Status code is 200", function () {\n    pm.response.to.have.status(200);\n});',
        'response_time': 'pm.test("Response time is acceptable", function () {\n    pm.expect(pm.response.responseTime).to.be.below(300);\n});',
        'response_json': 'pm.test("Response is valid JSON", function () {\n    const jsonData = pm.response.json();\n    pm.expect(jsonData).to.be.an("object");\n    pm.expect(jsonData).to.have.property("id");\n});',
        'response_header': 'pm.test("Content-Type header is present", function () {\n    pm.response.to.have.header("Content-Type");\n    pm.expect(pm.response.headers.get("Content-Type")).to.include("application/json");\n});',
        'schema_validation': 'const schema = {\n    "type": "object",\n    "required": ["id", "name"],\n    "properties": {\n        "id": { "type": "integer" },\n        "name": { "type": "string" }\n    }\n};\n\npm.test("Response matches schema", function () {\n    const jsonData = pm.response.json();\n    pm.expect(tv4.validate(jsonData, schema)).to.be.true;\n});',
        'data_validation': 'pm.test("Response data is valid", function () {\n    const jsonData = pm.response.json();\n    pm.expect(jsonData.active).to.be.true;\n    pm.expect(jsonData.items).to.be.an("array").that.is.not.empty;\n    pm.expect(jsonData.count).to.eql(jsonData.items.length);\n});',
    }
    
    return examples.get(test_type, "// Example test for this type not available")

def analyze_collection(collection_data):
    """Analyze a Postman collection"""
    # Extract basic collection info
    collection_info = extract_collection_info(collection_data)
    
    # Extract requests and analyze them
    folder_count = 0
    extract_result = extract_all_requests(collection_data, folder_count)
    requests = extract_result['requests']
    folder_count = extract_result['folderCount']
    
    # Analyze each request and build endpoints list
    endpoints = []
    test_coverage = {}
    test_types_present_count = {}
    
    total_test_count = 0
    script_analysis = {
        'avgComplexity': 0.0,
        'variableUsage': 0.0,
        'dynamicDataUsage': 0.0,
        'errorHandling': 0.0,
        'totalIfCount': 0,
        'totalLoopCount': 0,
        'totalFunctionCount': 0,
        'totalLinesOfCode': 0
    }
    
    for request in requests:
        endpoint = analyze_request(request)
        endpoints.append(endpoint)
        
        # Update test coverage statistics
        total_test_count += endpoint['testCount']
        
        # Count each test type
        for test_type in endpoint['testTypes']:
            test_types_present_count[test_type] = test_types_present_count.get(test_type, 0) + 1
        
        # Update script analysis
        if endpoint['testCount'] > 0:
            script_analysis['avgComplexity'] += 1
            
            if endpoint['usesVariables']:
                script_analysis['variableUsage'] += 1
            
            if endpoint['usesDynamicData']:
                script_analysis['dynamicDataUsage'] += 1
            
            if endpoint['hasErrorHandling']:
                script_analysis['errorHandling'] += 1
    
    # Calculate average script metrics
    requests_with_tests = sum(1 for e in endpoints if e['testCount'] > 0)
    
    if requests_with_tests > 0:
        script_analysis['avgComplexity'] = script_analysis['avgComplexity'] / requests_with_tests * 25
        script_analysis['variableUsage'] = script_analysis['variableUsage'] / requests_with_tests * 100
        script_analysis['dynamicDataUsage'] = script_analysis['dynamicDataUsage'] / requests_with_tests * 100
        script_analysis['errorHandling'] = script_analysis['errorHandling'] / requests_with_tests * 100
    
    # Calculate test coverage by types
    endpoint_count = len(endpoints)
    if endpoint_count > 0:
        for test_type, count in test_types_present_count.items():
            coverage = count / endpoint_count * 100
            test_coverage[test_type] = coverage
        
        # Add overall coverage
        endpoints_with_tests = sum(1 for e in endpoints if e['testCount'] > 0)
        overall_coverage = endpoints_with_tests / endpoint_count * 100
        test_coverage['overall'] = overall_coverage
    
    # Create analysis result
    analysis_result = {
        'collectionInfo': collection_info,
        'environmentInfo': None,
        'requestCount': len(requests),
        'folderCount': folder_count,
        'endpointCount': endpoint_count,
        'testCount': total_test_count,
        'testsPerRequest': total_test_count / len(requests) if requests else 0,
        'testCoverage': test_coverage,
        'scriptAnalysis': script_analysis,
        'endpoints': endpoints,
        'recommendations': [],
        'overallScore': 0,
        'timestamp': datetime.now().isoformat()
    }
    
    # Calculate scores for each endpoint
    for endpoint in endpoints:
        score = calculate_endpoint_score(endpoint)
        endpoint['score'] = score
    
    # Calculate overall collection score
    overall_score = calculate_collection_score(analysis_result)
    analysis_result['overallScore'] = overall_score
    
    # Generate recommendations
    recommendations = generate_recommendations(analysis_result)
    analysis_result['recommendations'] = recommendations
    
    return analysis_result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # Check if collection file was submitted
    if 'collection' not in request.files:
        return redirect(url_for('index'))
    
    collection_file = request.files['collection']
    
    # Check if filename is empty
    if collection_file.filename == '':
        return redirect(url_for('index'))
    
    # Parse Collection JSON
    try:
        collection_content = collection_file.read()
        collection_data = json.loads(collection_content)
        
        # Validate it's a Postman collection
        if not is_valid_postman_collection(collection_data):
            return render_template('index.html', error="The uploaded file is not a valid Postman collection")
        
        # Analyze collection
        analysis_result = analyze_collection(collection_data)
        
        # Add environment analysis if provided
        if 'environment' in request.files and request.files['environment'].filename != '':
            try:
                environment_file = request.files['environment']
                environment_content = environment_file.read()
                environment_data = json.loads(environment_content)
                
                if is_valid_postman_environment(environment_data):
                    # Basic environment info
                    environment_info = {
                        'name': environment_data.get('name', 'Unnamed Environment'),
                        'variableCount': len(environment_data.get('values', [])),
                        'qualityScore': 75.0,  # Placeholder
                    }
                    
                    analysis_result['environmentInfo'] = environment_info
            except Exception as e:
                print(f"Error analyzing environment: {e}")
        
        # Store in session
        session['analysis_result'] = analysis_result
        
        return redirect(url_for('report'))
        
    except Exception as e:
        print(f"Error analyzing files: {e}")
        return render_template('index.html', error=f"Error analyzing files: {str(e)}")

@app.route('/report')
def report():
    analysis_result = session.get('analysis_result')
    
    if not analysis_result:
        return redirect(url_for('index'))
    
    return render_template('report.html', report=analysis_result)

@app.route('/export/<format>')
def export_report(format):
    analysis_result = session.get('analysis_result')
    
    if not analysis_result:
        return redirect(url_for('index'))
    
    if format == 'pdf':
        # In a real implementation, we would generate a PDF here
        return "PDF export not implemented in demo version", 501
    elif format == 'excel':
        # Create a simple Excel export with pandas
        try:
            # Create a DataFrame with basic metrics
            df = pd.DataFrame({
                'Metric': [
                    'Collection Name', 
                    'Total Endpoints',
                    'Total Requests',
                    'Folders',
                    'Total Tests',
                    'Tests Per Request',
                    'Overall Coverage',
                    'Overall Score'
                ],
                'Value': [
                    analysis_result['collectionInfo']['name'],
                    analysis_result['endpointCount'],
                    analysis_result['requestCount'],
                    analysis_result['folderCount'],
                    analysis_result['testCount'],
                    round(analysis_result['testsPerRequest'], 2),
                    f"{round(analysis_result['testCoverage'].get('overall', 0), 2)}%",
                    f"{analysis_result['overallScore']}%"
                ]
            })
            
            # Create a second sheet with endpoints data
            endpoints_data = []
            for ep in analysis_result['endpoints']:
                endpoints_data.append({
                    'Name': ep['name'],
                    'Method': ep['method'],
                    'URL': ep['url'],
                    'Tests': ep['testCount'],
                    'Coverage': f"{ep['coverage']}%",
                    'Score': f"{ep['score']}%"
                })
            
            df_endpoints = pd.DataFrame(endpoints_data)
            
            # Create Excel with multiple sheets
            excel_file = 'temp_report.xlsx'
            with pd.ExcelWriter(excel_file) as writer:
                df.to_excel(writer, sheet_name='Summary', index=False)
                df_endpoints.to_excel(writer, sheet_name='Endpoints', index=False)
            
            return send_file(excel_file, 
                            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            as_attachment=True,
                            download_name='postman_analysis_report.xlsx')
        
        except Exception as e:
            print(f"Error generating Excel: {e}")
            return "Error generating Excel report", 500
    
    return "Invalid export format", 400

@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template('index.html', error="File too large. Maximum file size is 10MB."), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)