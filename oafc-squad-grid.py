import streamlit as st
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill
import re

# Load data
df = pd.read_csv("squad-grid-2025.csv")

# Map event keywords to icons and colours
event_map = {
    "start": {"icon": "🟩", "color": "90ee90"},  # Light green
    "goal": {"icon": "⚽", "color": "ffcc80"},   # Light orange
    "sub_on": {"icon": "⬆", "color": "add8e6"}, # Light blue
    "sub_off": {"icon": "⬇", "color": "ff7f7f"},# Light red
    "yellow": {"icon": "🟨", "color": "ffff00"},# Bright yellow
    "red": {"icon": "🟥", "color": "ff0000"},    # Bright red
    "unused": {"icon": "🚫", "color": "d3d3d3"} # Light gray
}

# Function to transform events into icon + minute and colour
def style_event(val):
    if pd.isna(val):
        return "", ""
    val_str = str(val).strip().lower()
    if val_str in ["", "nan"]:
        return "", ""
    # Match patterns
    if val_str == "x" or val_str.startswith("x "):
        return event_map["start"]["icon"] + val_str.replace("x", "").strip(), event_map["start"]["color"]
    if re.match(r"^g\s*\d*", val_str):  # 'g' at start, optional spaces, then digits
        return event_map["goal"]["icon"] + val_str.replace("g", "", 1).strip(), event_map["goal"]["color"]
    if val_str.startswith("off"):
        return event_map["sub_off"]["icon"] + val_str.replace("off", "").strip(), event_map["sub_off"]["color"]
    if "sub" in val_str and "on" in val_str:
        return event_map["sub_on"]["icon"] + val_str.replace("sub on", "").strip(), event_map["sub_on"]["color"]
    if val_str.startswith("y"):
        return event_map["yellow"]["icon"] + val_str.replace("y", "").strip(), event_map["yellow"]["color"]
    if val_str.startswith("r"):
        return event_map["red"]["icon"] + val_str.replace("r", "").strip(), event_map["red"]["color"]
    if val_str == "uu":
        return event_map["unused"]["icon"], event_map["unused"]["color"]
    return val, ""

# Columns
match_info_cols = ["Unnamed: 0", "Date", "opposition", "goals1", "goals2", "venue", "Kickoff", "attendance", "awayatt", "post.position", "referee"]
player_cols = [c for c in df.columns if c not in match_info_cols]

# Create a copy with icons
df_display = df.copy()
cell_colors = {}

for col in player_cols:
    for i, val in enumerate(df[col]):
        icon_val, bg_col = style_event(val)
        df_display.at[i, col] = icon_val
        if bg_col:
            cell_colors[(i, col)] = bg_col

# Streamlit UI
st.set_page_config(page_title="Oldham Athletic Season Events", layout="wide")
st.title("Oldham Athletic 2025 Season — Match Events")
st.write("Colour-coded match events with icons:")

# Apply Streamlit Styler for table display
def highlight_cells(val, row_idx, col_name):
    return f"background-color: #{cell_colors.get((row_idx, col_name), '')}" if (row_idx, col_name) in cell_colors else ""

styled_df = df_display.style.apply(lambda col: [highlight_cells(v, i, col.name) for i, v in enumerate(col)], axis=0)
st.dataframe(styled_df, use_container_width=True)

# Export to Excel with formatting
def export_to_excel():
    wb = openpyxl.Workbook()
    ws = wb.active

    # Write headers
    for j, col in enumerate(df_display.columns, start=1):
        ws.cell(row=1, column=j, value=col)

    # Write data with colour fills
    for i in range(len(df_display)):
        for j, col in enumerate(df_display.columns, start=1):
            cell_value = df_display.iloc[i, j-1]
            ws.cell(row=i+2, column=j, value=cell_value)
            if (i, col) in cell_colors:
                fill = PatternFill(start_color=cell_colors[(i, col)], end_color=cell_colors[(i, col)], fill_type="solid")
                ws.cell(row=i+2, column=j).fill = fill

    file_path = "oldham_events.xlsx"
    wb.save(file_path)
    return file_path

# Download button
excel_file = export_to_excel()
with open(excel_file, "rb") as f:
    st.download_button("📥 Download Excel with Colours", f, file_name="oldham_events.xlsx")
