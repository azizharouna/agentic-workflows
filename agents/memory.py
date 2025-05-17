import json
from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
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
        self.engine = create_async_engine(f"sqlite+aiosqlite:///{self.db_path}")
        self.async_session = async_sessionmaker(self.engine)
        self.db = self.async_session()
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

    async def _prune_sessions(self, session):
        # Size-based pruning
        if self._calculate_size() > self.max_storage_mb:
            oldest = await session.execute(
                session.query(Conversation).order_by(Conversation.last_updated).limit(1)
            )
            await session.delete(oldest.scalar())
        
        # Count-based pruning
        session_count = await session.execute(
            session.query(Conversation).count()
        )
        if session_count.scalar() > self.max_sessions:
            to_remove = session_count.scalar() - self.max_sessions
            oldest = await session.execute(
                session.query(Conversation).order_by(Conversation.last_updated).limit(to_remove)
            )
            for session in oldest:
                self.db.delete(session)
        
        self.db.commit()

    async def add_message(self, role: str, content: str):
        async with self.async_session() as session:
            async with session.begin():
                conv = await session.get(Conversation, self.session_id) or Conversation(
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
                
                session.add(conv)
                await self._prune_sessions(session)
            conv.size_kb = f"{len(conv.history) / 1024:.2f}"
            
            session.add(conv)
            await session.commit()
            await self._prune_sessions(session)