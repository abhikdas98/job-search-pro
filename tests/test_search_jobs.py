from app.workflows.graphs import GraphBuilder
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
model = ChatGroq(model="qwen3.6-27b", api_key=api_key)

graph = GraphBuilder(model=model)

initial_state = {
        "user_request": "Find GenAI Engineer jobs in India",
        "user_profile": {
            "target_roles": ["Generative AI Engineer"],
            "locations": ["India"],
        },
        "jobs": [],
        "selected_jobs": [],
        }

result = graph.invoke(initial_state)

print(result["jobs"])