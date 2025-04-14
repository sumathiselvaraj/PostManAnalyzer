"""
Utility functions for Postman Collection Analyzer
"""
import re
import json
from collections import defaultdict

def is_valid_postman_collection(data):
    """
    Validate if the JSON data is a valid Postman collection
    
    Args:
        data (dict): The parsed JSON data
    
    Returns:
        bool: True if valid, False otherwise
    """
    # Check for required keys that indicate this is a Postman collection
    if not isinstance(data, dict):
        return False
    
    # Check for info section
    if 'info' not in data:
        return False
    
    info = data.get('info', {})
    
    # Check for name in info
    if 'name' not in info:
        return False
    
    # Check for schema in info (should be a Postman schema URL)
    if 'schema' not in info:
        return False
    
    schema = info.get('schema', '')
    if not isinstance(schema, str) or not schema.startswith('https://schema.getpostman.com/'):
        return False
    
    # Check for item array (contains requests or folders)
    if 'item' not in data or not isinstance(data['item'], list):
        return False
    
    return True

def is_valid_postman_environment(data):
    """
    Validate if the JSON data is a valid Postman environment
    
    Args:
        data (dict): The parsed JSON data
    
    Returns:
        bool: True if valid, False otherwise
    """
    # Check for required keys that indicate this is a Postman environment
    if not isinstance(data, dict):
        return False
    
    # Check for name
    if 'name' not in data:
        return False
    
    # Check for values array
    if 'values' not in data or not isinstance(data['values'], list):
        return False
    
    # Check if values have the right structure
    for value in data.get('values', []):
        if not isinstance(value, dict):
            return False
        
        # Each environment variable should have a key
        if 'key' not in value or not value['key']:
            return False
    
    return True

def extract_variables_from_collection(collection_data):
    """
    Extract all variable references from a Postman collection
    
    Args:
        collection_data (dict): The parsed Postman collection JSON
    
    Returns:
        set: Set of variable names referenced in the collection
    """
    variable_pattern = re.compile(r'{{\s*([\w\-\.]+)\s*}}')
    referenced_variables = set()
    collection_str = json.dumps(collection_data)
    
    # Find all variable references in the collection JSON
    matches = variable_pattern.findall(collection_str)
    referenced_variables.update(matches)
    
    return referenced_variables

def extract_test_assertions(test_script):
    """
    Extract test assertions from a Postman test script
    
    Args:
        test_script (str): The test script content
    
    Returns:
        list: List of test assertions
    """
    # Pattern to match pm.test statements
    test_pattern = re.compile(r'pm\.test\(\s*[\'"`](.*?)[\'"`]')
    
    # Find all test assertions
    matches = test_pattern.findall(test_script)
    
    return matches

def categorize_assertions(assertions):
    """
    Categorize test assertions into groups
    
    Args:
        assertions (list): List of test assertion descriptions
    
    Returns:
        dict: Categories and counts
    """
    categories = defaultdict(int)
    
    for assertion in assertions:
        assertion_lower = assertion.lower()
        
        # Status code tests
        if any(term in assertion_lower for term in ['status', 'code', '200', '201', '400', '404', '500']):
            categories['status_code'] += 1
        
        # Response time tests
        elif any(term in assertion_lower for term in ['time', 'performance', 'fast', 'slow']):
            categories['response_time'] += 1
        
        # Header tests
        elif any(term in assertion_lower for term in ['header', 'content-type', 'content type']):
            categories['headers'] += 1
        
        # Body/data tests
        elif any(term in assertion_lower for term in ['body', 'response', 'data', 'json']):
            categories['response_body'] += 1
        
        # Schema tests
        elif any(term in assertion_lower for term in ['schema', 'structure', 'format']):
            categories['schema'] += 1
            
        # Authentication tests
        elif any(term in assertion_lower for term in ['auth', 'token', 'login', 'credential']):
            categories['authentication'] += 1
            
        # Error handling
        elif any(term in assertion_lower for term in ['error', 'fail', 'exception', 'invalid']):
            categories['error_handling'] += 1
            
        # Business logic
        elif any(term in assertion_lower for term in ['business', 'logic', 'calculation', 'rule']):
            categories['business_logic'] += 1
            
        # Other tests
        else:
            categories['other'] += 1
    
    return dict(categories)

