"""
Module for analyzing Postman collection files
"""
import re
import json
from collections import defaultdict

def analyze_collection(collection_data):
    """
    Analyze a Postman collection JSON
    
    Args:
        collection_data (dict): The parsed Postman collection JSON
    
    Returns:
        dict: Analysis results
    """
    # Initialize results
    results = {
        'collection_info': extract_collection_info(collection_data),
        'endpoints': [],
        'request_count': 0,
        'folder_count': 0,
        'test_count': 0,
        'tests_per_request': 0,
        'test_coverage': {
            'overall': 0,
            'by_type': {}
        },
        'test_types': {},
        'script_analysis': {
            'avg_complexity': 0,
            'dynamic_data_usage': 0,
            'variable_usage': 0,
            'error_handling': 0
        },
        'endpoint_scores': {},
        'overall_score': 0
    }
    
    # Extract all requests (items)
    all_requests, folder_count = extract_all_requests(collection_data)
    results['folder_count'] = folder_count
    results['request_count'] = len(all_requests)
    
    # Analyze each request
    endpoints = []
    total_tests = 0
    requests_with_tests = 0
    requests_with_dynamic_data = 0
    requests_with_variables = 0
    requests_with_error_handling = 0
    test_types_count = defaultdict(int)
    test_types_examples = defaultdict(list)
    test_types_missing = defaultdict(list)
    
    for request in all_requests:
        endpoint_analysis = analyze_request(request)
        endpoints.append(endpoint_analysis)
        
        # Update counts
        total_tests += endpoint_analysis['test_count']
        if endpoint_analysis['test_count'] > 0:
            requests_with_tests += 1
        if endpoint_analysis['uses_dynamic_data']:
            requests_with_dynamic_data += 1
        if endpoint_analysis['uses_variables']:
            requests_with_variables += 1
        if endpoint_analysis['has_error_handling']:
            requests_with_error_handling += 1
            
        # Update test types
        for test_type, count in endpoint_analysis['test_types'].items():
            test_types_count[test_type] += count
            if count > 0 and len(test_types_examples[test_type]) < 3:
                # Add example if available and we don't have too many yet
                if 'test_examples' in endpoint_analysis and test_type in endpoint_analysis['test_examples']:
                    test_types_examples[test_type].append(endpoint_analysis['test_examples'][test_type])
            elif count == 0:
                # Track missing test types
                endpoint_key = f"{endpoint_analysis['method']} {endpoint_analysis['url']}"
                test_types_missing[test_type].append(endpoint_key)
    
    # Calculate average tests per request
    results['tests_per_request'] = round(total_tests / max(1, results['request_count']), 2)
    results['test_count'] = total_tests
    
    # Calculate test coverage
    if results['request_count'] > 0:
        results['test_coverage']['overall'] = round((requests_with_tests / results['request_count']) * 100, 1)
    
    # Calculate script analysis metrics
    if results['request_count'] > 0:
        results['script_analysis']['dynamic_data_usage'] = round((requests_with_dynamic_data / results['request_count']) * 100, 1)
        results['script_analysis']['variable_usage'] = round((requests_with_variables / results['request_count']) * 100, 1)
        results['script_analysis']['error_handling'] = round((requests_with_error_handling / results['request_count']) * 100, 1)
    
    # Calculate complexity (based on average number of test types per request)
    if requests_with_tests > 0:
        avg_test_types_per_request = sum(1 for r in endpoints if r['test_count'] > 0) / requests_with_tests
        results['script_analysis']['avg_complexity'] = round(avg_test_types_per_request, 2)
    
    # Process test types
    test_type_descriptions = {
        'response_code': 'Verifies the HTTP status code of the response',
        'response_time': 'Checks if the API responds within an acceptable time frame',
        'response_json': 'Validates the structure or content of JSON responses',
        'response_header': 'Verifies response headers like Content-Type',
        'schema_validation': 'Ensures the response matches an expected schema',
        'data_validation': 'Validates specific data in the response',
        'error_handling': 'Tests how API handles error conditions',
        'authentication': 'Validates authentication mechanisms',
        'authorization': 'Checks authorization and permissions',
        'business_logic': 'Tests that verify business rules are enforced'
    }
    
    for test_type, count in test_types_count.items():
        coverage = 0
        if results['request_count'] > 0:
            coverage = round((count / results['request_count']) * 100, 1)
        
        results['test_coverage']['by_type'][test_type] = coverage
        
        results['test_types'][test_type] = {
            'count': count,
            'coverage': coverage,
            'description': test_type_descriptions.get(test_type, 'Custom test type'),
            'examples': test_types_examples.get(test_type, []),
            'missing_for': test_types_missing.get(test_type, [])[:5]  # Limit to 5 examples
        }
    
    # Calculate endpoint scores
    for endpoint in endpoints:
        score = calculate_endpoint_score(endpoint)
        endpoint['score'] = score
        results['endpoint_scores'][f"{endpoint['method']} {endpoint['url']}"] = score
    
    # Calculate overall score
    results['overall_score'] = calculate_overall_score(results)
    
    # Sort endpoints by score (descending)
    results['endpoints'] = sorted(endpoints, key=lambda x: x['score'], reverse=True)
    
    return results

