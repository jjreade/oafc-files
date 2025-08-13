import re
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Oldham Athletic Squad Grid", layout="wide")

# ---------- Load data ----------
df = pd.read_csv("squad-grid-2025.csv")

# ---------- Identify player columns (skip metadata/referee/etc.) ----------
META_COLS_KNOWN = {
    "unnamed: 0","date","opposition","goals1","goals2","venue","kickoff",
    "attendance","awayatt","post.position","opp.post.position","referee",
    "result","notes","competition","round"
}
def get_player_cols(df_: pd.DataFrame):
    meta_present = {c for c in df_.columns if c.lower() in META_COLS_KNOWN}
    with_space = [c for c in df_.columns if (" " in c and c not in meta_present)]
    return with_space if with_space else [c for c in df_.columns if c not in meta_present]

player_cols = get_player_cols(df)

# ---------- Regex to parse events (handles messy spacing) ----------
EVENT_RE = re.compile(
    r'(?P<sub_on>\bsub\s*\d*\s*on\s*(?P<sub_on_min>\d+)(?:\s*\d+)?\b)|'  # sub 2 on 68 2
    r'(?P<off>\boff\s*(?P<off_min>\d+)\b)|'                               # off 61
    r'(?P<og>\bog\s*(?P<og_min>\d+)\b)|'                                  # og 12
    r'(?P<g>\bg\s*(?P<g_min>\d+)\b)|'                                     # g 62 / g62
    r'(?P<y>\by\s*(?P<y_min>\d+)?\b)|'                                    # y / y 50
    r'(?P<r>\br\s*(?P<r_min>\d+)?\b)|'                                    # r / r 90
    r'(?P<uu>\buu\b)|'                                                    # uu
    r'(?P<x>\bx\b)',                                                      # x
    re.IGNORECASE
)

# ---------- Base background colours for role/status ----------
BG_START  = "#DFF0D8"  # light green
BG_SUB_ON = "#D9EDF7"  # light blue
BG_SUB_OFF= "#FCF8E3"  # pale yellow
BG_UNUSED = "#E6E6E6"  # light grey

def format_cell(raw) -> tuple[str, str]:
    if raw is None:
        return "", ""
    s = str(raw).strip().lower()
    if not s or s == "nan":
        return "", ""

    unused   = bool(re.search(r'\buu\b', s))
    sub_on_m = re.search(r'\bsub\s*\d*\s*on\s*(\d+)(?:\s*\d+)?', s)
    off_m    = re.search(r'\boff\s*(\d+)\b', s)
    started  = bool(re.search(r'\bx\b', s))

    # Background precedence
    if unused:
        bg = BG_UNUSED
    elif sub_on_m:
        bg = BG_SUB_ON
    elif off_m:
        bg = BG_SUB_OFF
    elif started:
        bg = BG_START
    else:
        bg = ""

    # Build visible events in original order
    parts = []
    for m in EVENT_RE.finditer(s):
        gd = m.groupdict()
        if gd["sub_on"]:
            parts.append(f"🔺 {gd['sub_on_min']}")
        elif gd["off"]:
            parts.append(f"🔻 {gd['off_min']}")
        elif gd["og"]:
            parts.append(f"🔴⚽ {gd['og_min']}")
        elif gd["g"]:
            parts.append(f"⚽ {gd['g_min']}")
        elif gd["y"]:
            parts.append(f"🟨 {gd['y_min']}" if gd["y_min"] else "🟨")
        elif gd["r"]:
            parts.append(f"🟥 {gd['r_min']}" if gd["r_min"] else "🟥")
        elif gd["uu"]:
            parts = ["🚫"]  # unused overrides display
        elif gd["x"]:
            if not unused and not sub_on_m:
                parts.insert(0, "🟩")

    return " ".join(parts).strip(), bg

# ---------- Build display DF + background map ----------
df_display = df.copy()
bg_map: dict[tuple[int, str], str] = {}

for col in player_cols:
    for i, val in df[col].items():
        disp, bg = format_cell(val)
        df_display.at[i, col] = disp
        if bg:
            bg_map[(i, col)] = bg

df_display = df_display.astype(str)

# ---------- Style for Streamlit ----------
def col_bg_styler(col: pd.Series):
    return [f"background-color: {bg_map.get((i, col.name), '')}" for i in col.index]

styled = df_display.style.apply(col_bg_styler, axis=0, subset=player_cols)

st.title("Oldham Athletic — Season Grid (emojis + role backgrounds)")
st.dataframe(styled, use_container_width=True)

# ---------- Legend ----------
legend_items = [
    "🟩 Start",
    "🔺 Sub on (minute)",
    "🔻 Sub off (minute)",
    "⚽ Goal (minute)",
    "🔴⚽ Own Goal (minute)",
    "🟨 Yellow Card (minute)",
    "🟥 Red Card (minute)",
    "🚫 Unused Sub"
]
legend_text = "\n".join(legend_items)
st.markdown("### Legend")
st.markdown("```\n" + legend_text + "\n```")

# ---------- Excel export ----------
def export_excel_with_bg_and_legend(df_disp: pd.DataFrame, bg_lookup: dict, filename: str = "squad_grid.xlsx"):
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill
    wb = Workbook()
    ws = wb.active

    # headers
    for j, col in enumerate(df_disp.columns, start=1):
        ws.cell(row=1, colum
