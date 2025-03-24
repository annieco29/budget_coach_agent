from flask import Flask, render_template, request, jsonify
import plaid
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.api import plaid_api
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Print environment variables (without secrets)
print("PLAID_CLIENT_ID:", os.getenv('PLAID_CLIENT_ID')[:5] + "..." if os.getenv('PLAID_CLIENT_ID') else "Not found")
print("PLAID_SECRET:", os.getenv('PLAID_SECRET')[:5] + "..." if os.getenv('PLAID_SECRET') else "Not found")

# Configure Plaid client
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,  # Changed back to Sandbox for testing
    api_key={
        'clientId': os.getenv('PLAID_CLIENT_ID'),
        'secret': os.getenv('PLAID_SECRET'),
    }
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_link_token', methods=['POST'])
def create_link_token():
    try:
        print("Creating link token...")
        request = LinkTokenCreateRequest(
            products=[Products("transactions")],
            client_name="Budget Coach",
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id="user-id"
            )
        )
        response = client.link_token_create(request)
        print("Link token created successfully")
        return jsonify({'link_token': response['link_token']})
    except plaid.ApiException as e:
        print("Error creating link token:", str(e))
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print("Unexpected error:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/exchange_public_token', methods=['POST'])
def exchange_public_token():
    try:
        public_token = request.json['public_token']
        print("Exchanging public token...")
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response['access_token']
        
        # Get the absolute path to the .env file
        env_path = Path('.env').absolute()
        print(f"\nSaving access token to: {env_path}")
        
        # Save the access token to a file
        with open('.env', 'a') as f:
            f.write(f"\nPLAID_ACCESS_TOKEN={access_token}")
            
        print("\nAccess token saved successfully!")
        print("You can now use this token to run the budget coach.")
        print("To run the budget coach, use: python example_budget_coach.py")
        
        return jsonify({
            'success': True, 
            'message': f'Access token saved to {env_path}'
        })
    except plaid.ApiException as e:
        print("Error exchanging token:", str(e))
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print("Unexpected error:", str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 