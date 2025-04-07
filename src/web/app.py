import streamlit as st
import time
import uuid
from utils import get_logger

logger = get_logger()


@st.cache_resource
def load_model():
    model = pipeline("sentiment-analysis")
    st.success("Loaded NLP model from Hugging Face!")  # 👈 Show a success message
    return model


st.html(
    """
<style>
    .st-emotion-cache-janbn0  {
        flex-direction: row-reverse;
        text-align: right;       
    }
</style>
"""
)

role_img = {"user":":material/chevron_left:", "assistant":"🐾"}

if 'session_token' not in st.session_state:
    st.session_state.session_token = str(uuid.uuid4())

#st.write(f"Your unique session token is: {st.session_state.session_token}")
st.title("Husky Bot")

def chat_stream(prompt):
    response = f'You said, "{prompt}" ...interesting.'
    for char in response:
        yield char
        time.sleep(0.02)


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
        response = st.write_stream(chat_stream(prompt))

    st.session_state.messages.append({"role": "assistant", "content": response})