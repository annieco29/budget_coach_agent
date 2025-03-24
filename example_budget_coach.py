from datetime import datetime
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Verify required environment variables
required_vars = ["OPENAI_API_KEY", "PLAID_CLIENT_ID", "PLAID_SECRET", "PLAID_ACCESS_TOKEN"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

from budget_coach import graph, BudgetCoachState
from plaid_transactions import PlaidTransactionFetcher

# Initialize Plaid client
plaid_client = PlaidTransactionFetcher(
    client_id=os.getenv("PLAID_CLIENT_ID"),
    secret=os.getenv("PLAID_SECRET"),
    access_token=os.getenv("PLAID_ACCESS_TOKEN")
)

# Fetch recent transactions (last 30 days)
transactions = plaid_client.get_recent_transactions(days_back=30)

# Initialize state with your transactions
initial_state = BudgetCoachState(
    transactions=transactions,
    monthly_budget=2000.0,  # Adjust this to your actual monthly budget
    messages=[]
)

# Run the graph
result = graph.invoke(initial_state)

# Print the results
print("\n=== Budget Coach Insights ===\n")
for message in result["messages"]:
    print(message.content) 