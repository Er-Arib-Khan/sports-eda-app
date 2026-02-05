import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Page Configuration
st.set_page_config(
    page_title="Basketball Analytics Dashboard",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #1E88E5;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #FF6B35;
        padding-bottom: 10px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .team-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF6B35;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🏀 Basketball Analytics Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3082/3082383.png", width=100)
    st.title("Navigation")
    
    analysis_type = st.radio(
        "Select Analysis Type:",
        ["Player Analytics", "Team Analytics", "Game Analytics", "Advanced Stats"]
    )
    
    st.divider()
    st.subheader("Data Options")
    
    # Data source selection
    data_source = st.radio(
        "Data Source:",
        ["Sample Data", "Upload Your Data"]
    )
    
    if data_source == "Upload Your Data":
        uploaded_file = st.file_uploader("Upload CSV or Excel", type=['csv', 'xlsx'])
    else:
        uploaded_file = None
    
    st.divider()
    st.subheader("Filter Options")
    
    # Filters
    position_filter = st.multiselect(
        "Filter by Position:",
        ["PG", "SG", "SF", "PF", "C"],
        default=["PG", "SG", "SF", "PF", "C"]
    )
    
    min_age, max_age = st.slider(
        "Age Range:",
        min_value=18, max_value=45, value=(20, 35)
    )
    
    st.divider()
    st.info("Explore basketball statistics and player performance metrics")

# Load Data Function
@st.cache_data
def load_basketball_data(uploaded_file=None):
    """Load basketball data from uploaded file or generate sample data"""
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success("✅ Custom data loaded successfully!")
            return df
        except Exception as e:
            st.error(f"Error loading file: {e}")
            st.info("Loading sample data instead...")
    
    # Generate sample basketball data
    np.random.seed(42)
    n_players = 300
    
    teams = ['Lakers', 'Warriors', 'Celtics', 'Bucks', 'Nets', 'Suns', 
             'Heat', '76ers', 'Grizzlies', 'Nuggets']
    
    positions = ['PG', 'SG', 'SF', 'PF', 'C']
    position_probs = [0.2, 0.2, 0.2, 0.2, 0.2]
    
    data = pd.DataFrame({
        'Player_ID': range(1, n_players + 1),
        'Player': [f'Player_{i}' for i in range(1, n_players + 1)],
        'Team': np.random.choice(teams, n_players),
        'Position': np.random.choice(positions, n_players, p=position_probs),
        'Age': np.random.randint(19, 38, n_players),
        'Height_cm': np.random.normal(200, 10, n_players).astype(int),
        'Weight_kg': np.random.normal(100, 15, n_players).astype(int),
        'Games_Played': np.random.randint(20, 82, n_players),
        'Minutes_Per_Game': np.random.uniform(15, 40, n_players).round(1),
        'Points_Per_Game': np.random.uniform(5, 30, n_players).round(1),
        'Assists_Per_Game': np.random.uniform(1, 10, n_players).round(1),
        'Rebounds_Per_Game': np.random.uniform(2, 15, n_players).round(1),
        'Steals_Per_Game': np.random.uniform(0.5, 2.5, n_players).round(1),
        'Blocks_Per_Game': np.random.uniform(0.3, 2.0, n_players).round(1),
        'Field_Goal_Pct': np.random.uniform(40, 55, n_players).round(1),
        'Three_Point_Pct': np.random.uniform(30, 45, n_players).round(1),
        'Free_Throw_Pct': np.random.uniform(70, 90, n_players).round(1),
        'Turnovers_Per_Game': np.random.uniform(1, 4, n_players).round(1),
        'Player_Efficiency_Rating': np.random.uniform(10, 30, n_players).round(1),
        'Salary_Millions': np.random.uniform(1, 40, n_players).round(2),
        'Plus_Minus': np.random.uniform(-5, 10, n_players).round(1)
    })
    
    return data

# Load data
df = load_basketball_data(uploaded_file)

if df is not None and not df.empty:
    # Apply filters
    df_filtered = df.copy()
    if 'Position' in df.columns:
        df_filtered = df_filtered[df_filtered['Position'].isin(position_filter)]
    
    if 'Age' in df.columns:
        df_filtered = df_filtered[(df_filtered['Age'] >= min_age) & (df_filtered['Age'] <= max_age)]
    
    # Main Dashboard Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Players", len(df_filtered))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        avg_ppg = df_filtered['Points_Per_Game'].mean() if 'Points_Per_Game' in df_filtered.columns else 0
        st.metric("Avg Points/Game", f"{avg_ppg:.1f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        avg_apg = df_filtered['Assists_Per_Game'].mean() if 'Assists_Per_Game' in df_filtered.columns else 0
        st.metric("Avg Assists/Game", f"{avg_apg:.1f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        avg_rpg = df_filtered['Rebounds_Per_Game'].mean() if 'Rebounds_Per_Game' in df_filtered.columns else 0
        st.metric("Avg Rebounds/Game", f"{avg_rpg:.1f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main Analysis Tabs
    if analysis_type == "Player Analytics":
        st.markdown('<h2 class="sub-header">👤 Player Performance Analysis</h2>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Distributions", "🎯 Top Performers", "🔍 Player Comparison"])
        
        with tab1:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Player Statistics")
                display_cols = ['Player', 'Team', 'Position', 'Age', 'Points_Per_Game', 
                              'Assists_Per_Game', 'Rebounds_Per_Game', 'Player_Efficiency_Rating']
                display_cols = [col for col in display_cols if col in df_filtered.columns]
                
                if display_cols:
                    st.dataframe(df_filtered[display_cols].head(15), use_container_width=True)
            
            with col2:
                st.subheader("Quick Stats")
                
                # Position distribution
                if 'Position' in df_filtered.columns:
                    pos_counts = df_filtered['Position'].value_counts()
                    fig = px.pie(values=pos_counts.values, names=pos_counts.index,
                               title='Player Positions', hole=0.3)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Age distribution
                if 'Age' in df_filtered.columns:
                    st.write("**Age Statistics:**")
                    st.write(f"• Youngest: {df_filtered['Age'].min()} years")
                    st.write(f"• Oldest: {df_filtered['Age'].max()} years")
                    st.write(f"• Average: {df_filtered['Age'].mean():.1f} years")
        
        with tab2:
            st.subheader("Statistical Distributions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Points distribution
                if 'Points_Per_Game' in df_filtered.columns:
                    fig = px.histogram(df_filtered, x='Points_Per_Game', nbins=30,
                                     title='Points Per Game Distribution',
                                     color_discrete_sequence=['#FF6B35'])
                    st.plotly_chart(fig, use_container_width=True)
                
                # Height vs Points
                if all(col in df_filtered.columns for col in ['Height_cm', 'Points_Per_Game']):
                    fig = px.scatter(df_filtered, x='Height_cm', y='Points_Per_Game',
                                   color='Position', size='Salary_Millions',
                                   title='Height vs Points Per Game',
                                   hover_data=['Player', 'Team', 'Age'])
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Salary distribution
                if 'Salary_Millions' in df_filtered.columns:
                    fig = px.box(df_filtered, x='Position', y='Salary_Millions',
                               title='Salary Distribution by Position',
                               color='Position')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Shooting percentages
                if all(col in df_filtered.columns for col in ['Field_Goal_Pct', 'Three_Point_Pct']):
                    fig = px.scatter(df_filtered, x='Field_Goal_Pct', y='Three_Point_Pct',
                                   color='Position', size='Points_Per_Game',
                                   title='Field Goal % vs 3-Point %',
                                   hover_data=['Player', 'Team'])
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Top Performers Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                metric = st.selectbox(
                    "Select Performance Metric:",
                    ['Points_Per_Game', 'Assists_Per_Game', 'Rebounds_Per_Game',
                     'Player_Efficiency_Rating', 'Salary_Millions']
                )
            
            with col2:
                top_n = st.slider("Number of Top Players:", 5, 25, 10)
            
            # Get top players
            if metric in df_filtered.columns:
                top_players = df_filtered.nlargest(top_n, metric)[
                    ['Player', 'Team', 'Position', 'Age', metric]
                ].reset_index(drop=True)
                
                st.write(f"**Top {top_n} Players by {metric.replace('_', ' ')}:**")
                st.dataframe(top_players, use_container_width=True)
                
                # Visualization
                fig = px.bar(top_players, x='Player', y=metric,
                           color='Team', title=f'Top {top_n} Players',
                           hover_data=['Position', 'Age'])
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Player Comparison")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Select players to compare
                player_options = df_filtered['Player'].tolist() if 'Player' in df_filtered.columns else []
                selected_players = st.multiselect(
                    "Select players to compare:",
                    player_options,
                    default=player_options[:3] if len(player_options) >= 3 else player_options
                )
            
            with col2:
                # Select metrics to compare
                metric_options = ['Points_Per_Game', 'Assists_Per_Game', 'Rebounds_Per_Game',
                                'Field_Goal_Pct', 'Three_Point_Pct', 'Player_Efficiency_Rating',
                                'Salary_Millions']
                selected_metrics = st.multiselect(
                    "Select metrics to compare:",
                    metric_options,
                    default=metric_options[:4]
                )
            
            if selected_players and selected_metrics:
                # Filter data for selected players
                comparison_data = df_filtered[df_filtered['Player'].isin(selected_players)]
                
                # Create comparison chart
                fig = go.Figure()
                
                for metric in selected_metrics:
                    if metric in comparison_data.columns:
                        fig.add_trace(go.Bar(
                            name=metric.replace('_', ' '),
                            x=comparison_data['Player'],
                            y=comparison_data[metric]
                        ))
                
                fig.update_layout(
                    barmode='group',
                    title='Player Comparison',
                    xaxis_title='Players',
                    yaxis_title='Value',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Team Analytics":
        st.markdown('<h2 class="sub-header">🏆 Team Performance Analysis</h2>', unsafe_allow_html=True)
        
        if 'Team' in df_filtered.columns:
            # Team statistics
            team_stats = df_filtered.groupby('Team').agg({
                'Points_Per_Game': 'mean',
                'Assists_Per_Game': 'mean',
                'Rebounds_Per_Game': 'mean',
                'Field_Goal_Pct': 'mean',
                'Three_Point_Pct': 'mean',
                'Player_Efficiency_Rating': 'mean',
                'Salary_Millions': 'mean'
            }).round(2).reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Team Performance Metrics")
                st.dataframe(team_stats, use_container_width=True)
            
            with col2:
                st.subheader("Team Comparison")
                
                # Select teams to compare
                teams = team_stats['Team'].tolist()
                selected_teams = st.multiselect(
                    "Select teams for radar chart:",
                    teams,
                    default=teams[:3] if len(teams) >= 3 else teams
                )
                
                if selected_teams:
                    # Prepare data for radar chart
                    radar_data = team_stats[team_stats['Team'].isin(selected_teams)]
                    
                    categories = ['Points', 'Assists', 'Rebounds', 'FG%', '3P%', 'PER']
                    
                    fig = go.Figure()
                    
                    for idx, row in radar_data.iterrows():
                        values = [
                            row['Points_Per_Game'],
                            row['Assists_Per_Game'],
                            row['Rebounds_Per_Game'],
                            row['Field_Goal_Pct'],
                            row['Three_Point_Pct'],
                            row['Player_Efficiency_Rating']
                        ]
                        
                        fig.add_trace(go.Scatterpolar(
                            r=values,
                            theta=categories,
                            fill='toself',
                            name=row['Team']
                        ))
                    
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True)),
                        showlegend=True,
                        title="Team Performance Comparison",
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            # Team scoring distribution
            st.subheader("Team Scoring Distribution")
            
            if 'Points_Per_Game' in df_filtered.columns:
                fig = px.box(df_filtered, x='Team', y='Points_Per_Game',
                           title='Points Per Game Distribution by Team',
                           color='Team')
                st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Advanced Stats":
        st.markdown('<h2 class="sub-header">📊 Advanced Basketball Analytics</h2>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Correlation Analysis", "Player Clustering", "Performance Prediction"])
        
        with tab1:
            st.subheader("Feature Correlation Matrix")
            
            # Select numerical columns for correlation
            numeric_cols = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) > 1:
                # Limit to top 15 columns for readability
                if len(numeric_cols) > 15:
                    numeric_cols = numeric_cols[:15]
                
                corr_matrix = df_filtered[numeric_cols].corr()
                
                fig = px.imshow(corr_matrix,
                              title='Feature Correlation Heatmap',
                              color_continuous_scale='RdBu',
                              text_auto='.2f',
                              aspect="auto")
                st.plotly_chart(fig, use_container_width=True)
                
                # Show strongest correlations
                st.subheader("Top Correlations")
                corr_pairs = corr_matrix.unstack().sort_values(ascending=False)
                top_corr = corr_pairs[corr_pairs < 1].head(10)
                
                for idx, value in top_corr.items():
                    col1, col2 = idx
                    st.write(f"**{col1}** ↔ **{col2}**: {value:.3f}")
        
        with tab2:
            st.subheader("Player Clustering by Performance")
            
            # Select features for clustering
            feature_options = ['Points_Per_Game', 'Assists_Per_Game', 'Rebounds_Per_Game',
                             'Field_Goal_Pct', 'Three_Point_Pct', 'Age', 'Player_Efficiency_Rating']
            
            selected_features = st.multiselect(
                "Select features for clustering:",
                feature_options,
                default=feature_options[:3]
            )
            
            if len(selected_features) >= 2:
                # Prepare data
                X = df_filtered[selected_features].fillna(0)
                
                # Scale data
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                
                # Perform clustering
                n_clusters = st.slider("Number of clusters:", 2, 6, 3)
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                df_filtered['Cluster'] = kmeans.fit_predict(X_scaled)
                
                # Visualization
                if len(selected_features) >= 3:
                    # 3D scatter plot
                    fig = px.scatter_3d(df_filtered, x=selected_features[0], 
                                      y=selected_features[1], z=selected_features[2],
                                      color='Cluster', hover_data=['Player', 'Team', 'Position'],
                                      title=f'Player Clusters (K-means, k={n_clusters})')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # 2D scatter plot
                    fig = px.scatter(df_filtered, x=selected_features[0], 
                                   y=selected_features[1],
                                   color='Cluster', hover_data=['Player', 'Team', 'Position'],
                                   title=f'Player Clusters (K-means, k={n_clusters})')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Cluster statistics
                st.subheader("Cluster Statistics")
                cluster_stats = df_filtered.groupby('Cluster')[selected_features].mean().round(2)
                st.dataframe(cluster_stats, use_container_width=True)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🏀 Basketball Analytics Dashboard | Created with Streamlit</p>
    <p>Use sample data or upload your own basketball statistics</p>
</div>
""", unsafe_allow_html=True)