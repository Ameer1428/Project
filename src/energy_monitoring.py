import boto3
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from prometheus_client import start_http_server, Gauge
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnergyMonitor:
    def __init__(self, config_path: str = "../configs/aws_config.json"):
        """Initialize the EnergyMonitor with configurations."""
        self.load_config(config_path)
        self.setup_clients()
        self.setup_metrics()
        
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
            self.cloudwatch = boto3.client('cloudwatch')
            self.ec2 = boto3.client('ec2')
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {str(e)}")
            raise
            
    def setup_metrics(self) -> None:
        """Setup Prometheus metrics for monitoring."""
        self.energy_consumption = Gauge(
            'instance_energy_consumption',
            'Energy consumption metrics per instance',
            ['instance_id', 'instance_type']
        )
        self.carbon_footprint = Gauge(
            'instance_carbon_footprint',
            'Estimated carbon footprint per instance',
            ['instance_id', 'region']
        )
        
    def get_instance_metrics(self, instance_id: str, hours: int = 1) -> Dict:
        """Retrieve detailed metrics for an EC2 instance."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            metrics = {
                'CPUUtilization': [],
                'NetworkIn': [],
                'NetworkOut': [],
                'DiskReadBytes': [],
                'DiskWriteBytes': []
            }
            
            for metric_name in metrics.keys():
                response = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/EC2',
                    MetricName=metric_name,
                    Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=300,
                    Statistics=['Average']
                )
                
                for datapoint in response['Datapoints']:
                    metrics[metric_name].append({
                        'timestamp': datapoint['Timestamp'],
                        'value': datapoint['Average']
                    })
                    
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get instance metrics: {str(e)}")
            return None
            
    def calculate_energy_consumption(self, metrics: Dict) -> float:
        """Calculate energy consumption based on resource utilization."""
        try:
            # Simple energy calculation based on CPU utilization
            # In a production environment, this would be more sophisticated
            cpu_utilization = pd.DataFrame(metrics['CPUUtilization'])
            if not cpu_utilization.empty:
                avg_cpu = cpu_utilization['value'].mean()
                # Assuming linear relationship between CPU and energy
                # In reality, this would be based on instance type specs
                base_power = 100  # Watts
                max_power = 200   # Watts
                return base_power + (max_power - base_power) * (avg_cpu / 100)
            return 0
        except Exception as e:
            logger.error(f"Failed to calculate energy consumption: {str(e)}")
            return 0
            
    def estimate_carbon_footprint(self, energy_consumption: float, region: str) -> float:
        """Estimate carbon footprint based on energy consumption and region."""
        try:
            # Carbon intensity factors (gCO2/kWh) for different regions
            # These would ideally come from real-time data sources
            carbon_factors = {
                'us-east-1': 400,
                'eu-west-1': 200,
                'ap-southeast-1': 600
            }
            
            factor = carbon_factors.get(region, 500)  # Default factor if region unknown
            # Convert Wh to kWh and calculate carbon emissions
            return (energy_consumption / 1000) * factor
            
        except Exception as e:
            logger.error(f"Failed to estimate carbon footprint: {str(e)}")
            return 0
            
    def monitor_instances(self) -> List[Dict]:
        """Monitor all running instances and collect metrics."""
        try:
            instances = self.ec2.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
            )
            
            monitoring_data = []
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    instance_type = instance['InstanceType']
                    region = instance['Placement']['AvailabilityZone'][:-1]
                    
                    metrics = self.get_instance_metrics(instance_id)
                    if metrics:
                        energy_consumption = self.calculate_energy_consumption(metrics)
                        carbon_footprint = self.estimate_carbon_footprint(
                            energy_consumption, region
                        )
                        
                        # Update Prometheus metrics
                        self.energy_consumption.labels(
                            instance_id=instance_id,
                            instance_type=instance_type
                        ).set(energy_consumption)
                        
                        self.carbon_footprint.labels(
                            instance_id=instance_id,
                            region=region
                        ).set(carbon_footprint)
                        
                        monitoring_data.append({
                            'instance_id': instance_id,
                            'instance_type': instance_type,
                            'region': region,
                            'energy_consumption': energy_consumption,
                            'carbon_footprint': carbon_footprint,
                            'metrics': metrics
                        })
                        
            return monitoring_data
            
        except Exception as e:
            logger.error(f"Failed to monitor instances: {str(e)}")
            return []
            
    def start_monitoring(self, port: int = 8000, interval: int = 300) -> None:
        """Start the monitoring server and periodic metric collection."""
        try:
            # Start Prometheus metrics server
            start_http_server(port)
            logger.info(f"Started metrics server on port {port}")
            
            while True:
                monitoring_data = self.monitor_instances()
                logger.info(f"Collected metrics for {len(monitoring_data)} instances")
                # Save monitoring data to logs
                with open('../logs/energy_logs.txt', 'a') as f:
                    json.dump({
                        'timestamp': datetime.utcnow().isoformat(),
                        'data': monitoring_data
                    }, f)
                    f.write('\n')
                    
                # Wait for next collection interval
                time.sleep(interval)
                
        except Exception as e:
            logger.error(f"Monitoring service failed: {str(e)}")
            raise
            
if __name__ == "__main__":
    monitor = EnergyMonitor()
    monitor.start_monitoring()