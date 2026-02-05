import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go

def calculate_basketball_efficiency(df):
    """Calculate player efficiency rating"""
    df = df.copy()
    if all(col in df.columns for col in ['points_per_game', 'rebounds_per_game', 'assists_per_game']):
        df['efficiency'] = (df['points_per_game'] + df['rebounds_per_game'] + 
                           df['assists_per_game']) / 3
    return df

def calculate_football_performance_score(df):
    """Calculate football performance score"""
    df = df.copy()
    if all(col in df.columns for col in ['goals', 'assists', 'rating']):
        df['performance_score'] = (df['goals'] * 0.4 + 
                                  df['assists'] * 0.3 + 
                                  df['rating'] * 2.5)
    return df

def detect_outliers_iqr(df, column):
    """Detect outliers using IQR method"""
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    return outliers

def create_correlation_matrix(df):
    """Create correlation matrix for numerical columns"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    return df[numeric_cols].corr()