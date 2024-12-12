import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os


def display_chatbot():
    st.set_page_config(page_title="CCulinary AI Assistant", page_icon="🍳")

    load_dotenv()
    key = os.getenv("API_KEY")
    
    unique_key = f"chatbot_input_{len(st.session_state.get('messages', []))}"
    
    # Title with some padding
    st.markdown("## ChefMate Chatbot")
    st.markdown("---")
    
    # Initialize chat history in session state if not exists
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("What would you like to know about cooking?", key=unique_key):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        try:
            genai.configure(api_key=key)
            
            system_instruction = """
            You are a Professional Culinary Assistant with the following guidelines:

            Core Responsibilities:
            - Provide expert cooking advice and culinary knowledge
            - Offer detailed recipes and cooking techniques
            - Explain ingredient properties and uses
            - Give kitchen safety and cooking tips
            - Discuss various cuisines and cooking methods

            Conversation Constraints:
            1. ONLY discuss topics directly related to cooking, food, and culinary arts
            2. If asked about non-cooking topics, politely redirect to cooking-related discussions
            3. Provide precise, actionable, and helpful cooking information
            4. Use professional culinary language when appropriate
            5. Be enthusiastic and engaging about food and cooking

            Interaction Guidelines:
            - Always respond with cooking-focused information
            - Offer practical advice and solutions
            - Use a friendly, instructive tone
            - Provide context and explanations with your responses

            Redirection Examples:
            - Non-cooking query: "While I can't help with that, I'd be happy to discuss a delicious recipe or cooking technique!"
            - Off-topic question: "My expertise is in culinary arts. Would you like to explore a new recipe or cooking method?"

            Response Style:
            - Be concise yet informative
            - Use clear, professional culinary language
            - Include practical tips and insights
            - Demonstrate deep cooking knowledge
            """
            
            model = genai.GenerativeModel(
                "gemini-1.5-flash", 
                system_instruction=system_instruction
            )
            
            response = model.generate_content(prompt)
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            with st.chat_message("assistant"):
                st.markdown(response.text)
        
        except Exception as e:
            st.error(f"Error generating content: {e}")
        

if __name__ == "__main__":
    display_chatbot()