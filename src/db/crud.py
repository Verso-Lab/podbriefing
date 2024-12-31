from sqlalchemy.orm import Session
from . import models
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

# Episode operations
def create_episode(
    db: Session, 
    rss_url: str,
    podcast_name: str,
    episode_title: str
) -> models.Episode:
    """Create a new episode record"""
    episode = models.Episode(
        rss_url=rss_url,
        podcast_name=podcast_name,
        episode_title=episode_title
    )
    db.add(episode)
    db.commit()
    db.refresh(episode)
    return episode

def get_episode(db: Session, episode_id: int) -> Optional[models.Episode]:
    """Get an episode by ID"""
    return db.query(models.Episode).filter(models.Episode.id == episode_id).first()

def update_episode_status(
    db: Session, 
    episode_id: int, 
    status: models.ProcessingStatus
) -> Optional[models.Episode]:
    """Update an episode's status"""
    episode = get_episode(db, episode_id)
    if episode:
        episode.status = status
        db.commit()
        db.refresh(episode)
    return episode

def update_episode_audio_path(
    db: Session, 
    episode_id: int, 
    audio_path: str
) -> Optional[models.Episode]:
    """Update an episode's audio file path"""
    episode = get_episode(db, episode_id)
    if episode:
        episode.audio_path = audio_path
        db.commit()
        db.refresh(episode)
    return episode

def get_episodes_by_podcast(
    db: Session, 
    podcast_name: str, 
    limit: int = 10
) -> List[models.Episode]:
    """Get recent episodes for a specific podcast"""
    return db.query(models.Episode)\
        .filter(models.Episode.podcast_name == podcast_name)\
        .order_by(models.Episode.created_at.desc())\
        .limit(limit)\
        .all()

# Analysis operations
def create_analysis(
    db: Session, 
    episode_id: int, 
    result_text: str, 
    analysis_type: models.AnalysisType
) -> models.Analysis:
    """Create a new analysis result"""
    analysis = models.Analysis(
        episode_id=episode_id,
        result_text=result_text,
        analysis_type=analysis_type
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    # Only update episode status to completed if we have both brief and lead
    analyses = get_episode_analyses(db, episode_id)
    if len(set(a.analysis_type for a in analyses)) == len(models.AnalysisType):
        update_episode_status(db, episode_id, models.ProcessingStatus.COMPLETED)
    
    return analysis

def get_episode_analyses(db: Session, episode_id: int) -> List[models.Analysis]:
    """Get all analyses for an episode"""
    return db.query(models.Analysis)\
        .filter(models.Analysis.episode_id == episode_id)\
        .all()

def get_analysis_by_type(
    db: Session, 
    episode_id: int, 
    analysis_type: models.AnalysisType
) -> Optional[models.Analysis]:
    """Get a specific type of analysis for an episode"""
    return db.query(models.Analysis)\
        .filter(
            models.Analysis.episode_id == episode_id,
            models.Analysis.analysis_type == analysis_type
        )\
        .first()

def get_recent_leads(
    db: Session, 
    limit: int = 10
) -> List[models.Analysis]:
    """Get recent lead analyses"""
    return db.query(models.Analysis)\
        .filter(models.Analysis.analysis_type == models.AnalysisType.LEAD)\
        .order_by(models.Analysis.created_at.desc())\
        .limit(limit)\
        .all()

def get_recent_briefs(
    db: Session, 
    limit: int = 10
) -> List[models.Analysis]:
    """Get recent brief analyses"""
    return db.query(models.Analysis)\
        .filter(models.Analysis.analysis_type == models.AnalysisType.BRIEF)\
        .order_by(models.Analysis.created_at.desc())\
        .limit(limit)\
        .all() 