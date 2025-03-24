from typing import Annotated, List, TypedDict
from pydantic import BaseModel, Field
from datetime import datetime
import operator
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Verify API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, MessagesState, START, StateGraph

### LLM
llm = ChatOpenAI(model="gpt-4", temperature=0.7)  

### Schema
class Transaction(BaseModel):
    date: datetime = Field(description="Date of the transaction")
    amount: float = Field(description="Amount spent")
    category: str = Field(description="Category of spending")
    description: str = Field(description="Description of the transaction")
    merchant: str = Field(description="Name of the merchant")

class SpendingInsight(BaseModel):
    category: str = Field(description="Category of spending being analyzed")
    total_spent: float = Field(description="Total amount spent in this category")
    num_transactions: int = Field(description="Number of transactions in this category")
    snarky_comment: str = Field(description="A passive-aggressive comment about the spending")
    helpful_suggestion: str = Field(description="A helpful suggestion to improve spending")

class BudgetCoachState(MessagesState):
    transactions: List[Transaction] = Field(default_factory=list)
    insights: List[SpendingInsight] = Field(default_factory=list)
    monthly_budget: float = Field(default=0.0)
    current_month_spending: float = Field(default=0.0)

class BudgetCoach:
    def __init__(self, transactions: List[Transaction], monthly_budget: float = 5000.0):
        self.transactions = transactions
        self.monthly_budget = monthly_budget
        self.state = BudgetCoachState(
            transactions=transactions,
            monthly_budget=monthly_budget
        )
        self.graph = budget_coach.compile()

    def get_response(self, prompt: str) -> str:
        """Get a response from the budget coach based on the user's prompt"""
        system_message = """You are a passive-aggressive budget coach. Your responses should be:
        1. Snarky but not mean
        2. Include specific details about spending
        3. End with a helpful suggestion
        4. Use emojis sparingly
        5. Keep it concise
        6. Format numbers with proper spacing and commas (e.g., "$1,234.56" not "$1234.56")
        7. Use proper spacing between sentences and after punctuation
        8. Use markdown formatting for emphasis where appropriate
        
        Base your response on the user's transactions and their question."""
        
        # Run the graph to analyze transactions and generate insights
        result = self.graph.invoke({
            "messages": [
                SystemMessage(content=system_message),
                HumanMessage(content=prompt)
            ],
            "transactions": self.transactions,
            "monthly_budget": self.monthly_budget
        })
        
        # Get the last message from the result
        if result["messages"]:
            response = result["messages"][-1].content
            # Ensure proper spacing around numbers
            response = response.replace("$", " $").replace("$ ", "$")
            # Ensure proper spacing after punctuation
            response = response.replace(".", ". ").replace("!", "! ").replace("?", "? ")
            return response
        return "I'm currently analyzing your questionable financial decisions... 🤔"

### Nodes and edges

def format_currency(amount: float) -> str:
    """Format a number as currency with proper spacing and commas"""
    return f"${amount:,.2f}"

def analyze_transactions(state: BudgetCoachState):
    """Analyze transactions and generate snarky insights"""
    
    # Group transactions by category
    category_spending = {}
    for transaction in state["transactions"]:
        if transaction.category not in category_spending:
            category_spending[transaction.category] = {
                "total": 0.0,
                "count": 0,
                "transactions": []
            }
        category_spending[transaction.category]["total"] += transaction.amount
        category_spending[transaction.category]["count"] += 1
        category_spending[transaction.category]["transactions"].append(transaction)

    # Generate insights for each category
    insights = []
    for category, data in category_spending.items():
        formatted_amount = format_currency(data['total'])
        system_message = f"""You are a passive-aggressive budget coach. Generate a snarky but helpful insight about spending in the {category} category.
        
        Total spent: {formatted_amount}
        Number of transactions: {data['count']}
        
        Recent transactions:
        {chr(10).join(f"- {format_currency(t.amount)} at {t.merchant}" for t in data['transactions'][-3:])}
        
        Make your response:
        1. Snarky but not mean
        2. Include a helpful suggestion
        3. Use emojis sparingly
        4. Keep it concise (2-3 sentences)
        5. Format all numbers with proper spacing and commas
        6. Do not split numbers across lines
        7. Use proper spacing between sentences
        """
        
        response = llm.invoke([SystemMessage(content=system_message)])
        
        insight = SpendingInsight(
            category=category,
            total_spent=data["total"],
            num_transactions=data["count"],
            snarky_comment=response.content,
            helpful_suggestion=""
        )
        insights.append(insight)

    return {"insights": insights}

def generate_monthly_summary(state: BudgetCoachState):
    """Generate a monthly spending summary with passive-aggressive commentary"""
    
    total_spent = sum(t.amount for t in state["transactions"])
    budget = state["monthly_budget"]
    
    system_message = f"""You are a passive-aggressive budget coach. Generate a monthly spending summary.
    
    Monthly Budget: {format_currency(budget)}
    Total Spent: {format_currency(total_spent)}
    Remaining: {format_currency(budget - total_spent)}
    
    Make your response:
    1. Start with a snarky observation about overall spending
    2. Include specific category breakdowns
    3. End with a passive-aggressive but helpful tip
    4. Use markdown formatting
    5. Format all numbers with proper spacing and commas
    6. Use proper spacing between sentences
    7. Do not split numbers across lines
    """
    
    summary = llm.invoke([SystemMessage(content=system_message)])
    
    return {
        "current_month_spending": total_spent,
        "messages": [AIMessage(content=summary.content)]
    }

def should_send_alert(state: BudgetCoachState):
    """Determine if we should send a spending alert"""
    
    total_spent = state["current_month_spending"]
    budget = state["monthly_budget"]
    
    # Alert if spending exceeds 80% of budget
    if total_spent > (budget * 0.8):
        return "send_alert"
    return END

def send_spending_alert(state: BudgetCoachState):
    """Generate and send a passive-aggressive spending alert"""
    
    total_spent = state["current_month_spending"]
    budget = state["monthly_budget"]
    
    system_message = f"""You are a passive-aggressive budget coach. Generate an alert about excessive spending.
    
    Monthly Budget: {format_currency(budget)}
    Total Spent: {format_currency(total_spent)}
    Remaining: {format_currency(budget - total_spent)}
    
    Make your response:
    1. Start with a dramatic observation about spending
    2. Include specific examples of "interesting" purchases
    3. End with a sarcastic but practical suggestion
    4. Use emojis for extra passive-aggressive effect
    5. Format all numbers with proper spacing and commas
    6. Use proper spacing between sentences
    7. Do not split numbers across lines
    """
    
    alert = llm.invoke([SystemMessage(content=system_message)])
    
    return {"messages": [AIMessage(content=alert.content)]}

# Create the graph
budget_coach = StateGraph(BudgetCoachState)

# Add nodes
budget_coach.add_node("analyze_transactions", analyze_transactions)
budget_coach.add_node("generate_summary", generate_monthly_summary)
budget_coach.add_node("send_alert", send_spending_alert)

# Add edges
budget_coach.add_edge(START, "analyze_transactions")
budget_coach.add_edge("analyze_transactions", "generate_summary")
budget_coach.add_conditional_edges("generate_summary", should_send_alert, ["send_alert", END])
budget_coach.add_edge("send_alert", END)

# Compile the graph
graph = budget_coach.compile() 