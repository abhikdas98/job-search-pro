from langgraph.graph import StateGraph, START, END
from app.workflows.state import State
from app.services.request_parser import RequestParser
from app.workflows.nodes import job_search_node, job_filter_node, rank_jobs_node

class GraphBuilder:
    def __init__(self, model):
        self.llm = model
        self.graph_builder = StateGraph(State)

    def basic_job_search_agent(self):
        """
        This is a basic Job Search Agent which takes text input and the resume from the user,
        Then creates a user profile and searches jobs according to the profile match and the
        requested fields
        """
        self.graph_builder.add_node("parse_request", RequestParser)
        self.graph_builder.add_node("search_jobs", job_search_node)
        self.graph_builder.add_node("filter_jobs", job_filter_node)
        self.graph_builder.add_node("rank_jobs", rank_jobs_node)

        self.graph_builder.add_edge(START, "parse_request")
        self.graph_builder.add_edge("parse_request", "search_jobs")
        self.graph_builder.add_edge("search_jobs", "filter_jobs")
        self.graph_builder.add_edge("filter_jobs", "rank_jobs")
        self.graph_builder.add_edge("rank_jobs", END)


        graph = self.graph_builder.compile()

        return graph

from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
model = ChatGroq(model="qwen3.6-27b", api_key=api_key)
builder = GraphBuilder(model=model)
final_graph = builder.basic_job_search_agent()

initial_state = {
"user_request": "Find GenAI Engineer jobs in India",
"user_profile": {
    "target_roles": ["Generative AI Engineer"],
    "locations": ["India"],
},
"jobs": [],
"selected_jobs": [],
}

result = final_graph.invoke(initial_state)

print(result["jobs"])
