import pytest
import time
import numpy as np
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.workload_allocator import WorkloadAllocator
from src.energy_monitoring import EnergyMonitor
from src.ml_training import MLPredictor

class TestPerformance:
    @pytest.fixture
    def setup(self):
        self.allocator = WorkloadAllocator()
        self.monitor = EnergyMonitor()
        self.predictor = MLPredictor()

    def test_allocation_performance(self, setup):
        """Test workload allocation performance under load."""
        requests = [
            {
                'cpu_request': np.random.uniform(1, 8),
                'memory_request': f'{int(np.random.uniform(1, 16))}Gi',
                'priority': np.random.choice(['high', 'medium', 'low'])
            }
            for _ in range(100)
        ]
        
        start_time = time.time()
        for request in requests:
            allocation = self.allocator.allocate_resources(request)
            assert allocation is not None
            
        duration = time.time() - start_time
        assert duration < 5.0, "Allocation too slow"

    def test_monitoring_performance(self, setup):
        """Test energy monitoring performance."""
        instance_ids = [f'i-{i:012d}' for i in range(50)]
        
        start_time = time.time()
        for instance_id in instance_ids:
            metrics = self.monitor.get_metrics(instance_id)
            assert metrics is not None
            
        duration = time.time() - start_time
        assert duration < 3.0, "Monitoring too slow"

    def test_ml_prediction_performance(self, setup):
        """Test ML prediction performance."""
        test_data = [
            {
                'cpu_utilization': np.random.uniform(0, 100),
                'memory_usage': np.random.uniform(0, 32),
                'network_in': np.random.uniform(0, 10000),
                'network_out': np.random.uniform(0, 10000)
            }
            for _ in range(1000)
        ]
        
        start_time = time.time()
        predictions = [self.predictor.predict(data) for data in test_data]
        duration = time.time() - start_time
        
        assert duration < 1.0, "Prediction too slow"
        assert all(isinstance(p, (int, float)) for p in predictions)

    def test_data_processing_performance(self, setup):
        """Test data processing performance."""
        data_file = project_root / 'data/workload_data.csv'
        if not data_file.exists():
            pytest.skip("No data file available")
            
        start_time = time.time()
        import pandas as pd
        df = pd.read_csv(data_file)
        processing_time = time.time() - start_time
        
        assert processing_time < 1.0, "Data processing too slow"
        assert len(df) > 0, "Empty dataset"

    @pytest.mark.asyncio
    async def test_api_response_time(self):
        """Test API endpoint response times."""
        import aiohttp
        import asyncio
        
        async with aiohttp.ClientSession() as session:
            endpoints = [
                "/metrics/energy/test-instance",
                "/metrics/sustainability/us-east-1",
                "/workload/allocate"
            ]
            
            for endpoint in endpoints:
                start_time = time.time()
                async with session.get(f"http://localhost:8000{endpoint}") as response:
                    duration = time.time() - start_time
                    assert duration < 0.5, f"Endpoint {endpoint} too slow"

    def test_memory_usage(self, setup):
        """Test memory usage under load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate load
        data = [np.random.rand(1000, 1000) for _ in range(10)]
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        assert memory_increase < 500, "Excessive memory usage"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
