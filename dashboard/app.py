import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class EAAWASDashboard:
    def __init__(self):
        st.set_page_config(
            page_title="EAAWAS Dashboard",
            page_icon="🌍",
            layout="wide"
        )
        self.load_data()
        
    def load_data(self):
        """Load data from CSV files and API."""
        try:
            self.workload_data = pd.read_csv(
                project_root / 'data/workload_data.csv'
            )
            self.energy_data = pd.read_csv(
                project_root / 'data/energy_metrics.csv'
            )
            
            # Convert timestamps
            self.workload_data['timestamp'] = pd.to_datetime(
                self.workload_data['timestamp']
            )
            self.energy_data['timestamp'] = pd.to_datetime(
                self.energy_data['timestamp']
            )
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            
    def render_header(self):
        """Render dashboard header."""
        st.title("🌍 EAAWAS Dashboard")
        st.markdown("""
        Energy-Aware Adaptive Workload Allocation System monitoring dashboard.
        Monitor real-time metrics, energy consumption, and system performance.
        """)
        
    def render_metrics_summary(self):
        """Render key metrics summary."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            latest_cpu = self.workload_data['cpu_utilization'].iloc[-1]
            st.metric(
                "CPU Utilization",
                f"{latest_cpu:.1f}%",
                f"{latest_cpu - self.workload_data['cpu_utilization'].iloc[-2]:.1f}%"
            )
            
        with col2:
            latest_energy = self.energy_data['energy_consumption'].iloc[-1]
            st.metric(
                "Energy Consumption",
                f"{latest_energy:.1f}W",
                f"{latest_energy - self.energy_data['energy_consumption'].iloc[-2]:.1f}W"
            )
            
        with col3:
            latest_carbon = self.energy_data['carbon_footprint'].iloc[-1]
            st.metric(
                "Carbon Footprint",
                f"{latest_carbon:.3f}kg",
                f"{latest_carbon - self.energy_data['carbon_footprint'].iloc[-2]:.3f}kg"
            )
            
        with col4:
            workload_demand = self.workload_data['workload_demand'].iloc[-1]
            st.metric(
                "Workload Demand",
                f"{workload_demand}",
                f"{workload_demand - self.workload_data['workload_demand'].iloc[-2]}"
            )
            
    def render_time_series(self):
        """Render time series charts."""
        # Energy consumption over time
        fig_energy = px.line(
            self.energy_data,
            x='timestamp',
            y='energy_consumption',
            title='Energy Consumption Over Time'
        )
        st.plotly_chart(fig_energy, use_container_width=True)
        
        # CPU and Memory usage
        col1, col2 = st.columns(2)
        
        with col1:
            fig_cpu = px.line(
                self.workload_data,
                x='timestamp',
                y='cpu_utilization',
                title='CPU Utilization'
            )
            st.plotly_chart(fig_cpu, use_container_width=True)
            
        with col2:
            fig_memory = px.line(
                self.workload_data,
                x='timestamp',
                y='memory_usage',
                title='Memory Usage'
            )
            st.plotly_chart(fig_memory, use_container_width=True)
            
    def render_resource_allocation(self):
        """Render resource allocation visualization."""
        st.subheader("Resource Allocation")
        
        # Get instance data from energy metrics
        instances = self.energy_data['instance_id'].unique()
        
        # Create a treemap of resource allocation
        fig = go.Figure(go.Treemap(
            labels=[f"Instance {i}" for i in instances],
            parents=[""] * len(instances),
            values=self.energy_data.groupby('instance_id')['energy_consumption'].mean(),
            textinfo="label+value"
        ))
        
        fig.update_layout(
            title="Resource Allocation by Instance"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    def render_performance_metrics(self):
        """Render system performance metrics."""
        st.subheader("System Performance")
        
        try:
            # Get metrics from Prometheus
            response = requests.get("http://localhost:9090/api/v1/query", params={
                'query': 'eaawas_response_time_seconds_bucket'
            })
            metrics = response.json()
            
            if metrics['status'] == 'success':
                # Process and display metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "API Response Time (p95)",
                        "0.2s"  # Replace with actual metric
                    )
                    
                with col2:
                    st.metric(
                        "Request Success Rate",
                        "99.9%"  # Replace with actual metric
                    )
        except Exception:
            st.warning("Could not fetch performance metrics")
            
    def render_advanced_visualizations(self):
        """Render advanced visualization types."""
        st.subheader("Advanced Analytics")
        
        # 1. Heatmap of resource usage patterns
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=self.workload_data.pivot_table(
                values='cpu_utilization',
                index=self.workload_data['timestamp'].dt.hour,
                columns=self.workload_data['timestamp'].dt.dayofweek,
                aggfunc='mean'
            ),
            x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            y=list(range(24)),
            colorscale='Viridis'
        ))
        fig_heatmap.update_layout(
            title='Resource Usage Patterns (Hour vs Day)',
            xaxis_title='Day of Week',
            yaxis_title='Hour of Day'
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

        # 2. Correlation Matrix
        metrics = ['cpu_utilization', 'memory_usage', 'network_in', 'network_out']
        corr_matrix = self.workload_data[metrics].corr()
        fig_corr = px.imshow(
            corr_matrix,
            labels=dict(color="Correlation"),
            title="Metric Correlations"
        )
        st.plotly_chart(fig_corr, use_container_width=True)

        # 3. Energy Efficiency Scatter Plot
        fig_scatter = px.scatter(
            self.energy_data,
            x='cpu_utilization',
            y='energy_consumption',
            color='instance_type',
            size='memory_usage',
            hover_data=['instance_id'],
            title='Energy Efficiency by Instance Type'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # 4. Resource Distribution
        col1, col2 = st.columns(2)
        with col1:
            fig_dist_cpu = px.histogram(
                self.workload_data,
                x='cpu_utilization',
                nbins=30,
                title='CPU Utilization Distribution'
            )
            st.plotly_chart(fig_dist_cpu, use_container_width=True)

        with col2:
            fig_dist_memory = px.histogram(
                self.workload_data,
                x='memory_usage',
                nbins=30,
                title='Memory Usage Distribution'
            )
            st.plotly_chart(fig_dist_memory, use_container_width=True)

        # 5. Workload Prediction
        st.subheader("Workload Prediction")
        fig_prediction = go.Figure()
        fig_prediction.add_trace(go.Scatter(
            x=self.workload_data['timestamp'],
            y=self.workload_data['workload_demand'],
            name='Actual'
        ))
        # Add predicted values (example)
        fig_prediction.add_trace(go.Scatter(
            x=self.workload_data['timestamp'],
            y=self.workload_data['workload_demand'].rolling(window=5).mean(),
            name='Predicted',
            line=dict(dash='dash')
        ))
        fig_prediction.update_layout(title='Workload Prediction vs Actual')
        st.plotly_chart(fig_prediction, use_container_width=True)

    def render_alerts(self):
        """Render system alerts and warnings."""
        st.subheader("System Alerts")
        
        # Check for high energy consumption
        high_energy = self.energy_data[
            self.energy_data['energy_consumption'] > 
            self.energy_data['energy_consumption'].mean() * 1.5
        ]
        
        if not high_energy.empty:
            st.warning(
                f"High energy consumption detected for {len(high_energy)} instances"
            )
            
        # Check for high CPU usage
        high_cpu = self.workload_data[
            self.workload_data['cpu_utilization'] > 80
        ]
        
        if not high_cpu.empty:
            st.warning(
                f"High CPU utilization detected: {len(high_cpu)} instances above 80%"
            )
            
    def render_controls(self):
        """Render dashboard controls."""
        st.sidebar.title("Controls")
        
        # Time range selector
        time_range = st.sidebar.selectbox(
            "Time Range",
            ["Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days"]
        )
        
        # Metric selectors
        st.sidebar.multiselect(
            "Metrics to Display",
            ["CPU Utilization", "Memory Usage", "Energy Consumption", 
             "Carbon Footprint", "Network I/O"],
            default=["CPU Utilization", "Energy Consumption"]
        )
        
        # Update frequency
        st.sidebar.slider(
            "Update Frequency (seconds)",
            min_value=5,
            max_value=60,
            value=30
        )
        
    def run(self):
        """Run the dashboard application."""
        self.render_header()
        self.render_controls()
        self.render_metrics_summary()
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "Resource Usage", "Performance", "Advanced Analytics", "Alerts"
        ])
        
        with tab1:
            self.render_time_series()
            self.render_resource_allocation()
            
        with tab2:
            self.render_performance_metrics()
            
        with tab3:
            self.render_advanced_visualizations()
            
        with tab4:
            self.render_alerts()

if __name__ == "__main__":
    dashboard = EAAWASDashboard()
    dashboard.run()
