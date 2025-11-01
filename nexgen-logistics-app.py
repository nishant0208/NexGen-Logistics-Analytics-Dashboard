import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from datetime import timedelta
import warnings
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="NexGen Logistics Dashboard",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .insight-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    .problem-highlight {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and process all CSV files"""
    try:
        # Load all datasets
        orders_df = pd.read_csv('orders.csv')
        delivery_df = pd.read_csv('delivery_performance.csv')
        cost_df = pd.read_csv('cost_breakdown.csv')
        routes_df = pd.read_csv('routes_distance.csv')
        fleet_df = pd.read_csv('vehicle_fleet.csv')
        warehouse_df = pd.read_csv('warehouse_inventory.csv')
        feedback_df = pd.read_csv('customer_feedback.csv')
        
        # Convert date columns
        orders_df['Order_Date'] = pd.to_datetime(orders_df['Order_Date'])
        feedback_df['Feedback_Date'] = pd.to_datetime(feedback_df['Feedback_Date'])
        warehouse_df['Last_Restocked_Date'] = pd.to_datetime(warehouse_df['Last_Restocked_Date'])
        
        # Merge main datasets on Order_ID
        main_df = orders_df.merge(delivery_df, on='Order_ID', how='left')
        main_df = main_df.merge(cost_df, on='Order_ID', how='left')
        main_df = main_df.merge(routes_df, on='Order_ID', how='left')
        main_df = main_df.merge(feedback_df, on='Order_ID', how='left')
        
        # Calculate derived metrics
        main_df['Total_Cost'] = (main_df['Fuel_Cost'] + main_df['Labor_Cost'] + 
                                main_df['Vehicle_Maintenance'] + main_df['Insurance'] + 
                                main_df['Packaging_Cost'] + main_df['Technology_Platform_Fee'] + 
                                main_df['Other_Overhead'])
        
        main_df['Delivery_Delay_Days'] = main_df['Actual_Delivery_Days'] - main_df['Promised_Delivery_Days']
        main_df['On_Time'] = main_df['Delivery_Status'] == 'On-Time'
        
        return main_df, fleet_df, warehouse_df
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

def create_kpi_metrics(df):
    """Calculate key performance indicators"""
    if df is None or df.empty:
        return {}
    
    total_orders = len(df)
    on_time_rate = (df['On_Time'].sum() / total_orders * 100) if total_orders > 0 else 0
    avg_rating = df['Customer_Rating'].mean() if 'Customer_Rating' in df.columns else 0
    avg_cost = df['Total_Cost'].mean() if 'Total_Cost' in df.columns else 0
    severely_delayed_rate = ((df['Delivery_Status'] == 'Severely-Delayed').sum() / total_orders * 100) if total_orders > 0 else 0
    
    return {
        'total_orders': total_orders,
        'on_time_rate': on_time_rate,
        'avg_rating': avg_rating,
        'avg_cost': avg_cost,
        'severely_delayed_rate': severely_delayed_rate
    }

def main():
    # Load data
    main_df, fleet_df, warehouse_df = load_data()
    
    if main_df is None:
        st.error("Unable to load data. Please ensure CSV files are available.")
        return
    
    # Title
    st.markdown('<h1 class="main-header">🚛 NexGen Logistics Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### Transforming Operations Through Data-Driven Insights")
    
    # Sidebar for filters
    st.sidebar.header("🔧 Filters & Controls")
    
    # Date filter
    if 'Order_Date' in main_df.columns:
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=[main_df['Order_Date'].min(), main_df['Order_Date'].max()],
            min_value=main_df['Order_Date'].min(),
            max_value=main_df['Order_Date'].max()
        )
        
        if len(date_range) == 2:
            main_df = main_df[(main_df['Order_Date'] >= pd.to_datetime(date_range[0])) & 
                             (main_df['Order_Date'] <= pd.to_datetime(date_range[1]))]
    
    # Other filters
    carriers = st.sidebar.multiselect("Select Carriers", 
                                     options=main_df['Carrier'].dropna().unique() if 'Carrier' in main_df.columns else [],
                                     default=main_df['Carrier'].dropna().unique() if 'Carrier' in main_df.columns else [])
    
    priorities = st.sidebar.multiselect("Select Priority Levels",
                                       options=main_df['Priority'].unique() if 'Priority' in main_df.columns else [],
                                       default=main_df['Priority'].unique() if 'Priority' in main_df.columns else [])
    
    segments = st.sidebar.multiselect("Select Customer Segments",
                                     options=main_df['Customer_Segment'].unique() if 'Customer_Segment' in main_df.columns else [],
                                     default=main_df['Customer_Segment'].unique() if 'Customer_Segment' in main_df.columns else [])
    
    # Apply filters
    if carriers and 'Carrier' in main_df.columns:
        main_df = main_df[main_df['Carrier'].isin(carriers)]
    if priorities and 'Priority' in main_df.columns:
        main_df = main_df[main_df['Priority'].isin(priorities)]
    if segments and 'Customer_Segment' in main_df.columns:
        main_df = main_df[main_df['Customer_Segment'].isin(segments)]
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Dashboard", "🚚 Delivery Performance", "💰 Cost Analysis", 
        "🗺️ Routes & Distance", "📦 Inventory", "😊 Customer Experience", "🔍 Insights"
    ])
    
    # Tab 1: Dashboard Overview
    with tab1:
        st.header("Executive Dashboard")
        
        # KPI metrics
        kpis = create_kpi_metrics(main_df)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Orders", f"{kpis['total_orders']:,}")
        with col2:
            st.metric("On-Time Rate", f"{kpis['on_time_rate']:.1f}%", 
                     delta=f"{kpis['on_time_rate'] - 75:.1f}%" if kpis['on_time_rate'] > 0 else None)
        with col3:
            st.metric("Avg Rating", f"{kpis['avg_rating']:.1f}/5", 
                     delta=f"{kpis['avg_rating'] - 4:.1f}" if kpis['avg_rating'] > 0 else None)
        with col4:
            st.metric("Avg Cost/Order", f"₹{kpis['avg_cost']:,.0f}" if kpis['avg_cost'] > 0 else "N/A")
        with col5:
            st.metric("Severe Delays", f"{kpis['severely_delayed_rate']:.1f}%", 
                     delta=f"{kpis['severely_delayed_rate'] - 10:.1f}%" if kpis['severely_delayed_rate'] > 0 else None)
        
        # Charts row 1
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Delivery_Status' in main_df.columns:
                delivery_status_counts = main_df['Delivery_Status'].value_counts()
                fig = px.pie(values=delivery_status_counts.values, names=delivery_status_counts.index,
                           title="Delivery Status Distribution", color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'Carrier' in main_df.columns and 'Customer_Rating' in main_df.columns:
                carrier_ratings = main_df.groupby('Carrier')['Customer_Rating'].mean().sort_values(ascending=True)
                fig = px.bar(x=carrier_ratings.values, y=carrier_ratings.index, orientation='h',
                           title="Average Rating by Carrier", color=carrier_ratings.values,
                           color_continuous_scale='RdYlGn')
                st.plotly_chart(fig, use_container_width=True)
        
        # Charts row 2
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Order_Date' in main_df.columns and 'On_Time' in main_df.columns:
                daily_performance = main_df.groupby(main_df['Order_Date'].dt.date)['On_Time'].mean() * 100
                fig = px.line(x=daily_performance.index, y=daily_performance.values,
                            title="On-Time Delivery Rate Trend", markers=True)
                fig.update_yaxes(title="On-Time Rate (%)")
                fig.update_xaxes(title="Date")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'Product_Category' in main_df.columns and 'Order_Value_INR' in main_df.columns:
                category_revenue = main_df.groupby('Product_Category')['Order_Value_INR'].sum().sort_values(ascending=True)
                fig = px.bar(x=category_revenue.values, y=category_revenue.index, orientation='h',
                           title="Revenue by Product Category", color=category_revenue.values,
                           color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
    
    # Tab 2: Delivery Performance
    with tab2:
        st.header("Delivery Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Carrier' in main_df.columns and 'Delivery_Status' in main_df.columns:
                carrier_performance = pd.crosstab(main_df['Carrier'], main_df['Delivery_Status'], normalize='index') * 100
                fig = px.bar(carrier_performance, title="Delivery Performance by Carrier (%)",
                           color_discrete_sequence=['#ff7f7f', '#ffdd7f', '#7fff7f'])
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'Quality_Issue' in main_df.columns:
                quality_issues = main_df['Quality_Issue'].value_counts()
                fig = px.pie(values=quality_issues.values, names=quality_issues.index,
                           title="Quality Issues Distribution")
                st.plotly_chart(fig, use_container_width=True)
        
        # Delivery delays analysis
        if 'Delivery_Delay_Days' in main_df.columns and 'Distance_KM' in main_df.columns:
            fig = px.scatter(main_df, x='Distance_KM', y='Delivery_Delay_Days', color='Carrier',
                           title="Delivery Delays vs Distance", hover_data=['Order_ID'])
            fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="On-Time Threshold")
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 3: Cost Analysis
    with tab3:
        st.header("Cost Analysis Dashboard")
        
        # Cost breakdown pie chart
        cost_columns = ['Fuel_Cost', 'Labor_Cost', 'Vehicle_Maintenance', 'Insurance', 
                       'Packaging_Cost', 'Technology_Platform_Fee', 'Other_Overhead']
        
        if all(col in main_df.columns for col in cost_columns):
            total_costs = main_df[cost_columns].sum()
            fig = px.pie(values=total_costs.values, names=total_costs.index,
                        title="Cost Component Breakdown")
            st.plotly_chart(fig, use_container_width=True)
            
            # Cost by priority level
            col1, col2 = st.columns(2)
            
            with col1:
                if 'Priority' in main_df.columns and 'Total_Cost' in main_df.columns:
                    priority_costs = main_df.groupby('Priority')['Total_Cost'].mean()
                    fig = px.bar(x=priority_costs.index, y=priority_costs.values,
                               title="Average Cost by Priority Level", color=priority_costs.values,
                               color_continuous_scale='Reds')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'Carrier' in main_df.columns and 'Total_Cost' in main_df.columns:
                    carrier_costs = main_df.groupby('Carrier')['Total_Cost'].mean().sort_values(ascending=True)
                    fig = px.bar(x=carrier_costs.values, y=carrier_costs.index, orientation='h',
                               title="Average Cost by Carrier", color=carrier_costs.values,
                               color_continuous_scale='Oranges')
                    st.plotly_chart(fig, use_container_width=True)
    
    # Tab 4: Routes & Distance Analytics
    with tab4:
        st.header("Route & Distance Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Distance_KM' in main_df.columns and 'Actual_Delivery_Days' in main_df.columns:
                fig = px.scatter(main_df, x='Distance_KM', y='Actual_Delivery_Days', color='Priority',
                               title="Distance vs Delivery Time", hover_data=['Route'])
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'Weather_Impact' in main_df.columns and 'Delivery_Delay_Days' in main_df.columns:
                weather_impact = main_df.groupby('Weather_Impact')['Delivery_Delay_Days'].mean()
                fig = px.bar(x=weather_impact.index, y=weather_impact.values,
                           title="Weather Impact on Delivery Delays")
                st.plotly_chart(fig, use_container_width=True)
        
        # Traffic delays impact
        if 'Traffic_Delay_Minutes' in main_df.columns and 'Delivery_Delay_Days' in main_df.columns:
            fig = px.scatter(main_df, x='Traffic_Delay_Minutes', y='Delivery_Delay_Days',
                           title="Traffic Delays vs Overall Delivery Delays", 
                           hover_data=['Route', 'Carrier'])
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 5: Inventory Management
    with tab5:
        st.header("Inventory Management Dashboard")
        
        if warehouse_df is not None and not warehouse_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Stock levels by location
                location_stock = warehouse_df.groupby('Location')['Current_Stock_Units'].sum()
                fig = px.bar(x=location_stock.index, y=location_stock.values,
                           title="Total Stock by Location", color=location_stock.values,
                           color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Storage costs by location
                location_costs = warehouse_df.groupby('Location')['Storage_Cost_per_Unit'].mean()
                fig = px.bar(x=location_costs.index, y=location_costs.values,
                           title="Average Storage Cost by Location", color=location_costs.values,
                           color_continuous_scale='Reds')
                st.plotly_chart(fig, use_container_width=True)
            
            # Stock vs Reorder Level Analysis
            warehouse_df['Stock_Status'] = warehouse_df.apply(
                lambda x: 'Low Stock' if x['Current_Stock_Units'] <= x['Reorder_Level'] else 'Adequate', axis=1
            )
            
            stock_status_counts = warehouse_df['Stock_Status'].value_counts()
            fig = px.pie(values=stock_status_counts.values, names=stock_status_counts.index,
                        title="Warehouse Stock Status", color_discrete_sequence=['#ff6b6b', '#51cf66'])
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 6: Customer Experience
    with tab6:
        st.header("Customer Experience Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Customer_Rating' in main_df.columns:
                rating_dist = main_df['Customer_Rating'].value_counts().sort_index()
                fig = px.bar(x=rating_dist.index, y=rating_dist.values,
                           title="Customer Rating Distribution", color=rating_dist.values,
                           color_continuous_scale='RdYlGn')
                fig.update_xaxes(title="Rating (1-5 stars)")
                fig.update_yaxes(title="Number of Orders")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'Would_Recommend' in main_df.columns:
                recommend_counts = main_df['Would_Recommend'].value_counts()
                fig = px.pie(values=recommend_counts.values, names=recommend_counts.index,
                           title="Would Recommend Distribution", 
                           color_discrete_sequence=['#ff6b6b', '#51cf66'])
                st.plotly_chart(fig, use_container_width=True)
        
        # Customer satisfaction by carrier
        if 'Carrier' in main_df.columns and 'Customer_Rating' in main_df.columns:
            carrier_satisfaction = main_df.groupby('Carrier').agg({
                'Customer_Rating': 'mean',
                'Order_ID': 'count'
            }).round(2)
            carrier_satisfaction.columns = ['Avg_Rating', 'Order_Count']
            
            fig = px.scatter(carrier_satisfaction, x='Order_Count', y='Avg_Rating', 
                           hover_name=carrier_satisfaction.index,
                           title="Carrier Performance: Rating vs Volume",
                           size='Order_Count', color='Avg_Rating', 
                           color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, use_container_width=True)
        
        # Issue categories analysis
        if 'Issue_Category' in main_df.columns:
            issue_counts = main_df['Issue_Category'].value_counts()
            fig = px.bar(x=issue_counts.values, y=issue_counts.index, orientation='h',
                        title="Common Issue Categories", color=issue_counts.values,
                        color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 7: Insights & Recommendations
    with tab7:
        st.header("🔍 Key Insights & Recommendations")
        
        # Calculate key insights
        insights = []
        
        if not main_df.empty:
            # Delivery performance insights
            on_time_rate = (main_df['On_Time'].sum() / len(main_df)) * 100 if 'On_Time' in main_df.columns else 0
            if on_time_rate < 75:
                insights.append({
                    'type': 'warning',
                    'title': 'Delivery Performance Issue',
                    'description': f'On-time delivery rate is only {on_time_rate:.1f}%, below industry standard of 75%.',
                    'recommendation': 'Focus on route optimization and carrier performance improvement.'
                })
            
            # Cost insights
            if 'Total_Cost' in main_df.columns:
                high_cost_orders = main_df[main_df['Total_Cost'] > main_df['Total_Cost'].quantile(0.9)]
                if not high_cost_orders.empty:
                    insights.append({
                        'type': 'info',
                        'title': 'Cost Optimization Opportunity',
                        'description': f'{len(high_cost_orders)} orders (top 10%) have significantly higher costs.',
                        'recommendation': 'Analyze these high-cost orders for potential savings in fuel, labor, or maintenance.'
                    })
            
            # Customer satisfaction insights
            if 'Customer_Rating' in main_df.columns:
                low_rated_orders = main_df[main_df['Customer_Rating'] <= 2]
                if not low_rated_orders.empty:
                    insights.append({
                        'type': 'warning',
                        'title': 'Customer Satisfaction Risk',
                        'description': f'{len(low_rated_orders)} orders received ratings of 2 or below.',
                        'recommendation': 'Investigate common factors in low-rated deliveries and implement quality improvements.'
                    })
        
        # Display insights
        for insight in insights:
            if insight['type'] == 'warning':
                st.error(f"⚠️ **{insight['title']}**: {insight['description']}")
            else:
                st.info(f"💡 **{insight['title']}**: {insight['description']}")
            st.write(f"**Recommendation**: {insight['recommendation']}")
            st.write("---")
        
        # Fleet analysis if available
        if fleet_df is not None and not fleet_df.empty:
            st.subheader("Fleet Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Vehicle age vs efficiency
                if 'Age_Years' in fleet_df.columns and 'Fuel_Efficiency_KM_per_L' in fleet_df.columns:
                    fig = px.scatter(fleet_df, x='Age_Years', y='Fuel_Efficiency_KM_per_L', 
                                   color='Vehicle_Type',
                                   title="Vehicle Age vs Fuel Efficiency")
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # CO2 emissions by vehicle type
                if 'Vehicle_Type' in fleet_df.columns and 'CO2_Emissions_Kg_per_KM' in fleet_df.columns:
                    emissions_by_type = fleet_df.groupby('Vehicle_Type')['CO2_Emissions_Kg_per_KM'].mean()
                    fig = px.bar(x=emissions_by_type.index, y=emissions_by_type.values,
                               title="Average CO2 Emissions by Vehicle Type",
                               color=emissions_by_type.values,
                               color_continuous_scale='Reds')
                    st.plotly_chart(fig, use_container_width=True)
        
        # Summary recommendations
        st.subheader("🎯 Strategic Recommendations")
        
        recommendations = [
            "**Carrier Performance**: Implement performance-based contracts with carriers to improve on-time delivery rates.",
            "**Cost Optimization**: Analyze top 10% high-cost orders to identify cost reduction opportunities.",
            "**Route Optimization**: Use AI-powered routing to minimize distance and delivery times.",
            "**Inventory Management**: Implement automated reorder systems for low-stock warehouses.",
            "**Customer Experience**: Develop a quality assurance program focusing on delivery excellence.",
            "**Sustainability**: Replace older, less efficient vehicles to reduce CO2 emissions and fuel costs."
        ]
        
        for i, rec in enumerate(recommendations, 1):
            st.write(f"{i}. {rec}")

if __name__ == "__main__":
    main()
