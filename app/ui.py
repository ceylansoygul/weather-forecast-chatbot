"""Streamlit user interface for the Weather Forecast Chatbot."""

import streamlit as st

from app.services.chatbot_service import run_chatbot


def render_app():
    """Render the chat interface and display chatbot responses.

    Maintains the conversation in Streamlit session state, sends each
    new user message to the chatbot service, and displays the result.
    """
    
    st.set_page_config(
        page_title="Weather Forecast Chatbot",
        page_icon="🌦️",
        layout="centered"
    )
    
    st.title("🌦️ Weather Forecast Chatbot")
    st.caption(
        "AI-powered weather information for outdoor activities"
    )
    
    st.write(
        "Ask about hiking, cycling, running, camping, "
        "mountain biking, or another outdoor activity."
    )
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    user_question = st.chat_input(
        "Example: Will it rain during my cycling tour in Berlin tomorrow afternoon?"
    )
    
    if user_question:
        st.session_state.messages.append({
            "role": "user",
            "content": user_question
        })
    
        with st.chat_message("user"):
            st.markdown(user_question)
    
        with st.chat_message("assistant"):
            with st.spinner("Checking the weather..."):
                try:
                    conversation_context = "\n".join(
                        f"{message['role']}: {message['content']}"
                        for message in st.session_state.messages[-6:]
                    )
    
                    result = run_chatbot(
                        user_question,
                        conversation_context=conversation_context
                    )
    
                    st.markdown(
                        result["answer"]
                    )
    
                    if result.get("type") == "weather":
    
                        with st.expander(
                            "Technical details"
                        ):
                            st.write(
                                "Structured request:"
                            )
                            st.json(
                                result["request"]
                            )
    
                            st.write(
                                "Forecast:"
                            )
                            st.json(
                                result["forecast"]
                            )
    
                            st.write(
                                "Activity assessment:"
                            )
                            st.json(
                                result["assessment"]
                            )
    
                except Exception as error:
                    st.error(
                        "The request could not be processed."
                    )
    
                    with st.expander(
                        "Technical error"
                    ):
                        st.exception(error)
    
                    result = None
    
        if result:
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"]
            })
    
    st.divider()
    
    st.caption(
        "Forecast data is retrieved from Open-Meteo. Activity assessments "
        "use heuristic rules and should not be treated as safety guarantees."
    )
    
    
