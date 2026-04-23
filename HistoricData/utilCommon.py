import os
import sys
import pandas as pd
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


def telegramMsg(message):

    BOT_TOKEN = os.getenv("FirstTrialBotToken")  # The Bot_Token is stored in environment variables
    CHAT_ID = os.getenv("MyTeleGramChatID")  # The ChatID is stored in environment variables

    if BOT_TOKEN and CHAT_ID:
        # Telegram API URL
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        # Request parameters
        params = {
            "chat_id": CHAT_ID,
            "text": message
        }

        # Send the request
        response = requests.get(url, params=params)


def connectPostgres():

    db_url =  "postgresql://postgres:"+os.getenv("postgrespwd")+"@localhost:5432/postgres"
    # Create SQLAlchemy engine
    if db_url:
        try:
            engine = create_engine(db_url)
            connection = engine.connect()  # Test the connection
            print("\n\nPostgres Connected successfully!")
            connection.close()  # Close the test connection
        except SQLAlchemyError as e:
            print(f"\nError: Failed to connect to Postgres. {e}")
            exit(404)
    else:
        print("\n\nError: Environment variable postgresurl not set.")

    return engine

def run_backup():
    engine = connectPostgres()

    with engine.connect() as conn:
        try:
            conn.execute(text("SELECT public.create_eq_trade_backup();"))
            conn.commit()   # important if function does INSERT/UPDATE
            print("Necessary backup taken")

        except Exception as e:
            print(f"Error executing function: {e}")