import re
from difflib import SequenceMatcher

class FeedbackGenerator:
    """
    Generate feedback based on speech analysis results
    """
    
    def __init__(self):
        # Thresholds for evaluation
        self.thresholds = {
            'pitch_variability': {
                'low': 15,
                'medium': 30,
                'high': 40
            },
            'energy_variability': {
                'low': 0.03,
                'medium': 0.06,
                'high': 0.1
            },
            'speech_rate': {
                'too_slow': 2.0,
                'slow': 2.5,
                'optimal_low': 3.0,
                'optimal_high': 4.0,
                'fast': 4.5,
                'too_fast': 5.0
            },
            'pause_ratio': {
                'low': 0.1,
                'medium': 0.15,
                'high': 0.25,
                'excessive': 0.35
            }
        }
    
    def generate(self, analysis_results, target_text=None):
        """
        Generate feedback based on analysis results
        
        Args:
            analysis_results: Dictionary containing analysis results
            target_text: Target text for content accuracy evaluation (optional)
            
        Returns:
            Dictionary containing feedback components
        """
        # Extract relevant metrics
        pitch_var = analysis_results.get('pitch_variability', 0)
        energy_var = analysis_results.get('energy_variability', 0)
        speech_rate = analysis_results.get('speech_rate', 0)
        pause_ratio = analysis_results.get('pause_ratio', 0)
        emphasis_ratio = analysis_results.get('emphasis_ratio', 0)
        primary_emotion = analysis_results.get('primary_emotion', 'neutral')
        transcription = analysis_results.get('transcription', '')
        expressiveness = analysis_results.get('expressiveness_score', 0)
        
        # Generate feedback components
        overall_assessment = self._generate_overall_assessment(
            expressiveness, pitch_var, energy_var, speech_rate, primary_emotion
        )
        
        specific_feedback = self._generate_specific_feedback(
            pitch_var, energy_var, speech_rate, pause_ratio, emphasis_ratio, primary_emotion
        )
        
        strengths = self._identify_strengths(
            pitch_var, energy_var, speech_rate, pause_ratio, emphasis_ratio, primary_emotion
        )
        
        improvement_suggestions = self._generate_improvement_suggestions(
            pitch_var, energy_var, speech_rate, pause_ratio, emphasis_ratio, primary_emotion
        )
        
        # Evaluate content accuracy if target text is provided
        content_accuracy = None
        if target_text and transcription:
            content_accuracy = self._evaluate_content_accuracy(transcription, target_text)
        
        # Combine all feedback components
        feedback = {
            'overall_assessment': overall_assessment,
            'specific_feedback': specific_feedback,
            'strengths': strengths,
            'improvement_suggestions': improvement_suggestions
        }
        
        if content_accuracy:
            feedback['content_accuracy'] = content_accuracy
        
        return feedback
    
    def generate_comparative(self, user_analysis, benchmark_analysis, target_text=None):
        """
        Generate comparative feedback between user and benchmark recordings
        
        Args:
            user_analysis: Dictionary containing user's analysis results
            benchmark_analysis: Dictionary containing benchmark analysis results
            target_text: Target text for content accuracy evaluation (optional)
            
        Returns:
            Dictionary containing comparative feedback components
        """
        # Generate standard feedback for user's recording
        user_feedback = self.generate(user_analysis, target_text)
        
        # If benchmark analysis is not available, return standard feedback
        if not benchmark_analysis:
            return user_feedback
        
        # Extract metrics for comparison
        user_pitch_var = user_analysis.get('pitch_variability', 0)
        user_energy_var = user_analysis.get('energy_variability', 0)
        user_speech_rate = user_analysis.get('speech_rate', 0)
        user_pause_ratio = user_analysis.get('pause_ratio', 0)
        user_emphasis_ratio = user_analysis.get('emphasis_ratio', 0)
        user_primary_emotion = user_analysis.get('primary_emotion', 'neutral')
        user_expressiveness = user_analysis.get('expressiveness_score', 0)
        user_transcription = user_analysis.get('transcription', '')
        
        benchmark_pitch_var = benchmark_analysis.get('pitch_variability', 0)
        benchmark_energy_var = benchmark_analysis.get('energy_variability', 0)
        benchmark_speech_rate = benchmark_analysis.get('speech_rate', 0)
        benchmark_pause_ratio = benchmark_analysis.get('pause_ratio', 0)
        benchmark_emphasis_ratio = benchmark_analysis.get('emphasis_ratio', 0)
        benchmark_primary_emotion = benchmark_analysis.get('primary_emotion', 'neutral')
        benchmark_expressiveness = benchmark_analysis.get('expressiveness_score', 0)
        benchmark_transcription = benchmark_analysis.get('transcription', '')
        
        # Generate comparative assessment
        comparison = self._generate_comparison(
            user_pitch_var, user_energy_var, user_speech_rate, user_pause_ratio, user_emphasis_ratio, user_primary_emotion, user_expressiveness,
            benchmark_pitch_var, benchmark_energy_var, benchmark_speech_rate, benchmark_pause_ratio, benchmark_emphasis_ratio, benchmark_primary_emotion, benchmark_expressiveness
        )
        
        # Generate overall comparative assessment
        overall_assessment = self._generate_comparative_assessment(
            user_expressiveness, benchmark_expressiveness,
            user_pitch_var, benchmark_pitch_var,
            user_energy_var, benchmark_energy_var,
            user_speech_rate, benchmark_speech_rate,
            user_primary_emotion, benchmark_primary_emotion
        )
        
        # If target text is provided, evaluate content accuracy for both
        content_accuracy = None
        if target_text and user_transcription:
            user_accuracy = self._evaluate_content_accuracy(user_transcription, target_text)
            
            if benchmark_transcription:
                benchmark_accuracy = self._evaluate_content_accuracy(benchmark_transcription, target_text)
                user_accuracy['benchmark_accuracy'] = benchmark_accuracy.get('accuracy_score', 0)
                
                # Add comparative feedback on accuracy
                if user_accuracy['accuracy_score'] >= benchmark_accuracy['accuracy_score']:
                    user_accuracy['feedback'] += f" Your content accuracy is similar to or better than the benchmark recording."
                else:
                    user_accuracy['feedback'] += f" The benchmark recording has higher content accuracy. Pay attention to the missing words in your delivery."
            
            content_accuracy = user_accuracy
        
        # Construct comprehensive comparative feedback
        feedback = {
            'overall_assessment': overall_assessment,
            'comparison': comparison,
            'specific_feedback': user_feedback.get('specific_feedback', []),
            'improvement_suggestions': user_feedback.get('improvement_suggestions', [])
        }
        
        if content_accuracy:
            feedback['content_accuracy'] = content_accuracy
        
        return feedback
    
    def _generate_overall_assessment(self, expressiveness, pitch_var, energy_var, speech_rate, primary_emotion):
        """
        Generate an overall assessment of the speech
        
        Args:
            expressiveness: Overall expressiveness score
            pitch_var: Pitch variability
            energy_var: Energy variability
            speech_rate: Speech rate in syllables per second
            primary_emotion: Primary emotion detected
            
        Returns:
            String containing overall assessment
        """
        # Determine expressiveness level
        if expressiveness >= 80:
            expressiveness_level = "very expressive"
        elif expressiveness >= 60:
            expressiveness_level = "expressive"
        elif expressiveness >= 40:
            expressiveness_level = "moderately expressive"
        elif expressiveness >= 20:
            expressiveness_level = "somewhat flat"
        else:
            expressiveness_level = "monotonous"
        
        # Determine pitch and energy descriptions
        if pitch_var >= self.thresholds['pitch_variability']['high']:
            pitch_desc = "varied pitch"
        elif pitch_var >= self.thresholds['pitch_variability']['medium']:
            pitch_desc = "good pitch variation"
        elif pitch_var >= self.thresholds['pitch_variability']['low']:
            pitch_desc = "limited pitch variation"
        else:
            pitch_desc = "monotonous pitch"
        
        if energy_var >= self.thresholds['energy_variability']['high']:
            energy_desc = "dynamic volume"
        elif energy_var >= self.thresholds['energy_variability']['medium']:
            energy_desc = "good volume variation"
        elif energy_var >= self.thresholds['energy_variability']['low']:
            energy_desc = "limited volume variation"
        else:
            energy_desc = "flat volume"
        
        # Determine pace description
        if speech_rate < self.thresholds['speech_rate']['too_slow']:
            pace_desc = "very slow pace"
        elif speech_rate < self.thresholds['speech_rate']['slow']:
            pace_desc = "slow pace"
        elif speech_rate >= self.thresholds['speech_rate']['too_fast']:
            pace_desc = "very fast pace"
        elif speech_rate >= self.thresholds['speech_rate']['fast']:
            pace_desc = "fast pace"
        else:
            pace_desc = "good pace"
        
        # Format emotion for readability
        emotion = primary_emotion.replace('_', ' ').capitalize()
        
        # Construct overall assessment
        assessment = f"Your speech was {expressiveness_level}, with {pitch_desc} and {energy_desc}, delivered at a {pace_desc}. "
        assessment += f"Your delivery primarily conveyed a {emotion} tone."
        
        return assessment
    
    def _generate_specific_feedback(self, pitch_var, energy_var, speech_rate, pause_ratio, emphasis_ratio, primary_emotion):
        """
        Generate specific feedback on different aspects of speech
        
        Args:
            pitch_var: Pitch variability
            energy_var: Energy variability
            speech_rate: Speech rate in syllables per second
            pause_ratio: Ratio of pauses to total frames
            emphasis_ratio: Ratio of emphasized segments to total frames
            primary_emotion: Primary emotion detected
            
        Returns:
            List of specific feedback points
        """
        feedback = []
        
        # Pitch feedback
        if pitch_var >= self.thresholds['pitch_variability']['high']:
            feedback.append("Your pitch variation was excellent, creating an engaging and dynamic delivery.")
        elif pitch_var >= self.thresholds['pitch_variability']['medium']:
            feedback.append("You demonstrated good pitch variation, which helped maintain listener interest.")
        elif pitch_var >= self.thresholds['pitch_variability']['low']:
            feedback.append("Your pitch variation was adequate but could be improved to create a more engaging delivery.")
        else:
            feedback.append("Your speech had limited pitch variation, which may come across as monotonous.")
        
        # Energy feedback
        if energy_var >= self.thresholds['energy_variability']['high']:
            feedback.append("Your volume dynamics were excellent, effectively emphasizing important points.")
        elif energy_var >= self.thresholds['energy_variability']['medium']:
            feedback.append("You showed good volume variation, which helped highlight key parts of your speech.")
        elif energy_var >= self.thresholds['energy_variability']['low']:
            feedback.append("Your volume variation was moderate. Consider using more dynamic volume to emphasize important points.")
        else:
            feedback.append("Your speech had limited volume variation, which may reduce impact and engagement.")
        
        # Pace feedback
        if speech_rate < self.thresholds['speech_rate']['too_slow']:
            feedback.append("Your speaking pace was very slow, which might cause listeners to lose interest.")
        elif speech_rate < self.thresholds['speech_rate']['slow']:
            feedback.append("Your speaking pace was somewhat slow. Consider speaking slightly faster for more engagement.")
        elif speech_rate >= self.thresholds['speech_rate']['too_fast']:
            feedback.append("Your speaking pace was very fast, which might make it difficult for listeners to follow.")
        elif speech_rate >= self.thresholds['speech_rate']['fast']:
            feedback.append("Your speaking pace was somewhat fast. Consider slowing down slightly for better clarity.")
        else:
            feedback.append("Your speaking pace was well-balanced, making it easy for listeners to follow.")
        
        # Pause feedback
        if pause_ratio >= self.thresholds['pause_ratio']['excessive']:
            feedback.append("You had too many pauses in your speech, which might disrupt the flow.")
        elif pause_ratio >= self.thresholds['pause_ratio']['high']:
            feedback.append("You used pauses effectively to emphasize key points.")
        elif pause_ratio >= self.thresholds['pause_ratio']['medium']:
            feedback.append("Your use of pauses was balanced, creating a natural speaking rhythm.")
        elif pause_ratio >= self.thresholds['pause_ratio']['low']:
            feedback.append("You had few pauses in your speech. Strategic pauses can help emphasize important points.")
        else:
            feedback.append("You had very few pauses, which might make your speech feel rushed.")
        
        # Emphasis feedback
        if emphasis_ratio >= 0.1:
            feedback.append("You emphasized key points effectively, which helps maintain listener attention.")
        elif emphasis_ratio >= 0.05:
            feedback.append("You used some emphasis in your speech, which helps highlight important information.")
        else:
            feedback.append("Your speech had limited emphasis. Consider emphasizing key points more to increase impact.")
        
        # Emotion feedback
        emotion = primary_emotion.replace('_', ' ').capitalize()
        feedback.append(f"Your speech primarily conveyed a {emotion} tone, which may affect how your message is received.")
        
        return feedback
    
    def _identify_strengths(self, pitch_var, energy_var, speech_rate, pause_ratio, emphasis_ratio, primary_emotion):
        """
        Identify strengths in the speech delivery
        
        Args:
            pitch_var: Pitch variability
            energy_var: Energy variability
            speech_rate: Speech rate in syllables per second
            pause_ratio: Ratio of pauses to total frames
            emphasis_ratio: Ratio of emphasized segments to total frames
            primary_emotion: Primary emotion detected
            
        Returns:
            List of strengths
        """
        strengths = []
        
        # Pitch strength
        if pitch_var >= self.thresholds['pitch_variability']['medium']:
            strengths.append("Good pitch variation that creates an engaging delivery")
        
        # Energy strength
        if energy_var >= self.thresholds['energy_variability']['medium']:
            strengths.append("Effective use of volume variation to emphasize points")
        
        # Pace strength
        if self.thresholds['speech_rate']['optimal_low'] <= speech_rate <= self.thresholds['speech_rate']['optimal_high']:
            strengths.append("Well-balanced speaking pace that is easy to follow")
        
        # Pause strength
        if self.thresholds['pause_ratio']['medium'] <= pause_ratio <= self.thresholds['pause_ratio']['high']:
            strengths.append("Strategic use of pauses to emphasize key points")
        
        # Emphasis strength
        if emphasis_ratio >= 0.05:
            strengths.append("Good emphasis on important information")
        
        # Emotion strength
        if primary_emotion in ['confident', 'joy', 'enthusiasm']:
            emotion = primary_emotion.replace('_', ' ').capitalize()
            strengths.append(f"{emotion} tone that enhances your message")
        
        # If no specific strengths identified, add a generic one
        if not strengths:
            strengths.append("Consistent delivery that provides a foundation to build upon")
        
        return strengths
    
    def _generate_improvement_suggestions(self, pitch_var, energy_var, speech_rate, pause_ratio, emphasis_ratio, primary_emotion):
        """
        Generate suggestions for improvement
        
        Args:
            pitch_var: Pitch variability
            energy_var: Energy variability
            speech_rate: Speech rate in syllables per second
            pause_ratio: Ratio of pauses to total frames
            emphasis_ratio: Ratio of emphasized segments to total frames
            primary_emotion: Primary emotion detected
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # Pitch suggestions
        if pitch_var < self.thresholds['pitch_variability']['medium']:
            suggestions.append("Vary your pitch more to make your delivery more engaging")
        
        # Energy suggestions
        if energy_var < self.thresholds['energy_variability']['medium']:
            suggestions.append("Use more dynamic volume to emphasize important points")
        
        # Pace suggestions
        if speech_rate < self.thresholds['speech_rate']['optimal_low']:
            suggestions.append("Increase your speaking pace slightly to maintain listener interest")
        elif speech_rate > self.thresholds['speech_rate']['optimal_high']:
            suggestions.append("Slow down your speaking pace slightly for better clarity")
        
        # Pause suggestions
        if pause_ratio < self.thresholds['pause_ratio']['medium']:
            suggestions.append("Use strategic pauses to emphasize key points and give listeners time to absorb information")
        elif pause_ratio > self.thresholds['pause_ratio']['high']:
            suggestions.append("Reduce the number of pauses to maintain better flow in your speech")
        
        # Emphasis suggestions
        if emphasis_ratio < 0.05:
            suggestions.append("Emphasize key points more to increase impact and highlight important information")
        
        # Emotion suggestions
        if primary_emotion in ['neutral', 'sadness', 'fear']:
            suggestions.append("Try to convey more enthusiasm and confidence in your delivery")
        
        # If no specific suggestions identified, add a generic one
        if not suggestions:
            suggestions.append("Practice with different styles to further enhance your already strong delivery")
        
        return suggestions
    
    def _evaluate_content_accuracy(self, transcription, target_text):
        """
        Evaluate content accuracy by comparing transcription to target text
        
        Args:
            transcription: Transcription of the speech
            target_text: Target text that should have been spoken
            
        Returns:
            Dictionary containing accuracy evaluation
        """
        # Normalize text for comparison
        trans_norm = self._normalize_text(transcription)
        target_norm = self._normalize_text(target_text)
        
        # Split into words
        trans_words = trans_norm.split()
        target_words = target_norm.split()
        
        # Calculate sequence similarity
        similarity = SequenceMatcher(None, trans_norm, target_norm).ratio()
        
        # Identify missing and added words
        missing_words = set(target_words) - set(trans_words)
        added_words = set(trans_words) - set(target_words)
        
        # Calculate accuracy score
        accuracy_score = int(similarity * 100)
        
        # Generate feedback
        if accuracy_score >= 90:
            feedback = "Your content was delivered with excellent accuracy, closely matching the intended text."
        elif accuracy_score >= 70:
            feedback = "Your content was delivered with good accuracy, though some words were missed or added."
        elif accuracy_score >= 50:
            feedback = "Your content had moderate accuracy. Pay attention to key words that were missed."
        else:
            feedback = "Your content had significant deviations from the intended text. Focus on delivering the key points accurately."
        
        return {
            'accuracy_score': accuracy_score,
            'feedback': feedback,
            'missing_words': list(missing_words)[:10] if len(missing_words) > 10 else list(missing_words),
            'added_words': list(added_words)[:10] if len(added_words) > 10 else list(added_words)
        }
    
    def _normalize_text(self, text):
        """
        Normalize text for comparison by removing punctuation and converting to lowercase
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Remove punctuation and convert to lowercase
        text = re.sub(r'[^\w\s]', '', text.lower())
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _generate_comparison(self, 
                            user_pitch_var, user_energy_var, user_speech_rate, user_pause_ratio, user_emphasis_ratio, user_primary_emotion, user_expressiveness,
                            benchmark_pitch_var, benchmark_energy_var, benchmark_speech_rate, benchmark_pause_ratio, benchmark_emphasis_ratio, benchmark_primary_emotion, benchmark_expressiveness):
        """
        Generate comparison between user and benchmark recordings
        
        Args:
            user_*: User's speech metrics
            benchmark_*: Benchmark speech metrics
            
        Returns:
            Dictionary containing comparison components
        """
        general = []
        strengths = []
        improvements = []
        matches = []
        
        # Overall expressiveness comparison
        if user_expressiveness >= benchmark_expressiveness * 0.9:
            general.append(f"Your overall expressiveness ({user_expressiveness:.1f}%) is comparable to the benchmark ({benchmark_expressiveness:.1f}%).")
            if user_expressiveness > benchmark_expressiveness:
                strengths.append("Your overall expressiveness exceeds the benchmark")
            else:
                matches.append("Your overall expressiveness matches the benchmark")
        else:
            general.append(f"Your overall expressiveness ({user_expressiveness:.1f}%) is lower than the benchmark ({benchmark_expressiveness:.1f}%).")
            improvements.append("Work on increasing your overall expressiveness to match the benchmark")
        
        # Pitch comparison
        pitch_diff = abs(user_pitch_var - benchmark_pitch_var)
        pitch_diff_percent = pitch_diff / benchmark_pitch_var if benchmark_pitch_var > 0 else 0
        
        if pitch_diff_percent <= 0.2:  # Within 20% of benchmark
            matches.append("Your pitch variation closely matches the benchmark")
        elif user_pitch_var > benchmark_pitch_var:
            if user_pitch_var > self.thresholds['pitch_variability']['high'] and benchmark_pitch_var < self.thresholds['pitch_variability']['high']:
                improvements.append("Your pitch variation is higher than the benchmark - consider a more controlled delivery")
            else:
                strengths.append("Your pitch variation is higher than the benchmark, which may increase engagement")
        else:  # user_pitch_var < benchmark_pitch_var
            improvements.append("Increase your pitch variation to match the benchmark for better engagement")
        
        # Energy comparison
        energy_diff = abs(user_energy_var - benchmark_energy_var)
        energy_diff_percent = energy_diff / benchmark_energy_var if benchmark_energy_var > 0 else 0
        
        if energy_diff_percent <= 0.2:  # Within 20% of benchmark
            matches.append("Your volume variation closely matches the benchmark")
        elif user_energy_var > benchmark_energy_var:
            if user_energy_var > self.thresholds['energy_variability']['high'] and benchmark_energy_var < self.thresholds['energy_variability']['high']:
                improvements.append("Your volume variation is higher than the benchmark - consider a more controlled delivery")
            else:
                strengths.append("Your dynamic volume use is more pronounced than the benchmark")
        else:  # user_energy_var < benchmark_energy_var
            improvements.append("Increase your volume variation to match the benchmark for better emphasis")
        
        # Speech rate comparison
        rate_diff = abs(user_speech_rate - benchmark_speech_rate)
        rate_diff_percent = rate_diff / benchmark_speech_rate if benchmark_speech_rate > 0 else 0
        
        if rate_diff_percent <= 0.1:  # Within 10% of benchmark
            matches.append("Your speaking pace closely matches the benchmark")
        elif user_speech_rate > benchmark_speech_rate:
            if benchmark_speech_rate < self.thresholds['speech_rate']['optimal_high'] and user_speech_rate > self.thresholds['speech_rate']['optimal_high']:
                improvements.append("Slow down your speaking pace to match the benchmark for better clarity")
            else:
                general.append(f"Your speaking pace ({user_speech_rate:.1f} syl/sec) is faster than the benchmark ({benchmark_speech_rate:.1f} syl/sec).")
        else:  # user_speech_rate < benchmark_speech_rate
            if benchmark_speech_rate > self.thresholds['speech_rate']['optimal_low'] and user_speech_rate < self.thresholds['speech_rate']['optimal_low']:
                improvements.append("Increase your speaking pace to match the benchmark for better engagement")
            else:
                general.append(f"Your speaking pace ({user_speech_rate:.1f} syl/sec) is slower than the benchmark ({benchmark_speech_rate:.1f} syl/sec).")
        
        # Pause ratio comparison
        pause_diff = abs(user_pause_ratio - benchmark_pause_ratio)
        pause_diff_percent = pause_diff / benchmark_pause_ratio if benchmark_pause_ratio > 0 else 0
        
        if pause_diff_percent <= 0.2:  # Within 20% of benchmark
            matches.append("Your use of pauses closely matches the benchmark")
        elif user_pause_ratio > benchmark_pause_ratio:
            if user_pause_ratio > self.thresholds['pause_ratio']['high'] and benchmark_pause_ratio < self.thresholds['pause_ratio']['high']:
                improvements.append("Reduce your pauses to maintain better flow like the benchmark")
            else:
                general.append("You use more pauses than the benchmark, which may affect your speaking rhythm.")
        else:  # user_pause_ratio < benchmark_pause_ratio
            if benchmark_pause_ratio > self.thresholds['pause_ratio']['medium'] and user_pause_ratio < self.thresholds['pause_ratio']['medium']:
                improvements.append("Use more strategic pauses like the benchmark to emphasize key points")
            else:
                general.append("You use fewer pauses than the benchmark, which may affect your emphasis.")
        
        # Emotion comparison
        if user_primary_emotion == benchmark_primary_emotion:
            matches.append(f"Your emotional tone ({user_primary_emotion.replace('_', ' ').capitalize()}) matches the benchmark")
        else:
            user_emotion = user_primary_emotion.replace('_', ' ').capitalize()
            benchmark_emotion = benchmark_primary_emotion.replace('_', ' ').capitalize()
            general.append(f"Your emotional tone ({user_emotion}) differs from the benchmark ({benchmark_emotion}).")
            
            # Check if benchmark emotion is generally more desirable for presentations
            if benchmark_primary_emotion in ['confident', 'joy', 'enthusiasm'] and user_primary_emotion not in ['confident', 'joy', 'enthusiasm']:
                improvements.append(f"Try to convey more {benchmark_emotion} in your delivery like the benchmark")
        
        # Return structured comparison
        return {
            'general': general,
            'strengths': strengths,
            'improvements': improvements,
            'matches': matches
        }
    
    def _generate_comparative_assessment(self, 
                                        user_expressiveness, benchmark_expressiveness,
                                        user_pitch_var, benchmark_pitch_var,
                                        user_energy_var, benchmark_energy_var,
                                        user_speech_rate, benchmark_speech_rate,
                                        user_primary_emotion, benchmark_primary_emotion):
        """
        Generate an overall comparative assessment
        
        Args:
            user_*: User's speech metrics
            benchmark_*: Benchmark speech metrics
            
        Returns:
            String containing comparative assessment
        """
        # Calculate overall similarity score
        similarity_factors = [
            min(user_expressiveness / benchmark_expressiveness, 1.0) if benchmark_expressiveness > 0 else 0.5,
            1.0 - min(abs(user_pitch_var - benchmark_pitch_var) / benchmark_pitch_var, 1.0) if benchmark_pitch_var > 0 else 0.5,
            1.0 - min(abs(user_energy_var - benchmark_energy_var) / benchmark_energy_var, 1.0) if benchmark_energy_var > 0 else 0.5,
            1.0 - min(abs(user_speech_rate - benchmark_speech_rate) / benchmark_speech_rate, 1.0) if benchmark_speech_rate > 0 else 0.5,
            1.0 if user_primary_emotion == benchmark_primary_emotion else 0.5
        ]
        
        similarity_score = sum(similarity_factors) / len(similarity_factors) * 100
        
        # Generate assessment based on similarity score
        if similarity_score >= 80:
            assessment = f"Your speech delivery is very similar to the benchmark recording ({similarity_score:.0f}% match). "
        elif similarity_score >= 60:
            assessment = f"Your speech delivery has many similarities to the benchmark recording ({similarity_score:.0f}% match). "
        elif similarity_score >= 40:
            assessment = f"Your speech delivery shares some characteristics with the benchmark recording ({similarity_score:.0f}% match). "
        else:
            assessment = f"Your speech delivery differs significantly from the benchmark recording ({similarity_score:.0f}% match). "
        
        # Add specific comparison points
        if user_expressiveness >= benchmark_expressiveness * 0.9:
            if user_expressiveness > benchmark_expressiveness:
                assessment += "Your expressiveness exceeds the benchmark. "
            else:
                assessment += "Your expressiveness closely matches the benchmark. "
        else:
            assessment += "The benchmark recording demonstrates higher expressiveness. "
        
        # Add pace comparison
        rate_diff = abs(user_speech_rate - benchmark_speech_rate)
        if rate_diff <= 0.5:
            assessment += "Your speaking pace matches the benchmark well. "
        elif user_speech_rate > benchmark_speech_rate:
            assessment += "You speak faster than the benchmark. "
        else:
            assessment += "You speak slower than the benchmark. "
        
        # Add emotion comparison
        if user_primary_emotion == benchmark_primary_emotion:
            assessment += f"Both you and the benchmark convey a {user_primary_emotion.replace('_', ' ')} tone."
        else:
            user_emotion = user_primary_emotion.replace('_', ' ').capitalize()
            benchmark_emotion = benchmark_primary_emotion.replace('_', ' ').capitalize()
            assessment += f"You convey a {user_emotion} tone, while the benchmark conveys a {benchmark_emotion} tone."
        
        return assessment