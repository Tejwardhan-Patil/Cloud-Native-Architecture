import json
import logging
import time
from datetime import datetime, timedelta
from functools import wraps, lru_cache
import random
import requests

# Setup a logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("service_b_utils")

# Utility function to log function calls and execution time
def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        logger.info(f"Executing {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        logger.info(f"{func.__name__} executed in {execution_time} seconds")
        return result
    return wrapper

# Utility function to handle JSON serialization/deserialization
def parse_json(data):
    try:
        if isinstance(data, str):
            return json.loads(data)  # Deserialize JSON string to Python dict
        return json.dumps(data)  # Serialize Python dict to JSON string
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON data: {e}")
        raise

# Decorator to handle exceptions and log errors
def exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    return wrapper

# Utility function to transform data (sanitize or format)
@log_execution_time
@exception_handler
def transform_data(data):
    if not isinstance(data, dict):
        raise ValueError("Input data must be a dictionary.")
    
    transformed_data = {k.lower(): v.strip() if isinstance(v, str) else v for k, v in data.items()}
    logger.info(f"Transformed data: {transformed_data}")
    return transformed_data

# Utility function for date formatting
@log_execution_time
@exception_handler
def format_date(date_str, format_in="%Y-%m-%d", format_out="%d-%m-%Y"):
    date_obj = datetime.strptime(date_str, format_in)
    formatted_date = date_obj.strftime(format_out)
    logger.info(f"Formatted date from {date_str} to {formatted_date}")
    return formatted_date

# Retry logic decorator
def retry_on_failure(retries=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    logger.warning(f"Attempt {attempts}/{retries} failed for {func.__name__}: {e}")
                    time.sleep(delay)
            raise Exception(f"Failed after {retries} attempts.")
        return wrapper
    return decorator

# Caching decorator for expensive computations
@lru_cache(maxsize=128)
def cached_computation(x, y):
    logger.info(f"Performing expensive computation for {x}, {y}")
    time.sleep(2)  # Simulate expensive computation
    return x * y

# Simulate external API call
@retry_on_failure(retries=5, delay=1)
@log_execution_time
@exception_handler
def call_external_api(url):
    logger.info(f"Making external API call to {url}")
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"API call failed with status code {response.status_code}")
    return response.json()

# Utility for retry logic on database connections
@retry_on_failure(retries=5, delay=5)
@exception_handler
def connect_to_database(connection_string):
    logger.info(f"Connecting to database with connection string: {connection_string}")
    # Simulate random connection failures
    if random.choice([True, False]):
        raise ConnectionError("Failed to connect to the database.")
    return "Database connection successful."

# Cache decorator for frequently used database queries
@lru_cache(maxsize=256)
def cached_query(query, params=None):
    logger.info(f"Performing cached query: {query} with params: {params}")
    # Simulate query execution
    time.sleep(1)
    return {"result": "query_result"}

# Input validation decorator
def validate_input(expected_type):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for arg in args:
                if not isinstance(arg, expected_type):
                    raise TypeError(f"Expected argument of type {expected_type}, got {type(arg)}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Utility function with input validation
@validate_input(dict)
@exception_handler
def validate_and_process_data(data):
    logger.info(f"Validating and processing data: {data}")
    processed_data = {k: v for k, v in data.items() if v is not None}
    return processed_data

# Utility function for date manipulation
@log_execution_time
@exception_handler
def add_days_to_date(date_str, days, format_in="%Y-%m-%d", format_out="%d-%m-%Y"):
    date_obj = datetime.strptime(date_str, format_in)
    new_date = date_obj + timedelta(days=days)
    formatted_date = new_date.strftime(format_out)
    logger.info(f"New date after adding {days} days: {formatted_date}")
    return formatted_date

# Utility for exponential backoff
def exponential_backoff(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        delay = 1
        max_delay = 64
        while delay < max_delay:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}. Retrying in {delay} seconds.")
                time.sleep(delay)
                delay *= 2
        raise Exception(f"Failed after maximum backoff delay.")
    return wrapper

# Exponential backoff for API call
@exponential_backoff
@log_execution_time
def api_call_with_backoff(url):
    logger.info(f"Calling API with exponential backoff: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"API call failed with status code {response.status_code}")
    return response.json()

# Utility to generate a random identifier
@log_execution_time
def generate_random_id(length=8):
    id_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    random_id = ''.join(random.choice(id_chars) for _ in range(length))
    logger.info(f"Generated random ID: {random_id}")
    return random_id

# Utility to batch process data
@log_execution_time
@exception_handler
def batch_process_data(data_list, batch_size=100):
    logger.info(f"Batch processing data with batch size: {batch_size}")
    for i in range(0, len(data_list), batch_size):
        batch = data_list[i:i+batch_size]
        logger.info(f"Processing batch: {batch}")
        # Simulate processing time
        time.sleep(1)

# Utility to check if a string is a valid email
@log_execution_time
@exception_handler
def is_valid_email(email):
    import re
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if re.match(email_regex, email):
        logger.info(f"Valid email: {email}")
        return True
    else:
        logger.warning(f"Invalid email: {email}")
        return False

# Usage of utility functions
if __name__ == "__main__":
    data = {"Name": "Max ", "Age": " 30 ", "Email": "max@website.com "}
    transformed = transform_data(data)
    logger.info(f"Transformed data: {transformed}")

    date_added = add_days_to_date("2023-09-23", 10)
    logger.info(f"Date after adding days: {date_added}")

    random_id = generate_random_id()
    logger.info(f"Generated random ID: {random_id}")

    is_valid = is_valid_email("test@website.com")
    logger.info(f"Email validation result: {is_valid}")