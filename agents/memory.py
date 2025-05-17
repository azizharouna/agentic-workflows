import json
from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from datetime import datetime
from typing import List, Dict, Optional
import os
from pathlib import Path
import yaml
from pydantic import BaseModel

Base = declarative_base()

class Scenario(BaseModel):
    scenario: str
    description: str
    personas: Dict[str, Dict]
    story_arc: List[Dict]

class PersonaManager:
    def __init__(self, scenario_dir: str = "scenarios"):
        self.scenario_dir = Path(scenario_dir)
        self.loaded_scenarios: Dict[str, Scenario] = {}

    def load_scenario(self, scenario_name: str) -> Scenario:
        filepath = self.scenario_dir / f"{scenario_name}.yaml"
        with open(filepath) as f:
            data = yaml.safe_load(f)
            scenario = Scenario(**data)
            self.loaded_scenarios[scenario_name] = scenario
            return scenario

    def get_persona(self, scenario_name: str, persona_name: str) -> Dict:
        return self.loaded_scenarios[scenario_name].personas[persona_name]

    def get_story_arc(self, scenario_name: str) -> List[Dict]:
        return self.loaded_scenarios[scenario_name].story_arc

class Conversation(Base):
    __tablename__ = "conversations"
    
    session_id = Column(String(64), primary_key=True, nullable=False)
    history = Column(Text, default="[]", nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)
    size_kb = Column(String(10), default="0.00", nullable=False)

    def get_history(self) -> List[Dict]:
        return json.loads(self.history or "[]")

class AgentMemory:
    async def initialize_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def __init__(self, session_id: str = None, max_sessions=1000, max_storage_mb=100):
        self.session_id = session_id or str(uuid.uuid4())
        self.max_sessions = max_sessions
        self.max_storage_mb = max_storage_mb
        self.db_path = "agent_memory.db"
        self.engine = create_async_engine(
            f"sqlite+aiosqlite:///{self.db_path}",
            connect_args={"check_same_thread": False}
        )
        self.async_session = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            autoflush=False
        )

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
        from sqlalchemy import select, func
        from sqlalchemy import delete
        
        # Size-based pruning
        if self._calculate_size() > self.max_storage_mb:
            stmt = select(Conversation).order_by(Conversation.last_updated).limit(1)
            oldest = (await session.execute(stmt)).scalar()
            if oldest:
                await session.delete(oldest)
        
        # Count-based pruning
        count = (await session.execute(select(func.count()).select_from(Conversation))).scalar()
        if count > self.max_sessions:
            to_remove = count - self.max_sessions
            stmt = select(Conversation).order_by(Conversation.last_updated).limit(to_remove)
            oldest = await session.execute(stmt)
            for conv in oldest.scalars():
                await session.delete(conv)
        
        await session.commit()

    async def get_messages(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Retrieve conversation messages with pagination"""
        async with self.async_session() as session:
            conv = await session.get(Conversation, self.session_id)
            if not conv:
                return []
                
            history = conv.get_history()
            return history[offset:offset+limit]

    async def add_message(self, role: str, content: str):
        async with self.async_session() as session:
            async with session.begin():
                conv = await session.get(Conversation, self.session_id) or Conversation(
                    session_id=self.session_id,
                    history="[]"
                )
                
                history = conv.get_history()
                # Handle AgentResponse objects
                if hasattr(content, 'response'):
                    serialized = {
                        "role": role,
                        "content": content.response,
                        "metadata": {
                            "confidence": content.confidence,
                            "action": content.action,
                            "emotion": content.emotion
                        },
                        "timestamp": str(datetime.now())
                    }
                else:
                    serialized = {
                        "role": role,
                        "content": str(content),
                        "timestamp": str(datetime.now())
                    }
                history.append(serialized)
                
                conv.history = json.dumps(history)
                conv.last_updated = datetime.utcnow()
                conv.size_kb = f"{len(conv.history) / 1024:.2f}"
                
                session.add(conv)
                await self._prune_sessions(session)
            conv.size_kb = f"{len(conv.history) / 1024:.2f}"
            
            session.add(conv)
            await session.commit()
            await self._prune_sessions(session)