def analyze_script_complexity(test_script):
    """
    Analyze the complexity of a test script
    
    Args:
        test_script (str): The test script content
    
    Returns:
        dict: Complexity metrics
    """
    # Count number of test assertions
    test_count = test_script.count('pm.test(')
    
    # Count conditional logic
    if_count = len(re.findall(r'\bif\s*\(', test_script))
    
    # Count loops
    loop_count = len(re.findall(r'\bfor\s*\(|\bwhile\s*\(|\bforeach\s*\(', test_script))
    
    # Count function definitions
    function_count = len(re.findall(r'function\s+\w+\s*\(', test_script))
    
    # Check for error handling
    has_error_handling = bool(re.search(r'try\s*{|catch\s*\(|if\s*\(.*(error|fail|exception)', test_script, re.IGNORECASE))
    
    # Check for variable usage
    uses_variables = bool(re.search(r'pm\.environment|pm\.globals|pm\.variables', test_script))
    
    # Count lines of code (approximate)
    loc = len(test_script.split('\n'))
    
    return {
        'test_count': test_count,
        'if_count': if_count,
        'loop_count': loop_count,
        'function_count': function_count,
        'has_error_handling': has_error_handling,
        'uses_variables': uses_variables,
        'lines_of_code': loc,
        # Complexity score (0-5 scale)
        'complexity_score': min(5, (test_count * 0.5 + if_count * 0.3 + loop_count * 0.7 + 
                                  function_count * 0.5 + (5 if has_error_handling else 0)) / 5)
    }

def clean_url(url):
    """
    Clean and normalize a URL for comparison
    
    Args:
        url (str): URL to clean
    
    Returns:
        str: Cleaned URL
    """
    # Remove query parameters
    url = url.split('?')[0]
    
    # Remove trailing slash
    if url.endswith('/'):
        url = url[:-1]
    
    # Replace path parameters with placeholders
    url = re.sub(r'\/[0-9a-f]{8,}(?:-[0-9a-f]{4,}){3,}-[0-9a-f]{12,}', '/:uuid', url)
    url = re.sub(r'\/[0-9]+', '/:id', url)
    
    return url

def group_similar_endpoints(endpoints):
    """
    Group similar endpoints together
    
    Args:
        endpoints (list): List of endpoint URLs
    
    Returns:
        dict: Grouped endpoints
    """
    groups = defaultdict(list)
    
    for endpoint in endpoints:
        # Clean and normalize the URL
        clean_endpoint = clean_url(endpoint)
        groups[clean_endpoint].append(endpoint)
    
    return dict(groups)

def parse_postman_request_url(request_url):
    """
    Parse a Postman request URL (handles both string and object formats)
    
    Args:
        request_url: URL from Postman request (can be string or object)
    
    Returns:
        str: Full URL string
    """
    if isinstance(request_url, str):
        return request_url
    
    # Handle URL as object
    if isinstance(request_url, dict):
        # Try to use raw URL if available
        if 'raw' in request_url:
            return request_url['raw']
        
        # Otherwise, reconstruct from components
        protocol = request_url.get('protocol', 'http')
        host = request_url.get('host', [])
        if isinstance(host, list):
            host = '.'.join(host)
        
        path = request_url.get('path', [])
        if isinstance(path, list):
            path = '/' + '/'.join(path)
        elif not path.startswith('/'):
            path = '/' + path
            
        return f"{protocol}://{host}{path}"
    
    return "unknown_url"

def extract_collection_version(collection_data):
    """
    Extract the Postman collection format version
    
    Args:
        collection_data (dict): The parsed Postman collection JSON
    
    Returns:
        str: Version (v1, v2, v2.1)
    """
    schema = collection_data.get('info', {}).get('schema', '')
    
    if 'schema.getpostman.com/json/collection/v2.1.0' in schema:
        return 'v2.1'
    elif 'schema.getpostman.com/json/collection/v2.0.0' in schema:
        return 'v2.0'
    elif 'schema.getpostman.com/json/collection/v1.0.0' in schema:
        return 'v1.0'
    else:
        return 'unknown'
