import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# Load Google credentials from Streamlit secrets
json_creds = st.secrets["google_service_account"]

# Define scope and credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_dict(json_creds, scope)

client = gspread.authorize(creds)

# Open the sheet by name or ID
sheet = client.open_by_key("1NAXfRtRqvHda4uyKqdOTgxxSeEwKdLNyUKNl8A-owxQ").sheet1

# --- Title and Introduction ---
st.title("Latics Match Input Form")

st.markdown("""
Welcome to the **Latics Match Input Form**.  
Please select a match you know some information about and fill in as many details as you can, including attendance figures, team colours, starting XI, and scorers.

All contributions will help build a detailed archive of Oldham Athletic's matches. Thank you!
""")

# Load your 5,000-match dataset
matches_df = pd.read_csv("oafc-all-history-1907-08-on.csv")  # assume columns like: match_id, date, team_home, team_away

# Create a searchable dropdown
matches_df['match_label'] = matches_df.apply(
    lambda row: f"{row['Date']} — Latics vs {row['opposition']}", axis=1
)
selected_match = st.selectbox("Search and select a match:", matches_df['match_label'])

# Form for input
with st.form("input_form"):
    performance = st.slider("Team performance rating", 1, 10)
    # New: Attendance fields
    total_attendance = st.number_input("Total attendance", min_value=0, step=1)
    away_attendance = st.number_input("Away attendance", min_value=0, step=1)

    # who was in the lineup?
    oafc_no1 = st.text_input("Latics No.1")
    oafc_no2 = st.text_input("Latics No.2")
    oafc_no3 = st.text_input("Latics No.3")
    oafc_no4 = st.text_input("Latics No.4")
    oafc_no5 = st.text_input("Latics No.5")
    oafc_no6 = st.text_input("Latics No.6")
    oafc_no7 = st.text_input("Latics No.7")
    oafc_no8 = st.text_input("Latics No.8")
    oafc_no9 = st.text_input("Latics No.9")
    oafc_no10 = st.text_input("Latics No.10")
    oafc_no11 = st.text_input("Latics No.11")
    oafc_usedsub1 = st.text_input("Latics Used substitute 1")
    oafc_usedsub2 = st.text_input("Latics Used substitute 2")
    oafc_usedsub3 = st.text_input("Latics Used substitute 3")
    oafc_usedsub4 = st.text_input("Latics Used substitute 4")
    oafc_usedsub5 = st.text_input("Latics Used substitute 5")
    oafc_scorer1 = st.text_input("Latics goalscorer 1")
    oafc_goaltime1 = st.text_input("Latics goal time 1")
    oafc_scorer2 = st.text_input("Latics goalscorer 2")
    oafc_goaltime2 = st.text_input("Latics goal time 2")
    oafc_scorer3 = st.text_input("Latics goalscorer 3")
    oafc_goaltime3 = st.text_input("Latics goal time 3")
    oafc_scorer4 = st.text_input("Latics goalscorer 4")
    oafc_goaltime4 = st.text_input("Latics goal time 4")
    oafc_scorer5 = st.text_input("Latics goalscorer 5")
    oafc_goaltime5 = st.text_input("Latics goal time 5")
    
    # New: Kit colours
    oafc_colour = st.selectbox(
        "OAFC kit colour",
        [
            "Red", "Blue", "Green", "White", "Black", "Yellow", "Orange", "Purple", 
            "Claret", "Navy", "Sky Blue", "Amber", "Maroon", "Gold", "Grey", "Other"
        ]
    )
    opp_colour = st.selectbox(
        "Opponent kit colour",
        [
            "Red", "Blue", "Green", "White", "Black", "Yellow", "Orange", "Purple", 
            "Claret", "Navy", "Sky Blue", "Amber", "Maroon", "Gold", "Grey", "Other"
        ]
    )
    notes = st.text_area("Additional comments")
    author = st.text_area("Your name (if you want credit, otherwise leave blank)")
    submit = st.form_submit_button("Submit")

    if submit:
        # Extract match info
        # match_id = matches_df[matches_df['match_label'] == selected_match]['match_id'].values[0]
        match_row = matches_df[matches_df['match_label'] == selected_match].iloc[0]
        # NEW - writing to Google Sheet
        row_values = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            selected_match,
            performance,
            total_attendance,
            away_attendance,
            oafc_colour,
            opp_colour,
            oafc_no1,
            oafc_no2,
            oafc_no3,
            oafc_no4,
            oafc_no5,
            oafc_no6,
            oafc_no7,
            oafc_no8,
            oafc_no9,
            oafc_no10,
            oafc_no11,
            oafc_usedsub1,
            oafc_usedsub2,
            oafc_usedsub3,
            oafc_usedsub4,
            oafc_usedsub5,
            oafc_scorer1,
            oafc_goaltime1,
            oafc_scorer2,
            oafc_goaltime2,
            oafc_scorer3,
            oafc_goaltime3,
            oafc_scorer4,
            oafc_goaltime4,
            oafc_scorer5,
            oafc_goaltime5,
            notes
        ]
        sheet.append_row(row_values)
        st.success("Submission received. Thank you!")
