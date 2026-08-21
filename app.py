"""
Hafta 4 - Streamlit sohbet arayüzü

rag.py'deki answer_query() fonksiyonunu kullanan, sohbet geçmişini ve
kullanılan kaynak pasajları gösteren bir arayüz.

Çalıştırma:
    streamlit run app.py
"""

import streamlit as st

from rag import answer_query, get_manager

st.set_page_config(page_title="Semiconductor RAG Assistant")
st.title("Semiconductor RAG Assistant")


@st.cache_resource
def load_manager():
    """FoundryLocalManager'ı bir kere başlatıp önbelleğe alır; her soruda
    Foundry Local Core yeniden başlatılmasın diye."""
    return get_manager()


load_manager()

if "messages" not in st.session_state:
    # Her eleman: {"question": str, "answer": str, "sources": [(title, score), ...]}
    st.session_state.messages = []


def show_sources(sources):
    with st.expander("Kullanılan kaynaklar"):
        for title, score in sources:
            st.caption(f"Retrieved: {title} (score: {score:.2f})")


# Geçmiş sohbeti göster
for msg in st.session_state.messages:
    with st.chat_message("user"):
        st.write(msg["question"])
    with st.chat_message("assistant"):
        st.write(msg["answer"])
        show_sources(msg["sources"])

question = st.chat_input("Sorunuzu yazın...")

if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Yanıt hazırlanıyor... (CPU üzerinde biraz sürebilir)"):
            answer, sources = answer_query(question)
        st.write(answer)
        show_sources(sources)

    st.session_state.messages.append(
        {"question": question, "answer": answer, "sources": sources}
    )
