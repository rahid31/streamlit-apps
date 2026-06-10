import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

BASE_URL = st.secrets["BASE_URL"]
SECRET_KEY = st.secrets["SECRET_KEY"]


def fetch_and_flatten_chat_data(simulation_uuid):

    # API config
    url = f"{BASE_URL}/tenants/{simulation_uuid}/simulation-chats"

    headers = {
        "X-API-KEY": SECRET_KEY
    }

    # Fetch API
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch data. "
            f"Status code: {response.status_code}, "
            f"Error: {response.text}"
        )

    data = response.json()

    if not data:
        return pd.DataFrame()

    # Main dataframe
    df = pd.DataFrame(data)

    # Safe parser
    def ensure_parsed(x):

        if isinstance(x, str):
            try:
                return json.loads(x)
            except Exception:
                return []

        if isinstance(x, list):
            return x

        return []

    # Normalize chats column
    df["chats"] = df["chats"].apply(ensure_parsed)

    # Explode chats into rows
    df_exploded = df.explode("chats", ignore_index=True)

    # Normalize nested dict
    chat_df = pd.json_normalize(df_exploded["chats"])

    # Rename columns
    chat_df = chat_df.rename(columns={
        "user": "user_message",
        "avatar": "avatar_message"
    })

    # Drop original nested column
    df_exploded = df_exploded.drop(columns=["chats"])

    # Merge back
    df_final = pd.concat(
        [df_exploded.reset_index(drop=True),
         chat_df.reset_index(drop=True)],
        axis=1
    )
    return df_final

def fetch_session_data(simulation_uuid):
    # API config
    url = f"{BASE_URL}/tenants/{simulation_uuid}/simulations"

    headers = {
        "X-API-KEY": SECRET_KEY
    }

    # Fetch API
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch data. "
            f"Status code: {response.status_code}, "
            f"Error: {response.text}"
        )

    data = response.json()

    if not data:
        return pd.DataFrame()

    # Main dataframe
    df = pd.DataFrame(data)
    return df