from datetime import datetime, timedelta
from typing import List
import plaid
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.transactions_get_response import TransactionsGetResponse
from plaid.api import plaid_api
from budget_coach import Transaction

class PlaidTransactionFetcher:
    def __init__(self, client_id: str, secret: str, access_token: str):
        """
        Initialize Plaid client with your credentials.
        
        Args:
            client_id: Your Plaid client ID
            secret: Your Plaid secret
            access_token: The access token for your Chase United Explorer card
        """
        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox,  # Changed back to Sandbox for testing
            api_key={
                'clientId': client_id,
                'secret': secret,
            }
        )
        self.api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(self.api_client)
        self.access_token = access_token

    def get_recent_transactions(self, days_back: int = 30) -> List[Transaction]:
        """
        Fetch recent transactions from Plaid.
        
        Args:
            days_back: Number of days of transactions to fetch
            
        Returns:
            List of Transaction objects
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Create request
        request = TransactionsGetRequest(
            access_token=self.access_token,
            start_date=start_date.date(),
            end_date=end_date.date(),
            options=TransactionsGetRequestOptions(
                count=500,  # Adjust based on your needs
                offset=0
            )
        )
        
        try:
            # Get transactions
            response = self.client.transactions_get(request)
            transactions = response.transactions
            
            # Convert to our Transaction model
            return [
                Transaction(
                    date=datetime.combine(t.date, datetime.min.time()),  # Convert date to datetime
                    amount=float(t.amount),
                    category=self._map_plaid_category(t.category),
                    description=t.name,
                    merchant=t.merchant_name or t.name
                )
                for t in transactions
            ]
            
        except plaid.ApiException as e:
            print(f"Error fetching transactions: {e}")
            return []

    def _map_plaid_category(self, plaid_category: List[str]) -> str:
        """
        Map Plaid categories to our budget coach categories.
        """
        if not plaid_category:
            return 'Other'
            
        category = plaid_category[0].lower()
        
        # Dining categories
        if any(word in category for word in ['restaurant', 'cafe', 'coffee', 'bar', 'pub', 'food', 'dining']):
            return 'Dining'
        
        # Shopping categories
        if any(word in category for word in ['amazon', 'walmart', 'target', 'store', 'shop', 'retail']):
            return 'Shopping'
        
        # Entertainment categories
        if any(word in category for word in ['netflix', 'spotify', 'hulu', 'entertainment', 'movie', 'theater']):
            return 'Entertainment'
        
        # Travel categories
        if any(word in category for word in ['united', 'airline', 'hotel', 'travel', 'flight']):
            return 'Travel'
        
        # Transportation categories
        if any(word in category for word in ['uber', 'lyft', 'taxi', 'transit', 'parking']):
            return 'Transportation'
        
        # Utilities categories
        if any(word in category for word in ['electric', 'water', 'gas', 'utility', 'internet', 'phone']):
            return 'Utilities'
        
        return 'Other' 