def extract_collection_info(collection_data):
    """Extract basic information about the collection"""
    info = collection_data.get('info', {})
    return {
        'name': info.get('name', 'Unknown Collection'),
        'description': info.get('description', ''),
        'schema': info.get('schema', ''),
        'version': info.get('version', 'Unknown')
    }

def extract_all_requests(collection_data, folder_count=0):
    """
    Recursively extract all requests from the collection
    
    Args:
        collection_data (dict): The collection or folder data
        folder_count (int): Counter for folders
    
    Returns:
        tuple: (list of requests, folder count)
    """
    all_requests = []
    
    # Process items at current level
    items = collection_data.get('item', [])
    for item in items:
        # Check if this is a folder (has items) or a request
        if 'item' in item:
            # This is a folder
            folder_count += 1
            folder_requests, folder_count = extract_all_requests(item, folder_count)
            all_requests.extend(folder_requests)
        else:
            # This is a request
            all_requests.append(item)
    
    return all_requests, folder_count

def analyze_request(request):
    """
    Analyze a single request from the collection
    
    Args:
        request (dict): The request data
    
    Returns:
        dict: Analysis results for this request
    """
    # Initialize result
    result = {
        'name': request.get('name', 'Unnamed Request'),
        'url': extract_url(request),
        'method': extract_method(request),
        'test_count': 0,
        'test_types': defaultdict(int),
        'test_examples': {},
        'uses_dynamic_data': False,
        'uses_variables': False,
        'has_error_handling': False,
        'coverage': 0,
        'score': 0
    }
    
    # Analyze tests in event scripts
    events = request.get('event', [])
    for event in events:
        if event.get('listen') == 'test':
            test_script = event.get('script', {}).get('exec', [])
            if isinstance(test_script, list):
                test_script = '\n'.join(test_script)
            
            # Count tests
            test_count = test_script.count('pm.test(')
            result['test_count'] = test_count
            
            # Identify test types
            result['test_types'] = identify_test_types(test_script)
            
            # Collect examples
            result['test_examples'] = extract_test_examples(test_script, result['test_types'])
            
            # Check for dynamic data usage
            if re.search(r'pm\.environment|pm\.globals|pm\.variables', test_script):
                result['uses_variables'] = True
            
            # Check for dynamic data generation or parsing
            if re.search(r'JSON\.parse|pm\.response\.json\(\)|Math\.random|Date|moment', test_script):
                result['uses_dynamic_data'] = True
                
            # Check for error handling
            if re.search(r'try\s*{|catch\s*\(|if\s*\(.*(error|fail|exception)', test_script, re.IGNORECASE):
                result['has_error_handling'] = True
    
    # Calculate basic coverage percentage
    result['coverage'] = calculate_coverage_score(result)
    
    return result

def extract_url(request):
    """Extract URL from request object"""
    url = request.get('request', {}).get('url', {})
    
    # Handle string URLs
    if isinstance(url, str):
        return url
    
    # Handle object URLs
    if isinstance(url, dict):
        # Try the 'raw' property first
        if 'raw' in url:
            return url['raw']
        
        # Otherwise, try to reconstruct from path
        path = url.get('path', [])
        if path:
            return '/' + '/'.join([str(segment) for segment in path])
    
    return 'unknown_url'

def extract_method(request):
    """Extract HTTP method from request object"""
    method = request.get('request', {}).get('method', 'GET')
    return method

