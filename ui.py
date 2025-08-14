import streamlit as st
# 从我们的核心逻辑文件中导入函数
from prompt_enhancer import get_rag_context, refine_prompt_with_llm

# --- 页面配置 ---
st.set_page_config(page_title="RAG Prompt Enhancer", page_icon="🤖", layout="wide")

st.title("🤖 RAG Prompt Enhancer")
st.caption("A tool to enrich your prompts using a local vector database.")

# --- 用户输入 ---
raw_prompt = st.text_area(
    "Enter your raw prompt here:",
    height=150,
    placeholder="e.g., How can I run python functions concurrently for I/O tasks?"
)

if st.button("Enhance Prompt ✨"):
    if not raw_prompt.strip():
        st.warning("Please enter a prompt before enhancing.")
    else:
        final_prompt = raw_prompt
        # 使用 st.status 来显示一个漂亮的、可展开的进度框
        with st.status("Running enhancement process...", expanded=True) as status:
            try:
                # --- 阶段一 ---
                st.write("🔍 [Step 1] Retrieving context from local memory service...")
                rag_context = get_rag_context(raw_prompt)
                
                if rag_context:
                    st.success("✅ Context retrieved successfully.")
                    
                    # --- 阶段二 ---
                    st.write("🧠 [Step 2] Refining the prompt with Orchestrator LLM...")
                    final_prompt = refine_prompt_with_llm(raw_prompt, rag_context)
                    st.success("✅ Prompt refined successfully.")
                    status.update(label="Enhancement complete!", state="complete", expanded=False)
                else:
                    st.info("ℹ️ No relevant context found. Returning the original prompt.")
                    status.update(label="Process finished.", state="complete", expanded=False)

            except ConnectionError as e:
                st.error(f"Connection Error: {e}")
                st.info("Please ensure the backend microservice (`main.py`) is running.")
                status.update(label="Process failed.", state="error")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                status.update(label="Process failed.", state="error")
        
        # --- 显示最终结果 ---
        st.divider()
        st.subheader("🚀 Final Enhanced Prompt")
        st.code(final_prompt, language=None)

# 添加一个侧边栏，用于添加新文档到数据库
with st.sidebar:
    st.header("📚 Add to Knowledge Base")
    st.caption("Add new documents to your local vector DB.")
    
    new_doc_text = st.text_area("Document Text", height=100)
    
    if st.button("Add Document"):
        if new_doc_text.strip():
            try:
                # 直接调用后端的 /add_document 接口
                import requests
                from prompt_enhancer import MICROSERVICE_URL
                
                response = requests.post(
                    f"{MICROSERVICE_URL}/add_document",
                    json={"document": new_doc_text, "source": "frontend_input"}
                )
                response.raise_for_status()
                st.success("Document added successfully!")
            except Exception as e:
                st.error(f"Failed to add document: {e}")
        else:
            st.warning("Please enter some text for the document.")