"""
Hafta 6 - Streamlit sohbet arayüzü

rag.py'deki answer_query() fonksiyonunu kullanan, sohbet geçmişini,
kullanılan kaynak pasajları ve konu seçimini gösteren bir arayüz.

Çalıştırma:
    streamlit run app.py
"""

import streamlit as st

from rag import answer_query, get_manager

TOPICS = ["Semiconductors", "Space Exploration"]

st.set_page_config(page_title="Semiconductor RAG Assistant", page_icon="🔬")

st.markdown(
    """
    <style>
    :root {
        --brand-teal: #0f766e;
        --brand-dark-blue: #0c4a6e;
    }
    h1, [data-testid="stMarkdownContainer"] h1 { color: var(--brand-dark-blue) !important; }
    .stButton > button,
    [data-testid="stChatInputSubmitButton"],
    [data-testid="stBaseButton-secondary"] {
        border-radius: 12px !important;
        background-color: var(--brand-teal) !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button:hover,
    [data-testid="stChatInputSubmitButton"]:hover {
        background-color: var(--brand-dark-blue) !important;
    }
    [data-testid="stChatInput"] {
        border-radius: 14px !important;
    }
    [data-testid="stChatInput"] textarea {
        border-radius: 14px !important;
    }
    [data-testid="stExpander"] {
        border-radius: 12px !important;
        border: 1px solid rgba(15, 118, 110, 0.35) !important;
        overflow: hidden;
    }
    [data-testid="stChatMessage"] {
        border-radius: 16px !important;
        border: 1px solid rgba(12, 74, 110, 0.12) !important;
    }
    [data-testid="stSelectbox"] > div > div {
        border-radius: 12px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🔬 Semiconductor RAG Assistant")
st.caption(
    "Yerel çalışan, kaynak gösteren bir RAG asistanı — Microsoft Foundry Local "
    "ile %100 çevrimdışı. Yarı iletkenler ve uzay araştırmaları konularında sorular sorabilirsiniz."
)


@st.cache_resource
def load_manager():
    """FoundryLocalManager'ı bir kere başlatıp önbelleğe alır; her soruda
    Foundry Local Core yeniden başlatılmasın diye."""
    return get_manager()


load_manager()

if "messages" not in st.session_state:
    # Her eleman: {"question": str, "answer": str, "sources": [(title, score), ...], "topic": str}
    st.session_state.messages = []

topic = st.selectbox("Konu seçin:", TOPICS)


def show_sources(sources):
    with st.expander("Kullanılan kaynaklar"):
        for title, score in sources:
            st.caption(f"Retrieved: {title} (score: {score:.2f})")


# Geçmiş sohbeti göster
for msg in st.session_state.messages:
    with st.chat_message("user"):
        st.write(msg["question"])
    with st.chat_message("assistant"):
        st.caption(f"Konu: {msg['topic']}")
        st.write(msg["answer"])
        show_sources(msg["sources"])

question = st.chat_input("Sorunuzu yazın...")

if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        st.caption(f"Konu: {topic}")
        with st.spinner("Yanıt hazırlanıyor... (CPU üzerinde biraz sürebilir)"):
            answer, sources = answer_query(question, topic=topic)
        st.write(answer)
        show_sources(sources)

    st.session_state.messages.append(
        {"question": question, "answer": answer, "sources": sources, "topic": topic}
    )
