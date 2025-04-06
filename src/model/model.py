from langgraph.graph import START, END, StateGraph, MessagesState
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_core.documents import Document
from typing_extensions import List, TypedDict
from langchain_core.prompts import PromptTemplate
from langgraph.prebuilt import ToolNode, tools_condition
from embedding.vector_db_search import search_vector_db


def build_RAG_pipeline(llm, vector_store):
    @tool(response_format="content_and_artifact")
    def retrieve(query: str):
        """Retrieve relevant information from the University of Connecticut knowledge base based on the user's query and provide context to help answer the question effectively."""
        retrieved_docs = search_vector_db(query, vector_store)
        serialized = "\n\n".join(
            (f"Source: {doc[0].metadata}\n" f"Content: {doc[0].page_content}")
            for doc in retrieved_docs
        )
        return serialized, retrieved_docs

    def query_or_respond(state: MessagesState):
        """Generate tool call for retrieval or respond."""
        llm_with_tools = llm.bind_tools([retrieve])
        response = llm_with_tools.invoke(state["messages"])
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
            """"You are an assistant designed to answer questions about the University of Connecticut (UConn) knowledge base. 
            Use the provided context to respond to each question. If you are unsure of the answer, simply acknowledge that you don't know. For questions that ask 'How,
            ' please provide a clear, step-by-step explanation."""
            "\n\n"
            f"{docs_content}"
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

