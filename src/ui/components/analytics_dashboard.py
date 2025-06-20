"""
Analytics Dashboard Component for email campaign performance tracking.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    px = None
    go = None
    make_subplots = None

from src.services.analytics_service import AnalyticsService
from src.utils.session_state import initialize_session_state
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AnalyticsDashboard:
    def __init__(self):
        self.analytics_service = AnalyticsService()
    
    def render(self):
        """Render the analytics dashboard."""
        st.header("📊 Analytics Dashboard")
        
        # Check plotly availability and show warning if not available
        if not PLOTLY_AVAILABLE:
            st.warning("📈 For advanced interactive charts, install plotly: `pip install plotly`")
            st.info("Currently showing basic charts only")
        
        # Date range selector
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now().date() - timedelta(days=30),
                key="analytics_start_date"
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now().date(),
                key="analytics_end_date"
            )
        with col3:
            if st.button("Refresh Data", type="primary"):
                st.cache_data.clear()
                st.experimental_rerun()
        
        # Get analytics data
        user_id = st.session_state.user_id
        analytics_data = self.analytics_service.get_dashboard_metrics(
            user_id, start_date, end_date
        )
        
        # Main metrics overview
        self._render_metrics_overview(analytics_data)
        
        # Tabs for different analytics views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Performance", "📧 Campaigns", "👥 Audience", "🎯 A/B Tests", "📊 Reports"
        ])
        
        with tab1:
            self._render_performance_analytics(analytics_data, start_date, end_date)
        
        with tab2:
            self._render_campaign_analytics(analytics_data, start_date, end_date)
        
        with tab3:
            self._render_audience_analytics(analytics_data, start_date, end_date)
        
        with tab4:
            self._render_ab_test_analytics(analytics_data, start_date, end_date)
        
        with tab5:
            self._render_reports_section(analytics_data, start_date, end_date)
    
    def _render_metrics_overview(self, data: Dict):
        """Render key metrics overview cards."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Sent",
                f"{data.get('total_sent', 0):,}",
                delta=data.get('sent_change', 0),
                delta_color="normal"
            )
        
        with col2:
            open_rate = data.get('avg_open_rate', 0)
            st.metric(
                "Avg Open Rate",
                f"{open_rate:.1f}%",
                delta=f"{data.get('open_rate_change', 0):.1f}%",
                delta_color="normal"
            )
        
        with col3:
            click_rate = data.get('avg_click_rate', 0)
            st.metric(
                "Avg Click Rate",
                f"{click_rate:.1f}%",
                delta=f"{data.get('click_rate_change', 0):.1f}%",
                delta_color="normal"
            )
        
        with col4:
            conversion_rate = data.get('avg_conversion_rate', 0)
            st.metric(
                "Conversion Rate",
                f"{conversion_rate:.1f}%",
                delta=f"{data.get('conversion_change', 0):.1f}%",
                delta_color="normal"
            )
        
        # Additional metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Campaigns",
                data.get('total_campaigns', 0),
                delta=data.get('campaigns_change', 0)
            )
        
        with col2:
            st.metric(
                "Active Campaigns",
                data.get('active_campaigns', 0)
            )
        
        with col3:
            st.metric(
                "Total Contacts",
                f"{data.get('total_contacts', 0):,}",
                delta=data.get('contacts_change', 0)
            )
        
        with col4:
            bounce_rate = data.get('avg_bounce_rate', 0)
            st.metric(                "Bounce Rate",
                f"{bounce_rate:.1f}%",
                delta=f"{data.get('bounce_rate_change', 0):.1f}%",
                delta_color="inverse"
            )
    
    def _render_performance_analytics(self, data: Dict, start_date, end_date):
        """Render performance analytics charts."""
        st.subheader("📈 Performance Trends")
          # Get time series data
        time_series_data = self.analytics_service.get_time_series_data(
            st.session_state.user_id, start_date, end_date
        )
        
        if time_series_data:
            df = pd.DataFrame(time_series_data)
            
            if PLOTLY_AVAILABLE and make_subplots and go:
                # Performance trends chart
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=('Email Volume', 'Open Rate', 'Click Rate', 'Bounce Rate'),
                    specs=[[{"secondary_y": False}, {"secondary_y": False}],
                           [{"secondary_y": False}, {"secondary_y": False}]]
                )
                
                # Email volume
                fig.add_trace(
                    go.Scatter(x=df['date'], y=df['emails_sent'], name='Emails Sent', line=dict(color='blue')),
                    row=1, col=1
                )
            
            # Open rate
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['open_rate'], name='Open Rate', line=dict(color='green')),
                row=1, col=2
            )
            
            # Click rate
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['click_rate'], name='Click Rate', line=dict(color='orange')),
                row=2, col=1
            )
            
            # Bounce rate
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['bounce_rate'], name='Bounce Rate', line=dict(color='red')),
                row=2, col=2
            )
            
            fig.update_layout(height=600, showlegend=False, title_text="Performance Trends Over Time")
            st.plotly_chart(fig, use_container_width=True)
          # Performance by hour/day analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Best Sending Times")
            time_performance = self.analytics_service.get_time_performance(st.session_state.user_id)
            if time_performance:
                df_time = pd.DataFrame(time_performance)
                if PLOTLY_AVAILABLE and px:
                    fig = px.bar(
                        df_time, x='hour', y='open_rate',
                        title='Open Rate by Hour of Day',
                        labels={'hour': 'Hour', 'open_rate': 'Open Rate (%)'}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.bar_chart(df_time.set_index('hour')['open_rate'])
            else:
                st.info("No time performance data available")
        
        with col2:
            st.subheader("Performance by Day")
            day_performance = self.analytics_service.get_day_performance(st.session_state.user_id)
            if day_performance:
                df_day = pd.DataFrame(day_performance)
                if PLOTLY_AVAILABLE:
                    fig = px.bar(
                        df_day, x='day_of_week', y='click_rate',
                        title='Click Rate by Day of Week',
                        labels={'day_of_week': 'Day', 'click_rate': 'Click Rate (%)'}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Fallback to streamlit bar chart
                    st.bar_chart(df_day.set_index('day_of_week')['click_rate'])
    
    def _render_campaign_analytics(self, data: Dict, start_date, end_date):
        """Render campaign-specific analytics."""
        st.subheader("📧 Campaign Performance")
        
        # Get campaign performance data
        campaign_data = self.analytics_service.get_campaign_performance(
            st.session_state.user_id, start_date, end_date
        )
        
        if campaign_data:
            df = pd.DataFrame(campaign_data)
            
            # Campaign performance table
            st.subheader("Campaign Performance Summary")
            
            # Format the dataframe for display
            display_df = df.copy()
            display_df['open_rate'] = display_df['open_rate'].apply(lambda x: f"{x:.1f}%")
            display_df['click_rate'] = display_df['click_rate'].apply(lambda x: f"{x:.1f}%")
            display_df['bounce_rate'] = display_df['bounce_rate'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(
                display_df[['campaign_name', 'sent_count', 'open_rate', 'click_rate', 'bounce_rate']],
                use_container_width=True
            )
              # Top performing campaigns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Top Campaigns by Open Rate")
                top_open = df.nlargest(5, 'open_rate')
                if PLOTLY_AVAILABLE and px:
                    fig = px.bar(
                        top_open, x='open_rate', y='campaign_name',
                        orientation='h',
                        title='Top 5 Campaigns by Open Rate',
                        labels={'open_rate': 'Open Rate (%)', 'campaign_name': 'Campaign'}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.bar_chart(top_open.set_index('campaign_name')['open_rate'])
            
            with col2:
                st.subheader("Top Campaigns by Click Rate")
                top_click = df.nlargest(5, 'click_rate')
                if PLOTLY_AVAILABLE and px:
                    fig = px.bar(
                        top_click, x='click_rate', y='campaign_name',
                        orientation='h',
                        title='Top 5 Campaigns by Click Rate',
                        labels={'click_rate': 'Click Rate (%)', 'campaign_name': 'Campaign'}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.bar_chart(top_click.set_index('campaign_name')['click_rate'])
            
            # Campaign type performance
            if 'campaign_type' in df.columns:
                st.subheader("Performance by Campaign Type")
                type_performance = df.groupby('campaign_type').agg({
                    'open_rate': 'mean',
                    'click_rate': 'mean',
                    'sent_count': 'sum'
                }).reset_index()
                
                fig = px.scatter(
                    type_performance,
                    x='open_rate', y='click_rate',
                    size='sent_count',
                    color='campaign_type',
                    title='Campaign Type Performance',
                    labels={'open_rate': 'Open Rate (%)', 'click_rate': 'Click Rate (%)'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_audience_analytics(self, data: Dict, start_date, end_date):
        """Render audience analytics."""
        st.subheader("👥 Audience Insights")
        
        # Get audience data
        audience_data = self.analytics_service.get_audience_insights(
            st.session_state.user_id, start_date, end_date
        )
        
        if audience_data:
            col1, col2 = st.columns(2)
            
            with col1:                # Engagement segments
                st.subheader("Engagement Segments")
                segments = audience_data.get('engagement_segments', {})
                
                if segments:
                    labels = list(segments.keys())
                    values = list(segments.values())
                    
                    if PLOTLY_AVAILABLE and px:
                        fig = px.pie(
                            values=values,
                            names=labels,
                            title='Audience Engagement Segments'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        # Fallback - show as metrics
                        for label, value in segments.items():
                            st.metric(label, value)
            
            with col2:
                # Geographic distribution
                st.subheader("Geographic Distribution")
                geo_data = audience_data.get('geographic_data', [])
                
                if geo_data:
                    df_geo = pd.DataFrame(geo_data)
                    fig = px.choropleth(
                        df_geo,
                        locations='country_code',
                        color='engagement_rate',
                        hover_name='country',
                        title='Engagement Rate by Country'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
              # Device and client analytics
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Email Clients")
                client_data = audience_data.get('email_clients', [])
                if client_data:
                    df_clients = pd.DataFrame(client_data)
                    if PLOTLY_AVAILABLE and px:
                        fig = px.bar(
                            df_clients, x='client', y='percentage',
                            title='Email Client Usage',
                            labels={'client': 'Email Client', 'percentage': 'Usage (%)'}
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        # Fallback - show as bar chart
                        st.bar_chart(df_clients.set_index('client')['percentage'])
            
            with col2:
                st.subheader("Device Types")
                device_data = audience_data.get('device_types', [])
                if device_data:
                    df_devices = pd.DataFrame(device_data)
                    if PLOTLY_AVAILABLE and px:
                        fig = px.pie(
                            df_devices,
                            values='percentage',
                            names='device_type',
                            title='Device Type Distribution'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        # Fallback - show as metrics
                        for _, row in df_devices.iterrows():
                            st.metric(row['device_type'], f"{row['percentage']}%")
    
    def _render_ab_test_analytics(self, data: Dict, start_date, end_date):
        """Render A/B test analytics."""
        st.subheader("🎯 A/B Test Results")
        
        # Get A/B test data
        ab_test_data = self.analytics_service.get_ab_test_results(
            st.session_state.user_id, start_date, end_date
        )
        
        if ab_test_data:
            for test in ab_test_data:
                with st.expander(f"A/B Test: {test['campaign_name']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Test Variable", test['test_variable'])
                        st.metric("Test Status", test['status'])
                        st.metric("Statistical Significance", f"{test.get('significance', 0):.2f}")
                    
                    with col2:
                        st.subheader("Version A")
                        st.metric("Sent", test['version_a_sent'])
                        st.metric("Open Rate", f"{test['version_a_open_rate']:.1f}%")
                        st.metric("Click Rate", f"{test['version_a_click_rate']:.1f}%")
                    
                    with col3:
                        st.subheader("Version B")
                        st.metric("Sent", test['version_b_sent'])
                        st.metric("Open Rate", f"{test['version_b_open_rate']:.1f}%")
                        st.metric("Click Rate", f"{test['version_b_click_rate']:.1f}%")
                    
                    # Winner declaration
                    if test.get('winner'):
                        if test['winner'] == 'A':
                            st.success(f"🏆 Version A is the winner with {test['winner_confidence']:.1f}% confidence!")
                        elif test['winner'] == 'B':
                            st.success(f"🏆 Version B is the winner with {test['winner_confidence']:.1f}% confidence!")
                        else:
                            st.info("📊 No statistically significant winner yet.")
                      # Performance comparison chart
                    if test.get('performance_data'):
                        comparison_data = pd.DataFrame(test['performance_data'])
                        if PLOTLY_AVAILABLE and px:
                            fig = px.bar(
                                comparison_data,
                                x='metric',
                                y=['version_a', 'version_b'],
                                title=f'A/B Test Performance Comparison: {test["campaign_name"]}',
                                barmode='group'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            # Fallback - show as simple bar chart
                            st.bar_chart(comparison_data.set_index('metric')[['version_a', 'version_b']])
        else:
            st.info("No A/B tests found for the selected date range.")
    
    def _render_reports_section(self, data: Dict, start_date, end_date):
        """Render reports and export section."""
        st.subheader("📊 Reports & Export")
        
        # Report type selection
        report_type = st.selectbox(
            "Select Report Type",
            ["Campaign Performance", "Audience Insights", "A/B Test Results", "Custom Report"]
        )
        
        # Report configuration
        col1, col2 = st.columns(2)
        with col1:
            report_format = st.selectbox("Format", ["PDF", "CSV", "Excel"])
        with col2:
            include_charts = st.checkbox("Include Charts", value=True)
        
        # Generate report button
        if st.button("Generate Report", type="primary"):
            self._generate_report(report_type, report_format, include_charts, start_date, end_date)
        
        # Scheduled reports
        st.subheader("Scheduled Reports")
        
        with st.expander("Create Scheduled Report"):
            schedule_name = st.text_input("Report Name")
            schedule_type = st.selectbox("Report Type", ["Weekly", "Monthly", "Quarterly"])
            schedule_recipients = st.text_input("Email Recipients (comma-separated)")
            
            if st.button("Schedule Report"):
                self._schedule_report(schedule_name, schedule_type, schedule_recipients)
        
        # Data export
        st.subheader("Data Export")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export Campaign Data"):
                self._export_campaign_data(start_date, end_date)
        
        with col2:
            if st.button("Export Contact Data"):
                self._export_contact_data()
        
        # Real-time monitoring
        st.subheader("Real-time Monitoring")
        
        if st.button("View Live Campaign Status"):
            self._show_live_status()
    
    def _generate_report(self, report_type: str, format_type: str, include_charts: bool, start_date, end_date):
        """Generate and download a report."""
        try:
            report_data = self.analytics_service.generate_report(
                st.session_state.user_id,
                report_type,
                start_date,
                end_date,
                format_type,
                include_charts
            )
            
            if report_data:
                st.success("Report generated successfully!")
                
                # Provide download link
                if format_type == "PDF":
                    st.download_button(
                        "Download PDF Report",
                        data=report_data,
                        file_name=f"{report_type.lower().replace(' ', '_')}_report.pdf",
                        mime="application/pdf"
                    )
                elif format_type == "CSV":
                    st.download_button(
                        "Download CSV Report",
                        data=report_data,
                        file_name=f"{report_type.lower().replace(' ', '_')}_report.csv",
                        mime="text/csv"
                    )
                elif format_type == "Excel":
                    st.download_button(
                        "Download Excel Report",
                        data=report_data,
                        file_name=f"{report_type.lower().replace(' ', '_')}_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.error("Failed to generate report.")
        
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")
            logger.error(f"Report generation failed: {str(e)}")
    
    def _schedule_report(self, name: str, report_type: str, recipients: str):
        """Schedule a recurring report."""
        try:
            schedule_data = {
                "name": name,
                "type": report_type,
                "recipients": [email.strip() for email in recipients.split(",")],
                "user_id": st.session_state.user_id
            }
            
            self.analytics_service.schedule_report(schedule_data)
            st.success(f"Report '{name}' scheduled successfully!")
            
        except Exception as e:
            st.error(f"Failed to schedule report: {str(e)}")
            logger.error(f"Report scheduling failed: {str(e)}")
    
    def _export_campaign_data(self, start_date, end_date):
        """Export campaign data."""
        try:
            data = self.analytics_service.export_campaign_data(
                st.session_state.user_id, start_date, end_date
            )
            
            if data:
                df = pd.DataFrame(data)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    "Download Campaign Data",
                    data=csv,
                    file_name=f"campaign_data_{start_date}_{end_date}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No campaign data to export.")
                
        except Exception as e:
            st.error(f"Export failed: {str(e)}")
            logger.error(f"Campaign data export failed: {str(e)}")
    
    def _export_contact_data(self):
        """Export contact data."""
        try:
            data = self.analytics_service.export_contact_data(st.session_state.user_id)
            
            if data:
                df = pd.DataFrame(data)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    "Download Contact Data",
                    data=csv,
                    file_name="contact_data.csv",
                    mime="text/csv"
                )
            else:
                st.info("No contact data to export.")
                
        except Exception as e:
            st.error(f"Export failed: {str(e)}")
            logger.error(f"Contact data export failed: {str(e)}")
    
    def _show_live_status(self):
        """Show live campaign status."""
        try:
            live_data = self.analytics_service.get_live_campaign_status(st.session_state.user_id)
            
            if live_data:
                st.subheader("Live Campaign Status")
                
                for campaign in live_data:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Campaign", campaign['name'])
                    with col2:
                        st.metric("Status", campaign['status'])
                    with col3:
                        st.metric("Sent", campaign['sent_count'])
                    with col4:
                        st.metric("Opens", campaign['open_count'])
            else:
                st.info("No active campaigns found.")
                
        except Exception as e:
            st.error(f"Failed to load live status: {str(e)}")
            logger.error(f"Live status loading failed: {str(e)}")
