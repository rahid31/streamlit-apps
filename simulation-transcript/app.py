import streamlit as st
import pandas as pd
from fetch_api import (
    fetch_and_flatten_chat_data,
    fetch_session_data
)
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent

user_url = str(BASE_DIR / "data/image/user-png-icon-user-2-icon-png-file-512x512-pixel-512.png")
avatar_url = str(BASE_DIR / "data/image/nexa_icon_256.png")
page_icon = Image.open(BASE_DIR / "data/image/lx_icon_192.png")

st.set_page_config(
    layout="centered",
    initial_sidebar_state="collapsed",
    page_title="Learnext - Simulations Transcript",
    page_icon=page_icon
)

# Hide default Streamlit UI elements
st.markdown(
    """
    <style>
    header { visibility: hidden; }
    footer { visibility: hidden; }
    .st-emotion-cache-z5fcl4 { display: none; }
    .viewerBadge_container__1QSob {display: none !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stThemeToggle"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# Read simulation id from URL
simulation_uuid = st.query_params.get("simulation_uuid")

try:
    if '-' in simulation_uuid:
        fact_id = int(simulation_uuid.split('-')[0])
    else:
        fact_id = int(simulation_uuid)

    simulation_uuid = int(fact_id)
except (TypeError, ValueError):
    simulation_uuid = None

if simulation_uuid is None:
    st.error("No simulation_uuid provided in the URL.")
    st.stop()


@st.cache_data
def load_chat_data(simulation_uuid):

    try:
        df = fetch_and_flatten_chat_data(simulation_uuid)

        if isinstance(df, pd.DataFrame):
            return df

        return pd.DataFrame()

    except Exception as e:
        st.error(f"Failed loading chat data: {e}")
        return pd.DataFrame()


@st.cache_data
def load_session_data(simulation_uuid):

    try:
        df = fetch_session_data(simulation_uuid)

        if isinstance(df, pd.DataFrame):
            return df

        return pd.DataFrame()

    except Exception:
        return pd.DataFrame()
    

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")


# Load transcript and session details
df_chat = load_chat_data(simulation_uuid)
df_session = load_session_data(simulation_uuid)

# Transcript data is required for the page to render
if df_chat.empty:
    st.warning("No transcript found for this simulation.")
    st.stop()

# Default values when session details are unavailable
chat_topic = "Topic not available"
user_email = "-"
created_at = "-"
feedback = "Feedback not available."

if not df_session.empty:

    row = df_session.iloc[0]

    chat_topic = row.get(
        "lesson_name",
        chat_topic
    )

    user_email = row.get(
        "user_email",
        "-"
    )

    created_at = row.get(
        "created_at",
        "-"
    )

    feedback = row.get(
        "feedback",
        "Feedback not available."
    )

    suggested_answer = row.get(
        "suggested_answer",
        "Suggested Answer not available"
    )

    score = row.get(
        "score",
        None
    )

    passing_grade = row.get(
        "passing_grade",
        None
    )

def check_status(score):
    if score >= passing_grade:
        return "Passed"
    else:
        return "Failed"
    
def justified_text(text):
    st.markdown(
        f"""
        <div style="text-align: justify; white-space: pre-wrap;">
            {text}
        </div>
        """,
        unsafe_allow_html=True
    )

st.subheader(chat_topic)

csv = convert_df(df_chat)

st.download_button(
    "Download CSV",
    data=csv,
    file_name=f"simulation_transcript_{simulation_uuid}.csv",
    mime="text/csv"
)

tabs = st.tabs([
    "Transcript",
    "Feedback",
    "Suggested Answer",
    "Session Details"
])

with tabs[0]:

    for _, row in df_chat.iterrows():

        avatar_message = row.get("avatar_message")
        user_message = row.get("user_message")

        if pd.notna(avatar_message) and str(avatar_message).strip():

            with st.chat_message("assistant", avatar=avatar_url):
                st.write(avatar_message)

        if pd.notna(user_message) and str(user_message).strip():

            with st.chat_message("user", avatar=user_url):
                st.write(user_message)

with tabs[1]:
    justified_text(feedback)

with tabs[2]:
    justified_text(suggested_answer)

with tabs[3]:
    status = check_status(score)

    st.write(f"**User:** {user_email}")
    st.write(f"**Skor Akhir:** {score}")

    if status.lower() == "passed":
        st.success(f"Status: {status}")
    else:
        st.error(f"**Status:** {status}")

    st.write(f"**Created At:** {created_at}")


st.divider()

st.image(
    "https://raw.githubusercontent.com/rahid31/gk-gaia-transcript/master/data/image/lx_primary_256.png",
    width=120
)