from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./doc_intel.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, nullable=False)
    filename = Column(Text, nullable=False)
    extracted_text = Column(Text, nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.now)

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("SQLite database initialized successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()