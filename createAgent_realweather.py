import os
import json
import time
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import MessageRole
from dotenv import load_dotenv
from user_functions_for_api_weather import (
    weather_tool_definition,
    fetch_weather
)
import logging
from azure.identity import AzureCliCredential
import os
import io
import json
import time
import uuid
import pandas as pd

from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
# logging.basicConfig(level=logging.DEBUG) 
# logging.getLogger("azure.identity").setLevel(logging.DEBUG)
from azure.ai.projects import AIProjectClient
credential = AzureCliCredential()
PROJECT_ENDPOINT = "https://try-to-solve.services.ai.azure.com/api/projects/financial-solve"
# Example: https://<your-resource>.services.ai.azure.com/api/projects/<your-project-name>

project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=credential,
)


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
    instructions="""
You are a weather reporting assistant.

When the user asks about weather:
1. Use the `get_weather` tool to fetch the latest weather data.
2. Provide a short and clear weather summary in text.
3. Generate a professional PNG weather report for download.

The PNG must include:
- Title: Weather Report
- Location
- Report date/time
- A well-formatted table of weather details

Include these fields if available:
- Condition
- Temperature
- Feels like
- Humidity
- Wind speed
- Wind direction
- Pressure
- Visibility
- Sunrise
- Sunset

Design rules:
- White background
- Readable font
- Clean table borders
- Proper spacing and alignment
- Professional appearance

File rules:
- Always generate the PNG after fetching weather
- Save it with the filename: weather_report_<location>.png
- If some data is missing, still create the PNG using available data
- Never make up missing weather values
- If tool execution fails, explain the error clearly instead of guessing
""",
    tools=weather_tool_definition
)
print(f"Created agent: {agent.id}")


function_registry = {
    "get_weather": fetch_weather
}

# -------------------------------------------------------
# Create thread
# -------------------------------------------------------
thread = agent_client.threads.create()
print(f"Created thread: {thread.id}")
# -------------------------------------------------------
# Function registry for manual handling
# -------------------------------------------------------
msg = agent_client.messages.create(
    thread_id=thread.id,
    role=MessageRole.USER,
    content="What is the weather in Brisbane?Please fetch the weather data, summarize it, and generate a clean downloadable PNG weather report with a nice table."
)

run = agent_client.runs.create(
    thread_id=thread.id,
    agent_id=agent.id
)


import os
import json
import time
import pandas as pd

from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont


