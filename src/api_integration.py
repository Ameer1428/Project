
import boto3
import requests
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EAAWAS API",
    description="Energy-Aware Adaptive Workload Allocation System API",
    version="1.0.0"
)

class WorkloadRequest(BaseModel):
    """Request model for workload allocation."""
    cpu_request: float
    memory_request: str
    priority: str
    max_energy_consumption: Optional[float] = None

class MetricsResponse(BaseModel):
    """Response model for energy metrics."""
    instance_id: str
    energy_consumption: float
    carbon_footprint: float
    timestamp: str

class APIIntegration:
    def __init__(self, config_path: str = "../configs/aws_config.json"):
        """Initialize the APIIntegration with configurations."""
        self.load_config(config_path)
        self.setup_clients()
        
    def load_config(self, config_path: str) -> None:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            raise
            
    def setup_clients(self) -> None:
        """Initialize AWS service clients."""
        try:
            self.s3 = boto3.client('s3')
            self.cloudwatch = boto3.client('cloudwatch')
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {str(e)}")
            raise
            
    def get_sustainability_metrics(self, region: str) -> Dict:
        """Get sustainability metrics for a region."""
        try:
            # This would typically call an external sustainability API
            # For demonstration, using mock data
            sustainability_data = {
                'us-east-1': {
                    'renewable_percentage': 35,
                    'carbon_intensity': 400
                },
                'eu-west-1': {
                    'renewable_percentage': 60,
                    'carbon_intensity': 200
                },
                'ap-southeast-1': {
                    'renewable_percentage': 25,
                    'carbon_intensity': 600
                }
            }
            
            return sustainability_data.get(region, {
                'renewable_percentage': 30,
                'carbon_intensity': 500
            })
            
        except Exception as e:
            logger.error(f"Failed to get sustainability metrics: {str(e)}")
            return {}
            
    def store_metrics(self, metrics: Dict) -> bool:
        """Store metrics data in S3."""
        try:
            bucket_name = self.config.get('metrics_bucket', 'eaawas-metrics')
            timestamp = datetime.utcnow().strftime('%Y-%m-%d-%H')
            key = f"metrics/{timestamp}.json"
            
            self.s3.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=json.dumps(metrics)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store metrics: {str(e)}")
            return False
            
    def publish_cloudwatch_metrics(self, metrics: Dict) -> bool:
        """Publish metrics to CloudWatch."""
        try:
            metric_data = []
            
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    metric_data.append({
                        'MetricName': key,
                        'Value': value,
                        'Unit': 'None',
                        'Timestamp': datetime.utcnow()
                    })
            
            if metric_data:
                self.cloudwatch.put_metric_data(
                    Namespace='EAAWAS/Metrics',
                    MetricData=metric_data
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish CloudWatch metrics: {str(e)}")
            return False

# API Routes
@app.post("/workload/allocate", response_model=Dict)
async def allocate_workload(request: WorkloadRequest):
    """Endpoint to allocate workload."""
    try:
        # This would integrate with workload_allocator.py
        from workload_allocator import WorkloadAllocator
        
        allocator = WorkloadAllocator()
        result = allocator.allocate_workload({
            'cpu_request': request.cpu_request,
            'memory_request': request.memory_request,
            'priority': request.priority,
            'max_energy_consumption': request.max_energy_consumption
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Workload allocation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/energy/{instance_id}", response_model=MetricsResponse)
async def get_energy_metrics(instance_id: str):
    """Endpoint to get energy metrics for an instance."""
    try:
        # This would integrate with energy_monitoring.py
        from energy_monitoring import EnergyMonitor
        
        monitor = EnergyMonitor()
        metrics = monitor.get_instance_metrics(instance_id)
        
        if not metrics:
            raise HTTPException(status_code=404, detail="Instance not found")
            
        return {
            'instance_id': instance_id,
            'energy_consumption': metrics.get('energy_consumption', 0),
            'carbon_footprint': metrics.get('carbon_footprint', 0),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get energy metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/sustainability/{region}")
async def get_region_sustainability(region: str):
    """Endpoint to get sustainability metrics for a region."""
    try:
        api = APIIntegration()
        metrics = api.get_sustainability_metrics(region)
        
        if not metrics:
            raise HTTPException(
                status_code=404,
                detail="Sustainability metrics not found for region"
            )
            
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get sustainability metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)