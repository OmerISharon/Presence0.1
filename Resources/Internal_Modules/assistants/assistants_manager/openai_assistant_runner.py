# openai_assistant_runner.py

import json
import sys
from openai import OpenAI

# ------------------------------------------------------------------
# Local module path
# ------------------------------------------------------------------
MODULES_DIR = fr"D:\2025\Projects\Presence\Presence0.1\Resources\Internal_Modules"
sys.path.insert(0, MODULES_DIR)
from utilities.request_chatgpt.request_chatgpt import get_api_key
from assistants.assistants_manager.assistants_manager import OpenAIAssistantManager

class OpenAIAssistantRunner:
    def __init__(self, assistant_name: str, tool_callbacks: dict):
        """
        assistant_name: Name of your OpenAI assistant (from dashboard)
        tool_callbacks: Dict of function name → Python function to call
        """
        self.client = OpenAI(api_key=get_api_key())
        self.assistant_id = OpenAIAssistantManager().get_agent_id(assistant_name)
        self.tool_callbacks = tool_callbacks

    def run(self, prompt: str) -> str:
        """
        Run a new thread with the assistant and optional tool callbacks.
        """
        thread = self.client.beta.threads.create()

        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt
        )

        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant_id
        )

        while True:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

            if run.status == "requires_action":
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                outputs = []

                for call in tool_calls:
                    fn_name = call.function.name
                    if fn_name not in self.tool_callbacks:
                        raise ValueError(f"No callback found for tool: {fn_name}")

                    args = json.loads(call.function.arguments)
                    result = self.tool_callbacks[fn_name](**args)
                    outputs.append({
                        "tool_call_id": call.id,
                        "output": result
                    })

                self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=outputs
                )

            elif run.status == "completed":
                break

            elif run.status in ("failed", "cancelled", "expired"):
                raise RuntimeError(f"Run ended: {run.status}")

        messages = self.client.beta.threads.messages.list(thread_id=thread.id)
        for message in reversed(messages.data):
            if message.role == "assistant":
                return message.content[0].text.value

        return "[ERROR] No assistant reply"
