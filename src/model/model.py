from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from embedding.vector_db_search import search_vector_db
from embedding.vector_store_factory import VectorStoreFactory
from embedding.embedding_factory import EmbeddingFactory
from utils import get_logger
from config import Config
from model.llm_factory import LLMFactory
from model.prompt import *
import uuid

logger = get_logger()



def build_context_prompt(docs):

    blocks = []
    for idx, doc in enumerate(docs, start=1):
        meta = doc.metadata or {}
        block = (
            f"### Doc {idx}\n"
            f"Title : {meta.get('title', 'Untitled')}\n"
            f"URL   : {meta.get('url', 'N/A')}\n"
            f"{doc.page_content.strip()}"
        )
        blocks.append(block)

    serialized = "\n\n---\n\n".join(blocks)
    return serialized



class PipelineFactory:
    @staticmethod
    def build_pipeline(config):
        logger.info("Initializing embedding model...")
        embedding = EmbeddingFactory.get_embeddings_from_config(config=config)

        logger.info("Loading LLM...")
        llm = LLMFactory.get_llm_from_config(config=config)

        logger.info("Setting up vector store...")
        vector_store = VectorStoreFactory.get_vector_store_from_config(
            embedding, config=config
        )


        logger.info("Building RAG pipeline...")

        # Build RAG graph (retriever + LLM pipeline)
        graph = PipelineFactory.build_RAG_pipeline(llm, vector_store, config=config)

        logger.info("Pipeline successfully built.")

        return graph
    
    @staticmethod
    def build_RAG_pipeline(llm, vector_store, config=None):

        if config is None:
            config = Config.default_config()

        @tool(response_format="content_and_artifact")
        def retrieve(query: str):
            """Retrieve relevant information from the University of Connecticut knowledge base based on the user's query and provide context to help answer the question effectively."""
            
            logger.debug(f"Received query: {query}")
            
            try:
                retrieved_docs = search_vector_db(query, vector_store, k=config.num_documents, search_type=config.sim_search_type, keep_with_score=config.keep_with_score)
                logger.debug(f"Found {len(retrieved_docs)} documents for query: {query}")
            except Exception as e:
                logger.error(f"Error occurred while retrieving documents for query: {query} - {str(e)}")
                retrieved_docs = []
            
            serialized = build_context_prompt(retrieved_docs)

            logger.debug(f"Serialized retrieval result: {serialized}...") 
            return serialized, retrieved_docs

        def query_or_respond(state: MessagesState):
            """Generate tool call for retrieval or respond."""       
        
            logger.debug(f"Starting query_or_respond with state: {state}")

            llm_with_tools = llm.bind_tools([retrieve])
            prompt = [SystemMessage(SYSTEM_TOOL_MSG)] + state['messages']
            logger.debug(f"Input prompt for LLM: {prompt[-1]}")
            
            try:
                response = llm_with_tools.invoke(prompt)
                logger.debug(f"query_or_respond Node Received response from LLM: {response}")
            except Exception as e:
                logger.error(f"Error occurred while invoking LLM: {str(e)}")
                response = "Error occurred during processing."
            
            return {"messages": [response]}


        def generate(state: MessagesState):
            """Generate answer."""
            logger.debug(f"Generating response with state: {state}")

            # Get generated ToolMessages
            recent_tool_messages = []
            for message in reversed(state["messages"]):
                if message.type == "tool":
                    recent_tool_messages.append(message)
                else:
                    break
            tool_messages = recent_tool_messages[::-1]
            logger.debug(f"Found {len(tool_messages)} recent tool messages.")
            recent_tool_messages = []        

            # Format into prompt
            docs_content = "\n\n".join(doc.content for doc in tool_messages)
            system_message_content = SYSTEM_MSG.format(CONTEXT_BLOCK=docs_content)

            logger.debug(f"System message content: {system_message_content}...")

            conversation_messages = [
                message
                for message in state["messages"]
                if message.type in ("human", "system")
                or (message.type == "ai" and not message.tool_calls)
            ]
            prompt = [SystemMessage(system_message_content)] + conversation_messages
            logger.debug(f"Formatted prompt for LLM: {prompt}")

            # Run LLM
            try:
                response = llm.invoke(prompt)
                logger.debug(f"Received response from LLM: {response}")
            except Exception as e:
                logger.error(f"Error occurred while invoking LLM for final response: {str(e)}")
                response = "Error occurred during processing."

            return {"messages": [response]}

        graph_builder = StateGraph(MessagesState)
        tools = ToolNode([retrieve])
        graph_builder.add_node(query_or_respond)
        graph_builder.add_node(tools)
        graph_builder.add_node(generate)

        graph_builder.set_entry_point("query_or_respond")
        graph_builder.add_conditional_edges(
            "query_or_respond",
            tools_condition,
            {END: END, "tools": "tools"},
        )
        graph_builder.add_edge("tools", "generate")
        graph_builder.add_edge("generate", END)
        graph = graph_builder.compile()

        checkpointer = None
        if config.multi_turn:
            checkpointer = MemorySaver()
        
        graph = graph_builder.compile(checkpointer=checkpointer)
        
        logger.debug("RAG pipeline built successfully.")
        return graph



def run_terminal_chatbot(config=None):   

    if config is None:
        config = Config.default_config()   

    pipeline = PipelineFactory.build_pipeline(config=config)

    thread_config = {"configurable": {"thread_id": uuid.uuid4()}}
    while True:
        input_message = input("Enter Query: - ")
        if input_message == "exit":
            break
        
        for step in pipeline.stream(
                {"messages": [{ "role": "user", "content": input_message }]},
                stream_mode="values",
                config=thread_config,
                ):
            step["messages"][-1].pretty_print()
