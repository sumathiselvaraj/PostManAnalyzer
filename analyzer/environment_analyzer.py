"""
Module for analyzing Postman environment files
"""
import re
from collections import defaultdict

def analyze_environment(environment_data):
    """
    Analyze a Postman environment JSON
    
    Args:
        environment_data (dict): The parsed Postman environment JSON
    
    Returns:
        dict: Analysis results
    """
    # Initialize results
    results = {
        'environment_info': extract_environment_info(environment_data),
        'environment_analysis': {
            'variables_with_initial_value': 0,
            'variables_with_current_value': 0,
            'variables_used_in_collection': 0,  # Will be updated later when analyzing collection
            'naming_convention_quality': 0
        },
        'variable_categories': {},
        'environment_recommendations': []
    }
    
    # Extract environment variables
    variables = environment_data.get('values', [])
    results['environment_info']['variable_count'] = len(variables)
    
    # Analyze variables
    if variables:
        variables_with_initial = sum(1 for v in variables if 'value' in v and v['value'])
        variables_with_current = sum(1 for v in variables if 'enabled' in v and v['enabled'] is True)
        
        # Calculate percentages
        results['environment_analysis']['variables_with_initial_value'] = round((variables_with_initial / len(variables)) * 100, 1)
        results['environment_analysis']['variables_with_current_value'] = round((variables_with_current / len(variables)) * 100, 1)
        
        # Analyze naming conventions
        results['environment_analysis']['naming_convention_quality'] = analyze_naming_conventions(variables)
        
        # Categorize variables
        results['variable_categories'] = categorize_variables(variables)
        
        # Generate recommendations
        results['environment_recommendations'] = generate_environment_recommendations(results)
    
    # Calculate environment quality score
    results['environment_info']['quality_score'] = calculate_environment_quality_score(results)
    
    return results

def extract_environment_info(environment_data):
    """Extract basic information about the environment"""
    return {
        'name': environment_data.get('name', 'Unknown Environment'),
        'variable_count': 0,
        'quality_score': 0
    }

def analyze_naming_conventions(variables):
    """
    Analyze variable naming conventions
    
    Args:
        variables (list): List of environment variables
    
    Returns:
        float: Naming convention quality score (0-100)
    """
    if not variables:
        return 0
    
    consistent_format_count = 0
    good_descriptiveness_count = 0
    proper_casing_count = 0
    
    # Common naming formats
    camel_case_pattern = re.compile(r'^[a-z][a-zA-Z0-9]*$')
    snake_case_pattern = re.compile(r'^[a-z][a-z0-9_]*$')
    kebab_case_pattern = re.compile(r'^[a-z][a-z0-9\-]*$')
    
    # Track which format is most common
    format_counts = {'camel': 0, 'snake': 0, 'kebab': 0, 'other': 0}
    
    for variable in variables:
        name = variable.get('key', '')
        
        # Check casing format
        if camel_case_pattern.match(name):
            format_counts['camel'] += 1
        elif snake_case_pattern.match(name):
            format_counts['snake'] += 1
        elif kebab_case_pattern.match(name):
            format_counts['kebab'] += 1
        else:
            format_counts['other'] += 1
        
        # Check descriptiveness (simple heuristic: length > 3 and not just abbreviation)
        if len(name) > 3 and not name.isupper():
            good_descriptiveness_count += 1
        
        # Check proper casing (not all uppercase or all lowercase)
        if not (name.isupper() or name.islower()) and name.islower()[0]:
            proper_casing_count += 1
    
    # Determine most common format
    most_common_format = max(format_counts, key=format_counts.get)
    
    # Calculate consistency score
    if most_common_format != 'other':
        consistent_format_count = format_counts[most_common_format]
    
    # Calculate overall scores
    consistency_score = (consistent_format_count / len(variables)) * 100
    descriptiveness_score = (good_descriptiveness_count / len(variables)) * 100
    casing_score = (proper_casing_count / len(variables)) * 100
    
    # Weighted average
    final_score = (consistency_score * 0.5) + (descriptiveness_score * 0.3) + (casing_score * 0.2)
    
    return round(final_score, 1)

