"""
openai_agent_manager.py
~~~~~~~~~~~~~~~~~~~~~~~
Manages persistent OpenAI Assistant agents by name + ID.

Dependencies:
pip install openai
"""

from typing import Optional
from openai import OpenAI


# ================== ⚙️ AGENT MANAGER ============================

class OpenAIAssistantManager:
    def __init__(self, client: Optional[OpenAI] = None):
        self.client = client or OpenAI()

    def assign_agent(
        self,
        name: str,
        instructions: str,
        model: str = "gpt-3.5-turbo",
        tools: Optional[list] = None,
    ) -> str:
        """
        Create a new agent if name does not exist, or return existing agent's ID.
        """
        for assistant in self.client.beta.assistants.list().data:
            if assistant.name == name:
                print(f"[ℹ️] Assistant '{name}' already exists → ID: {assistant.id}")
                return assistant.id

        assistant = self.client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=model,
            tools=tools or [],
        )
        print(f"[✅] Created assistant '{name}' → ID: {assistant.id}")
        return assistant.id

    def update_agent_instructions(self, name: str, new_instructions: str, tools: Optional[list] = None):
        """
        Updates instructions (and optionally tools) of an existing agent by name.
        """
        agent_id = self.get_agent_id(name)
        update_data = {"instructions": new_instructions}
        if tools is not None:
            update_data["tools"] = tools

        self.client.beta.assistants.update(
            assistant_id=agent_id,
            **update_data
        )
        print(f"[✅] Updated assistant '{name}' (ID: {agent_id})")

    def update_agent_tools(self, name: str, tools: list):
        """
        Updates only the tools of an existing agent by name.
        """
        agent_id = self.get_agent_id(name)
        self.client.beta.assistants.update(
            assistant_id=agent_id,
            tools=tools
        )
        print(f"[✅] Updated tools for assistant '{name}' (ID: {agent_id})")

    def delete_agent(self, assistant_id: str):
        """
        Deletes an assistant by ID.
        """
        self.client.beta.assistants.delete(assistant_id=assistant_id)
        print(f"[✅] Assistant {assistant_id} deleted.")

    def get_agent_id(self, name: str) -> str:
        """
        Returns agent ID by assistant name.
        """
        for assistant in self.client.beta.assistants.list().data:
            if assistant.name == name:
                return assistant.id
        raise ValueError(f"Agent '{name}' not found in your OpenAI account.")

    def list_all_agents(self) -> list[str]:
        """
        Dynamically fetch all assistants from OpenAI + show name + ID.
        """
        agents = []
        try:
            response = self.client.beta.assistants.list()
            for assistant in response.data:
                agents.append(f"{assistant.name} ({assistant.id})")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch agents from OpenAI: {e}")
        return agents

    def get_agent_details(self, assistant_id: str) -> dict:
        """
        Retrieves the assistant's instructions, model, and tools by its ID.
        """
        try:
            assistant = self.client.beta.assistants.retrieve(assistant_id)
            return {
                "name": assistant.name,
                "model": assistant.model,
                "instructions": assistant.instructions,
                "tools": assistant.tools,
            }
        except Exception as e:
            raise ValueError(f"Could not fetch details for assistant {assistant_id}: {e}")