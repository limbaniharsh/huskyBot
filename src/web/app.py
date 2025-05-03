import streamlit as st
import uuid
from config import Config
from model.model import PipelineFactory
from utils import get_logger

logger = get_logger()


@st.cache_resource
def load_model():
    config = Config.default_config()
    RAGpipeline = PipelineFactory.build_pipeline(config=config)
    return RAGpipeline


st.html(
    """
<style>
    .st-emotion-cache-1c7y2kd  {
        flex-direction: row-reverse;
        text-align: right;       
    }
</style>
"""
)

role_img = {"user":":material/chevron_left:", "assistant":"🐾"}

RAGpipeline = load_model()
if 'session_token' not in st.session_state:
    st.session_state.session_token = str(uuid.uuid4())

st.write(f"Your unique session token is: {st.session_state.session_token}")
thread_config = {"configurable": {"thread_id": st.session_state.session_token}}

def answer(prompt):
    for step in RAGpipeline.stream(
                {"messages": [{ "role": "user", "content": prompt }]},
                stream_mode="values",
                config=thread_config,
                ):
        message = step["messages"][-1]
        if message.type == "ai" and not message.tool_calls:
            return message.content




st.title("Husky Bot")




if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=role_img[message["role"]]):
        st.markdown(message["content"])

if prompt := st.chat_input("Say something"):
    
    with st.chat_message("user", avatar=role_img["user"]):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant", avatar=role_img["assistant"]):
        response = answer(prompt)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})