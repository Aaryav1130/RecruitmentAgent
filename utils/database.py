"""
Database module for RecruitmentAgent.
Uses SQLAlchemy with SQLite for persistent storage of saved jobs and interview sessions.
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

# Database file location (in project root)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recruitment_agent.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# ━━━ Models ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SavedJob(Base):
    """Model for saved job listings."""
    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), default="")
    platform = Column(String(100), default="")
    url = Column(Text, default="")
    description = Column(Text, default="")
    date_posted = Column(String(100), default="")
    date_saved = Column(DateTime, default=datetime.now)
    job_data_json = Column(JSON, nullable=True)

    def to_dict(self):
        """Convert to dictionary (compatible with existing code)."""
        data = self.job_data_json or {}
        data.update({
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "platform": self.platform,
            "url": self.url,
            "description": self.description,
            "date_posted": self.date_posted,
            "date_saved": self.date_saved.strftime("%Y-%m-%d %H:%M:%S") if self.date_saved else "",
        })
        return data


class InterviewSession(Base):
    """Model for interview sessions and their messages."""
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_name = Column(String(255), nullable=False, index=True)
    user_name = Column(String(255), default="")
    started_at = Column(DateTime, default=datetime.now)
    ended_at = Column(DateTime, nullable=True)
    messages_json = Column(JSON, default=list)
    evaluation_json = Column(JSON, nullable=True)


# ━━━ Database Initialization ━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def create_tables():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Get a new database session."""
    return SessionLocal()


# ━━━ Saved Jobs CRUD ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def db_save_job(job_data: dict) -> int:
    """Save a job to the database.
    
    Args:
        job_data: Dictionary containing job information.
        
    Returns:
        The ID of the saved job.
    """
    session = get_session()
    try:
        saved_job = SavedJob(
            title=job_data.get("title", ""),
            company=job_data.get("company", ""),
            location=job_data.get("location", ""),
            platform=job_data.get("platform", job_data.get("site", "")),
            url=job_data.get("url", job_data.get("job_url", "")),
            description=job_data.get("description", ""),
            date_posted=str(job_data.get("date_posted", "")),
            date_saved=datetime.now(),
            job_data_json=job_data,
        )
        session.add(saved_job)
        session.commit()
        job_id = saved_job.id
        return job_id
    except Exception as e:
        session.rollback()
        print(f"Error saving job to database: {e}")
        raise
    finally:
        session.close()


def db_get_all_saved_jobs() -> list:
    """Load all saved jobs from the database.
    
    Returns:
        List of job dictionaries.
    """
    session = get_session()
    try:
        jobs = session.query(SavedJob).order_by(SavedJob.date_saved.desc()).all()
        return [job.to_dict() for job in jobs]
    except Exception as e:
        print(f"Error loading saved jobs from database: {e}")
        return []
    finally:
        session.close()


def db_remove_saved_job(job_title: str, job_company: str) -> bool:
    """Remove a saved job from the database.
    
    Args:
        job_title: Title of the job to remove.
        job_company: Company of the job to remove.
        
    Returns:
        True if the job was removed, False otherwise.
    """
    session = get_session()
    try:
        job = session.query(SavedJob).filter(
            SavedJob.title == job_title,
            SavedJob.company == job_company
        ).first()
        if job:
            session.delete(job)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error removing saved job from database: {e}")
        return False
    finally:
        session.close()


# ━━━ Interview Sessions CRUD ━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def db_save_interview_messages(room_name: str, messages: list, user_name: str = "") -> int:
    """Save or append interview messages for a room.
    
    Args:
        room_name: The LiveKit room name.
        messages: List of message dictionaries.
        user_name: Name of the interviewee.
        
    Returns:
        The session ID.
    """
    session = get_session()
    try:
        # Check if a session for this room already exists
        interview = session.query(InterviewSession).filter(
            InterviewSession.room_name == room_name
        ).first()
        
        if interview:
            # Append messages to existing session
            existing = interview.messages_json or []
            existing.extend(messages)
            interview.messages_json = existing
        else:
            # Create new session
            interview = InterviewSession(
                room_name=room_name,
                user_name=user_name,
                started_at=datetime.now(),
                messages_json=messages,
            )
            session.add(interview)
        
        session.commit()
        return interview.id
    except Exception as e:
        session.rollback()
        print(f"Error saving interview messages: {e}")
        raise
    finally:
        session.close()


def db_get_interview_messages(room_name: str = None) -> list:
    """Get all interview messages, optionally filtered by room.
    
    Args:
        room_name: Optional room name to filter by.
        
    Returns:
        List of message dictionaries.
    """
    session = get_session()
    try:
        if room_name:
            interview = session.query(InterviewSession).filter(
                InterviewSession.room_name == room_name
            ).first()
            return interview.messages_json if interview else []
        else:
            # Return all messages from the most recent session
            interview = session.query(InterviewSession).order_by(
                InterviewSession.started_at.desc()
            ).first()
            return interview.messages_json if interview else []
    except Exception as e:
        print(f"Error loading interview messages: {e}")
        return []
    finally:
        session.close()


def db_save_evaluation(room_name: str, evaluation: dict):
    """Save interview evaluation results.
    
    Args:
        room_name: The LiveKit room name.
        evaluation: Evaluation dictionary from the LLM.
    """
    session = get_session()
    try:
        interview = session.query(InterviewSession).filter(
            InterviewSession.room_name == room_name
        ).first()
        if interview:
            interview.evaluation_json = evaluation
            interview.ended_at = datetime.now()
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error saving evaluation: {e}")
    finally:
        session.close()
