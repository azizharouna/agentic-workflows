import json
from sqlalchemy import create_engine, Column, String, Text, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from typing import List, Dict
import os

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    
    session_id = Column(String(36), primary_key=True)
    history = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow)
    size_kb = Column(String(10))

    def get_history(self) -> List[Dict]:
        return json.loads(self.history or "[]")

class AgentMemory:
    def __init__(self, session_id: str, max_sessions=1000, max_storage_mb=100):
        self.session_id = session_id
        self.max_sessions = max_sessions
        self.max_storage_mb = max_storage_mb
        self.db_path = "agent_memory.db"
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        Base.metadata.create_all(self.engine)

    def get_context(self) -> str:
        """Returns formatted conversation history"""
        conv = self.db.get(Conversation, self.session_id)
        if not conv:
            return "No conversation history"
            
        history = conv.get_history()
        return "\n".join(
            f"{msg['role']}: {msg['content']}"
            for msg in history
        )

    def _calculate_size(self):
        return os.path.getsize(self.db_path) / 1024 / 1024

    def _prune_sessions(self):
        # Size-based pruning
        if self._calculate_size() > self.max_storage_mb:
            oldest = self.db.query(Conversation).order_by(
                Conversation.last_updated).first()
            self.db.delete(oldest)
        
        # Count-based pruning
        session_count = self.db.query(Conversation).count()
        if session_count > self.max_sessions:
            to_remove = session_count - self.max_sessions
            oldest = self.db.query(Conversation).order_by(
                Conversation.last_updated).limit(to_remove).all()
            for session in oldest:
                self.db.delete(session)
        
        self.db.commit()

    def add_message(self, role: str, content: str):
        conv = self.db.get(Conversation, self.session_id) or Conversation(
            session_id=self.session_id,
            history="[]"
        )
        
        history = conv.get_history()
        history.append({
            "role": role,
            "content": content,
            "timestamp": str(datetime.now())
        })
        
        conv.history = json.dumps(history)
        conv.last_updated = datetime.utcnow()
        conv.size_kb = f"{len(conv.history) / 1024:.2f}"
        
        self.db.add(conv)
        self.db.commit()
        self._prune_sessions()