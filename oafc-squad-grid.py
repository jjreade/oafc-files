import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Oldham Athletic Squad Grid", layout="wide")

# Load CSV
df = pd.read_csv("squad-grid-2025.csv")

# Identify player columns (exclude non-player columns)
non_player_cols = ["Unnamed: 0", "Date", "opposition", "goals1", "goals2", "venue", "Kickoff", "attendance", "awayatt", "post.position" ,"opp.post.position", "ftscore1", "ftscore2", "htscore1", "htscore2", "possession1", "possession2", "shotson1", "shotson2", "shotsoff1", "shotsoff2", "corners1", "corners2", "referee", "stadium"]
player_cols = [col for col in df.columns if col not in non_player_cols]

# Event formatting function
def format_cell(cell):
    if pd.isna(cell) or str(cell).strip() == "":
        return ""
    
    text = str(cell)
    events = []

    # Start
    if re.search(r"\bx\b", text):
        events.append("🟦")  # Blue square for starting

    # Sub on
    if re.search(r"\bsub\s*(\d+)\s*on\b", text, re.IGNORECASE):
        time = re.search(r"\bsub\s*(\d+)\s*on\b", text, re.IGNORECASE).group(1)
        events.append(f"🟩{time}'")  # Green square + time

    # Sub off
    if re.search(r"\b(\d+)\s*off\b", text, re.IGNORECASE):
        time = re.search(r"\b(\d+)\s*off\b", text, re.IGNORECASE).group(1)
        events.append(f"⬜{time}'")  # White square + time

    # Goals
    for match in re.finditer(r"\bg\s*(\d+)", text, re.IGNORECASE):
        time = match.group(1)
        events.append(f"⚽{time}'")

    # Own goals
    for match in re.finditer(r"\bog\s*(\d+)", text, re.IGNORECASE):
        time = match.group(1)
        events.append(f"🔴⚽{time}'")

    # Yellow cards
    for match in re.finditer(r"\byel\b", text, re.IGNORECASE):
        events.append("🟨")

    # Red cards
    for match in re.finditer(r"\bred\b", text, re.IGNORECASE):
        events.append("🟥")

    # Unused sub
    if re.fullmatch(r"sub", text, re.IGNORECASE):
        events.append("🪑")  # Bench icon

    return " ".join(events)

# Apply formatting only to player columns
df_formatted = df.copy()
for col in player_cols:
    df_formatted[col] = df[col].apply(format_cell)

# Show in Streamlit
st.dataframe(df_formatted)

# Download as Excel
def to_excel(df):
    from io import BytesIO
    import openpyxl
    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    return output.getvalue()

st.download_button(
    label="Download as Excel",
    data=to_excel(df_formatted),
    file_name="squad_grid_formatted.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
