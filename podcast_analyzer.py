import os
from dotenv import load_dotenv
import google.generativeai as genai
from pathlib import Path
from pydub import AudioSegment
import tempfile
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class PodcastAnalyzer:
    def __init__(self):
        logger.info("Initializing PodcastAnalyzer")
        # Load environment variables
        load_dotenv()
        
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("GEMINI_API_KEY not found in environment variables")
            
        genai.configure(api_key=api_key)
        logger.info("Gemini API configured successfully")
        
        # Create the model
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=generation_config,
        )
        logger.info("Gemini model initialized")
    
    def transform_audio(self, audio_path):
        """Transform audio to reduce file size"""
        try:
            start_time = time.time()
            logger.info(f"Starting audio transformation for: {audio_path}")
            
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Get original file size
            original_size = os.path.getsize(audio_path) / (1024 * 1024)
            logger.info(f"Original file size: {original_size:.2f} MB")
            
            try:
                # Load audio file
                logger.info("Loading audio file...")
                audio = AudioSegment.from_file(audio_path)
            except Exception as e:
                raise Exception(f"Failed to load audio file: {str(e)}")
            
            logger.info(f"Original audio: {audio.channels} channels, {audio.frame_rate}Hz")
            
            try:
                # Convert to mono
                audio = audio.set_channels(1)
                logger.info("Converted to mono")
                
                # Reduce sample rate to 16kHz
                audio = audio.set_frame_rate(16000)
                logger.info("Reduced sample rate to 16kHz")
            except Exception as e:
                raise Exception(f"Failed to process audio: {str(e)}")
            
            try:
                # Export with reduced quality
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                    logger.info("Exporting compressed audio...")
                    audio.export(tmp_file.name, format='mp3', 
                               parameters=["-q:a", "9"])
                    
                    compressed_size = os.path.getsize(tmp_file.name) / (1024 * 1024)
                    reduction = ((original_size - compressed_size) / original_size) * 100
                    
                    logger.info(f"Compressed file size: {compressed_size:.2f} MB")
                    logger.info(f"Size reduction: {reduction:.1f}%")
                    logger.info(f"Transformation completed in {time.time() - start_time:.1f} seconds")
                    
                    return tmp_file.name
            except Exception as e:
                raise Exception(f"Failed to export compressed audio: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error in transform_audio: {str(e)}", exc_info=True)
            raise
    
    def analyze_audio_detailed(self, audio_path):
        """First pass: Get detailed analysis of a podcast episode"""
        DETAILED_PROMPT = """Analyze this podcast episode in detail. Focus on capturing:

1. Main Topic & Context: What's being discussed and why it matters now
2. Key Arguments/Points: The most important ideas and insights shared
3. Notable Moments: Surprising facts, strong opinions, or memorable exchanges
4. Best Quotes: The most impactful or revealing statements (with speaker attribution)
5. Implications: The bigger picture takeaways or why this matters

Be thorough but clear - this is our source material for the final newsletter."""

        transformed_audio_path = None
        try:
            logger.info(f"Starting detailed analysis for: {audio_path}")
            
            # Transform audio to reduce size
            transformed_audio_path = self.transform_audio(audio_path)
            
            # Read the transformed audio file
            logger.info("Reading transformed audio file...")
            audio_data = Path(transformed_audio_path).read_bytes()
            
            # Send the audio with the prompt
            logger.info("Sending audio to Gemini for detailed analysis...")
            start_time = time.time()
            
            response = self.model.generate_content([
                DETAILED_PROMPT,
                {
                    "mime_type": "audio/mp3",
                    "data": audio_data
                }
            ])
            
            logger.info(f"Detailed analysis completed in {time.time() - start_time:.1f} seconds")
            return response.text
                
        except Exception as e:
            logger.error(f"Error in detailed analysis: {str(e)}", exc_info=True)
            return f"Error in detailed analysis: {str(e)}"
            
        finally:
            if transformed_audio_path and os.path.exists(transformed_audio_path):
                try:
                    logger.info("Cleaning up temporary files...")
                    os.unlink(transformed_audio_path)
                except Exception as e:
                    logger.error(f"Failed to clean up temporary file: {str(e)}")

    def generate_cohesive_newsletter(self, podcast_analyses):
        """Generate a cohesive newsletter from multiple podcast analyses"""
        NEWSLETTER_PROMPT = """Write a sharp, insider-style briefing based ONLY on the podcast episode analyses provided below.
Do not add any episodes or information that wasn't provided.

Start with this exact format:

# Today's Podcast Briefing

Hey! [One punchy line introeducing the briefing]

---

Then for each provided podcast analysis, format exactly like this:

## [Podcast Name]

TLDR: [One punchy line that nails what this episode is really about]

WHY NOW: [Quick context on the timing/relevance]

KEY POINTS:
→ [First insight - be specific and surprising]
→ [Second insight - focus on what's newsworthy]
→ [Third insight - highlight what matters most]

QUOTED: "[Choose the single most powerful quote]" —[Speaker]

---

That's it. Hear ya later!

-------

Keep it tight and conversational. No jargon, no fluff. Write ONLY about the podcasts provided in the analysis."""

        try:
            logger.info(f"Generating newsletter from {len(podcast_analyses)} analyses...")
            start_time = time.time()
            
            # Prepare the input by combining podcast name and analysis
            combined_input = "Here are the podcast episode analyses to include (and ONLY these):\n\n"
            for podcast_name, analysis in podcast_analyses.items():
                combined_input += f"# {podcast_name}\n\n{analysis}\n\n---\n\n"
            
            response = self.model.generate_content([
                NEWSLETTER_PROMPT,
                combined_input
            ])
            
            logger.info(f"Newsletter generated in {time.time() - start_time:.1f} seconds")
            return response.text
                
        except Exception as e:
            logger.error(f"Error generating newsletter: {str(e)}", exc_info=True)
            return f"Error generating newsletter: {str(e)}"