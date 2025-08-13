import re
import pandas as pd
import streamlit as st

# Example event mapping
event_map = {
    "g": ("⚽", "#FFFFFF"),        # Goal
    "y": ("🟨", "#FFFFFF"),        # Yellow card
    "r": ("🟥", "#FFFFFF"),        # Red card
    "og": ("🔴⚽", "#FFFFFF"),      # Own goal (red football)
}

# Background colours for starting/sub statuses
status_bg = {
    "start": "#DFF0D8",     # Light green for starting
    "sub_on": "#D9EDF7",    # Light blue for sub on
    "sub_off": "#FCF8E3",   # Light yellow for sub off
}

def format_player_cell(cell):
    if not isinstance(cell, str) or cell.strip() == "":
        return "", ""

    text = cell
    bg_color = ""

    # Detect starting/sub-on/sub-off
    if re.search(r"\bx\b", text):
        bg_color = status_bg["start"]
    elif re.search(r"\bsub\s+\d+\s+on\b", text):
        bg_color = status_bg["sub_on"]
    elif re.search(r"\bx\s+\d+\s+off\b", text):
        bg_color = status_bg["sub_off"]

    # Remove start/sub markers from display text
    text = re.sub(r"\bx\b", "", text)
    text = re.sub(r"\bsub\s+\d+\s+on\b", "", text)
    text = re.sub(r"\bx\s+\d+\s+off\b", "", text)

    # Replace events with emojis
    def repl_event(match):
        code = match.group(1).lower()
        minute = match.group(2)
        if code in event_map:
            emoji, _ = event_map[code]
            return f"{emoji} {minute}"
        return match.group(0)

    text = re.sub(r"\b(g|y|r|og)\s*(\d+)", repl_event, text)

    return text.strip(), bg_color

def format_dataframe(df):
    # Define which columns contain player entries
    match_info_cols = ["Unnamed: 0", "Date", "opposition", "goals1", "goals2", "venue", "Kickoff", "attendance", "awayatt", "post.position", "referee", "stadium"]
    player_cols = [c for c in df.columns if c not in match_info_cols]
    styled_df = df.copy()

    styles = pd.DataFrame("", index=df.index, columns=df.columns)

    for col in player_cols:
        for i, val in df[col].items():
            new_val, bg = format_player_cell(val)
            styled_df.at[i, col] = new_val
            styles.at[i, col] = f"background-color: {bg}" if bg else ""

    return styled_df.style.apply(lambda _: styles, axis=None)

# Example Streamlit app
st.title("Squad Grid with Events & Status Colours")

df = pd.read_csv("squad-grid-2025.csv")
st.dataframe(format_dataframe(df), use_container_width=True)
