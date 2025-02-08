import boto3
import pandas as pd
import logging
from datetime import datetime, timedelta
import time
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealTimeDataCollector:
    def __init__(self):
        """Initialize AWS clients and configure data paths."""
        self.setup_aws_clients()
        self.setup_data_directories()
        
    def setup_aws_clients(self):
        """Initialize AWS service clients."""
        try:
            self.ec2 = boto3.client('ec2')
            self.cloudwatch = boto3.client('cloudwatch')
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {str(e)}")
            raise
            
    def setup_data_directories(self):
        """Ensure data directories exist."""
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
    def get_instance_metrics(self, instance_id: str, start_time: datetime, end_time: datetime):
        """Retrieve metrics for a specific EC2 instance."""
        try:
            metrics = {}
            metric_names = [
                'CPUUtilization',
                'MemoryUtilization',
                'NetworkIn',
                'NetworkOut',
                'DiskReadBytes',
                'DiskWriteBytes'
            ]
            
            for metric_name in metric_names:
                response = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/EC2',
                    MetricName=metric_name,
                    Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=300,  # 5-minute intervals
                    Statistics=['Average']
                )
                
                if response['Datapoints']:
                    metrics[metric_name] = response['Datapoints'][0]['Average']
                else:
                    metrics[metric_name] = 0
                    
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics for instance {instance_id}: {str(e)}")
            return None
            
    def estimate_energy_consumption(self, cpu_utilization: float, instance_type: str):
        """Estimate energy consumption based on CPU utilization and instance type."""
        # These are approximate values, adjust based on your instance types
        instance_base_power = {
            't2.micro': 2,
            't2.small': 4,
            't2.medium': 8,
            't3.micro': 2,
            't3.small': 4,
            't3.medium': 8,
            # Add more instance types as needed
        }
        
        base_power = instance_base_power.get(instance_type, 5)
        max_power = base_power * 2.5
        
        # Linear relationship between CPU utilization and power consumption
        power_consumption = base_power + (max_power - base_power) * (cpu_utilization / 100)
        return power_consumption
        
    def estimate_carbon_footprint(self, energy_consumption: float, region: str):
        """Estimate carbon footprint based on energy consumption and region."""
        # Carbon intensity factors (gCO2/kWh) for different regions
        carbon_factors = {
            'us-east-1': 400,
            'eu-west-1': 200,
            'ap-southeast-1': 600,
            # Add more regions as needed
        }
        
        factor = carbon_factors.get(region, 500)
        return (energy_consumption / 1000) * factor  # Convert to kg CO2
        
    def collect_and_save_data(self, duration_minutes: int = 5):
        """Collect real-time data and save to CSV files."""
        try:
            # Get all running instances
            instances = self.ec2.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
            )
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=duration_minutes)
            
            workload_data = []
            energy_metrics = []
            
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    instance_type = instance['InstanceType']
                    region = instance['Placement']['AvailabilityZone'][:-1]
                    
                    metrics = self.get_instance_metrics(instance_id, start_time, end_time)
                    if metrics:
                        # Calculate energy consumption and carbon footprint
                        energy_consumption = self.estimate_energy_consumption(
                            metrics['CPUUtilization'],
                            instance_type
                        )
                        carbon_footprint = self.estimate_carbon_footprint(
                            energy_consumption,
                            region
                        )
                        
                        # Prepare workload data
                        workload_data.append({
                            'timestamp': end_time.isoformat(),
                            'cpu_utilization': metrics['CPUUtilization'],
                            'memory_usage': metrics.get('MemoryUtilization', 0),
                            'network_in': metrics['NetworkIn'],
                            'network_out': metrics['NetworkOut'],
                            'workload_demand': max(1, int(metrics['CPUUtilization'] / 20))  # Simple estimation
                        })
                        
                        # Prepare energy metrics
                        energy_metrics.append({
                            'timestamp': end_time.isoformat(),
                            'instance_id': instance_id,
                            'instance_type': instance_type,
                            'region': region,
                            'energy_consumption': energy_consumption,
                            'carbon_footprint': carbon_footprint,
                            'cpu_utilization': metrics['CPUUtilization'],
                            'memory_usage': metrics.get('MemoryUtilization', 0)
                        })
            
            # Save to CSV files
            if workload_data:
                workload_df = pd.DataFrame(workload_data)
                workload_df.to_csv(
                    os.path.join(self.data_dir, 'workload_data.csv'),
                    mode='a',
                    header=not os.path.exists(os.path.join(self.data_dir, 'workload_data.csv')),
                    index=False
                )
                
            if energy_metrics:
                energy_df = pd.DataFrame(energy_metrics)
                energy_df.to_csv(
                    os.path.join(self.data_dir, 'energy_metrics.csv'),
                    mode='a',
                    header=not os.path.exists(os.path.join(self.data_dir, 'energy_metrics.csv')),
                    index=False
                )
                
            logger.info(f"Collected data for {len(workload_data)} instances")
            
        except Exception as e:
            logger.error(f"Failed to collect and save data: {str(e)}")
            
    def start_collection(self, interval_minutes: int = 5):
        """Start continuous data collection."""
        logger.info("Starting real-time data collection...")
        
        try:
            while True:
                self.collect_and_save_data(interval_minutes)
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            logger.info("Data collection stopped by user")
        except Exception as e:
            logger.error(f"Data collection failed: {str(e)}")
            
if __name__ == "__main__":
    collector = RealTimeDataCollector()
    collector.start_collection()
