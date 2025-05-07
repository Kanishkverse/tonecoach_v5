import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def create_pitch_chart(pitch, timestamps):
    """
    Create a plot of pitch over time
    
    Args:
        pitch: List of pitch values
        timestamps: List of timestamps
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Filter out empty values
    if len(pitch) == 0:
        return fig
    
    # Add pitch line
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=pitch,
        mode='lines',
        name='Pitch (Hz)',
        line=dict(color='#4F46E5', width=2)
    ))
    
    # Add a horizontal line for average pitch
    avg_pitch = np.mean(pitch)
    fig.add_trace(go.Scatter(
        x=[min(timestamps), max(timestamps)],
        y=[avg_pitch, avg_pitch],
        mode='lines',
        name='Average Pitch',
        line=dict(color='rgba(255, 99, 132, 0.5)', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title='Pitch Variation Over Time',
        xaxis_title='Time (seconds)',
        yaxis_title='Frequency (Hz)',
        yaxis=dict(range=[80, 500]),
        height=400,
        template='plotly_white'
    )
    
    return fig

def create_energy_chart(energy, timestamps):
    """
    Create a plot of energy over time
    
    Args:
        energy: List of energy values
        timestamps: List of timestamps
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Filter out empty values
    if len(energy) == 0:
        return fig
    
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=energy,
        mode='lines',
        name='Energy',
        line=dict(color='#10B981', width=2),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.2)'
    ))
    
    fig.update_layout(
        title='Energy Variation Over Time',
        xaxis_title='Time (seconds)',
        yaxis_title='Energy (RMS)',
        yaxis=dict(range=[0, max(energy) * 1.2]),
        height=400,
        template='plotly_white'
    )
    
    return fig

def create_emotion_chart(emotions):
    """
    Create a bar chart of emotion scores
    
    Args:
        emotions: Dictionary of emotion scores
        
    Returns:
        Plotly figure object
    """
    # Convert to dataframe for plotting
    if isinstance(emotions, dict):
        emotions_df = pd.DataFrame({
            'Emotion': list(emotions.keys()),
            'Score': list(emotions.values())
        })
    else:
        return go.Figure()  # Return empty figure
    
    # Define colors for emotions
    colors = {
        'neutral': '#4F46E5',
        'joy': '#10B981',
        'sadness': '#F59E0B',
        'anger': '#EF4444',
        'fear': '#8B5CF6',
        'disgust': '#EC4899',
        'surprise': '#3B82F6'
    }
    
    fig = px.bar(
        emotions_df, 
        x='Emotion', 
        y='Score',
        color='Emotion',
        color_discrete_map=colors
    )
    
    fig.update_layout(
        title='Emotion Detection Results',
        xaxis_title='Emotion',
        yaxis_title='Confidence Score',
        yaxis=dict(range=[0, 1.0]),
        height=400,
        template='plotly_white',
        showlegend=False
    )
    
    return fig

def create_progress_chart(progress_data):
    """
    Create a line chart of progress over time
    
    Args:
        progress_data: Dictionary containing progress metrics
        
    Returns:
        Plotly figure object
    """
    if not progress_data or 'dates' not in progress_data or not progress_data['dates']:
        return None
    
    # Convert data to DataFrame for easier plotting
    df = pd.DataFrame({
        'Date': progress_data['dates'],
        'Expressiveness': progress_data['expressiveness_scores'],
        'Pitch Variability': progress_data['pitch_variability'],
        'Energy Variability': [e * 100 for e in progress_data['energy_variability']],  # Scale for visibility
    })
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Expressiveness'],
        mode='lines+markers',
        name='Expressiveness',
        line=dict(color='#4F46E5', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Pitch Variability'],
        mode='lines+markers',
        name='Pitch Variability',
        line=dict(color='#10B981', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Energy Variability'],
        mode='lines+markers',
        name='Energy Variability',
        line=dict(color='#F59E0B', width=2)
    ))
    
    fig.update_layout(
        title='Progress Over Time',
        xaxis_title='Date',
        height=500,
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig