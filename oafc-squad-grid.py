import streamlit as st
import pandas as pd

# Load data
df = pd.read_csv("squad-grid-2025.csv")

# Function to map events to colours
def highlight_events(val):
    if pd.isna(val):
        return ""
    val_str = str(val).strip().lower()
    if val_str == "" or val_str == "nan":
        return ""
    if "g" in val_str and not val_str.startswith("sub"):
        return "background-color: gold; font-weight: bold"
    elif val_str.startswith("off"):
        return "background-color: lightcoral"
    elif "sub" in val_str and "on" in val_str:
        return "background-color: lightblue"
    elif val_str == "x" or val_str.startswith("x "):
        return "background-color: lightgreen"
    elif val_str == "uu":  # unused sub
        return "background-color: lightgray"
    else:
        return ""

# Columns for match info
match_info_cols = ["Unnamed: 0", "Date", "opposition", "goals1", "goals2", "venue", "Kickoff", "attendance", "awayatt", "post.position"]
player_cols = [c for c in df.columns if c not in match_info_cols]

# Apply styling
styled_df = df.style.applymap(highlight_events, subset=player_cols)

# Streamlit UI
st.set_page_config(page_title="Oldham Athletic Season Events", layout="wide")
st.title("Oldham Athletic 2025 Season — Match Events")
st.write("Colour-coded match events by player:")

st.dataframe(styled_df, use_container_width=True)
