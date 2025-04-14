"""
Module for scoring and evaluating Postman collections
"""

# Score weights for different aspects of API tests
SCORE_WEIGHTS = {
    'test_coverage': 0.3,           # How many endpoints have tests
    'test_depth': 0.2,              # How many different types of tests
    'test_quality': 0.2,            # Quality of test implementations
    'environment_usage': 0.1,       # Use of environment variables
    'documentation': 0.1,           # Documentation in tests
    'error_handling': 0.1           # Error handling in tests
}

# Score weights for test types
TEST_TYPE_WEIGHTS = {
    'response_code': 0.15,          # Status code validation
    'response_json': 0.15,          # JSON structure validation
    'data_validation': 0.15,        # Specific data validation
    'schema_validation': 0.15,      # Schema validation
    'error_handling': 0.10,         # Error scenarios
    'authentication': 0.10,         # Authentication testing
    'authorization': 0.10,          # Authorization testing
    'response_header': 0.05,        # Header validation
    'response_time': 0.05,          # Performance validation
    'business_logic': 0.10          # Business rules validation
}

def calculate_collection_score(collection_analysis):
    """
    Calculate overall collection quality score
    
    Args:
        collection_analysis (dict): Collection analysis results
    
    Returns:
        float: Quality score (0-100)
    """
    # Calculate test coverage score
    coverage_score = collection_analysis['test_coverage']['overall']
    
    # Calculate test depth score
    test_types = collection_analysis['test_coverage'].get('by_type', {})
    
    test_depth_score = 0
    if test_types:
        # Calculate weighted score based on coverage of each test type
        weighted_sum = sum(TEST_TYPE_WEIGHTS.get(test_type, 0.05) * coverage 
                          for test_type, coverage in test_types.items())
        test_depth_score = weighted_sum * 100 / sum(TEST_TYPE_WEIGHTS.values())
    
    # Calculate test quality score
    test_quality_score = (
        collection_analysis['script_analysis']['avg_complexity'] * 25  # 0-4 scale -> 0-100
    )
    test_quality_score = min(100, test_quality_score)  # Cap at 100
    
    # Calculate environment usage score
    environment_score = collection_analysis['script_analysis']['variable_usage']
    
    # Calculate documentation score (placeholder - would need more analysis)
    documentation_score = 50  # Default middle value
    
    # Calculate error handling score
    error_handling_score = collection_analysis['script_analysis']['error_handling']
    
    # Calculate weighted total score
    total_score = (
        coverage_score * SCORE_WEIGHTS['test_coverage'] +
        test_depth_score * SCORE_WEIGHTS['test_depth'] +
        test_quality_score * SCORE_WEIGHTS['test_quality'] +
        environment_score * SCORE_WEIGHTS['environment_usage'] +
        documentation_score * SCORE_WEIGHTS['documentation'] +
        error_handling_score * SCORE_WEIGHTS['error_handling']
    )
    
    return round(total_score, 1)

def calculate_endpoint_score(endpoint_analysis):
    """
    Calculate quality score for an endpoint
    
    Args:
        endpoint_analysis (dict): Analysis data for an endpoint
    
    Returns:
        float: Quality score (0-100)
    """
    if endpoint_analysis['test_count'] == 0:
        return 0
    
    # Calculate test type coverage score
    test_types = endpoint_analysis['test_types']
    weighted_sum = sum(TEST_TYPE_WEIGHTS.get(test_type, 0.05) 
                       for test_type in test_types)
    test_type_score = weighted_sum * 100 / sum(TEST_TYPE_WEIGHTS.values())
    
    # Calculate implementation quality score
    implementation_quality = 50  # Default baseline
    
    # Adjust for various quality factors
    if endpoint_analysis['uses_variables']:
        implementation_quality += 10
    
    if endpoint_analysis['uses_dynamic_data']:
        implementation_quality += 15
        
    if endpoint_analysis['has_error_handling']:
        implementation_quality += 15
    
    # Adjust based on test count
    test_count_factor = min(1.0, endpoint_analysis['test_count'] / 5)  # Cap at 5 tests
    implementation_quality = implementation_quality * test_count_factor
    
    # Calculate final score (50% test types, 50% implementation)
    final_score = (test_type_score * 0.5) + (implementation_quality * 0.5)
    
    return round(min(100, max(0, final_score)), 1)

def categorize_score(score):
    """
    Categorize a numeric score into a text representation
    
    Args:
        score (float): Numeric score (0-100)
    
    Returns:
        str: Category label
    """
    if score >= 90:
        return "Excellent"
    elif score >= 75:
        return "Good"
    elif score >= 60:
        return "Satisfactory"
    elif score >= 40:
        return "Needs Improvement"
    else:
        return "Poor"

def get_score_recommendations(score):
    """
    Get generic recommendations based on score
    
    Args:
        score (float): Numeric score (0-100)
    
    Returns:
        list: List of recommendations
    """
    if score >= 90:
        return [
            "Maintain your excellent test coverage and quality",
            "Consider adding advanced scenarios like chaos testing or security testing",
            "Share your test approach with other teams as a best practice example"
        ]
    elif score >= 75:
        return [
            "Add test coverage for the few remaining untested areas",
            "Enhance documentation within tests",
            "Consider adding performance testing assertions"
        ]
    elif score >= 60:
        return [
            "Focus on increasing overall test coverage",
            "Add more diverse test types for critical endpoints",
            "Improve error handling in tests"
        ]
    elif score >= 40:
        return [
            "Significantly increase test coverage across endpoints",
            "Add basic validation for all API responses",
            "Implement environment variables for test flexibility",
            "Add error handling to make tests more robust"
        ]
    else:
        return [
            "Create a test plan targeting key endpoints first",
            "Implement basic status code validation for all endpoints",
            "Add response body validation tests",
            "Use environment variables for configurable testing",
            "Develop a phased approach to improve test coverage over time"
        ]
