from prometheus_client import Counter, Gauge, Histogram, Summary
import time
import functools

# System metrics
REQUESTS_TOTAL = Counter(
    'eaawas_requests_total',
    'Total number of requests',
    ['endpoint', 'method', 'status']
)

RESPONSE_TIME = Histogram(
    'eaawas_response_time_seconds',
    'Response time in seconds',
    ['endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

# Resource metrics
CPU_UTILIZATION = Gauge(
    'eaawas_cpu_utilization_percent',
    'CPU utilization percentage',
    ['instance_id']
)

MEMORY_USAGE = Gauge(
    'eaawas_memory_usage_bytes',
    'Memory usage in bytes',
    ['instance_id']
)

# Energy metrics
ENERGY_CONSUMPTION = Gauge(
    'eaawas_energy_consumption_watts',
    'Energy consumption in watts',
    ['instance_id']
)

CARBON_FOOTPRINT = Gauge(
    'eaawas_carbon_footprint_kg',
    'Carbon footprint in kg CO2',
    ['instance_id']
)

# ML metrics
PREDICTION_TIME = Summary(
    'eaawas_prediction_time_seconds',
    'Time spent making predictions'
)

PREDICTION_ACCURACY = Gauge(
    'eaawas_prediction_accuracy_percent',
    'ML model prediction accuracy'
)

# Workload metrics
WORKLOAD_ALLOCATION = Counter(
    'eaawas_workload_allocations_total',
    'Total number of workload allocations',
    ['priority', 'status']
)

ALLOCATION_TIME = Histogram(
    'eaawas_allocation_time_seconds',
    'Time spent allocating workloads',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

# System health metrics
SYSTEM_HEALTH = Gauge(
    'eaawas_system_health',
    'Overall system health score (0-100)',
    ['component']
)

COMPONENT_STATUS = Gauge(
    'eaawas_component_status',
    'Component status (0=down, 1=degraded, 2=healthy)',
    ['component']
)

# Resource efficiency metrics
RESOURCE_EFFICIENCY = Gauge(
    'eaawas_resource_efficiency',
    'Resource utilization efficiency score',
    ['resource_type', 'instance_id']
)

RESOURCE_WASTE = Counter(
    'eaawas_resource_waste',
    'Accumulated resource waste',
    ['resource_type', 'instance_id']
)

# Cost metrics
COST_METRICS = Gauge(
    'eaawas_cost',
    'Cost metrics in USD',
    ['cost_type', 'instance_id']
)

COST_SAVINGS = Counter(
    'eaawas_cost_savings',
    'Accumulated cost savings in USD',
    ['optimization_type']
)

# Sustainability metrics
GREEN_ENERGY_RATIO = Gauge(
    'eaawas_green_energy_ratio',
    'Ratio of green energy usage (0-1)',
    ['region']
)

CARBON_SAVINGS = Counter(
    'eaawas_carbon_savings',
    'Carbon emissions saved in kg CO2',
    ['optimization_type']
)

# Performance metrics
RESOURCE_SATURATION = Gauge(
    'eaawas_resource_saturation',
    'Resource saturation level (0-1)',
    ['resource_type', 'instance_id']
)

QUEUE_LENGTH = Gauge(
    'eaawas_queue_length',
    'Number of items in processing queue',
    ['queue_type']
)

# Error metrics
ERROR_RATE = Counter(
    'eaawas_errors_total',
    'Total number of errors',
    ['error_type', 'component']
)

ERROR_DURATION = Histogram(
    'eaawas_error_duration_seconds',
    'Time taken to resolve errors',
    ['error_type'],
    buckets=[1, 5, 15, 30, 60, 300]
)

# ML model metrics
MODEL_ACCURACY = Gauge(
    'eaawas_model_accuracy',
    'ML model accuracy metrics',
    ['model_type', 'metric_type']
)

PREDICTION_ERROR = Histogram(
    'eaawas_prediction_error',
    'ML model prediction error distribution',
    ['model_type'],
    buckets=[0.1, 0.5, 1, 2, 5, 10]
)

def track_time(metric):
    """Decorator to track function execution time."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            metric.observe(duration)
            return result
        return wrapper
    return decorator

def track_requests(endpoint):
    """Decorator to track API requests."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                REQUESTS_TOTAL.labels(
                    endpoint=endpoint,
                    method='GET',
                    status='success'
                ).inc()
                return result
            except Exception as e:
                REQUESTS_TOTAL.labels(
                    endpoint=endpoint,
                    method='GET',
                    status='error'
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                RESPONSE_TIME.labels(endpoint=endpoint).observe(duration)
        return wrapper
    return decorator

def update_resource_metrics(instance_id, cpu_util, memory_usage):
    """Update resource utilization metrics."""
    CPU_UTILIZATION.labels(instance_id=instance_id).set(cpu_util)
    MEMORY_USAGE.labels(instance_id=instance_id).set(memory_usage)

def update_energy_metrics(instance_id, energy_consumption, carbon_footprint):
    """Update energy consumption metrics."""
    ENERGY_CONSUMPTION.labels(instance_id=instance_id).set(energy_consumption)
    CARBON_FOOTPRINT.labels(instance_id=instance_id).set(carbon_footprint)

def update_ml_metrics(accuracy):
    """Update ML model metrics."""
    PREDICTION_ACCURACY.set(accuracy)

def track_workload_allocation(priority, status):
    """Track workload allocation metrics."""
    WORKLOAD_ALLOCATION.labels(
        priority=priority,
        status=status
    ).inc()

def update_system_health(component: str, score: float):
    """Update system health score."""
    SYSTEM_HEALTH.labels(component=component).set(score)

def update_component_status(component: str, status: int):
    """Update component status."""
    COMPONENT_STATUS.labels(component=component).set(status)

def track_resource_efficiency(resource_type: str, instance_id: str, score: float):
    """Track resource utilization efficiency."""
    RESOURCE_EFFICIENCY.labels(
        resource_type=resource_type,
        instance_id=instance_id
    ).set(score)

def record_cost_metrics(cost_type: str, instance_id: str, amount: float):
    """Record cost-related metrics."""
    COST_METRICS.labels(
        cost_type=cost_type,
        instance_id=instance_id
    ).set(amount)

def update_sustainability_metrics(region: str, green_ratio: float):
    """Update sustainability metrics."""
    GREEN_ENERGY_RATIO.labels(region=region).set(green_ratio)

def track_error(error_type: str, component: str):
    """Track error occurrences."""
    ERROR_RATE.labels(
        error_type=error_type,
        component=component
    ).inc()

def update_ml_metrics(model_type: str, metric_type: str, value: float):
    """Update ML model metrics."""
    MODEL_ACCURACY.labels(
        model_type=model_type,
        metric_type=metric_type
    ).set(value)

def track_prediction_error(model_type: str, error: float):
    """Track ML model prediction errors."""
    PREDICTION_ERROR.labels(model_type=model_type).observe(error)

def update_queue_metrics(queue_type: str, length: int):
    """Update queue length metrics."""
    QUEUE_LENGTH.labels(queue_type=queue_type).set(length)

def track_resource_saturation(resource_type: str, instance_id: str, level: float):
    """Track resource saturation levels."""
    RESOURCE_SATURATION.labels(
        resource_type=resource_type,
        instance_id=instance_id
    ).set(level)
