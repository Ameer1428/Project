# Energy-Aware Adaptive Workload Allocation System (EAAWAS)

EAAWAS is a sophisticated system designed to optimize energy efficiency in multi-cloud environments by dynamically allocating workloads based on real-time energy metrics, workload demands, and sustainability indicators.

## Features

- Real-time energy consumption monitoring
- ML-based workload prediction
- Dynamic resource allocation
- Carbon footprint tracking
- Multi-cloud support (AWS EC2 and EKS)
- REST API endpoints
- Prometheus metrics integration

## Prerequisites

- Python 3.8 or higher
- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Docker (for containerized workloads)
- Kubernetes CLI (kubectl) for EKS integration

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd EAAWAS
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/MacOS
python -m venv venv
source venv/bin/activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

4. Configure AWS credentials:
```bash
aws configure
```
Enter your AWS credentials when prompted:
- AWS Access Key ID
- AWS Secret Access Key
- Default region name (e.g., us-east-1)
- Default output format (json)

## Configuration

1. Update AWS configuration (`configs/aws_config.json`):
```json
{
    "region": "us-east-1",
    "metrics_bucket": "eaawas-metrics",
    "energy_threshold": 80,
    "monitoring_interval": 300
}
```

2. Configure ML hyperparameters (`configs/ml_hyperparameters.json`):
```json
{
    "n_estimators": 100,
    "max_depth": 10,
    "test_size": 0.2,
    "random_state": 42
}
```

## Project Structure

```
EAAWAS/
│
├── data/                          # Datasets for training ML models
│   ├── workload_data.csv         # Historical workload data
│   ├── energy_metrics.csv        # Energy consumption metrics
│
├── models/                        # Trained ML models
│   ├── workload_prediction.pkl   # Predictive model for workload
│   ├── energy_optimization.pkl   # Energy optimization model
│
├── src/                          # Source code directory
│   ├── ml_training.py           # ML model training scripts
│   ├── workload_allocator.py    # Dynamic workload allocation logic
│   ├── energy_monitoring.py     # Real-time energy monitoring logic
│   ├── api_integration.py       # Integration with sustainability APIs
```

## Running the System

1. Train the ML model:
```bash
cd src
python ml_training.py
```

2. Start the energy monitoring service:
```bash
python energy_monitoring.py
```

3. Launch the API server:
```bash
python api_integration.py
```

The API server will start on `http://localhost:8000`

## API Endpoints

### Workload Allocation
```
POST /workload/allocate
```
Request body:
```json
{
    "cpu_request": 2.0,
    "memory_request": "4Gi",
    "priority": "high",
    "max_energy_consumption": 100.0
}
```

### Energy Metrics
```
GET /metrics/energy/{instance_id}
```

### Sustainability Metrics
```
GET /metrics/sustainability/{region}
```

## Monitoring

1. Access Prometheus metrics:
```
http://localhost:8000/metrics
```

2. View energy consumption logs:
```bash
tail -f logs/energy_logs.txt
```

3. Monitor CloudWatch metrics:
- Navigate to AWS CloudWatch console
- Check the "EAAWAS/Metrics" namespace

## AWS EKS Integration

1. Configure EKS cluster:
```bash
aws eks update-kubeconfig --name your-cluster-name --region your-region
```

2. Verify connection:
```bash
kubectl get nodes
```

## Troubleshooting

1. Check application logs:
```bash
tail -f logs/allocation_logs.txt
tail -f logs/energy_logs.txt
```

2. Verify AWS connectivity:
```bash
aws sts get-caller-identity
```

3. Test API endpoints:
```bash
curl http://localhost:8000/metrics/sustainability/us-east-1
```

## Common Issues

1. AWS Credentials:
- Ensure AWS credentials are properly configured
- Verify IAM permissions for required services

2. ML Model Training:
- Check if training data is properly formatted
- Verify model hyperparameters in configuration

3. API Connection:
- Confirm API server is running
- Check for correct endpoint URLs and request formats

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and queries:
- Contact the developer: Ameer (ameerkhanpk1428@gmail.com)
- Create an issue in the repository
- Check the documentation

## Acknowledgments

- AWS Cloud Services
- Scikit-learn community
- FastAPI framework
- Prometheus monitoring