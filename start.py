import subprocess
import sys
import os
import time
import logging
import json
from pathlib import Path
import requests
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/startup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class EAAWASStartup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.processes = {}
        
    def check_python_version(self):
        """Verify Python version meets requirements."""
        required_version = (3, 8)
        current_version = sys.version_info[:2]
        
        if current_version < required_version:
            logger.error(f"Python {required_version[0]}.{required_version[1]} or higher is required")
            sys.exit(1)
        logger.info(f"Python version check passed: {sys.version}")

    def check_aws_credentials(self):
        """Verify AWS credentials are configured."""
        try:
            import boto3
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            logger.info(f"AWS credentials verified for user: {identity['Arn']}")
            return True
        except Exception as e:
            logger.error(f"AWS credentials check failed: {str(e)}")
            return False

    def install_dependencies(self):
        """Install required packages from requirements.txt."""
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info("Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e.stderr}")
            return False

    def check_directories(self):
        """Ensure all required directories exist."""
        required_dirs = ['configs', 'data', 'logs', 'models', 'scripts', 'src']
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True)
                logger.info(f"Created directory: {dir_name}")
            else:
                logger.info(f"Directory exists: {dir_name}")

    def verify_configs(self):
        """Verify configuration files exist and are valid."""
        config_files = {
            'configs/aws_config.json': {
                'required_fields': ['region', 'metrics_bucket', 'energy_threshold', 'monitoring_interval']
            },
            'configs/ml_hyperparameters.json': {
                'required_fields': ['n_estimators', 'max_depth', 'test_size', 'random_state']
            }
        }

        for config_file, requirements in config_files.items():
            path = self.project_root / config_file
            if not path.exists():
                logger.error(f"Missing config file: {config_file}")
                return False
                
            try:
                with open(path) as f:
                    config = json.load(f)
                    missing_fields = [field for field in requirements['required_fields'] 
                                    if field not in config]
                    if missing_fields:
                        logger.error(f"Missing fields in {config_file}: {missing_fields}")
                        return False
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in config file: {config_file}")
                return False
                
        logger.info("All configuration files verified")
        return True

    def start_service(self, service_name, command, cwd=None):
        """Start a service process."""
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd or self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes[service_name] = process
            logger.info(f"Started {service_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to start {service_name}: {str(e)}")
            return False

    def check_service_health(self, service_name, health_check_url=None):
        """Check if a service is healthy."""
        if health_check_url:
            try:
                response = requests.get(health_check_url)
                if response.status_code == 200:
                    logger.info(f"{service_name} health check passed")
                    return True
            except requests.RequestException:
                pass
                
        process = self.processes.get(service_name)
        if process and process.poll() is None:
            logger.info(f"{service_name} is running")
            return True
            
        logger.error(f"{service_name} health check failed")
        return False

    def start_all_services(self):
        """Start all required services."""
        services = [
            ('data_collector', [sys.executable, 'scripts/collect_realtime_data.py']),
            ('api_server', [sys.executable, 'src/api_integration.py'])
        ]

        with ThreadPoolExecutor() as executor:
            futures = []
            for service_name, command in services:
                futures.append(
                    executor.submit(self.start_service, service_name, command)
                )

            # Wait for all services to start
            for future in futures:
                future.result()

        # Check health of services
        time.sleep(5)  # Give services time to start
        all_healthy = True
        for service_name in [s[0] for s in services]:
            if not self.check_service_health(service_name):
                all_healthy = False

        return all_healthy

    def run(self):
        """Run the complete startup sequence."""
        steps = [
            (self.check_python_version, "Checking Python version"),
            (self.check_aws_credentials, "Verifying AWS credentials"),
            (self.install_dependencies, "Installing dependencies"),
            (self.check_directories, "Verifying directory structure"),
            (self.verify_configs, "Verifying configuration files"),
            (self.start_all_services, "Starting services")
        ]

        for step_func, step_name in steps:
            logger.info(f"Starting: {step_name}")
            try:
                result = step_func()
                if result is False:
                    logger.error(f"Failed: {step_name}")
                    return False
            except Exception as e:
                logger.error(f"Error in {step_name}: {str(e)}")
                return False

        logger.info("EAAWAS startup completed successfully")
        return True

    def cleanup(self):
        """Cleanup processes on shutdown."""
        for service_name, process in self.processes.items():
            if process.poll() is None:
                process.terminate()
                logger.info(f"Terminated {service_name}")

if __name__ == "__main__":
    startup = EAAWASStartup()
    try:
        if startup.run():
            logger.info("Press Ctrl+C to stop all services")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        startup.cleanup()