def identify_test_types(test_script):
    """
    Identify the types of tests in the test script
    
    Args:
        test_script (str): The test script content
    
    Returns:
        dict: Count of each test type
    """
    test_types = defaultdict(int)
    
    # Response code tests
    if re.search(r'pm\.response\.code|pm\.expect\(pm\.response\.code\)|status\s*===|status\s*==|statusCode', test_script):
        test_types['response_code'] = len(re.findall(r'pm\.response\.code|pm\.expect\(pm\.response\.code\)|status\s*===|status\s*==|statusCode', test_script))
    
    # Response time tests
    if re.search(r'pm\.response\.responseTime|responseTime|response\.time', test_script):
        test_types['response_time'] = len(re.findall(r'pm\.response\.responseTime|responseTime|response\.time', test_script))
    
    # Response JSON/body tests
    if re.search(r'pm\.response\.json\(\)|pm\.response\.body|response\.json|body\[|JSON\.parse', test_script):
        test_types['response_json'] = len(re.findall(r'pm\.response\.json\(\)|pm\.response\.body|response\.json|body\[|JSON\.parse', test_script))
    
    # Response header tests
    if re.search(r'pm\.response\.headers|headers\.|\.header|Content-Type|Authorization', test_script):
        test_types['response_header'] = len(re.findall(r'pm\.response\.headers|headers\.|\.header|Content-Type|Authorization', test_script))
    
    # Schema validation
    if re.search(r'tv4\.validate|ajv|schema|jsonSchema', test_script):
        test_types['schema_validation'] = len(re.findall(r'tv4\.validate|ajv|schema|jsonSchema', test_script))
    
    # Data validation
    if re.search(r'\.to\.equal|\.to\.eql|\.to\.deep\.equal|\.to\.include|\.to\.have|expect\(.*\)\.to\.be|assert\.', test_script):
        test_types['data_validation'] = len(re.findall(r'\.to\.equal|\.to\.eql|\.to\.deep\.equal|\.to\.include|\.to\.have|expect\(.*\)\.to\.be|assert\.', test_script))
    
    # Error handling
    if re.search(r'try\s*{|catch\s*\(|if\s*\(.*(error|fail|exception)', test_script, re.IGNORECASE):
        test_types['error_handling'] = len(re.findall(r'try\s*{|catch\s*\(|if\s*\(.*(error|fail|exception)', test_script, re.IGNORECASE))
    
    # Authentication tests
    if re.search(r'auth|token|jwt|bearer|basic|oauth|login|credential', test_script, re.IGNORECASE):
        test_types['authentication'] = len(re.findall(r'auth|token|jwt|bearer|basic|oauth|login|credential', test_script, re.IGNORECASE))
    
    # Authorization tests
    if re.search(r'permission|access|role|privilege|admin|user\.can|authorized|forbidden|401|403', test_script, re.IGNORECASE):
        test_types['authorization'] = len(re.findall(r'permission|access|role|privilege|admin|user\.can|authorized|forbidden|401|403', test_script, re.IGNORECASE))
    
    # Business logic tests (harder to detect, using some common patterns)
    if re.search(r'business|logic|rule|calculate|validate|verify|check|ensure', test_script, re.IGNORECASE):
        test_types['business_logic'] = 1  # Just assume 1 for now
    
    return dict(test_types)

def extract_test_examples(test_script, test_types):
    """
    Extract examples of each test type
    
    Args:
        test_script (str): The test script content
        test_types (dict): The identified test types
    
    Returns:
        dict: Examples for each test type
    """
    examples = {}
    
    # Extract lines with pm.test 
    test_lines = re.findall(r'pm\.test\(.*\)', test_script)
    
    # Map lines to test types
    for test_type in test_types:
        for line in test_lines:
            if test_type == 'response_code' and re.search(r'status|code|200|201|400|404|500', line, re.IGNORECASE):
                examples[test_type] = line.strip()
                break
            elif test_type == 'response_time' and re.search(r'time|ms|seconds|performance', line, re.IGNORECASE):
                examples[test_type] = line.strip()
                break
            elif test_type == 'response_json' and re.search(r'json|body|response.*data', line, re.IGNORECASE):
                examples[test_type] = line.strip()
                break
            elif test_type == 'response_header' and re.search(r'header|content-type|content', line, re.IGNORECASE):
                examples[test_type] = line.strip()
                break
            elif test_type == 'schema_validation' and re.search(r'schema|format|valid', line, re.IGNORECASE):
                examples[test_type] = line.strip()
                break
            elif test_type == 'data_validation' and re.search(r'data|value|field|property|match', line, re.IGNORECASE):
                examples[test_type] = line.strip()
                break
            elif test_type == 'error_handling' and re.search(r'error|exception|fail', line, re.IGNORECASE):
                examples[test_type] = line.strip()
                break
            elif test_type == 'authentication' and re.search(r'auth|token|login', line, re.IGNORECASE):
                examples[test_type] = line.strip()
                break
            elif test_type == 'authorization' and re.search(r'permission|access|authorize', line, re.IGNORECASE):
                examples[test_type] = line.strip()
                break
            elif test_type == 'business_logic' and re.search(r'business|logic|rule|calculation', line, re.IGNORECASE):
                examples[test_type] = line.strip()
                break
    
    return examples

