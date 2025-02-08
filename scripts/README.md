# Real-Time Data Collection Script

This script collects real-time metrics from your AWS infrastructure for the EAAWAS system.

## Prerequisites

1. AWS credentials configured (`aws configure`)
2. Required Python packages:
   - boto3
   - pandas
   - logging

## What Data is Collected?

### Workload Data
- CPU Utilization
- Memory Usage
- Network I/O
- Estimated Workload Demand

### Energy Metrics
- Instance Details (ID, Type, Region)
- Energy Consumption (estimated)
- Carbon Footprint (estimated)
- Resource Utilization

## How to Run

1. Make sure your AWS credentials are configured:
```bash
aws configure
```

2. Install required packages:
```bash
pip install boto3 pandas
```

3. Run the script:
```bash
python collect_realtime_data.py
```

The script will continuously collect data at 5-minute intervals and save it to:
- `data/workload_data.csv`
- `data/energy_metrics.csv`

## Notes

- Energy consumption is estimated based on instance type and CPU utilization
- Carbon footprint is calculated using regional carbon intensity factors
- Data is collected every 5 minutes by default (configurable)
- Press Ctrl+C to stop data collection
