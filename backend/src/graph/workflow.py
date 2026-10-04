"""
Workflow Definition for the Brand Guardian AI.

This module defines the Directed Acyclic Graph (DAG) that orchestrates the
video compliance audit process. It connects the nodes (functional units)
using the StateGraph primitive from LangGraph.

Architecture:
    [START] -> [index_video_node] -> [audit_content_node] -> [END]
"""


from langgraph.graph import State_graph, START,END
from backend.src.graph.states import VideoAuditState
from backend.src.graph.states import (index_video_node, audit_content_node)


def create_graph():
    """"
    Constructs and compile the langGraph workflow
    Returns:
        Complied Graph: Runnable Graph object for execution
    """
    workflow = State_graph(VideoAuditState)
    # ADD THE NODES
    workflow.add_node("indexer", "index_video_node")
    workflow.add_node("auditor", "audit_content_node")
    # Define the entry point
    workflow.set_entry_point("indexer")
    # Define the edges
    workflow.add_edge("indexer", "auditor")
    workflow.add_edge("auditor", "END")

    # Compile the graph
    app = workflow.compile()

    return app

# Expose the runnable app for import by the Api or Cli
app = create_graph()