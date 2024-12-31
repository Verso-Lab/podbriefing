from celery import shared_task
import logging
from src.core.podcast import PodcastAnalyzer
import os

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def analyze_podcast(self, audio_path: str) -> str:
    """
    Analyze a podcast episode using Gemini.
    Returns the analysis text or error message.
    """
    try:
        if not os.path.exists(audio_path):
            error_msg = f"Audio file not found: {audio_path}"
            logger.error(error_msg)
            return error_msg
            
        analyzer = PodcastAnalyzer()
        result = analyzer.analyze_audio_detailed(audio_path)
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing podcast: {str(e)}")
        raise self.retry(exc=e)

@shared_task(bind=True)
def generate_newsletter(self, podcast_analyses: dict) -> str:
    """
    Generate a cohesive newsletter from multiple podcast analyses.
    """
    try:
        analyzer = PodcastAnalyzer()
        return analyzer.generate_cohesive_newsletter(podcast_analyses)
        
    except Exception as e:
        logger.error(f"Error generating newsletter: {str(e)}")
        raise self.retry(exc=e)
