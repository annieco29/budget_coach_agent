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

### Nodes and edges

def analyze_transactions(state: BudgetCoachState):
    """Analyze transactions and generate snarky insights"""
    
    # Group transactions by category
    category_spending = {}
    for transaction in state["transactions"]:
        if transaction.category not in category_spending:
            category_spending[transaction.category] = {
                "total": 0.0,
                "count": 0
            }
        category_spending[transaction.category]["total"] += transaction.amount
        category_spending[transaction.category]["count"] += 1

    # Generate insights for each category
    insights = []
    for category, data in category_spending.items():
        system_message = f"""You are a passive-aggressive budget coach. Generate a snarky but helpful insight about spending in the {category} category.
        
        Total spent: ${data['total']:.2f}
        Number of transactions: {data['count']}
        
        Make your response:
        1. Snarky but not mean
        2. Include a helpful suggestion
        3. Use emojis sparingly
        4. Keep it concise (2-3 sentences)
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
    
    Monthly Budget: ${budget:.2f}
    Total Spent: ${total_spent:.2f}
    Remaining: ${budget - total_spent:.2f}
    
    Make your response:
    1. Start with a snarky observation about overall spending
    2. Include specific category breakdowns
    3. End with a passive-aggressive but helpful tip
    4. Use markdown formatting
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
    
    Monthly Budget: ${budget:.2f}
    Total Spent: ${total_spent:.2f}
    Remaining: ${budget - total_spent:.2f}
    
    Make your response:
    1. Start with a dramatic observation about spending
    2. Include specific examples of "interesting" purchases
    3. End with a sarcastic but practical suggestion
    4. Use emojis for extra passive-aggressive effect
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