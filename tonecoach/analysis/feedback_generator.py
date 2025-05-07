class FeedbackGenerator:
    def __init__(self):
        # Define thresholds for different speech features
        self.thresholds = {
            'pitch_variability': {
                'low': 10,
                'moderate': 25,
                'high': 40
            },
            'energy_variability': {
                'low': 0.05,
                'moderate': 0.1,
                'high': 0.2
            },
            'speech_rate': {
                'slow': 2.5,
                'moderate': 4.0,
                'fast': 5.5
            },
            'pause_ratio': {
                'low': 0.1,
                'moderate': 0.2,
                'high': 0.3
            }
        }
    
    def generate(self, analysis_results, target_text=None):
        """
        Generate feedback based on speech analysis
        
        Args:
            analysis_results: Dictionary containing speech analysis results
            target_text: Optional target text for content accuracy assessment
            
        Returns:
            Dictionary containing feedback components
        """
        if not analysis_results:
            return None
        
        # Extract key metrics
        pitch_var = analysis_results['pitch_variability']
        energy_var = analysis_results['energy_variability']
        speech_rate = analysis_results['speech_rate']
        pause_ratio = analysis_results['pause_ratio']
        primary_emotion = analysis_results['primary_emotion']
        
        # Generate overall assessment
        assessment = self._generate_overall_assessment(
            pitch_var, energy_var, speech_rate, pause_ratio, primary_emotion
        )
        
        # Generate specific feedback
        specific_feedback = self._generate_specific_feedback(
            pitch_var, energy_var, speech_rate, pause_ratio
        )
        
        # Generate improvement suggestions
        suggestions = self._generate_improvement_suggestions(
            pitch_var, energy_var, speech_rate, pause_ratio, primary_emotion
        )
        
        # Identify strengths
        strengths = self._identify_strengths(
            pitch_var, energy_var, speech_rate, pause_ratio
        )
        
        # If we have target text, assess content accuracy
        content_accuracy = None
        if target_text and 'transcription' in analysis_results:
            content_accuracy = self._assess_content_accuracy(
                analysis_results['transcription'], target_text
            )
        
        return {
            'overall_assessment': assessment,
            'specific_feedback': specific_feedback,
            'improvement_suggestions': suggestions,
            'strengths': strengths,
            'content_accuracy': content_accuracy
        }
    
    def _generate_overall_assessment(self, pitch_var, energy_var, speech_rate, pause_ratio, emotion):
        """Generate an overall assessment of the speech"""
        # Rate speech as monotone or expressive
        is_monotone = pitch_var < self.thresholds['pitch_variability']['low']
        
        # Rate pacing
        if speech_rate < self.thresholds['speech_rate']['slow']:
            pacing = "slow"
        elif speech_rate > self.thresholds['speech_rate']['fast']:
            pacing = "fast"
        else:
            pacing = "good"
        
        # Generate assessment
        assessment = ""
        if is_monotone:
            assessment += "Your speech sounds somewhat monotone. "
        else:
            assessment += "Your speech has good tonal variation. "
        
        if pacing == "slow":
            assessment += "Your pacing is quite slow, which might reduce engagement. "
        elif pacing == "fast":
            assessment += "Your speaking pace is quite fast, which might make it difficult for listeners to follow. "
        else:
            assessment += "Your speaking pace is appropriate. "
        
        # Add emotion assessment
        assessment += f"Your speech conveys a primarily {emotion} tone. "
        
        return assessment
    
    def _generate_specific_feedback(self, pitch_var, energy_var, speech_rate, pause_ratio):
        """Generate specific feedback on different aspects of speech"""
        feedback = []
        
        # Pitch variation feedback
        if pitch_var < self.thresholds['pitch_variability']['low']:
            feedback.append("Your speech has limited pitch variation, which can sound monotonous. Try varying your tone more to sound engaging.")
        elif pitch_var < self.thresholds['pitch_variability']['moderate']:
            feedback.append("Your pitch variation is good. You're using a pleasant range of tones.")
        else:
            feedback.append("You're using excellent pitch variation. Your voice is very expressive and engaging.")
        
        # Energy variation feedback
        if energy_var < self.thresholds['energy_variability']['low']:
            feedback.append("Try emphasizing important words by varying your volume more.")
        elif energy_var < self.thresholds['energy_variability']['moderate']:
            feedback.append("Your volume variation is good. You're emphasizing words appropriately.")
        else:
            feedback.append("Excellent job varying your volume for emphasis. Your speech is dynamic and engaging.")
        
        # Speech rate feedback
        if speech_rate < self.thresholds['speech_rate']['slow']:
            feedback.append("Your speaking pace is a bit slow. Try speaking slightly faster to maintain engagement.")
        elif speech_rate > self.thresholds['speech_rate']['fast']:
            feedback.append("You're speaking quite quickly. Try slowing down slightly and adding pauses for emphasis.")
        else:
            feedback.append("Your speaking pace is good - not too fast or too slow.")
        
        # Pause usage feedback
        if pause_ratio < self.thresholds['pause_ratio']['low']:
            feedback.append("Try adding more strategic pauses to give listeners time to absorb important points.")
        elif pause_ratio > self.thresholds['pause_ratio']['high']:
            feedback.append("You have many pauses in your speech. Some may be effective, but try to reduce unnecessary hesitations.")
        else:
            feedback.append("You're using pauses effectively. Good job!")
        
        return feedback
    
    def _generate_improvement_suggestions(self, pitch_var, energy_var, speech_rate, pause_ratio, emotion):
        """Generate specific suggestions for improvement"""
        suggestions = []
        
        # Pitch variation suggestions
        if pitch_var < self.thresholds['pitch_variability']['moderate']:
            suggestions.append("Practice emphasizing key words by raising or lowering your pitch. Try exaggerating at first, then find a natural level.")
        
        # Energy suggestions
        if energy_var < self.thresholds['energy_variability']['moderate']:
            suggestions.append("Practice emphasizing important words by slightly increasing your volume. Record yourself reading a passage with deliberate emphasis on key words.")
        
        # Pacing suggestions
        if speech_rate < self.thresholds['speech_rate']['slow']:
            suggestions.append("Try practicing with a metronome set at a slightly faster pace than your comfortable speaking rate.")
        elif speech_rate > self.thresholds['speech_rate']['fast']:
            suggestions.append("Mark your script with deliberate pause points and practice honoring those pauses.")
        
        # Pause suggestions
        if pause_ratio < self.thresholds['pause_ratio']['low']:
            suggestions.append("Practice inserting strategic pauses before important points or after asking questions. This gives listeners time to process your message.")
        
        # Emotional expression suggestions
        if pitch_var < self.thresholds['pitch_variability']['low']:
            suggestions.append("Try 'mirroring' the emotional delivery of speakers you admire. Record yourself matching their expressiveness, then find your own style.")
        
        return suggestions
    
    def _identify_strengths(self, pitch_var, energy_var, speech_rate, pause_ratio):
        """Identify strengths in the speech delivery"""
        strengths = []
        
        # Pitch variation strengths
        if pitch_var >= self.thresholds['pitch_variability']['moderate']:
            strengths.append("Good pitch variation that keeps your speech engaging")
        
        # Energy strengths
        if energy_var >= self.thresholds['energy_variability']['moderate']:
            strengths.append("Effective use of emphasis through volume variation")
        
        # Pacing strengths
        if speech_rate >= self.thresholds['speech_rate']['slow'] and speech_rate <= self.thresholds['speech_rate']['fast']:
            strengths.append("Well-balanced speaking pace that's easy to follow")
        
        # Pause usage strengths
        if pause_ratio >= self.thresholds['pause_ratio']['low'] and pause_ratio <= self.thresholds['pause_ratio']['high']:
            strengths.append("Effective use of pauses for emphasis")
        
        # If no specific strengths were identified, add a general positive note
        if not strengths:
            strengths.append("You're making good progress with your public speaking practice")
        
        return strengths
    
    def _assess_content_accuracy(self, transcription, target_text):
        """Assess how closely the spoken content matches the target text"""
        from difflib import SequenceMatcher
        
        # Calculate similarity ratio
        similarity = SequenceMatcher(None, transcription.lower(), target_text.lower()).ratio()
        
        # Identify missing or added words
        target_words = set(target_text.lower().split())
        spoken_words = set(transcription.lower().split())
        
        missing_words = target_words - spoken_words
        added_words = spoken_words - target_words
        
        # Generate feedback based on similarity
        if similarity > 0.9:
            feedback = "Excellent content accuracy! You delivered the message very close to the intended text."
        elif similarity > 0.7:
            feedback = "Good content accuracy with some variations from the original text."
        else:
            feedback = "Your delivery varied significantly from the intended text. Consider practicing to improve content accuracy."
        
        return {
            'accuracy_score': round(similarity * 100, 1),
            'missing_words': list(missing_words)[:5],  # Limit to 5 words
            'added_words': list(added_words)[:5],      # Limit to 5 words
            'feedback': feedback
        }