def normalize_weather_result(result: dict) -> dict:
    return {
        "location": result.get("location") or result.get("city") or result.get("name") or "Unknown",
        "region": result.get("region", ""),
        "country": result.get("country", ""),
        "condition": result.get("condition", ""),
        "temperature_c": result.get("temperature_c"),
        "feels_like_c": result.get("feels_like_c"),
        "humidity": result.get("humidity"),
        "wind_kph": result.get("wind_kph"),
        "local_time": result.get("local_time", ""),
        "report_time_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }


def save_weather_csv_and_png(weather_result: dict, output_dir: str = "outputs") -> dict:
    os.makedirs(output_dir, exist_ok=True)

    data = normalize_weather_result(weather_result)
    safe_location = data["location"].lower().replace(" ", "_").replace("/", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_path = os.path.join(output_dir, f"weather_{safe_location}_{timestamp}.csv")
    png_path = os.path.join(output_dir, f"weather_{safe_location}_{timestamp}.png")

    # Save full CSV
    df = pd.DataFrame([data])
    df.to_csv(csv_path, index=False)

    # PNG rows
    rows = [
        ("Location", data["location"]),
        ("Region", data["region"] or "N/A"),
        ("Country", data["country"] or "N/A"),
        ("Condition", data["condition"] or "N/A"),
        ("Temperature (C)", data["temperature_c"] if data["temperature_c"] is not None else "N/A"),
        ("Feels Like (C)", data["feels_like_c"] if data["feels_like_c"] is not None else "N/A"),
        ("Humidity (%)", data["humidity"] if data["humidity"] is not None else "N/A"),
        ("Wind (kph)", data["wind_kph"] if data["wind_kph"] is not None else "N/A"),
        ("Local Time", data["local_time"] or "N/A"),
        ("Report Time (UTC)", data["report_time_utc"]),
    ]

    width = 1100
    row_height = 50
    margin = 40
    header_height = 80
    footer_height = 80
    table_height = row_height * (len(rows) + 1)
    height = margin * 2 + header_height + table_height + footer_height

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    try:
        title_font = ImageFont.truetype("arial.ttf", 30)
        header_font = ImageFont.truetype("arial.ttf", 22)
        cell_font = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        cell_font = ImageFont.load_default()

    y = margin
    draw.text((margin, y), "Weather Report", fill="black", font=title_font)
    y += header_height

    x0 = margin
    x1 = width - margin
    split = x0 + 320

    # header
    draw.rectangle([x0, y, x1, y + row_height], outline="black", width=2)
    draw.line([split, y, split, y + row_height], fill="black", width=2)
    draw.text((x0 + 10, y + 12), "Field", fill="black", font=header_font)
    draw.text((split + 10, y + 12), "Value", fill="black", font=header_font)

    current_y = y + row_height
    for field, value in rows:
        draw.rectangle([x0, current_y, x1, current_y + row_height], outline="black", width=1)
        draw.line([split, current_y, split, current_y + row_height], fill="black", width=1)
        draw.text((x0 + 10, current_y + 12), str(field), fill="black", font=cell_font)
        draw.text((split + 10, current_y + 12), str(value), fill="black", font=cell_font)
        current_y += row_height

    image.save(png_path, format="PNG")

    return {
        "data": data,
        "csv_path": csv_path,
        "png_path": png_path,
    }

def upload_csv_to_foundry_dataset(project_client, csv_path: str, dataset_name: str):
    version = datetime.now().strftime("%Y%m%d%H%M%S")
    dataset = project_client.datasets.upload_file(
        name=dataset_name,
        version=version,
        file_path=csv_path,
    )
    return dataset

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

            print("Requested function:", function_name)
            print("Function args:", function_args)

            if function_name in function_registry:
                try:
                    result = function_registry[function_name](**function_args)
                    print("Function result:", result)

                    # Save local CSV + PNG from the weather result
                    saved = save_weather_csv_and_png(result, output_dir="outputs")
                    print("CSV saved to:", saved["csv_path"])
                    print("PNG saved to:", saved["png_path"])

                    # Upload CSV into Foundry Dataset
                    dataset_name = f'weather-data-{saved["data"]["location"].lower().replace(" ", "-")}'
                    dataset = upload_csv_to_foundry_dataset(
                        project_client=project_client,
                        csv_path=saved["csv_path"],
                        dataset_name=dataset_name
                    )
                    print("Dataset uploaded:", dataset)

                    # Return useful metadata to the agent
                    enriched_result = {
                        **result,
                        "_artifacts": {
                            "local_csv_path": saved["csv_path"],
                            "local_png_path": saved["png_path"],
                            "dataset_name": dataset_name,
                            "dataset_version": getattr(dataset, "version", None),
                        }
                    }

                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(enriched_result, default=str)
                    })

                except Exception as e:
                    print("Function exception:", repr(e))
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps({"error": str(e)})
                    })
                except Exception as e:
                    print("Function exception:", repr(e))
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps({"error": str(e)})
                    })
            else:
                print("Function not found in registry:", function_name)
        print("Submitting tool outputs:", tool_outputs)
        run = agent_client.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
    else:
        time.sleep(1)
        run = agent_client.runs.get(
            thread_id=thread.id,
            run_id=run.id
        )

messages = agent_client.messages.list(
    thread_id=thread.id,
    run_id=run.id,
    order="asc"
)

for m in messages:
    if m.role == "assistant":
        for c in m.content:
            if c.type == "text":
                print(c.text.value)