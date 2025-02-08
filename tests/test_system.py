import pytest
import sys
import os
import json
import requests
from pathlib import Path
import boto3
from unittest.mock import Mock, patch

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.workload_allocator import WorkloadAllocator
from src.energy_monitoring import EnergyMonitor
from src.ml_training import MLPredictor

class TestSystemIntegration:
    @pytest.fixture
    def setup(self):
        """Setup test environment."""
        # Load configurations
        with open(project_root / 'configs/aws_config.json') as f:
            self.aws_config = json.load(f)
        with open(project_root / 'configs/ml_hyperparameters.json') as f:
            self.ml_config = json.load(f)
            
    def test_aws_connectivity(self):
        """Test AWS connectivity."""
        sts = boto3.client('sts')
        response = sts.get_caller_identity()
        assert 'Account' in response
        assert 'Arn' in response

    def test_data_collection(self):
        """Test data collection functionality."""
        data_file = project_root / 'data/workload_data.csv'
        energy_file = project_root / 'data/energy_metrics.csv'
        
        assert data_file.exists(), "Workload data file not found"
        assert energy_file.exists(), "Energy metrics file not found"

    @pytest.mark.asyncio
    async def test_api_endpoints(self):
        """Test API endpoints."""
        base_url = "http://localhost:8000"
        endpoints = [
            "/metrics/energy/test-instance",
            "/metrics/sustainability/us-east-1",
            "/workload/allocate"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{base_url}{endpoint}")
            assert response.status_code in [200, 404], f"Endpoint {endpoint} failed"

    def test_ml_predictor(self):
        """Test ML predictor functionality."""
        predictor = MLPredictor()
        test_data = {
            'cpu_utilization': 50.0,
            'memory_usage': 4.0,
            'network_in': 1024,
            'network_out': 2048
        }
        prediction = predictor.predict(test_data)
        assert isinstance(prediction, (int, float)), "Invalid prediction type"

    def test_workload_allocator(self):
        """Test workload allocation logic."""
        allocator = WorkloadAllocator()
        allocation = allocator.allocate_resources({
            'cpu_request': 2.0,
            'memory_request': '4Gi',
            'priority': 'high'
        })
        assert 'instance_type' in allocation
        assert 'region' in allocation

    def test_energy_monitor(self):
        """Test energy monitoring functionality."""
        monitor = EnergyMonitor()
        metrics = monitor.get_metrics('test-instance')
        required_fields = ['energy_consumption', 'carbon_footprint']
        for field in required_fields:
            assert field in metrics

    def test_configuration_validity(self):
        """Test configuration file validity."""
        config_files = [
            'configs/aws_config.json',
            'configs/ml_hyperparameters.json'
        ]
        
        for config_file in config_files:
            path = project_root / config_file
            assert path.exists(), f"Missing config file: {config_file}"
            with open(path) as f:
                config = json.load(f)
                assert isinstance(config, dict), f"Invalid config format in {config_file}"

    @pytest.mark.asyncio
    async def test_system_integration(self):
        """Test complete system integration."""
        # Test data collection
        self.test_data_collection()
        
        # Test ML prediction
        self.test_ml_predictor()
        
        # Test workload allocation
        self.test_workload_allocator()
        
        # Test energy monitoring
        self.test_energy_monitor()
        
        # Test API endpoints
        await self.test_api_endpoints()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
