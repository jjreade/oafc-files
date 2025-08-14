import re
import pandas as pd
import streamlit as st
from io import BytesIO

# --------------------------
# Event parser function
# --------------------------
def parse_events(event_str):
    if not isinstance(event_str, str):
        return "", None  # No events

    event_map = {
        'start': {'pattern': r'^x(?:\s+\d+)?', 'emoji': '🟩', 'bgcolor': '#c6efce'},
        'sub_on': {'pattern': r'sub\s+(\d+)\s+on', 'emoji': '🟢', 'bgcolor': '#d9ead3'},
        'sub_off': {'pattern': r'off\s+(\d+)', 'emoji': '🔻', 'bgcolor': '#fff2cc'},
        'goal': {'pattern': r'g\s+(\d+)', 'emoji': '⚽'},
        'pen_goal': {'pattern': r'pen\s+(\d+)', 'emoji': '🟢⚽'},
        'own_goal': {'pattern': r'og\s+(\d+)', 'emoji': '🔴⚽'},
        'yellow': {'pattern': r'y\s+(\d+)', 'emoji': '🟨'},
        'red': {'pattern': r'r\s+(\d+)', 'emoji': '🟥'},
    }

    tokens = event_str.strip().split()
    parsed_tokens = []
    bgcolor = None

    i = 0
    while i < len(tokens):
        matched = False
        for ev, data in event_map.items():
            match = re.match(data['pattern'], " ".join(tokens[i:i+2]))
            if match:
                if match.groups():
                    parsed_tokens.append(f"{data['emoji']} {match.group(1)}")
                else:
                    parsed_tokens.append(data['emoji'])

                if 'bgcolor' in data and bgcolor is None:
                    bgcolor = data['bgcolor']

                length = len(match.group(0).split())
                i += length
                matched = True
                break

        if not matched:
            if tokens[i].isdigit():
                parsed_tokens.append(f"⚽ {tokens[i]}")
            else:
                parsed_tokens.append(tokens[i])
            i += 1

    return " ".join(parsed_tokens), bgcolor


# --------------------------
# Streamlit UI
# --------------------------
st.title("Matchday Squad Sheet")

uploaded_file = st.file_uploader("Upload squad CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Assume "Events" column exists for each player
    formatted_rows = []
    bg_colors = []

    for idx, row in df.iterrows():
        events, color = parse_events(row.get("Events", ""))
        formatted_rows.append(events)
        bg_colors.append(color)

    df["Events (Formatted)"] = formatted_rows
    df["BG Color"] = bg_colors

    # Show in Streamlit with colours
    st.write("### Squad")
    for idx, r in df.iterrows():
        bg = r["BG Color"] if pd.notnull(r["BG Color"]) else "white"
        st.markdown(
            f"<div style='background-color:{bg};padding:4px;border-radius:4px'>"
            f"{r['Name']} — {r['Events (Formatted)']}</div>",
            unsafe_allow_html=True
        )

    # Excel download with formatting
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name="Squad", index=False)
            workbook = writer.book
            worksheet = writer.sheets["Squad"]

            for idx, color in enumerate(df["BG Color"], start=2):  # Excel rows start at 1, plus header
                if pd.notnull(color):
                    fmt = workbook.add_format({'bg_color': color})
                    worksheet.set_row(idx-1, None, fmt)

        output.seek(0)
        return output

    st.download_button(
        label="Download Excel",
        data=to_excel(df),
        file_name="squad.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Legend
    st.write("### Legend")
    legend = {
        "🟩": "Start",
        "🟢": "Sub on",
        "🔻": "Sub off",
        "⚽": "Goal",
        "🟢⚽": "Penalty goal",
        "🔴⚽": "Own goal",
        "🟨": "Yellow card",
        "🟥": "Red card"
    }
    st.table(pd.DataFrame(list(legend.items()), columns=["Symbol", "Meaning"]))
