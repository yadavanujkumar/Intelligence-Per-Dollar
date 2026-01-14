"""Streamlit dashboard for visualizing LLM efficiency metrics."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from src.models import get_session, BenchmarkRepository
from src.router import ValueRouter

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="LLM Cost-Efficiency Dashboard",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database connection
@st.cache_resource
def init_database():
    database_url = os.getenv("DATABASE_URL", "sqlite:///./benchmark.db")
    session = get_session(database_url)
    return BenchmarkRepository(session)

repository = init_database()
router = ValueRouter(repository)

# Title and description
st.title("💡 LLM Cost-Efficiency Dashboard")
st.markdown("### Intelligence-per-Dollar Benchmarking & Analysis")

# Sidebar filters
st.sidebar.header("Filters")
category_filter = st.sidebar.selectbox(
    "Task Category",
    ["All", "coding", "summarization", "creative_writing"]
)

quality_threshold = st.sidebar.slider(
    "Quality Threshold",
    min_value=0.0,
    max_value=1.0,
    value=0.8,
    step=0.05,
    help="Minimum intelligence score required"
)

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Efficiency Frontier", 
    "🏆 Model Rankings", 
    "📈 Detailed Metrics",
    "🎯 Smart Router"
])

# Tab 1: Efficiency Frontier
with tab1:
    st.header("Efficiency Frontier: Value Kings vs. Overpriced")
    
    category = None if category_filter == "All" else category_filter
    frontier_data = router.get_efficiency_frontier(category=category)
    
    if frontier_data:
        df_frontier = pd.DataFrame(frontier_data)
        
        # Create scatter plot
        fig = px.scatter(
            df_frontier,
            x="avg_cost",
            y="avg_intelligence_score",
            size="intelligence_per_dollar",
            color="model_name",
            hover_data={
                "model_name": True,
                "avg_cost": ":.4f",
                "avg_intelligence_score": ":.3f",
                "intelligence_per_dollar": ":.2f",
                "avg_latency": ":.2f",
                "total_samples": True
            },
            labels={
                "avg_cost": "Average Cost per Request ($)",
                "avg_intelligence_score": "Intelligence Score",
                "intelligence_per_dollar": "Intelligence/$"
            },
            title="LLM Efficiency Frontier"
        )
        
        fig.update_layout(
            height=600,
            xaxis_title="Cost per Request ($)",
            yaxis_title="Intelligence Score (0-1)",
            hovermode="closest"
        )
        
        # Add quadrant lines
        if len(df_frontier) > 0:
            median_cost = df_frontier["avg_cost"].median()
            median_quality = df_frontier["avg_intelligence_score"].median()
            
            fig.add_hline(
                y=median_quality, 
                line_dash="dash", 
                line_color="gray",
                annotation_text="Median Quality"
            )
            fig.add_vline(
                x=median_cost, 
                line_dash="dash", 
                line_color="gray",
                annotation_text="Median Cost"
            )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Interpretation guide
        col1, col2 = st.columns(2)
        with col1:
            st.success("🏆 **Value Kings**: High quality, low cost (top-left quadrant)")
        with col2:
            st.error("💸 **Overpriced**: Low quality, high cost (bottom-right quadrant)")
    else:
        st.warning("No benchmark data available. Run a benchmark first!")

# Tab 2: Model Rankings
with tab2:
    st.header("Model Rankings by Intelligence-per-Dollar")
    
    if frontier_data:
        df_ranked = pd.DataFrame(frontier_data)
        df_ranked = df_ranked.sort_values("intelligence_per_dollar", ascending=False)
        
        # Display ranking
        for idx, row in df_ranked.iterrows():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            
            with col1:
                st.subheader(f"{idx + 1}. {row['model_name']}")
            with col2:
                st.metric(
                    "Intelligence/$",
                    f"{row['intelligence_per_dollar']:.2f}"
                )
            with col3:
                st.metric(
                    "Quality Score",
                    f"{row['avg_intelligence_score']:.3f}"
                )
            with col4:
                st.metric(
                    "Avg Cost",
                    f"${row['avg_cost']:.4f}"
                )
            
            st.divider()
        
        # Bar chart comparison
        fig_bar = go.Figure()
        
        fig_bar.add_trace(go.Bar(
            name="Intelligence per Dollar",
            x=df_ranked["model_name"],
            y=df_ranked["intelligence_per_dollar"],
            marker_color="lightblue"
        ))
        
        fig_bar.update_layout(
            title="Intelligence-per-Dollar Comparison",
            xaxis_title="Model",
            yaxis_title="Intelligence per Dollar",
            height=400
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("No benchmark data available.")

# Tab 3: Detailed Metrics
with tab3:
    st.header("Detailed Performance Metrics")
    
    if frontier_data:
        df_metrics = pd.DataFrame(frontier_data)
        
        # Multi-metric comparison
        metrics_to_plot = st.multiselect(
            "Select metrics to compare",
            ["avg_intelligence_score", "avg_cost", "avg_latency", "intelligence_per_dollar"],
            default=["avg_intelligence_score", "avg_cost"]
        )
        
        if metrics_to_plot:
            # Normalize metrics for comparison
            df_normalized = df_metrics.copy()
            for col in metrics_to_plot:
                if col in df_normalized.columns:
                    min_val = df_normalized[col].min()
                    max_val = df_normalized[col].max()
                    if max_val > min_val:
                        df_normalized[f"{col}_norm"] = (df_normalized[col] - min_val) / (max_val - min_val)
            
            # Radar chart
            fig_radar = go.Figure()
            
            for _, row in df_metrics.iterrows():
                values = []
                for metric in metrics_to_plot:
                    if metric in df_normalized.columns:
                        norm_col = f"{metric}_norm"
                        if norm_col in df_normalized.columns:
                            val = df_normalized[df_normalized["model_name"] == row["model_name"]][norm_col].values[0]
                            values.append(val)
                
                if values:
                    fig_radar.add_trace(go.Scatterpolar(
                        r=values,
                        theta=metrics_to_plot,
                        name=row["model_name"]
                    ))
            
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                title="Normalized Performance Metrics",
                height=500
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Data table
        st.subheader("Raw Data")
        st.dataframe(
            df_metrics,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = df_metrics.to_csv(index=False)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f"llm_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No benchmark data available.")

# Tab 4: Smart Router
with tab4:
    st.header("🎯 Smart Model Router")
    st.markdown("Let the router automatically select the best model for your needs!")
    
    with st.form("router_form"):
        prompt_input = st.text_area(
            "Enter your prompt",
            height=150,
            placeholder="Type your prompt here..."
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            router_quality = st.slider(
                "Quality Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.8,
                step=0.05
            )
            
            router_category = st.selectbox(
                "Task Category (optional)",
                ["Auto-detect", "coding", "summarization", "creative_writing"]
            )
        
        with col2:
            max_cost_input = st.number_input(
                "Max Cost per Request ($)",
                min_value=0.0,
                value=0.05,
                step=0.01,
                format="%.4f"
            )
        
        submit_button = st.form_submit_button("🚀 Get Model Recommendation")
    
    if submit_button and prompt_input:
        category_param = None if router_category == "Auto-detect" else router_category
        
        selection = router.select_model(
            quality_threshold=router_quality,
            category=category_param,
            max_cost=max_cost_input if max_cost_input > 0 else None
        )
        
        st.success(f"**Selected Model:** {selection['model_name']}")
        st.info(f"**Reasoning:** {selection['reasoning']}")
        
        if "expected_quality" in selection:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Expected Quality", f"{selection['expected_quality']:.3f}")
            with col2:
                st.metric("Expected Cost", f"${selection['expected_cost']:.4f}")
            with col3:
                st.metric("Expected Latency", f"{selection['expected_latency']:.2f}s")
            with col4:
                st.metric("Intelligence/$", f"{selection['intelligence_per_dollar']:.2f}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "This dashboard visualizes the cost-efficiency of different LLMs "
    "based on benchmark results. Use it to identify 'Value Kings' and "
    "avoid 'Overpriced' models."
)

# Auto-refresh option
if st.sidebar.checkbox("Auto-refresh (60s)"):
    st.rerun()
