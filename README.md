# tonecoach_v5# ToneCoach

ToneCoach is an AI-powered speech coaching application that helps users improve their public speaking skills by providing real-time feedback on speech expressiveness, emotional tone, and content delivery.

## Features

- Real-time speech analysis
- Pitch and energy variation tracking
- Emotional tone detection
- Content accuracy assessment
- Progress tracking over time
- Personalized feedback and improvement suggestions

## Technologies Used

- Python
- Streamlit
- Librosa (audio processing)
- Transformers (speech-to-text and emotion detection)
- Plotly (data visualization)
- SQLite (database)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/tonecoach.git

# Navigate to the project directory
cd tonecoach

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\\Scripts\\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py