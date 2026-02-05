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
    page_title="Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #2196F3;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #4CAF50;
        padding-bottom: 10px;
    }
    .metric-card {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
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
        border-left: 5px solid #4CAF50;
        margin: 10px 0;
    }
    .player-card {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">⚽ Football Analytics Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/919/919481.png", width=100)
    st.title("Navigation")
    
    analysis_type = st.radio(
        "Select Analysis Type:",
        ["Player Analytics", "Team Analytics", "Match Analytics", "Advanced Stats"]
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
        ["GK", "DEF", "MID", "FWD"],
        default=["GK", "DEF", "MID", "FWD"]
    )
    
    min_age, max_age = st.slider(
        "Age Range:",
        min_value=16, max_value=40, value=(18, 35)
    )
    
    min_matches = st.slider(
        "Minimum Matches Played:",
        min_value=0, max_value=50, value=5
    )
    
    st.divider()
    st.info("Explore football statistics and player performance metrics")

# Load Data Function
@st.cache_data
def load_football_data(uploaded_file=None):
    """Load football data from uploaded file or generate sample data"""
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
    
    # Generate sample football data
    np.random.seed(42)
    n_players = 400
    
    teams = ['Real Madrid', 'Barcelona', 'Manchester United', 'Liverpool', 
             'Bayern Munich', 'PSG', 'Juventus', 'Chelsea', 'AC Milan', 'Arsenal']
    
    positions = ['GK', 'DEF', 'MID', 'FWD']
    position_probs = [0.1, 0.35, 0.35, 0.2]
    
    data = pd.DataFrame({
        'Player_ID': range(1, n_players + 1),
        'Player': [f'Player_{i}' for i in range(1, n_players + 1)],
        'Team': np.random.choice(teams, n_players),
        'Nationality': np.random.choice(['Spain', 'England', 'Germany', 'France', 
                                       'Italy', 'Brazil', 'Argentina', 'Portugal'], n_players),
        'Position': np.random.choice(positions, n_players, p=position_probs),
        'Age': np.random.randint(18, 36, n_players),
        'Height_cm': np.random.normal(180, 8, n_players).astype(int),
        'Weight_kg': np.random.normal(75, 10, n_players).astype(int),
        'Matches_Played': np.random.randint(10, 50, n_players),
        'Minutes_Played': np.random.randint(500, 4500, n_players),
        'Goals': np.random.randint(0, 40, n_players),
        'Assists': np.random.randint(0, 30, n_players),
        'Yellow_Cards': np.random.randint(0, 15, n_players),
        'Red_Cards': np.random.randint(0, 3, n_players),
        'Pass_Accuracy': np.random.uniform(70, 95, n_players).round(1),
        'Tackle_Success': np.random.uniform(50, 90, n_players).round(1),
        'Shots_Per_Game': np.random.uniform(0.5, 4.0, n_players).round(1),
        'Key_Passes_Per_Game': np.random.uniform(0.5, 3.0, n_players).round(1),
        'Dribbles_Per_Game': np.random.uniform(0.5, 3.5, n_players).round(1),
        'Interceptions_Per_Game': np.random.uniform(0.5, 3.0, n_players).round(1),
        'Clearances_Per_Game': np.random.uniform(0.5, 4.0, n_players).round(1),
        'Clean_Sheets': np.random.randint(0, 25, n_players),
        'Saves_Per_Game': np.random.uniform(1.0, 5.0, n_players).round(1),
        'Rating': np.random.uniform(6.0, 9.0, n_players).round(1),
        'Market_Value_Millions': np.random.uniform(1, 150, n_players).round(2),
        'Weekly_Wage_K': np.random.uniform(10, 500, n_players).round(2)
    })
    
    # Adjust stats based on position
    for idx, row in data.iterrows():
        if row['Position'] == 'GK':
            data.at[idx, 'Goals'] = 0
            data.at[idx, 'Assists'] = np.random.randint(0, 3)
            data.at[idx, 'Pass_Accuracy'] = np.random.uniform(60, 85)
        elif row['Position'] == 'DEF':
            data.at[idx, 'Goals'] = np.random.randint(0, 10)
            data.at[idx, 'Assists'] = np.random.randint(0, 10)
        elif row['Position'] == 'MID':
            data.at[idx, 'Goals'] = np.random.randint(0, 20)
            data.at[idx, 'Assists'] = np.random.randint(0, 20)
        elif row['Position'] == 'FWD':
            data.at[idx, 'Goals'] = np.random.randint(5, 40)
            data.at[idx, 'Assists'] = np.random.randint(0, 15)
    
    return data

# Load data
df = load_football_data(uploaded_file)

if df is not None and not df.empty:
    # Apply filters
    df_filtered = df.copy()
    
    if 'Position' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['Position'].isin(position_filter)]
    
    if 'Age' in df_filtered.columns:
        df_filtered = df_filtered[(df_filtered['Age'] >= min_age) & (df_filtered['Age'] <= max_age)]
    
    if 'Matches_Played' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['Matches_Played'] >= min_matches]
    
    # Main Dashboard Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Players", len(df_filtered))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        avg_goals = df_filtered['Goals'].mean() if 'Goals' in df_filtered.columns else 0
        st.metric("Avg Goals", f"{avg_goals:.1f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        avg_assists = df_filtered['Assists'].mean() if 'Assists' in df_filtered.columns else 0
        st.metric("Avg Assists", f"{avg_assists:.1f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        avg_rating = df_filtered['Rating'].mean() if 'Rating' in df_filtered.columns else 0
        st.metric("Avg Rating", f"{avg_rating:.1f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main Analysis Tabs
    if analysis_type == "Player Analytics":
        st.markdown('<h2 class="sub-header">👤 Player Performance Analysis</h2>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Distributions", "⭐ Top Performers", "🔍 Player Comparison"])
        
        with tab1:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Player Statistics")
                display_cols = ['Player', 'Team', 'Position', 'Age', 'Goals', 
                              'Assists', 'Rating', 'Market_Value_Millions']
                display_cols = [col for col in display_cols if col in df_filtered.columns]
                
                if display_cols:
                    st.dataframe(df_filtered[display_cols].head(15), use_container_width=True)
            
            with col2:
                st.subheader("Quick Stats")
                
                # Position distribution
                if 'Position' in df_filtered.columns:
                    pos_counts = df_filtered['Position'].value_counts()
                    fig = px.pie(values=pos_counts.values, names=pos_counts.index,
                               title='Player Positions', hole=0.3,
                               color_discrete_sequence=px.colors.sequential.Greens)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Top scorers preview
                if 'Goals' in df_filtered.columns:
                    top_scorers = df_filtered.nlargest(3, 'Goals')[['Player', 'Team', 'Goals']]
                    st.write("**Top Scorers:**")
                    for _, row in top_scorers.iterrows():
                        st.markdown(f'<div class="player-card">{row["Player"]} ({row["Team"]}) - {row["Goals"]} goals</div>', 
                                  unsafe_allow_html=True)
        
        with tab2:
            st.subheader("Statistical Distributions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Goals distribution
                if 'Goals' in df_filtered.columns:
                    fig = px.histogram(df_filtered, x='Goals', nbins=30,
                                     title='Goals Distribution',
                                     color_discrete_sequence=['#4CAF50'])
                    st.plotly_chart(fig, use_container_width=True)
                
                # Age vs Goals
                if all(col in df_filtered.columns for col in ['Age', 'Goals']):
                    fig = px.scatter(df_filtered, x='Age', y='Goals',
                                   color='Position', size='Market_Value_Millions',
                                   title='Age vs Goals',
                                   hover_data=['Player', 'Team', 'Assists'])
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Market value distribution
                if 'Market_Value_Millions' in df_filtered.columns:
                    fig = px.box(df_filtered, x='Position', y='Market_Value_Millions',
                               title='Market Value by Position (€ Millions)',
                               color='Position')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Pass accuracy vs Rating
                if all(col in df_filtered.columns for col in ['Pass_Accuracy', 'Rating']):
                    fig = px.scatter(df_filtered, x='Pass_Accuracy', y='Rating',
                                   color='Position', size='Goals',
                                   title='Pass Accuracy vs Player Rating',
                                   hover_data=['Player', 'Team', 'Assists'])
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Top Performers Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                metric = st.selectbox(
                    "Select Performance Metric:",
                    ['Goals', 'Assists', 'Rating', 'Market_Value_Millions',
                     'Pass_Accuracy', 'Tackle_Success']
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
                           hover_data=['Position', 'Age'],
                           color_discrete_sequence=px.colors.sequential.Greens)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show key stats for top players
                if metric == 'Goals':
                    st.subheader("Goal-Scoring Insights")
                    avg_goals_top = top_players[metric].mean()
                    total_goals_top = top_players[metric].sum()
                    st.write(f"• Average goals among top {top_n}: {avg_goals_top:.1f}")
                    st.write(f"• Total goals among top {top_n}: {total_goals_top}")
        
        with tab4:
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
                metric_options = ['Goals', 'Assists', 'Rating', 'Market_Value_Millions',
                                'Pass_Accuracy', 'Tackle_Success', 'Age']
                selected_metrics = st.multiselect(
                    "Select metrics to compare:",
                    metric_options,
                    default=metric_options[:4]
                )
            
            if selected_players and selected_metrics:
                # Filter data for selected players
                comparison_data = df_filtered[df_filtered['Player'].isin(selected_players)]
                
                # Create radar chart for comparison
                categories = selected_metrics
                
                fig = go.Figure()
                
                for _, player in comparison_data.iterrows():
                    values = [player[metric] for metric in selected_metrics]
                    
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        name=player['Player']
                    ))
                
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True)),
                    showlegend=True,
                    title="Player Comparison Radar Chart",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Team Analytics":
        st.markdown('<h2 class="sub-header">🏆 Team Performance Analysis</h2>', unsafe_allow_html=True)
        
        if 'Team' in df_filtered.columns:
            # Team statistics
            team_stats = df_filtered.groupby('Team').agg({
                'Goals': 'sum',
                'Assists': 'sum',
                'Rating': 'mean',
                'Market_Value_Millions': 'sum',
                'Pass_Accuracy': 'mean',
                'Tackle_Success': 'mean'
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
                    "Select teams for comparison:",
                    teams,
                    default=teams[:3] if len(teams) >= 3 else teams
                )
                
                if selected_teams:
                    # Filter data
                    team_comparison = team_stats[team_stats['Team'].isin(selected_teams)]
                    
                    # Create bar chart comparison
                    metrics_to_show = ['Goals', 'Assists', 'Market_Value_Millions']
                    fig = make_subplots(rows=1, cols=len(metrics_to_show),
                                      subplot_titles=metrics_to_show)
                    
                    for idx, metric in enumerate(metrics_to_show, 1):
                        fig.add_trace(
                            go.Bar(
                                x=team_comparison['Team'],
                                y=team_comparison[metric],
                                name=metric
                            ),
                            row=1, col=idx
                        )
                    
                    fig.update_layout(
                        height=400,
                        showlegend=False,
                        title_text="Team Comparison"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            # Team goal distribution
            st.subheader("Team Goal Distribution")
            
            if 'Goals' in df_filtered.columns:
                fig = px.box(df_filtered, x='Team', y='Goals',
                           title='Goals Distribution by Team',
                           color='Team',
                           color_discrete_sequence=px.colors.sequential.Greens)
                st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Advanced Stats":
        st.markdown('<h2 class="sub-header">📊 Advanced Football Analytics</h2>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Correlation Analysis", "Player Clustering", "Position Analysis"])
        
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
                              color_continuous_scale='Greens',
                              text_auto='.2f',
                              aspect="auto")
                st.plotly_chart(fig, use_container_width=True)
                
                # Show strongest correlations
                st.subheader("Strongest Correlations")
                corr_pairs = corr_matrix.unstack().sort_values(ascending=False)
                
                # Positive correlations
                positive_corr = corr_pairs[corr_pairs < 1].head(5)
                st.write("**Top Positive Correlations:**")
                for idx, value in positive_corr.items():
                    col1, col2 = idx
                    st.write(f"• {col1} ↔ {col2}: {value:.3f}")
                
                # Negative correlations
                negative_corr = corr_pairs[corr_pairs < 0].tail(5)
                if len(negative_corr) > 0:
                    st.write("**Top Negative Correlations:**")
                    for idx, value in negative_corr.items():
                        col1, col2 = idx
                        st.write(f"• {col1} ↔ {col2}: {value:.3f}")
        
        with tab2:
            st.subheader("Player Clustering by Performance")
            
            # Select features for clustering
            feature_options = ['Goals', 'Assists', 'Rating', 'Pass_Accuracy',
                             'Tackle_Success', 'Age', 'Market_Value_Millions']
            
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
                                      title=f'Player Clusters (K-means, k={n_clusters})',
                                      color_continuous_scale='Greens')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # 2D scatter plot
                    fig = px.scatter(df_filtered, x=selected_features[0], 
                                   y=selected_features[1],
                                   color='Cluster', hover_data=['Player', 'Team', 'Position'],
                                   title=f'Player Clusters (K-means, k={n_clusters})',
                                   color_continuous_scale='Greens')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Cluster analysis
                st.subheader("Cluster Analysis")
                
                for cluster_num in range(n_clusters):
                    cluster_data = df_filtered[df_filtered['Cluster'] == cluster_num]
                    
                    with st.expander(f"Cluster {cluster_num} - {len(cluster_data)} players"):
                        st.write(f"**Position Distribution:**")
                        pos_dist = cluster_data['Position'].value_counts()
                        st.bar_chart(pos_dist)
                        
                        st.write(f"**Average Stats:**")
                        avg_stats = cluster_data[selected_features].mean().round(2)
                        st.write(avg_stats)
        
        with tab3:
            st.subheader("Position-Specific Analysis")
            
            if 'Position' in df_filtered.columns:
                position = st.selectbox(
                    "Select position to analyze:",
                    ['GK', 'DEF', 'MID', 'FWD']
                )
                
                position_data = df_filtered[df_filtered['Position'] == position]
                
                if len(position_data) > 0:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Key metrics for position
                        st.write(f"**Key Metrics for {position}s:**")
                        
                        if position == 'GK':
                            metrics = ['Clean_Sheets', 'Saves_Per_Game', 'Pass_Accuracy', 'Rating']
                        elif position == 'DEF':
                            metrics = ['Tackle_Success', 'Clearances_Per_Game', 'Interceptions_Per_Game', 'Goals']
                        elif position == 'MID':
                            metrics = ['Assists', 'Pass_Accuracy', 'Key_Passes_Per_Game', 'Goals']
                        else:  # FWD
                            metrics = ['Goals', 'Assists', 'Shots_Per_Game', 'Rating']
                        
                        for metric in metrics:
                            if metric in position_data.columns:
                                avg_val = position_data[metric].mean()
                                max_val = position_data[metric].max()
                                max_player = position_data.loc[position_data[metric].idxmax(), 'Player']
                                st.write(f"• **{metric.replace('_', ' ')}**: Avg: {avg_val:.1f} | Best: {max_player} ({max_val})")
                    
                    with col2:
                        # Distribution of key metric
                        if position == 'FWD' and 'Goals' in position_data.columns:
                            fig = px.histogram(position_data, x='Goals', nbins=20,
                                             title=f'Goals Distribution for {position}s',
                                             color_discrete_sequence=['#4CAF50'])
                            st.plotly_chart(fig, use_container_width=True)
                        elif position == 'MID' and 'Assists' in position_data.columns:
                            fig = px.histogram(position_data, x='Assists', nbins=20,
                                             title=f'Assists Distribution for {position}s',
                                             color_discrete_sequence=['#2196F3'])
                            st.plotly_chart(fig, use_container_width=True)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>⚽ Football Analytics Dashboard | Created with Streamlit</p>
    <p>Use sample data or upload your own football statistics</p>
</div>
""", unsafe_allow_html=True)