import asyncio
import random
from deriv_api import DerivAPI, APIError

# Define trading parameters
app_id = 1089
api_token = 'MtrZIbR0fpbGXQa'  # Replace with your actual API token
symbol_list = "1HZ10V"
stake1 = 1  # Placeholder value; adjust as needed
contract_type = "DIGITUNDER"  # Ensure this is correct for your trading strategy

# Variables
Stake = 0.50
Win_Stake = 0.50
Loss = 0
Expected_Profit = 2.50
Stop_Loss = 100
contract_result = None  # Define contract_result

async def ping_api(api):
    response = await api.ping({'ping': 1})
    print("Ping Response:", response)
    return response

async def authorize_api(api):
    authorize = await api.authorize(api_token)
    print("Authorize Response:", authorize)
    return authorize

async def get_balance(api):
    balance_response = await api.balance()
    print("Balance Response:", balance_response)

    # Extracting balance details
    balance_info = balance_response.get('balance', {})
    currency = balance_info.get('currency', 'Unknown')
    balance = balance_info.get('balance', 'Unknown')
    print(f"Your current balance is {currency} {balance}")
    return balance_response

async def make_proposal(api, Stake, contract_type):
    prediction = 1 if Loss == 0 else 5
    proposal_params = {
        "proposal": 1,
        "amount": Stake,
        "barrier": 9,
        "basis": "payout",
        "contract_type": "DIGITUNDER",
        "duration": 1,
        "duration_unit": "t",
        "symbol": symbol_list,
        "prediction": prediction
    }
    print("Proposal Parameters:", proposal_params)

    try:
        proposal = await api.proposal(proposal_params)
        print("Raw Proposal Response:", proposal)  # Log the full response

        # Check if the response is valid
        if proposal is None:
            raise ValueError("Proposal response is None. This indicates that the API did not return a valid response.")

        if not isinstance(proposal, dict):
            raise ValueError(f"Proposal response is not a dictionary. Type: {type(proposal)}")

        if 'error' in proposal:
            raise ValueError(f"API returned an error: {proposal['error']}")

        # Further checks to see if the response structure is as expected
        if 'proposal' not in proposal:
            raise ValueError(f"Expected 'proposal' in response, but got: {proposal}")

        return proposal

    except Exception as e:
        print(f"An error occurred while making the proposal: {e}")
        return None


async def purchase_contract(api, stake1, contract_type):
    global contract_result
    proposal_response = await make_proposal(api, stake1, contract_type)

    # If the proposal was unsuccessful, do not proceed further
    if proposal_response is None:
        print("Skipping purchase due to invalid proposal response.")
        return

    # Simulate contract purchase
    contract_result = "win" if random.choice([True, False]) else "loss"  # Simulating result
    print("Contract Result:", contract_result)
    await handle_after_purchase(api, stake1, contract_type)

async def handle_after_purchase(api, stake1, contract_type):
    global Loss
    if contract_result == 'win':
        stake1 = Win_Stake
        Loss = 0
    elif contract_result == 'loss':
        Loss += 1
        if Loss >= 1:
            stake1 = abs(9) * 2.1  # Adjust this calculation based on your strategy
    await make_proposal(api, stake1, contract_type)

async def handle_before_purchase(api, stake1, contract_type):
    random_number = random.randint(0, 9)
    if Loss == 0 and random_number >= 1:
        await purchase_contract(api, stake1, contract_type)
    elif Loss >= 1 and random_number >= 6:
        await purchase_contract(api, stake1, contract_type)
    elif 1 <= Loss < 4 and 0 <= random_number <= 4:
        await purchase_contract(api, stake1, contract_type)
    else:
        await purchase_contract(api, stake1, contract_type)

async def sample_calls():
    api = DerivAPI(app_id=app_id)

    try:
        message = "ALGOCDK AI PREMIUM [By: GHOST] • Expected Profit -> $100 | Stop Loss $100"
        print(message)

        await ping_api(api)
        await authorize_api(api)
        await get_balance(api)
        await handle_before_purchase(api, stake1, contract_type)

    except APIError as e:
        print("API Error:", e)
    except ValueError as e:
        print("Value Error:", e)
    except Exception as e:
        print("Unexpected Error:", e)
    finally:
        await api.clear()

asyncio.run(sample_calls())
