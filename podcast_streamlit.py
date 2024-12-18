import streamlit as st
import feedparser
import requests
import os
from urllib.parse import urlparse
from pathlib import Path
import time
from podcast_analyzer import PodcastAnalyzer
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Predefined RSS feeds
PODCAST_FEEDS = {
    "The Ezra Klein Show": "https://feeds.simplecast.com/82FI35Px",
    "Hard Fork": "https://feeds.simplecast.com/l2i9YnTd",
    "The Daily": "https://feeds.simplecast.com/54nAGcIl"
}

# Cache for feed data
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_feed_data(rss_url):
    return feedparser.parse(rss_url)

# Hardcoded analysis prompt
ANALYSIS_PROMPT = """You're writing sharp, insider-style briefings for smart people who want the key points from important podcasts. Be concise and conversational - think smart friend giving quick insights over coffee.

Format exactly like this, starting directly with TLDR (no introduction or meta-commentary):

TLDR: [One punchy line that nails what this episode is really about]

WHY NOW: [Quick context on the timing/relevance]

KEY POINTS:
→ [First insight - be specific and surprising]
→ [Second insight - focus on what's newsworthy]
→ [Third insight - highlight what matters most]

QUOTED: "[Choose something short but powerful]" —[Speaker]

Keep it tight, specific, and conversational. No jargon, no fluff. Start directly with TLDR - no introductory sentences."""

def generate_newsletter(analyses, feeds):
    """Generate a punchy newsletter from podcast analyses"""
    today = datetime.now().strftime("%B %d")
    
    newsletter = f"""# Podcast Briefiong
#### {today}

*Quick update on today's episodes:*

"""
    
    for podcast_name, analysis in analyses.items():
        feed = get_feed_data(feeds[podcast_name])
        latest_episode = feed.entries[0]
        
        # Format the analysis text to ensure proper spacing and bullet points
        formatted_analysis = analysis.replace("KEY POINTS:", "**KEY POINTS:**")
        formatted_analysis = formatted_analysis.replace("→", "▸")  # nicer bullet
        formatted_analysis = formatted_analysis.replace("TLDR:", "**TLDR:**")
        formatted_analysis = formatted_analysis.replace("WHY NOW:", "**WHY NOW:**")
        formatted_analysis = formatted_analysis.replace("QUOTED:", "**QUOTED:**")
        
        newsletter += f"""
---

## {podcast_name}

{formatted_analysis}
"""
    
    newsletter += """
---
"""
    return newsletter

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip('. ')

def create_filename(entry, output_dir):
    """Create a filename from podcast entry with date and title"""
    try:
        date_str = entry.published_parsed
        date = f"{date_str.tm_year}-{date_str.tm_mon:02d}-{date_str.tm_mday:02d}"
    except (AttributeError, TypeError):
        date = time.strftime("%Y-%m-%d")
    
    title = sanitize_filename(entry.title)
    base_filename = f"{date}_{title}"
    
    if len(base_filename) > 200:
        base_filename = base_filename[:200]
    
    return os.path.join(output_dir, base_filename + '.mp3')

def get_podcast_image(feed):
    """Extract podcast image from feed"""
    try:
        # Try different possible image locations in the feed
        if 'image' in feed.feed and 'href' in feed.feed.image:
            return feed.feed.image.href
        elif 'image' in feed.feed:
            return feed.feed.image
        elif hasattr(feed.feed, 'itunes_image'):
            return feed.feed.itunes_image['href']
        return None
    except Exception as e:
        logger.error(f"Error getting podcast image: {str(e)}")
        return None

