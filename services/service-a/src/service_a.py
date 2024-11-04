import logging
import os
import yaml
import requests
import json
import time
from functools import lru_cache
from requests.exceptions import RequestException

# Initialize logger
logger = logging.getLogger("service_a")
logging.basicConfig(level=logging.INFO)

# Retry decorator for API calls
def retry(tries, delay=3, backoff=2):
    def retry_decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < tries:
                try:
                    return func(*args, **kwargs)
                except RequestException as e:
                    attempt += 1
                    logger.error(f"Error during API call: {e}. Retrying {attempt}/{tries}...")
                    time.sleep(delay)
                    delay *= backoff
            logger.error("Max retries exceeded.")
            return None
        return wrapper
    return retry_decorator

# Caching the config loader to avoid reading the file multiple times
@lru_cache(maxsize=1)
class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = None

    def load_config(self):
        logger.info(f"Loading configuration from {self.config_file}")
        try:
            with open(self.config_file, 'r') as file:
                self.config = yaml.safe_load(file)
            logger.info(f"Configuration loaded: {self.config}")
        except FileNotFoundError:
            logger.error(f"Config file {self.config_file} not found")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML: {e}")
        return self.config

class DataValidator:
    @staticmethod
    def validate_data(data):
        logger.info("Validating data...")
        if not isinstance(data, dict):
            logger.error("Invalid data format: Expected dictionary")
            return False
        for key, value in data.items():
            if value is None or value == "":
                logger.warning(f"Missing value for key: {key}")
        logger.info("Data validation complete")
        return True

class CacheManager:
    def __init__(self, cache_file="cache/data_cache.json"):
        self.cache_file = cache_file

    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as file:
                try:
                    logger.info("Loading data from cache")
                    return json.load(file)
                except json.JSONDecodeError:
                    logger.error("Cache file is corrupted")
                    return None
        else:
            logger.info("No cache file found, starting fresh")
            return None

    def save_cache(self, data):
        logger.info("Saving data to cache")
        with open(self.cache_file, 'w') as file:
            json.dump(data, file)
        logger.info("Data saved to cache successfully")

class ServiceAProcessor:
    def __init__(self, config):
        self.api_endpoint = config['api']['endpoint']
        self.api_key = config['api']['key']
        self.cache_manager = CacheManager()

    @retry(tries=3)
    def fetch_data(self):
        logger.info(f"Fetching data from {self.api_endpoint}")
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(self.api_endpoint, headers=headers)
        if response.status_code == 200:
            logger.info("Data fetched successfully")
            return response.json()
        else:
            logger.error(f"Failed to fetch data: {response.status_code}")
            return None

    def process_data(self, data):
        logger.info("Processing data...")
        processed_data = {key: value for key, value in data.items() if value is not None}
        logger.info(f"Processed data: {processed_data}")
        return processed_data

    def handle_data(self, data):
        if not DataValidator.validate_data(data):
            logger.error("Invalid data, aborting processing")
            return

        logger.info("Data validation passed, proceeding with caching and processing")
        self.cache_manager.save_cache(data)
        processed_data = self.process_data(data)
        logger.info(f"Final processed data: {processed_data}")
        return processed_data

    def execute(self):
        cached_data = self.cache_manager.load_cache()
        if cached_data:
            logger.info("Using cached data")
            return self.handle_data(cached_data)

        raw_data = self.fetch_data()
        if raw_data:
            return self.handle_data(raw_data)
        else:
            logger.error("No data fetched or found in cache")

def health_check():
    logger.info("Performing health check...")
    try:
        response = requests.get("http://localhost:8080/health")
        if response.status_code == 200:
            logger.info("Service is healthy")
            return True
        else:
            logger.warning(f"Service health check failed with status: {response.status_code}")
            return False
    except RequestException as e:
        logger.error(f"Health check error: {e}")
        return False

def log_system_status():
    logger.info("Logging system status...")
    logger.info(f"CPU usage: {os.cpu_count()} cores")
    logger.info(f"Memory usage: {os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024.**3):.2f} GB")
    logger.info("System status logged")

if __name__ == "__main__":
    # Load configuration
    config_loader = ConfigLoader("config/config.yaml")
    config = config_loader.load_config()

    if config:
        # Perform health check before starting
        if health_check():
            log_system_status()

            # Start processing the data
            service_processor = ServiceAProcessor(config)
            service_processor.execute()

        else:
            logger.error("Service health check failed. Shutting down...")
    else:
        logger.error("Failed to load configuration. Exiting...")