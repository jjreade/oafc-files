import streamlit as st
import pandas as pd
import altair as alt

st.title("Player Performance Tracker")

# --- Load the file directly (adjust path as needed) ---
DATA_PATH = "player-match-ratings.csv"
df = pd.read_csv(DATA_PATH)

# Ensure match_date is datetime
date_ok = False
if "match_date" in df.columns:
    df["match_date"] = pd.to_datetime(df["match_date"], errors="coerce")
    if df["match_date"].notna().any():
        date_ok = True

# Sanitize column names for Altair (replace . with _)
df = df.rename(columns=lambda c: c.replace(".", "_"))

# Identify score columns
score_columns = [col for col in df.columns if col.startswith("cat_") or col.endswith("_score") or col.startswith("player_match_")]

# Sidebar selections
default_team = "Oldham Athletic"
teams_sorted = sorted(df["team_name"].unique())

team_name = st.selectbox(
    "Select team",
    teams_sorted,
    index=teams_sorted.index(default_team) if default_team in teams_sorted else 0
)
available_players = df.loc[df["team_name"] == team_name, "player_name"].unique()
player_name = st.selectbox("Select player", sorted(available_players))
score_metric = st.selectbox("Select score metric", score_columns)

# Filter for player (strip spaces just in case)
player_df = df[df["player_name"].str.strip() == player_name.strip()].copy()

# Convert score column to numeric (fixes string issues)
player_df[score_metric] = pd.to_numeric(player_df[score_metric], errors="coerce")

# Build match label
if {"home_team_home_team_name", "away_team_away_team_name", "match_date"} <= set(player_df.columns):
    player_df["match_label"] = (
        player_df["home_team_home_team_name"] + " vs " + player_df["away_team_away_team_name"] +
        " (" + player_df["match_date"].dt.strftime("%Y-%m-%d") + ")"
    )
elif {"teams", "match_date"} <= set(player_df.columns):
    player_df["match_label"] = (
        player_df["teams"] + " (" + player_df["match_date"].dt.strftime("%Y-%m-%d") + ")"
    )
else:
    # fallback to just date if nothing else available
    player_df["match_label"] = player_df["match_date"].dt.strftime("%Y-%m-%d")

# Sort by date if available
if date_ok:
    player_df = player_df.sort_values("match_date")
    x_axis = alt.X("match_date:T", title="Date")
else:
    player_df = player_df.reset_index().rename(columns={"index": "match_order"})
    x_axis = alt.X("match_order:O", title="Match order")

# --- Diagnostics / status box ---
matches_count = len(player_df)
if player_df.empty:
    st.error(f"⚠️ No rows found for {player_name}. Check spelling/filters.")
elif player_df[score_metric].isna().all():
    st.error(f"⚠️ All values for {score_metric} are missing or non-numeric.")
else:
    st.success(
        f"✅ Showing **{score_metric}** for **{player_name}** "
        f"over {matches_count} matches. "
        f"{'Dates parsed correctly.' if date_ok else 'Using match order instead of dates.'}"
    )
# st.write("Debug preview (first 10 rows):")
# st.write(player_df[["match_date", score_metric, "match_label"]].head(10))
# st.write("Shape:", player_df.shape)

# --- Altair line plot ---
if matches_count > 0 and not player_df[score_metric].isna().all():
    base = alt.Chart(player_df).encode(
        x=x_axis,
        y=alt.Y(score_metric, title="Score", type="quantitative"),
        tooltip=["match_label", score_metric]
    )
    points = base.mark_point(size=80, filled=True, color="steelblue")
    line   = base.mark_line(color="orange")
    chart = points + line
    st.altair_chart(chart, use_container_width=True)

    # Debug preview
    with st.expander("See match-by-match scores"):
      # Select only relevant columns to display
      display_cols = ["match_date", "match_label", "team_name", "player_name"] + score_columns
      display_df = player_df[display_cols].sort_values("match_date")
  
      # Identify numeric columns (to avoid "0-0" strings or similar)
      numeric_cols = display_df.select_dtypes(include=["number"]).columns.tolist()
  
      # Style only the numeric ones
      styled_df = (
          display_df.style
          .background_gradient(
              subset=numeric_cols,
              cmap="RdYlGn",   # red = low, green = high
              axis=0
          )
          .format(precision=1)  # optional: decimals
      )
  
      st.dataframe(styled_df, use_container_width=True, height=600)
