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
Welcome to the **Latics Historical Match Input Form**.  
You will find in the first drop down menu every single match in Oldham Athletic's checkered history.
You can search by opponent and you'll have listed by date each match against that team.
The very oldest fixtures were typed into a spreadsheet manually from the Stewart Beckett history books.
However, adding in each player that played in each match, and each goalscorer (and time, where known), is a huge undertaking for any individual.
What we would like is to digitise this shared and glorious history of ours, and if we are able to share out this task amongst our fanbase, it will immeasurably help in terms of constructing such a database.
To do so will enable authoritative lists of appearances by players at the club, and also of goalscorers.
Please select a match you know some information about and fill in as many details as you can, including attendance figures, team colours, starting XI, and scorers.

All contributions will help build a detailed archive of Oldham Athletic's matches. Thank you!
""")

# Load your 5,000-match dataset
matches_df = pd.read_csv("oafc-all-history-1907-08-on.csv")  # assume columns like: match_id, date, team_home, team_away

# Load your player names from CSV
player_df = pd.read_csv("oafc-player-names-1989-on.csv")  # Replace with actual filename
player_names = sorted(player_df["x"].dropna().unique())

# Custom function: allow autocomplete-like dropdown with fallback
def player_input(label, key):
    selected = st.selectbox(
        f"Start typing to search {label} (or type your own):",
        options=[""] + player_names,
        index=0,
        key=f"{key}_selectbox"
    )
    if selected == "":
        return st.text_input(f"Enter {label}:", key=f"{key}_text")
    else:
        return selected

# Create a searchable dropdown
matches_df['match_label'] = matches_df.apply(
    lambda row: f"{row['Date']} — Latics vs {row['opposition']}", axis=1
)
selected_match = st.selectbox("Search and select a match:", matches_df['match_label'])

# Form for input
with st.form("input_form"):
    performance = st.slider("Team performance rating (your subjective rating)", 1, 10)
    # New: Attendance fields
    total_attendance = st.number_input("Total attendance", min_value=0, step=1)
    away_attendance = st.number_input("Away attendance", min_value=0, step=1)

    # who was in the lineup?
    oafc_no1 = player_input("Latics No.1","oafc_no1")
    oafc_no2 = player_input("Latics No.2","oafc_no2")
    oafc_no3 = player_input("Latics No.3","oafc_no3")
    oafc_no4 = player_input("Latics No.4","oafc_no4")
    oafc_no5 = player_input("Latics No.5","oafc_no5")
    oafc_no6 = player_input("Latics No.6","oafc_no6")
    oafc_no7 = player_input("Latics No.7","oafc_no7")
    oafc_no8 = player_input("Latics No.8","oafc_no8")
    oafc_no9 = player_input("Latics No.9","oafc_no9")
    oafc_no10 = player_input("Latics No.10","oafc_no10")
    oafc_no11 = player_input("Latics No.11","oafc_no11")
    oafc_usedsub1 = player_input("Latics Used substitute 1","oafc_usedsub1")
    oafc_usedsub2 = player_input("Latics Used substitute 2","oafc_usedsub2")
    oafc_usedsub3 = player_input("Latics Used substitute 3","oafc_usedsub3")
    oafc_usedsub4 = player_input("Latics Used substitute 4","oafc_usedsub4")
    oafc_usedsub5 = player_input("Latics Used substitute 5","oafc_usedsub5")
    oafc_unusedsubs = player_input("Latics Unused subs (list all if possible)","oafc_unusedsubs")
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
    oafc_scorer6 = st.text_input("Latics goalscorer 6")
    oafc_goaltime6 = st.text_input("Latics goal time 6")
    oafc_scorer7 = st.text_input("Latics goalscorer 7")
    oafc_goaltime7 = st.text_input("Latics goal time 7")
    oafc_scorer8 = st.text_input("Latics goalscorer 8")
    oafc_goaltime8 = st.text_input("Latics goal time 8")
    oafc_scorer9 = st.text_input("Latics goalscorer 9")
    oafc_goaltime9 = st.text_input("Latics goal time 9")
    oafc_scorer10 = st.text_input("Latics goalscorer 10")
    oafc_goaltime10 = st.text_input("Latics goal time 10")
    oafc_scorer5 = st.text_input("Latics goalscorer 5")
    oafc_goaltime5 = st.text_input("Latics goal time 5")
    
    # New: Kit colours
    oafc_colour = st.selectbox(
        "OAFC kit colour",
        [
            "Blue", "Blue and white stripes", "Blue and red hoops", "Red", "Red and white stripes", "Green", "White", 
            "Black", "Yellow", "Orange", "Purple", 
            "Claret", "Navy", "Sky Blue", "Amber", "Maroon", "Gold", "Grey", "Other"
        ]
    )
    opp_colour = st.selectbox(
        "Opponent kit colour",
        [
            "Red", "Red and white", "Red and blue", "Blue", "Blue and white", "Green", "White", "Black", "Yellow", 
            "Orange", "Purple", 
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
            oafc_unusedsubs,
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
            oafc_scorer6,
            oafc_goaltime6,
            oafc_scorer7,
            oafc_goaltime7,
            oafc_scorer8,
            oafc_goaltime8,
            oafc_scorer9,
            oafc_goaltime9,
            oafc_scorer10,
            oafc_goaltime10,
            oafc_scorer11,
            oafc_goaltime11,
            notes,
            author
        ]
        sheet.append_row(row_values)
        st.success("Submission received. Thank you!")