def download_and_analyze_episode(rss_url, output_dir='downloads'):
    """Download and analyze a podcast episode, return the analysis"""
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        feed = feedparser.parse(rss_url)
        if not feed.entries:
            st.error("No episodes found in the feed.")
            return None
        
        # Get latest episode
        entry = feed.entries[0]
        
        # Create podcast-specific subdirectory
        podcast_dir = os.path.join(output_dir, sanitize_filename(feed.feed.title))
        Path(podcast_dir).mkdir(parents=True, exist_ok=True)
        
        # Find audio URL and download
        for enclosure in entry.enclosures:
            if 'audio' in enclosure.type:
                audio_url = enclosure.href
                filename = create_filename(entry, podcast_dir)
                
                if os.path.exists(filename):
                    st.info(f"Using existing file: {os.path.basename(filename)}")
                else:
                    with st.spinner(f"Downloading: {entry.title}"):
                        response = requests.get(audio_url, stream=True)
                        response.raise_for_status()
                        
                        with open(filename, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        st.success(f"Downloaded: {os.path.basename(filename)}")
                
                # Get detailed analysis
                with st.spinner('Analyzing podcast content...'):
                    analyzer = PodcastAnalyzer()
                    detailed_analysis = analyzer.analyze_audio_detailed(filename)
                    if detailed_analysis.startswith("Error"):
                        st.error(detailed_analysis)
                        return None
                    return detailed_analysis
                
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def truncate_title(title, max_length=50):
    """Truncate title to a fixed length"""
    return title[:max_length] + "..." if len(title) > max_length else title

def main():
    # Add padding to make content area wider
    st.markdown("""
        <style>
        .block-container {
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1000px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🎧 Podcast Briefing Generator")
    
    # Header section
    st.markdown("Pick your podcasts. We'll analyze the latest episodes and create your briefing.")
    
    # Podcast selection section
    st.write("### 📱 Today's Lineup")
    
    # Create a 3-column layout for podcast cards
    podcast_cols = st.columns(3)
    selected_podcasts = {}
    
    for idx, (podcast_name, rss_url) in enumerate(PODCAST_FEEDS.items()):
        with podcast_cols[idx % 3]:
            # Container for the entire card
            with st.container():
                # Image container
                feed = get_feed_data(rss_url)
                image_url = get_podcast_image(feed)
                if image_url:
                    st.image(image_url, use_container_width=True)
                
                # Title
                st.markdown(f"#### {podcast_name}")
                
                # Episode title - truncated
                if feed.entries:
                    st.caption(f"Latest: {truncate_title(feed.entries[0].title)}")
                else:
                    st.caption("No episodes available")
                
                # Checkbox
                selected_podcasts[podcast_name] = st.checkbox("✨ Include in briefing", key=podcast_name)
    
    # Add some spacing
    st.write("")
    
    # Generate button - make it wider
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button("🚀 Generate Briefing", type="primary", use_container_width=True)
    
    # Progress and Newsletter section
    if generate_button:
        if not any(selected_podcasts.values()):
            st.warning("⚠️ Please select at least one podcast.")
            return
        
        # Add some spacing
        st.write("")
        
        # Create a progress section
        st.write("### 🎯 Analyzing Episodes")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Collect all analyses
        detailed_analyses = {}
        total_selected = sum(selected_podcasts.values())
        current = 0
        
        # First pass: Get detailed analysis for each podcast
        for podcast_name, is_selected in selected_podcasts.items():
            if is_selected:
                current += 1
                progress = current / total_selected
                progress_bar.progress(progress)
                status_text.write(f"Analyzing: {podcast_name} ({current}/{total_selected})")
                
                analysis = download_and_analyze_episode(PODCAST_FEEDS[podcast_name])
                if analysis:
                    detailed_analyses[podcast_name] = analysis
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        if detailed_analyses:
            # Second pass: Generate cohesive newsletter
            st.write("### 📝 Generating Newsletter")
            with st.spinner('Crafting your briefing...'):
                analyzer = PodcastAnalyzer()
                newsletter = analyzer.generate_cohesive_newsletter(detailed_analyses)
            
            if newsletter.startswith("Error"):
                st.error("Failed to generate newsletter. Please try again.")
                return
            
            # Display the newsletter
            st.write("### 📬 Your Podcast Briefing")
            
            # Add download button
            col1, col2 = st.columns([6, 1])
            with col2:
                st.download_button(
                    "📥 Download",
                    newsletter,
                    file_name=f"podcast_digest_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            # Display in container
            with st.container():
                st.markdown("""
                <style>
                .newsletter-container {
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 10px 0;
                }
                </style>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="newsletter-container">', unsafe_allow_html=True)
                st.markdown(newsletter)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("❌ Failed to analyze episodes. Please try again.")

if __name__ == "__main__":
    main() 