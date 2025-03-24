from datetime import datetime
from dotenv import load_dotenv
import os
from pathlib import Path
from budget_coach import Transaction

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

def get_sample_transactions():
    """Get a list of sample transactions for testing"""
    return [
        Transaction(
            date=datetime(2024, 3, 15),
            amount=150.50,
            category="Dining",
            description="Dinner at Fancy Restaurant",
            merchant="Fancy Restaurant"
        ),
        Transaction(
            date=datetime(2024, 3, 14),
            amount=45.99,
            category="Shopping",
            description="New pair of shoes",
            merchant="Shoe Store"
        ),
        Transaction(
            date=datetime(2024, 3, 13),
            amount=25.00,
            category="Entertainment",
            description="Movie tickets",
            merchant="Movie Theater"
        ),
        Transaction(
            date=datetime(2024, 3, 12),
            amount=89.99,
            category="Shopping",
            description="New clothes",
            merchant="Clothing Store"
        ),
        Transaction(
            date=datetime(2024, 3, 11),
            amount=35.00,
            category="Dining",
            description="Lunch with friends",
            merchant="Cafe"
        ),
        Transaction(
            date=datetime(2024, 3, 10),
            amount=200.00,
            category="Entertainment",
            description="Concert tickets",
            merchant="TicketMaster"
        ),
        Transaction(
            date=datetime(2024, 3, 9),
            amount=75.50,
            category="Dining",
            description="Weekend brunch",
            merchant="Brunch Place"
        ),
        Transaction(
            date=datetime(2024, 3, 8),
            amount=120.00,
            category="Shopping",
            description="Electronics",
            merchant="Tech Store"
        ),
        Transaction(
            date=datetime(2024, 3, 7),
            amount=40.00,
            category="Entertainment",
            description="Bowling night",
            merchant="Bowling Alley"
        ),
        Transaction(
            date=datetime(2024, 3, 6),
            amount=65.00,
            category="Dining",
            description="Takeout dinner",
            merchant="Local Restaurant"
        )
    ]

if __name__ == "__main__":
    # Example usage
    transactions = get_sample_transactions()
    from budget_coach import BudgetCoach
    coach = BudgetCoach(transactions)
    print(coach.get_response("Give me a summary of my spending.")) 