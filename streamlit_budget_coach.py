import streamlit as st
from budget_coach import BudgetCoach
from plaid_transactions import PlaidTransactionFetcher
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'budget_coach' not in st.session_state:
    st.session_state.budget_coach = None
if 'current_budget' not in st.session_state:
    st.session_state.current_budget = 5000.0

def format_message(message: str) -> str:
    """Format the message to ensure proper spacing and line breaks"""
    # Escape dollar signs to prevent LaTeX interpretation
    message = message.replace("$", "\\$")
    # Replace multiple spaces with single space
    message = re.sub(r'\s+', ' ', message)
    # Ensure proper spacing around numbers
    message = re.sub(r'(\d+\.?\d*)', r' \1 ', message)
    # Ensure proper spacing after punctuation
    message = re.sub(r'([.!?])([^\s])', r'\1 \2', message)
    # Clean up any double spaces
    message = re.sub(r'\s+', ' ', message)
    return message.strip()

# Page config
st.set_page_config(
    page_title="Passive-Aggressive Budget Coach",
    page_icon="💰",
    layout="wide"
)

# Title and description
st.title("Passive-Aggressive Budget Coach 💰")
st.markdown("""
    Welcome to your budget coach! I'll analyze your spending habits and provide some 
    *constructive* feedback. Don't worry, I'm here to help... in my own special way.
""")

# Sidebar for configuration
with st.sidebar:
    st.header("Settings")
    monthly_budget = st.number_input(
        "Monthly Budget ($)",
        min_value=0.0,
        max_value=100000.0,
        value=st.session_state.current_budget,
        step=100.0
    )
    
    # Update budget coach if budget value changes
    if monthly_budget != st.session_state.current_budget:
        st.session_state.current_budget = monthly_budget
        if st.session_state.budget_coach is not None:
            st.session_state.budget_coach.monthly_budget = monthly_budget
            st.session_state.budget_coach.state["monthly_budget"] = monthly_budget
    
    if st.button("Connect Chase Card"):
        st.info("Please run 'python plaid_link.py' in your terminal to connect your card.")

# Initialize budget coach if not already done
if st.session_state.budget_coach is None:
    # Use Plaid transactions
    fetcher = PlaidTransactionFetcher(
        client_id=os.getenv('PLAID_CLIENT_ID'),
        secret=os.getenv('PLAID_SECRET'),
        access_token=os.getenv('PLAID_ACCESS_TOKEN')
    )
    transactions = fetcher.get_recent_transactions()
    st.session_state.budget_coach = BudgetCoach(transactions, monthly_budget=st.session_state.current_budget)

# Main chat interface
st.subheader("Chat with Your Budget Coach")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        formatted_content = format_message(message["content"])
        st.markdown(formatted_content)

# Chat input
if prompt := st.chat_input("Ask your budget coach anything..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get coach's response
    with st.chat_message("assistant"):
        response = st.session_state.budget_coach.get_response(prompt)
        formatted_response = format_message(response)
        st.markdown(formatted_response)
        st.session_state.messages.append({"role": "assistant", "content": formatted_response})

# Add some helpful buttons
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Show Spending Summary"):
        with st.chat_message("assistant"):
            response = st.session_state.budget_coach.get_response("Give me a summary of my spending.")
            formatted_response = format_message(response)
            st.markdown(formatted_response)
            st.session_state.messages.append({"role": "assistant", "content": formatted_response})

with col2:
    if st.button("Get Budget Tips"):
        with st.chat_message("assistant"):
            response = st.session_state.budget_coach.get_response("Give me some budget tips.")
            # Escape dollar signs in the response
            response = response.replace("$", "\\$")
            formatted_response = format_message(response)
            st.markdown(formatted_response)
            st.session_state.messages.append({"role": "assistant", "content": formatted_response})

with col3:
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Built with ❤️ and a dash of passive-aggressiveness</p>
        <p>Powered by LangGraph and Plaid</p>
    </div>
""", unsafe_allow_html=True) 