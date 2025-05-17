#!/usr/bin/env python3
import asyncio
from typing import Optional
from pathlib import Path
import uuid
from agents.general_agent import GeneralAgent

class ConversationCLI:
    def __init__(self, persona_dir: str = "personas"):
        self.persona_dir = Path(persona_dir)
        self.session_id = str(uuid.uuid4())
        self.agent1: Optional[GeneralAgent] = None
        self.agent2: Optional[GeneralAgent] = None
    
    async def initialize_agents(self, scenario: str, role1: str, role2: str):
        """Initialize both agents with their roles"""
        # Initialize agents with default memory
        self.agent1 = GeneralAgent(
            persona_dir=self.persona_dir,
            session_id=self.session_id
        )
        self.agent2 = GeneralAgent(
            persona_dir=self.persona_dir,
            session_id=self.session_id
        )
        
        await asyncio.gather(
            self.agent1.assign_role(scenario, role1),
            self.agent2.assign_role(scenario, role2)
        )
        
        print(f"\n🚀 New session started (ID: {self.session_id[:8]})")
        print(f"Scenario: {scenario.replace('_', ' ').title()}")
        print(f"Agents: {role1.replace('_', ' ')} ↔ {role2.replace('_', ' ')}\n")
    
    async def start_conversation(self, first_message: str):
        """Run the conversation loop"""
        current_message = first_message
        current_speaker = self.agent1
        other_speaker = self.agent2
        
        while True:
            # Get response
            response = await current_speaker.execute(
                current_message,
                sender_role=other_speaker.current_role.role_type
            )
            
            # Display response
            self._print_response(
                speaker=current_speaker.current_role.role_type,
                response=response.response,
                confidence=response.confidence,
                emotion=response.emotion
            )
            
            # Switch speakers
            current_message = response.response
            current_speaker, other_speaker = other_speaker, current_speaker
            
            # Check for exit condition
            if self._should_exit(current_message):
                print("\n💬 Conversation ended by user")
                break
    
    def _print_response(self, speaker: str, response: str, confidence: float, emotion: str):
        """Format and print agent responses"""
        emotion_icons = {
            "happy": "😊",
            "angry": "😠",
            "frustrated": "😤",
            "neutral": "😐"
        }
        print(f"\n{speaker.upper()} {emotion_icons.get(emotion, '')}")
        print(f"{'=' * (len(speaker)+2)}")
        print(response)
        print(f"\n(Confidence: {confidence:.0%} | Emotion: {emotion})")
    
    def _should_exit(self, message: str) -> bool:
        """Check for exit commands in user input"""
        return message.lower() in ("exit", "quit", "end", "stop")
    
    async def run(self):
        """Main CLI loop"""
        print("🤖 Multi-Agent Conversation Simulator\n")
        
        # Get scenario configuration
        scenario = input("Enter scenario (e.g., 'late_delivery'): ").strip()
        role1 = input("Enter first agent role (e.g., 'angry_customer'): ").strip()
        role2 = input("Enter second agent role (e.g., 'support_agent'): ").strip()
        starter_msg = input("Enter first message: ").strip()
        
        # Initialize agents
        await self.initialize_agents(scenario, role1, role2)
        
        # Start conversation
        await self.start_conversation(starter_msg)

if __name__ == "__main__":
    try:
        asyncio.run(ConversationCLI().run())
    except KeyboardInterrupt:
        print("\n🛑 Session terminated by user")