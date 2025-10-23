import streamlit as st
from openai import OpenAI
import os
import dotenv

dotenv.load_dotenv()

with st.sidebar:
    base_url = st.text_input("OpenAI Base URL", value=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY"))
    model = st.text_input("OpenAI Model", value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

client = OpenAI(api_key=api_key, base_url=base_url)

# 聊天历史存储在 session state
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("💬 Chatbot")
st.caption("🚀 A streamlit chatbot powered by OpenAI Responses API")

# 显示历史对话
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 调用 Responses API 进行流式对话
def chat_stream(prompt):
    with client.responses.stream(
        model=model,
        input=prompt,
        previous_response_id=st.session_state.get("response_id", None),
    ) as stream:
        for event in stream:
            if event.type == "response.created":
                st.session_state.response_id = event.response.id
                continue
            if event.type == "response.output_text.delta":
                yield event.delta

# 输入框
if prompt := st.chat_input():
    # 保存用户输入
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 开始生成模型输出
    with st.chat_message("assistant"):
        stream = chat_stream(prompt) 
        response = st.write_stream(stream)

    # 保存模型回复
    st.session_state.messages.append({"role": "assistant", "content": response})