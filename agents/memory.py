import json
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from typing import List, Dict

Base = declarative_base()
engine = create_engine("sqlite:///agent_memory.db")
Session = sessionmaker(bind=engine)

class Conversation(Base):
    __tablename__ = "conversations"
    
    session_id = Column(String(36), primary_key=True)
    history = Column(Text)  # JSON-serialized list of messages
    last_updated = Column(String(20))

    def get_history(self) -> List[Dict]:
        return json.loads(self.history or "[]")

# Initialize DB
Base.metadata.create_all(engine)

class AgentMemory:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.db = Session()
        
    def add_message(self, role: str, content: str):
        """Store user/agent messages"""
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
        conv.last_updated = str(datetime.now())
        self.db.add(conv)
        self.db.commit()

    def get_context(self, max_messages=5) -> str:
        """Retrieve recent history as context string"""
        conv = self.db.get(Conversation, self.session_id)
        if not conv:
            return ""
            
        history = conv.get_history()[-max_messages:]
        return "\n".join(
            f"{msg['role']}: {msg['content']}" 
            for msg in history
        )