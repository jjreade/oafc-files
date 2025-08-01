import streamlit as st
import pandas as pd
from datetime import datetime

# Load your 5,000-match dataset
matches_df = pd.read_csv("oafc-all-history-1907-1908-on.csv")  # assume columns like: match_id, date, team_home, team_away

# Create a searchable dropdown
matches_df['match_label'] = matches_df.apply(
    lambda row: f"{row['date']} — {row['team_home']} vs {row['team_away']}", axis=1
)
selected_match = st.selectbox("Search and select a match:", matches_df['match_label'])

# Form for input
with st.form("input_form"):
    performance = st.slider("Team performance rating", 1, 10)
    notes = st.text_area("Additional comments")
    submit = st.form_submit_button("Submit")

    if submit:
        # Extract match info
        match_id = matches_df[matches_df['match_label'] == selected_match]['match_id'].values[0]
        row = {
            "timestamp": datetime.now(),
            "match_id": match_id,
            "match_label": selected_match,
            "rating": performance,
            "notes": notes
        }
        # Append to CSV or send to Google Sheet
        pd.DataFrame([row]).to_csv("submissions.csv", mode='a', header=False, index=False)
        st.success("Submission received. Thank you!")
