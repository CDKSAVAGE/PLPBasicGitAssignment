import smtplib
import ssl
import sys
import asyncio
import os
from deriv_api import DerivAPI, APIError
from email.message import EmailMessage
from prettytable import PrettyTable
from dotenv import load_dotenv

def configure():
  load_dotenv()

configure()
# Email configuration
email_sender = 'chepketidaniel20@gmail.com'
email_password = 'nlqf kiea osfx bjxy'
email_receivers = ['cdksavage7@gmail.com']
subject = 'Deriv Bot Alert'

def send_email(subject, body):
    try:
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = ','.join(email_receivers)
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receivers, em.as_string())
        print(f"Email sent successfully with subject: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")

app_id = 1089
api_token = os.getenv('API_TOKENS')
minimum_stake = 1
target_profit = 5
stop_loss = -50
initial_stake = minimum_stake

if not api_token:
    sys.exit("API_TOKEN environment variable is not set")

async def trade_with_strategy(api, digits_threshold, stake):
    try:
        proposal = await api.proposal({
            "proposal": 1,
            "amount": stake,
            "barrier": digits_threshold,
            "basis": "payout",
            "contract_type": "DIGITUNDER",
            "currency": "USD",
            "duration": 1,
            "duration_unit": "t",
            "symbol": "R_100"
        })
        response = await api.buy({"buy": proposal.get('proposal').get('id'), "price": 100})
        contract_id = response.get('buy').get('contract_id')

        await asyncio.sleep(1)

        poc = await api.proposal_open_contract({"proposal_open_contract": 1, "contract_id": contract_id})
        while not poc.get('proposal_open_contract').get('is_sold'):
            await asyncio.sleep(1)
            poc = await api.proposal_open_contract({"proposal_open_contract": 1, "contract_id": contract_id})

        is_winner = poc.get('proposal_open_contract').get('profit') > 0
        profit = poc.get('proposal_open_contract').get('profit')

        return is_winner, profit
    except APIError as e:
        print(f"API error: {e}")
        return False, 0
    except Exception as e:
        print(f"Error in trading strategy: {e}")
        return False, 0

async def sample_calls():
    try:
        api = DerivAPI(app_id=app_id)

        response = await api.ping({'ping': 1})
        if response['ping']:
            print(response['ping'])

        active_symbols = await api.active_symbols({"active_symbols": "brief", "product_type": "basic"})
        print(active_symbols)

        authorize = await api.authorize(api_token)
        print(authorize)

        balance_response = await api.balance()
        balance = balance_response['balance']
        initial_balance = balance['balance']
        print("Your current balance is", balance['currency'], balance['balance'])

        digits_threshold = 9
        consecutive_losses = 0
        total_profit = 0
        stake = minimum_stake
        last_loss = 0

        results = []
        total_trades = 0
        total_wins = 0
        total_losses = 0

        # Notify that trading has started
        send_email('AlgoCdk Bot Trading Started', 'The Deriv bot has started trading.')

        while total_profit < target_profit and total_profit > stop_loss:
            is_winner, profit = await trade_with_strategy(api, digits_threshold, stake)
            total_trades += 1

            if is_winner:
                consecutive_losses = 0
                stake = minimum_stake
                digits_threshold = 9
                last_loss = 0
                total_wins += 1
            else:
                consecutive_losses += 1
                last_loss = abs(profit)
                total_losses += 1

                if last_loss > 4:
                    stake = (stake * 2) + abs(profit)
                    digits_threshold = 7
                elif last_loss > 2:
                    stake = (stake * 2) + abs(profit)
                    digits_threshold = 6
                else:
                    stake = (stake * 2) + abs(profit)
                    digits_threshold = 5

            total_profit += profit
            print(f"Total profit: {total_profit:.3f} USD")  # Display total profit with 3 decimal places

            results.append([digits_threshold, f"{profit:.3f}", f"{total_profit:.3f}", 'WIN' if is_winner else 'LOSS'])  # Format profit and total profit to 3 decimal places

            if total_profit >= target_profit:
                print(f"Target profit of {target_profit} USD reached. Stopping trading.")
                break

            elif total_profit <= stop_loss:
                print(f"Stop loss of {stop_loss} USD reached. Stopping trading.")
                break

            await asyncio.sleep(5)

        # Create the trade summary table
        summary_table = PrettyTable()
        summary_table.field_names = ["Total Trades", "Total Wins", "Total Losses", "Target Profit", "Final Profit", "Time"]
        summary_table.add_row([total_trades, total_wins, total_losses, target_profit, f"{total_profit:.3f}", asyncio.get_event_loop().time()])  # Format final profit to 3 decimal places

        # Create the detailed trade table
        detailed_table = PrettyTable()
        detailed_table.field_names = ["Digits Threshold", "Profit", "Total Profit", "Result"]
        for row in results:
            detailed_table.add_row(row)

        detailed_results = f"""
        AlgoCdk AI has finished trading. Please check the details below:

        Trade Summary:
        {summary_table}

        Detailed Trade Results:
        {detailed_table}
        """

        # Send summary email
        send_email('Deriv Bot Trading Summary', detailed_results)

    except Exception as e:
        print(f"Error in sample calls: {e}")
    finally:
        print("End of script.")
        await api.clear()

asyncio.run(sample_calls())
