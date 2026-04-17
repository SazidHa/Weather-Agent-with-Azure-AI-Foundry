import os
import json
import time
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import MessageRole
from dotenv import load_dotenv
from user_functions import (
    weather_tool_definition,
    fetch_weather
)
import logging
from azure.identity import AzureCliCredential

# logging.basicConfig(level=logging.DEBUG) 
# logging.getLogger("azure.identity").setLevel(logging.DEBUG)

credential = AzureCliCredential()
# -------------------------------------------------------
# Load environment
# -------------------------------------------------------
load_dotenv()
# -------------------------------------------------------
# Environment
# -------------------------------------------------------
AGENT_PROJECT_ENDPOINT = os.getenv(
    "AGENT_PROJECT_ENDPOINT",
    "https://try-to-solve.services.ai.azure.com/api/projects/financial-solve"
)

# -------------------------------------------------------
# Client
# -------------------------------------------------------
agent_client = AgentsClient(
    endpoint=AGENT_PROJECT_ENDPOINT,
    credential=credential
)

# -------------------------------------------------------
# Create agent
# -------------------------------------------------------
agent = agent_client.create_agent(
    model="gpt-4o-mini",
    name="weather-agent-sazid",
    instructions="You are a weather bot. Use fetch_weather to answer weather questions.",
    tools=[{"type": "function", "function": weather_tool_definition}]
)
print(f"Created agent: {agent.id}")

# -------------------------------------------------------
# Function registry for manual handling
# -------------------------------------------------------
function_registry = {
    "fetch_weather": fetch_weather
}

# -------------------------------------------------------
# Create thread
# -------------------------------------------------------
thread = agent_client.threads.create()
print(f"Created thread: {thread.id}")

# -------------------------------------------------------
# Create user message
# -------------------------------------------------------
msg = agent_client.messages.create(
    thread_id=thread.id,
    role=MessageRole.USER,
    content="Hello, what's the weather in Melbourne?"
)
print(f"Created message: {msg.id}")

# -------------------------------------------------------
# Run agent with manual function call handling
# -------------------------------------------------------
run = agent_client.runs.create(
    thread_id=thread.id,
    agent_id=agent.id
)

# Poll the run and handle function calls manually
max_iterations = 30
iteration = 0

while run.status in ["queued", "in_progress", "requires_action"] and iteration < max_iterations:
    iteration += 1
    
    if run.status == "requires_action":
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"Calling function: {function_name} with args: {function_args}")
            
            # Execute the function
            if function_name in function_registry:
                function_result = function_registry[function_name](**function_args)
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": function_result
                })
        
        # Submit tool outputs
        run = agent_client.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
    else:
        # Wait a bit before polling again
        time.sleep(1)
        run = agent_client.runs.get(  # Changed from retrieve to get
            thread_id=thread.id,
            run_id=run.id
        )

print(f"Run status: {run.status}")

# -------------------------------------------------------
# Display output
# -------------------------------------------------------
messages = agent_client.messages.list(thread_id=thread.id,order="asc")
print("\n===== AGENT OUTPUT =====\n")
for m in messages:
    for c in m.get("content", []):
        if c.get("type") == "text":
            print(c["text"]["value"])

# -------------------------------------------------------
# Delete agent
# -------------------------------------------------------
# agent_client.delete_agent(agent.id)
# print("Deleted agent.")