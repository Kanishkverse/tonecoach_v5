# ToneCoach: Emotional Intelligence for Public Speaking


ToneCoach is an AI-powered application that helps users enhance their speech expressiveness through real-time analysis and personalized feedback. By providing detailed insights on tone, pitch, energy, and pacing, ToneCoach creates a personalized learning experience to improve public speaking and communication skills.

## Features

- **Speech Analysis**: Advanced analysis of pitch variation, energy dynamics, and speaking tempo
- **Real-time Feedback**: Immediate actionable suggestions for improving expressiveness
- **Voice Cloning**: Hear improvements in your own voice through AI voice modeling
- **Emotional Intelligence**: Practice different emotional tones for various speaking contexts
- **Progress Tracking**: Monitor improvements over time with detailed metrics
- **Benchmark Exercises**: Practice with curated exercises for different speaking styles


## Getting Started

### Prerequisites

- Python 3.10 or higher
- ffmpeg (for audio processing)
- Internet connection (for voice cloning API)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Kanishkverse/ToneCoach.git
   cd ToneCoach
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Set up ElevenLabs API for voice cloning:
   - Create an account at [ElevenLabs](https://elevenlabs.io/)
   - Get your API key from your account dashboard
   - Create a file at `config/elevenlabs_config.json` with your API key:
     ```json
     {
       "api_key": "your_api_key_here"
     }
     ```

4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

### Navigation

ToneCoach provides an intuitive interface with five main sections:

1. **Dashboard**: View your progress and statistics
2. **Practice**: Record your speech and get immediate feedback
3. **Exercises**: Choose from various speaking exercises
4. **My Recordings**: Review your previous recordings and analyses
5. **Voice Enrollment**: Create your voice profile for personalized feedback

### Workflow

1. Select an exercise from the library
2. Listen to the benchmark recording for reference
3. Record your own speech following the provided text
4. Review the analysis of your speech patterns
5. Receive personalized feedback and suggestions
6. (Optional) Hear an improved version in your own voice using voice cloning
7. Practice again to improve your expressiveness score

## Project Structure

```
tonecoach/
├── app.py                      # Main Streamlit application entry point
├── analysis/                   # Speech analysis components
│   ├── speech_analyzer.py      # Core audio feature extraction
│   ├── feedback_generator.py   # Generates feedback based on analysis
│   └── emotion_detector.py     # Emotion detection in speech
├── ui/                         # User interface components
│   ├── components.py           # Reusable UI elements
│   ├── charts.py               # Data visualization functions
│   └── pages.py                # Page layout definitions
├── utils/                      # Utility functions
│   ├── audio.py                # Audio recording and processing
│   ├── auth.py                 # User authentication
│   └── voice_cloning.py        # Voice cloning integration
├── database/                   # Database management
│   ├── db_utils.py             # Database operations
│   └── models.py               # Data models
├── admin/                      # Administrative tools
│   ├── benchmark_tool.py       # Creates benchmark recordings
│   └── admin_benchmark_uploader.py  # Uploads benchmark data
├── benchmarks/                 # Stored benchmark audio files
├── voice_models/               # Voice model storage
├── uploads/                    # User audio storage
└── requirements.txt            # Dependencies
```

## Technologies Used

- **Streamlit**: Web application framework
- **librosa & pyAudioAnalysis**: Advanced audio feature extraction
- **SQLite**: Database for user data and recordings
- **ElevenLabs API**: Voice cloning capabilities
- **Plotly**: Interactive data visualizations

## Development

### Contributing

We welcome contributions to ToneCoach! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a pull request

### Future Enhancements

- Mobile application support
- Integration with video analysis
- Group practice sessions
- Expanded exercise library
- Additional language support

## Research & Evaluation



Our research showed significant improvements in expressiveness scores, with undergraduate students showing the largest average improvement (38%) and professionals showing more modest but still significant gains (21%).

## Team

- **Kanishka Samrat Kolakaluri**: Audio Analysis, Feedback Generation
- **Anurag Kopila**: Speech-to-Text, Voice Cloning
- **Kaushik Reddy ChinnapuReddy**: UI/UX, Data Visualization

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- University of Dayton, Department of Computer Science
- CPS 499/592 Human-AI Interaction course
- All participants in our user testing and evaluation phases