import plotly.graph_objects as go
import plotly.express as px
import numpy as np

def create_pitch_chart(pitch_data, timestamps):
    """
    Create a pitch over time chart
    
    Args:
        pitch_data: List of pitch values
        timestamps: List of timestamps
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=pitch_data,
        mode='lines',
        name='Pitch',
        line=dict(color='blue', width=2)
    ))
    
    fig.update_layout(
        title='Pitch Variation Over Time',
        xaxis_title='Time (seconds)',
        yaxis_title='Pitch (Hz)',
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig

def create_energy_chart(energy_data, timestamps):
    """
    Create an energy over time chart
    
    Args:
        energy_data: List of energy values
        timestamps: List of timestamps
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=energy_data,
        mode='lines',
        name='Energy',
        line=dict(color='orange', width=2),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        title='Energy Variation Over Time',
        xaxis_title='Time (seconds)',
        yaxis_title='Energy',
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig

def create_emotion_chart(emotion_data):
    """
    Create an emotion distribution chart
    
    Args:
        emotion_data: Dictionary of emotions and their probabilities
        
    Returns:
        Plotly figure object
    """
    if isinstance(emotion_data, dict):
        emotions = list(emotion_data.keys())
        probabilities = list(emotion_data.values())
    else:
        # Handle the case where emotion_data is a counter or other format
        emotions = []
        probabilities = []
        for emotion, count in emotion_data.items():
            emotions.append(emotion.capitalize())
            probabilities.append(count)
    
    # Sort by probability
    sorted_indices = np.argsort(probabilities)[::-1]
    emotions = [emotions[i] for i in sorted_indices]
    probabilities = [probabilities[i] for i in sorted_indices]
    
    colors = px.colors.qualitative.Plotly[:len(emotions)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=emotions,
        y=probabilities,
        marker_color=colors,
        text=[f"{p:.1%}" if isinstance(p, float) else p for p in probabilities],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='Emotion Distribution',
        xaxis_title='Emotion',
        yaxis_title='Probability' if isinstance(probabilities[0], float) else 'Count',
        template='plotly_white'
    )
    
    return fig

def create_progress_chart(progress_data):
    """
    Create a progress over time chart
    
    Args:
        progress_data: Dictionary containing progress data
        
    Returns:
        Plotly figure object
    """
    if not progress_data or 'time_series' not in progress_data:
        return None
    
    time_series = progress_data['time_series']
    
    if not time_series:
        return None
    
    dates = [entry['date'] for entry in time_series]
    expressiveness = [entry['expressiveness'] for entry in time_series]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=expressiveness,
        mode='lines+markers',
        name='Expressiveness',
        line=dict(color='blue', width=2)
    ))
    
    fig.update_layout(
        title='Expressiveness Progress Over Time',
        xaxis_title='Date',
        yaxis_title='Expressiveness Score (%)',
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig

def create_combined_pitch_chart(user_pitch, user_timestamps, benchmark_pitch, benchmark_timestamps):
    """
    Create a combined pitch chart comparing user and benchmark recordings
    
    Args:
        user_pitch: List of user's pitch values
        user_timestamps: List of user's timestamps
        benchmark_pitch: List of benchmark pitch values
        benchmark_timestamps: List of benchmark timestamps
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Add user pitch trace
    fig.add_trace(go.Scatter(
        x=user_timestamps, 
        y=user_pitch,
        mode='lines',
        name='Your Speech',
        line=dict(color='blue', width=2)
    ))
    
    # Add benchmark pitch trace
    fig.add_trace(go.Scatter(
        x=benchmark_timestamps, 
        y=benchmark_pitch,
        mode='lines',
        name='Benchmark Speech',
        line=dict(color='green', width=2, dash='dash')
    ))
    
    # Update layout
    fig.update_layout(
        title='Pitch Comparison',
        xaxis_title='Time (seconds)',
        yaxis_title='Pitch (Hz)',
        legend_title='Recording',
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig

def create_combined_energy_chart(user_energy, user_timestamps, benchmark_energy, benchmark_timestamps):
    """
    Create a combined energy chart comparing user and benchmark recordings
    
    Args:
        user_energy: List of user's energy values
        user_timestamps: List of user's timestamps
        benchmark_energy: List of benchmark energy values
        benchmark_timestamps: List of benchmark timestamps
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Add user energy trace
    fig.add_trace(go.Scatter(
        x=user_timestamps, 
        y=user_energy,
        mode='lines',
        name='Your Speech',
        line=dict(color='orange', width=2),
        fill='tozeroy',
        fillcolor='rgba(255, 165, 0, 0.1)'
    ))
    
    # Add benchmark energy trace
    fig.add_trace(go.Scatter(
        x=benchmark_timestamps, 
        y=benchmark_energy,
        mode='lines',
        name='Benchmark Speech',
        line=dict(color='green', width=2, dash='dash')
    ))
    
    # Update layout
    fig.update_layout(
        title='Energy Comparison',
        xaxis_title='Time (seconds)',
        yaxis_title='Energy',
        legend_title='Recording',
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig