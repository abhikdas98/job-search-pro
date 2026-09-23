from langgraph.graph import StateGraph, START, END
from app.workflows.state import State
from app.workflows.nodes import parse_request_node,job_search_node, job_filter_node, rank_jobs_node, candidate_context_node

class GraphBuilder:
    def __init__(self):
        self.graph_builder = StateGraph(State)

    def basic_job_search_agent(self):
        """
        This is a basic Job Search Agent which takes text input and the resume from the user,
        Then creates a user profile and searches jobs according to the profile match and the
        requested fields
        """
        self.graph_builder.add_node("retrieve_context", candidate_context_node)
        self.graph_builder.add_node("parse_request", parse_request_node)
        self.graph_builder.add_node("search_jobs", job_search_node)
        self.graph_builder.add_node("filter_jobs", job_filter_node)
        self.graph_builder.add_node("rank_jobs", rank_jobs_node)

        self.graph_builder.add_edge(START, "retrieve_context")
        self.graph_builder.add_edge("retrieve_context", "parse_request")
        self.graph_builder.add_edge("parse_request", "search_jobs")
        self.graph_builder.add_edge("search_jobs", "filter_jobs")
        self.graph_builder.add_edge("filter_jobs", "rank_jobs")
        self.graph_builder.add_edge("rank_jobs", END)


        graph = self.graph_builder.compile()

        return graph