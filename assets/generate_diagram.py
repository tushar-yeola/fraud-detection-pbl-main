import base64
import urllib.request
import json
import os

mermaid_code = """
graph TD
    classDef purpleBox fill:#8a7df0,stroke:#333,stroke-width:2px,color:#000,font-weight:bold;
    classDef greyBox fill:#f0f0f0,stroke:#333,stroke-width:2px,color:#000,font-weight:bold;
    classDef yellowBox fill:#ffe066,stroke:#333,stroke-width:2px,color:#000,font-weight:bold;
    classDef orangeOval fill:#fcb84a,stroke:#333,stroke-width:2px,color:#000,font-weight:bold,shape:ellipse;
    classDef greenBox fill:#a0dfad,stroke:#333,stroke-width:2px,color:#000,font-weight:bold;
    classDef whiteBox fill:#ffffff,stroke:#333,stroke-width:2px,color:#000,font-weight:bold;
    classDef redBox fill:#ed2939,stroke:#333,stroke-width:2px,color:#fff,font-weight:bold;
    classDef pinkBox fill:#f9a9a3,stroke:#333,stroke-width:2px,color:#000,font-weight:bold;
    
    SysConfig["System Configuration"]:::purpleBox
    ReqGen(["Prediction\nRequests"]):::orangeOval
    
    subgraph FlowSubgraph [Preprocessing Flow]
        Rules["Model Parameters &\nThresholds"]:::greyBox
        Formats["Data Normalization\nRules"]:::greyBox
    end
    
    DB["Transactions Database\n(Structured Data SQLite)"]:::yellowBox
    
    subgraph ModelSubgraph [Fraud Detection Models]
        ML["Random Forest Model\n(High Accuracy)"]:::whiteBox
        AI["Risk Evaluation Engine\n(FastAPI / Python)"]:::redBox
    end
    
    AlertGen["Alert Generation &\nStructuring"]:::pinkBox
    
    UserInputs["User Inputs / Uploads\n(CSV / API)"]:::greenBox
    Validation["Input Validation Module\n(Pydantic)"]:::yellowBox
    PromptEngine["Feature Engineering\nEngine"]:::yellowBox
    FinalOutput["Final Dashboard Display\n(Alerts / Graphs)"]:::greenBox
    
    %% Relationships simulating the provided diagram
    SysConfig -->|Transaction\nProcessing\nFlow| FlowSubgraph
    SysConfig --> DB
    SysConfig --> ReqGen
    
    ReqGen -.-> DB
    FlowSubgraph --> DB
    
    UserInputs --> Validation
    Validation -->|Extracts clean data for features| PromptEngine
    
    PromptEngine --> ML
    PromptEngine -.-> AI
    
    DB --> ModelSubgraph
    ML --> AI
    
    AI --> AlertGen
    AlertGen -->|Organizes content into\ndashboard sections| FinalOutput
    
    style FlowSubgraph fill:#f9f9f9,stroke:#666,stroke-width:2px,stroke-dasharray: 5 5;
    style ModelSubgraph fill:#f9f9f9,stroke:#666,stroke-width:2px,stroke-dasharray: 5 5;
"""

# Use kroki or mermaid.ink
# Some texts in arrows are styled like the original diagram.

state = {
  "code": mermaid_code.strip(),
  "mermaid": "{\n  \"theme\": \"default\"\n}",
  "autoSync": True,
  "updateDiagram": True
}
json_string = json.dumps(state)
b64_string = base64.urlsafe_b64encode(json_string.encode('utf-8')).decode('utf-8')
url = f'https://mermaid.ink/img/{b64_string}?type=png'

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        with open('c:/webdev/fraud-detection/fraud-detection/assets/architecture_diagram.png', 'wb') as f:
            f.write(response.read())
    print('Architecture diagram saved successfully to assets/architecture_diagram.png')
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.reason}")
    print(e.read())
