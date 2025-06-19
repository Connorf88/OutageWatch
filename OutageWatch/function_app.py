import datetime
import logging
import os
import requests
import azure.functions as func
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Environment variables (configure these later in Azure settings)
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
FROM_EMAIL = os.environ.get("FROM_EMAIL")
TO_EMAIL = os.environ.get("TO_EMAIL")
TARGET_URL = os.environ.get("TARGET_URL", "https://example.com")

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    logging.info(f"Timer trigger function ran at {utc_timestamp}")
    
    try:
        response = requests.get(TARGET_URL)
        status_code = response.status_code
        if status_code != 200:
            logging.error(f"Outage detected! {TARGET_URL} returned status code: {status_code}")
            
            # Send an email alert via SendGrid
            message = Mail(
                from_email=FROM_EMAIL,
                to_emails=TO_EMAIL,
                subject="Outage Alert: Service Down",
                html_content=f"<strong>{TARGET_URL} is down. Status code: {status_code}</strong>")
            
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            send_response = sg.send(message)
            logging.info(f"Notification sent, SendGrid response: {send_response.status_code}")
        else:
            logging.info(f"{TARGET_URL} is up. Status code: {status_code}")
    except Exception as e:
        logging.error(f"Error checking {TARGET_URL}: {str(e)}")


@app.timer_trigger(schedule="0 */5 * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def CheckService(myTimer: func.TimerRequest) -> None:
    
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')