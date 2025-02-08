import pytest
import asyncio
import aiohttp
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import psutil
import os
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.workload_allocator import WorkloadAllocator
from src.energy_monitoring import EnergyMonitor

class TestStress:
    @pytest.fixture
    def setup(self):
        self.allocator = WorkloadAllocator()
        self.monitor = EnergyMonitor()
        self.base_url = "http://localhost:8000"

    async def generate_load(self, endpoint, duration_seconds=10, requests_per_second=100):
        """Generate load for a specific endpoint."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            request_times = []
            errors = 0
            
            while time.time() - start_time < duration_seconds:
                tasks = []
                for _ in range(requests_per_second):
                    tasks.append(self.make_request(session, endpoint))
                    
                results = await asyncio.gather(*tasks, return_exceptions=True)
                request_times.extend([r for r in results if isinstance(r, float)])
                errors += sum(1 for r in results if isinstance(r, Exception))
                
                # Wait for next second
                await asyncio.sleep(1)
                
            return {
                'mean_response_time': np.mean(request_times),
                'p95_response_time': np.percentile(request_times, 95),
                'p99_response_time': np.percentile(request_times, 99),
                'error_rate': errors / (len(request_times) + errors)
            }

    async def make_request(self, session, endpoint):
        """Make a single request and return response time."""
        start_time = time.time()
        try:
            async with session.get(f"{self.base_url}{endpoint}") as response:
                await response.text()
                return time.time() - start_time
        except Exception as e:
            return e

    @pytest.mark.asyncio
    async def test_api_stress(self, setup):
        """Test API performance under heavy load."""
        endpoints = [
            "/metrics/energy/test-instance",
            "/metrics/sustainability/us-east-1",
            "/workload/allocate"
        ]
        
        for endpoint in endpoints:
            results = await self.generate_load(endpoint)
            
            # Assert performance requirements
            assert results['mean_response_time'] < 0.1, f"High average response time for {endpoint}"
            assert results['p95_response_time'] < 0.5, f"High p95 response time for {endpoint}"
            assert results['p99_response_time'] < 1.0, f"High p99 response time for {endpoint}"
            assert results['error_rate'] < 0.01, f"High error rate for {endpoint}"

    def test_concurrent_allocations(self, setup):
        """Test workload allocator under concurrent requests."""
        def allocate_workload():
            return self.allocator.allocate_resources({
                'cpu_request': np.random.uniform(1, 8),
                'memory_request': f'{int(np.random.uniform(1, 16))}Gi',
                'priority': np.random.choice(['high', 'medium', 'low'])
            })

        with ThreadPoolExecutor(max_workers=50) as executor:
            start_time = time.time()
            results = list(executor.map(lambda _: allocate_workload(), range(1000)))
            duration = time.time() - start_time
            
            # Assert performance requirements
            assert duration < 10.0, "Slow concurrent allocation"
            assert all(r is not None for r in results), "Failed allocations"

    def test_memory_leak(self, setup):
        """Test for memory leaks during extended operation."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Generate sustained load
        for _ in range(1000):
            self.allocator.allocate_resources({
                'cpu_request': 2.0,
                'memory_request': '4Gi',
                'priority': 'high'
            })
            
        # Force garbage collection
        import gc
        gc.collect()
        
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Assert memory growth is reasonable
        assert memory_growth < 50 * 1024 * 1024, "Potential memory leak detected"

    def test_data_processing_scalability(self, setup):
        """Test data processing scalability with large datasets."""
        # Generate large dataset
        num_records = 100000
        data = []
        current_time = time.time()
        
        for i in range(num_records):
            data.append({
                'timestamp': current_time + i,
                'cpu_utilization': np.random.uniform(0, 100),
                'memory_usage': np.random.uniform(0, 32),
                'network_in': np.random.uniform(0, 10000),
                'network_out': np.random.uniform(0, 10000)
            })
            
        import pandas as pd
        df = pd.DataFrame(data)
        
        start_time = time.time()
        # Perform common operations
        df['cpu_moving_avg'] = df['cpu_utilization'].rolling(window=100).mean()
        df['memory_moving_avg'] = df['memory_usage'].rolling(window=100).mean()
        df['total_network'] = df['network_in'] + df['network_out']
        
        processing_time = time.time() - start_time
        assert processing_time < 5.0, "Slow data processing"

    @pytest.mark.asyncio
    async def test_system_recovery(self, setup):
        """Test system recovery after high load."""
        # Generate high load
        await self.generate_load("/metrics/energy/test-instance", duration_seconds=30, requests_per_second=200)
        
        # Check system metrics immediately after
        process = psutil.Process(os.getpid())
        high_load_cpu = process.cpu_percent()
        high_load_memory = process.memory_info().rss
        
        # Wait for recovery
        await asyncio.sleep(10)
        
        # Check metrics after recovery
        recovered_cpu = process.cpu_percent()
        recovered_memory = process.memory_info().rss
        
        assert recovered_cpu < high_load_cpu * 0.5, "System not recovering CPU usage"
        assert recovered_memory <= high_load_memory * 1.1, "Memory not being released"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
