from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .session import Base

class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"

class AnalysisType(str, enum.Enum):
    BRIEF = "brief"
    LEAD = "lead"

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    rss_url = Column(String, nullable=False)
    podcast_name = Column(String, nullable=False)
    episode_title = Column(String, nullable=False)
    audio_path = Column(String, nullable=True)
    status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Each episode has two analyses (brief and lead)
    analyses = relationship("Analysis", back_populates="episode")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"))
    analysis_type = Column(SQLEnum(AnalysisType), nullable=False)
    result_text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to Episode
    episode = relationship("Episode", back_populates="analyses")