def calculate_coverage_score(endpoint_analysis):
    """
    Calculate coverage score for an endpoint
    
    Args:
        endpoint_analysis (dict): Analysis data for an endpoint
    
    Returns:
        float: Coverage score (0-100)
    """
    if endpoint_analysis['test_count'] == 0:
        return 0
    
    # Basic weights for different test types
    weights = {
        'response_code': 15,
        'response_json': 15,
        'data_validation': 15,
        'schema_validation': 15,
        'error_handling': 10,
        'authentication': 10,
        'authorization': 10,
        'response_header': 5,
        'response_time': 5,
        'business_logic': 10
    }
    
    # Calculate weighted score
    total_weight = sum(weights.values())
    covered_weight = 0
    
    for test_type, weight in weights.items():
        if endpoint_analysis['test_types'].get(test_type, 0) > 0:
            covered_weight += weight
    
    return round((covered_weight / total_weight) * 100, 1)

def calculate_endpoint_score(endpoint_analysis):
    """
    Calculate overall quality score for an endpoint
    
    Args:
        endpoint_analysis (dict): Analysis data for an endpoint
    
    Returns:
        float: Quality score (0-100)
    """
    if endpoint_analysis['test_count'] == 0:
        return 0
    
    # Base score from coverage
    base_score = endpoint_analysis['coverage']
    
    # Adjust score based on additional factors
    adjustments = 0
    
    # Bonus for using variables
    if endpoint_analysis['uses_variables']:
        adjustments += 5
    
    # Bonus for using dynamic data
    if endpoint_analysis['uses_dynamic_data']:
        adjustments += 5
    
    # Bonus for error handling
    if endpoint_analysis['has_error_handling']:
        adjustments += 10
    
    # Bonus/penalty based on number of test types
    test_type_count = len(endpoint_analysis['test_types'])
    if test_type_count >= 5:
        adjustments += 10
    elif test_type_count >= 3:
        adjustments += 5
    elif test_type_count <= 1:
        adjustments -= 10
    
    # Adjust the score, keeping it within 0-100
    final_score = min(100, max(0, base_score + adjustments))
    
    return round(final_score, 1)

def calculate_overall_score(analysis):
    """
    Calculate overall collection quality score
    
    Args:
        analysis (dict): Collection analysis results
    
    Returns:
        float: Quality score (0-100)
    """
    # If no endpoints or no tests, score is 0
    if not analysis['endpoints'] or analysis['test_count'] == 0:
        return 0
    
    # Base score is the average of endpoint scores
    endpoint_scores = [ep['score'] for ep in analysis['endpoints']]
    base_score = sum(endpoint_scores) / len(endpoint_scores)
    
    # Adjust score based on collection-level metrics
    adjustments = 0
    
    # Adjust based on test coverage
    if analysis['test_coverage']['overall'] >= 80:
        adjustments += 10
    elif analysis['test_coverage']['overall'] >= 50:
        adjustments += 5
    elif analysis['test_coverage']['overall'] <= 20:
        adjustments -= 10
    
    # Adjust based on test distribution
    if analysis['tests_per_request'] >= 3:
        adjustments += 5
    elif analysis['tests_per_request'] <= 1:
        adjustments -= 5
    
    # Adjust based on script complexity
    if analysis['script_analysis']['avg_complexity'] >= 3:
        adjustments += 5
    elif analysis['script_analysis']['avg_complexity'] <= 1:
        adjustments -= 5
    
    # Adjust based on test type coverage
    test_type_coverage = analysis['test_coverage'].get('by_type', {})
    coverage_sum = sum(test_type_coverage.values())
    coverage_count = len(test_type_coverage)
    
    if coverage_count > 0:
        avg_type_coverage = coverage_sum / coverage_count
        if avg_type_coverage >= 70:
            adjustments += 10
        elif avg_type_coverage >= 40:
            adjustments += 5
        elif avg_type_coverage <= 20:
            adjustments -= 5
    
    # Calculate final score
    final_score = min(100, max(0, base_score + adjustments))
    
    return round(final_score, 1)
