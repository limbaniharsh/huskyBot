from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from embedding.vector_db_search import search_vector_db
from utils import get_logger

logger = get_logger()

SYSTEM_TOOL_MSG = """You are an assistant designed to provide answers based on the University of Connecticut (UConn) knowledge base.
                    If a query is related to UConn and requires more context, call the tool with an appropriate query to fetch relevant documents from the knowledge base. 
                    - Ensure the query is specific and clearly related to the subject matter to retrieve the most relevant documents.
                    - If you feel the query could be rewritten to fetch more relevant content, feel free to adjust or rephrase it to better align with the knowledge base.
"""
SYSTEM_MSG = """"You are an assistant designed to answer questions related to the University of Connecticut (UConn) knowledge base. 
                When responding, utilize the provided context to generate accurate answers. If you are uncertain about the answer, acknowledge that you don’t know.
                For questions that inquire "How," provide a detailed, step-by-step explanation. Whenever necessary,
                include metadata with the URL of the original source site to ensure proper attribution."""


def build_RAG_pipeline(llm, vector_store):

    @tool(response_format="content_and_artifact")
    def retrieve(query: str):
        """Retrieve relevant information from the University of Connecticut knowledge base based on the user's query and provide context to help answer the question effectively."""
        retrieved_docs = search_vector_db(query, vector_store)
        logger.debug(f"Found {len(retrieved_docs)} for {query}")
        serialized = "\n\n".join(
            (f"Source: {doc[0].metadata}\n" f"Content: {doc[0].page_content}")
            for doc in retrieved_docs
        )
        return serialized, retrieved_docs

    def query_or_respond(state: MessagesState):
        """Generate tool call for retrieval or respond."""
        llm_with_tools = llm.bind_tools([retrieve])
        prompt = [SystemMessage(SYSTEM_TOOL_MSG)] + state['messages']
        logger.debug(f"Input message in query_or_respond node ------ {prompt}")
        response = llm_with_tools.invoke(prompt)
        return {"messages": [response]}

    def generate(state: MessagesState):
        """Generate answer."""
        # Get generated ToolMessages
        recent_tool_messages = []
        for message in reversed(state["messages"]):
            if message.type == "tool":
                recent_tool_messages.append(message)
            else:
                break
        tool_messages = recent_tool_messages[::-1]

        # Format into prompt
        docs_content = "\n\n".join(doc.content for doc in tool_messages)

        system_message_content = (
            SYSTEM_MSG + f"\n\n {docs_content}"
        )
        conversation_messages = [
            message
            for message in state["messages"]
            if message.type in ("human", "system")
               or (message.type == "ai" and not message.tool_calls)
        ]
        prompt = [SystemMessage(system_message_content)] + conversation_messages

        # Run
        response = llm.invoke(prompt)
        return {"messages": [response]}

    graph_builder = StateGraph(MessagesState)
    tools = ToolNode([retrieve])
    graph_builder.add_node(query_or_respond)
    graph_builder.add_node(tools)
    graph_builder.add_node(generate)

    graph_builder.set_entry_point("query_or_respond")
    # graph_builder.add_edge("query_or_respond", "tools")
    graph_builder.add_conditional_edges(
        "query_or_respond",
        tools_condition,
        {END: END, "tools": "tools"},
    )
    graph_builder.add_edge("tools", "generate")
    graph_builder.add_edge("generate", END)
    graph = graph_builder.compile()

    return graph