def categorize_variables(variables):
    """
    Categorize environment variables by their likely purpose
    
    Args:
        variables (list): List of environment variables
    
    Returns:
        dict: Variable categories and counts
    """
    categories = defaultdict(int)
    
    for variable in variables:
        name = variable.get('key', '').lower()
        
        # URLs and endpoints
        if any(term in name for term in ['url', 'host', 'domain', 'endpoint', 'api', 'uri']):
            categories['urls_and_endpoints'] += 1
        
        # Authentication
        elif any(term in name for term in ['auth', 'token', 'key', 'secret', 'password', 'jwt', 'oauth', 'bearer', 'basic']):
            categories['authentication'] += 1
        
        # User data
        elif any(term in name for term in ['user', 'name', 'email', 'account', 'profile', 'customer']):
            categories['user_data'] += 1
        
        # Configuration
        elif any(term in name for term in ['config', 'setting', 'env', 'environment', 'mode', 'flag']):
            categories['configuration'] += 1
        
        # IDs and references
        elif any(term in name for term in ['id', 'uuid', 'guid', 'ref', 'reference']):
            categories['ids_and_references'] += 1
        
        # Time-related
        elif any(term in name for term in ['time', 'date', 'timestamp', 'expiry', 'ttl', 'timeout']):
            categories['time_related'] += 1
        
        # Other
        else:
            categories['other'] += 1
    
    return dict(categories)

def generate_environment_recommendations(environment_analysis):
    """
    Generate recommendations for environment improvements
    
    Args:
        environment_analysis (dict): Environment analysis results
    
    Returns:
        list: List of recommendations
    """
    recommendations = []
    
    analysis = environment_analysis['environment_analysis']
    info = environment_analysis['environment_info']
    
    # Check for missing initial values
    if analysis['variables_with_initial_value'] < 90:
        recommendations.append({
            'title': 'Provide Initial Values for Environment Variables',
            'description': 'Some environment variables are missing initial values. This can cause tests to fail when first run with this environment.',
            'severity': 'important'
        })
    
    # Check for disabled variables
    if analysis['variables_with_current_value'] < 90:
        recommendations.append({
            'title': 'Enable All Required Environment Variables',
            'description': 'Some environment variables are currently disabled. Make sure all required variables are enabled for consistent test execution.',
            'severity': 'important'
        })
    
    # Check naming conventions
    if analysis['naming_convention_quality'] < 70:
        recommendations.append({
            'title': 'Improve Variable Naming Conventions',
            'description': 'Variable names lack consistency in format or are not descriptive enough. Use a consistent naming convention (camelCase, snake_case, or kebab-case) and ensure names are descriptive of their purpose.',
            'severity': 'medium'
        })
    
    # Check for sensitive data
    categories = environment_analysis.get('variable_categories', {})
    if categories.get('authentication', 0) > 0:
        recommendations.append({
            'title': 'Secure Sensitive Environment Variables',
            'description': 'Your environment contains authentication variables. Make sure to not share these in version control, and consider using Postman\'s environment management for sensitive data.',
            'severity': 'critical'
        })
    
    # General environment documentation
    recommendations.append({
        'title': 'Document Environment Variables',
        'description': 'Add descriptions to environment variables to help team members understand their purpose and expected values.',
        'severity': 'low'
    })
    
    # If very few variables
    if info['variable_count'] < 3:
        recommendations.append({
            'title': 'Expand Environment Variable Usage',
            'description': 'You have very few environment variables. Consider using environment variables for URLs, authentication, and other values that change between environments to make your collection more portable.',
            'severity': 'medium'
        })
    
    return recommendations

def calculate_environment_quality_score(environment_results):
    """
    Calculate environment quality score
    
    Args:
        environment_results (dict): Environment analysis results
    
    Returns:
        float: Quality score (0-100)
    """
    analysis = environment_results['environment_analysis']
    
    # Weighted factors
    weights = {
        'variables_with_initial_value': 0.3,
        'variables_with_current_value': 0.3,
        'naming_convention_quality': 0.4
    }
    
    # Calculate weighted score
    score = 0
    for factor, weight in weights.items():
        if factor in analysis:
            score += analysis[factor] * weight
    
    # Adjust score based on recommendations
    critical_recs = sum(1 for r in environment_results['environment_recommendations'] if r['severity'] == 'critical')
    important_recs = sum(1 for r in environment_results['environment_recommendations'] if r['severity'] == 'important')
    
    # Penalties for issues
    if critical_recs > 0:
        score -= 15
    if important_recs > 0:
        score -= 10 * min(important_recs, 3)  # Cap penalty for multiple issues
    
    # Ensure score is within range
    score = max(0, min(100, score))
    
    return round(score, 1)

def update_usage_in_collection(environment_analysis, collection_analysis):
    """
    Update environment variable usage stats based on collection analysis
    
    Args:
        environment_analysis (dict): Environment analysis results
        collection_analysis (dict): Collection analysis results
    
    Returns:
        dict: Updated environment analysis
    """
    # This function would be called after both analyses are complete
    # For now, we'll just set a default value
    environment_analysis['environment_analysis']['variables_used_in_collection'] = 80
    
    # Recalculate quality score with updated info
    environment_analysis['environment_info']['quality_score'] = calculate_environment_quality_score(environment_analysis)
    
    return environment_analysis
