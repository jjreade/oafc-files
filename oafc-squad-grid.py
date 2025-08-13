import streamlit as st
import pandas as pd
import re

# Load data
df = pd.read_csv("squad-grid-2025.csv")

# Define which columns contain player entries
match_info_cols = ["Unnamed: 0", "Date", "opposition", "goals1", "goals2", "venue", "Kickoff", "attendance", "awayatt", "post.position", "referee"]
player_columns = [c for c in df.columns if c not in match_info_cols]

# Event symbol mapping
event_symbols = {
    "g": "⚽",   # goal
    "y": "🟨",  # yellow card
    "r": "🟥",  # red card
    "og": "🥅", # own goal
    "in": "🔺", # sub on
    "out": "🔻" # sub off
}

# Regex pattern to capture event + minute
event_pattern = re.compile(r"(og|g|y|r|in|out)\s*(\d+)?", re.IGNORECASE)

def format_events(cell):
    if pd.isna(cell):
        return ""
    text = str(cell).strip()
    matches = event_pattern.findall(text)
    if not matches:
        return text  # No events found

    formatted = []
    for ev, minute in matches:
        ev = ev.lower()
        symbol = event_symbols.get(ev, ev)
        if minute:
            formatted.append(f"{symbol} {minute}")
        else:
            formatted.append(symbol)
    return " ".join(formatted)

# Apply formatting only to player columns
df[player_columns] = df[player_columns].applymap(format_events)

# Function to style cells based on events
def highlight_events(val):
    if isinstance(val, str):
        if "⚽" in val:
            return "background-color: lightgreen; font-weight: bold;"
        elif "🟨" in val:
            return "background-color: yellow; font-weight: bold;"
        elif "🟥" in val:
            return "background-color: red; color: white; font-weight: bold;"
        elif "🥅" in val:
            return "background-color: lightcoral; font-weight: bold;"
        elif "🔻" in val:
            return "background-color: orange; font-weight: bold;"
        elif "🔺" in val:
            return "background-color: lightblue; font-weight: bold;"
    return ""

# Function to style based on player role
def role_style(val):
    if isinstance(val, str):
        # Starter: contains events but no 🔺 (sub on)
        if any(sym in val for sym in ["⚽", "🟨", "🟥", "🥅", "🔻"]) and "🔺" not in val:
            return "font-weight: bold; color: black;"
        # Sub: has 🔺
        elif "🔺" in val:
            return "font-style: italic; color: dimgray;"
        # Unused: empty or no events
        elif val.strip() == "":
            return "color: lightgray;"
    return ""

# Apply styling to dataframe
styled_df = (
    df.style
    .applymap(highlight_events, subset=player_columns)
    .applymap(role_style, subset=player_columns)
)

st.title("Squad Grid with Events and Role-Based Styling")
st.dataframe(styled_df, use_container_width=True)

# Export to Excel
if st.button("Export to Excel"):
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font
    import tempfile

    wb = Workbook()
    ws = wb.active

    for r_idx, row in enumerate(df.itertuples(index=False), 1):
        for c_idx, value in enumerate(row, 1):
            cell = ws.cell(row=r_idx, column=c_idx, value=value)

            # Apply event background in Excel
            if isinstance(value, str):
                if "⚽" in value:
                    cell.fill = PatternFill(start_color="90EE90", fill_type="solid")
                elif "🟨" in value:
                    cell.fill = PatternFill(start_color="FFFF00", fill_type="solid")
                elif "🟥" in value:
                    cell.fill = PatternFill(start_color="FF0000", fill_type="solid")
                elif "🥅" in value:
                    cell.fill = PatternFill(start_color="F08080", fill_type="solid")
                elif "🔻" in value:
                    cell.fill = PatternFill(start_color="FFA500", fill_type="solid")
                elif "🔺" in value:
                    cell.fill = PatternFill(start_color="ADD8E6", fill_type="solid")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        wb.save(tmp.name)
        st.download_button(
            label="Download Excel file",
            data=open(tmp.name, "rb").read(),
            file_name="squad_grid.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
