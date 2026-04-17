# 🌦️ Weather Agent with Azure AI Foundry

This project demonstrates how to build an **AI-powered weather agent** using **Azure AI Foundry (Agents + Projects SDK)** that:

* Fetches real-time weather data
* Generates a structured **CSV dataset**
* Creates a clean **PNG weather report**
* Optionally uploads data to **Azure Foundry Datasets**
* Handles tool-calling with an AI agent

---

## 🚀 Features

* ✅ AI Agent using Azure AI Foundry
* ✅ Function calling (`get_weather`)
* ✅ Automatic CSV generation
* ✅ Beautiful PNG weather report (table format)
* ✅ Dataset upload to Azure Foundry
* ✅ Extensible and production-ready structure

---

## 🧠 Architecture

```text
User Query
   ↓
Azure AI Agent
   ↓
Function Call (get_weather)
   ↓
Weather API
   ↓
Processing Layer
   ├── Save CSV
   ├── Generate PNG
   └── Upload Dataset (optional)
   ↓
Return Response to User
```

---

## 📂 Project Structure

```text
.
├── outputs/                  # Generated CSV & PNG files
├── createAgent_realweather.py
├── README.md
└── requirements.txt
```

---

## ⚙️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/weather-agent.git
cd weather-agent
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Set environment variables

#### Windows (PowerShell)

```powershell
setx PROJECT_ENDPOINT "https://<your-resource>.services.ai.azure.com/api/projects/<your-project>"
```

#### Mac/Linux

```bash
export PROJECT_ENDPOINT="https://<your-resource>.services.ai.azure.com/api/projects/<your-project>"
```

---

### 4. Azure Authentication

Make sure you're logged in:

```bash
az login
```

---

## ▶️ Running the Project

```bash
python createAgent_realweather.py
```

---

## 📊 Output

After running, the project generates:

### 📄 CSV File

Stored in `outputs/`

```text
weather_brisbane_YYYYMMDD_HHMMSS.csv
```

Contains:

* location
* region
* country
* condition
* temperature
* humidity
* wind speed
* timestamps

---

### 🖼️ PNG Weather Report

```text
weather_brisbane_YYYYMMDD_HHMMSS.png
```

Includes:

* Clean table layout
* Weather metrics
* Summary section

---

## ☁️ Azure Integration

### Dataset Upload

Weather data is uploaded to Azure Foundry using:

```python
project_client.datasets.upload_file(...)
```

Each run creates a **new dataset version**.

---

### Agent File Handling

* Generated images can be attached via `file_id`
* Download using:

```python
agent_client.files.get_content(file_id)
```

---

## 🧩 Example Weather Response

```json
{
  "city": "Brisbane",
  "country": "Australia",
  "temperature_c": 20.1,
  "condition": "Clear",
  "humidity": 83
}
```

---

## 🛠️ Tech Stack

* Python 🐍
* Azure AI Foundry (Agents + Projects SDK)
* Pandas
* Pillow (PIL)
* Azure Identity

---

## 🔥 Future Improvements

* 📊 Dashboard (Streamlit / Power BI)
* 🌍 Multi-city comparison
* 📈 Weather trend analysis
* 🤖 Scheduled data collection
* ☁️ Storage in Azure Blob / DB

---

## 🤝 Contributing

Feel free to fork this repo and improve it!

---

## 📜 License

This project is open-source and available under the MIT License.

---

## 🙌 Acknowledgements

Built using Azure AI Foundry and modern AI agent patterns.
