import streamlit as st
import pandas as pd

# ---------- LOAD DATA ----------
@st.cache_data
def load_data():
    # Replace with your CSV file path
    df = pd.read_csv("all-eng-matches.csv", parse_dates=["date"])
    return df

df = load_data()

# ---------- SIDEBAR SELECTION ----------
st.sidebar.header("Filters")

divisions = sorted(df["div"].unique())
seasons = sorted(df["season"].unique())

# Find the index for 'div4'
default_div_index = divisions.index("div4") if "div4" in divisions else 0

# Find the index for season 2025 (assuming it's stored as an int)
default_season_index = seasons.index(2025) if 2025 in seasons else 0

selected_div = st.sidebar.selectbox("Select Division", divisions, index=default_div_index)
selected_season = st.sidebar.selectbox("Select Season", seasons, index=default_season_index)

df_filtered = df[(df["div"] == selected_div) & (df["season"] == selected_season)]

df_filtered["date"] = df_filtered["date"].dt.strftime("%Y-%m-%d")

# Get the full league name for the selected div
full_division_name = df_filtered["division"].iloc[0]

# ---------- MAIN TABS ----------
tab1, tab2 = st.tabs(["📅 Matches & Predictions", "📊 League Table"])

# ---------- TAB 1 ----------
with tab1:
    st.subheader(f"Matches — {full_division_name}, {selected_season}")
    cols_to_show = ["date", "team1", "team2", "forcPH", "forcPD", "forcPA", "xG1", "xG2", "goals1", "goals2"]
    st.dataframe(df_filtered[cols_to_show].sort_values("date"))

# ---------- TAB 2 ----------
with tab2:
    st.subheader(f"League Table — {full_division_name}, {selected_season}")

    # Predicted table
    pred_points_t1 = df_filtered.groupby("team1").apply(lambda x: (3 * x["forcPH"] + 1 * x["forcPD"]).sum()).reset_index(name="exp_points_home")
    pred_points_t2 = df_filtered.groupby("team2").apply(lambda x: (3 * x["forcPA"] + 1 * x["forcPD"]).sum()).reset_index(name="exp_points_away")
    pred_points = pd.merge(pred_points_t1, pred_points_t2, left_on="team1", right_on="team2", how="outer")
    pred_points["team"] = pred_points["team1"].combine_first(pred_points["team2"])
    pred_points["exp_points"] = pred_points["exp_points_home"].fillna(0) + pred_points["exp_points_away"].fillna(0)
    pred_points = pred_points[["team", "exp_points"]]

    # Expected goal difference
    exp_gd_t1 = df_filtered.groupby("team1").apply(lambda x: (x["xG1"] - x["xG2"]).sum()).reset_index(name="exp_gd_home")
    exp_gd_t2 = df_filtered.groupby("team2").apply(lambda x: (x["xG2"] - x["xG1"]).sum()).reset_index(name="exp_gd_away")
    exp_gd = pd.merge(exp_gd_t1, exp_gd_t2, left_on="team1", right_on="team2", how="outer")
    exp_gd["team"] = exp_gd["team1"].combine_first(exp_gd["team2"])
    exp_gd["exp_gd"] = exp_gd["exp_gd_home"].fillna(0) + exp_gd["exp_gd_away"].fillna(0)
    exp_gd = exp_gd[["team", "exp_gd"]]

    predicted_table = pd.merge(pred_points, exp_gd, on="team")
    predicted_table = predicted_table.sort_values(by=["exp_points", "exp_gd"], ascending=False).reset_index(drop=True)
    predicted_table.index = predicted_table.index + 1
    
    st.markdown("**Predicted Table**")
    st.dataframe(predicted_table)

    # Actual table (if actual results available)
    if "goals1" in df_filtered.columns and not df_filtered["goals1"].isna().all():
        actual_points_t1 = df_filtered.groupby("team1").apply(
            lambda x: (3*(x["goals1"] > x["goals2"]) + 1*(x["goals1"] == x["goals2"])).sum()
        ).reset_index(name="points_home")
        actual_points_t2 = df_filtered.groupby("team2").apply(
            lambda x: (3*(x["goals2"] > x["goals1"]) + 1*(x["goals2"] == x["goals1"])).sum()
        ).reset_index(name="points_away")
        actual_points = pd.merge(actual_points_t1, actual_points_t2, left_on="team1", right_on="team2", how="outer")
        actual_points["team"] = actual_points["team1"].combine_first(actual_points["team2"])
        actual_points["points"] = actual_points["points_home"].fillna(0) + actual_points["points_away"].fillna(0)
        actual_points = actual_points[["team", "points"]]

        # Actual goal difference
        actual_gd_t1 = df_filtered.groupby("team1").apply(lambda x: (x["goals1"] - x["goals2"]).sum()).reset_index(name="gd_home")
        actual_gd_t2 = df_filtered.groupby("team2").apply(lambda x: (x["goals2"] - x["goals1"]).sum()).reset_index(name="gd_away")
        actual_gd = pd.merge(actual_gd_t1, actual_gd_t2, left_on="team1", right_on="team2", how="outer")
        actual_gd["team"] = actual_gd["team1"].combine_first(actual_gd["team2"])
        actual_gd["gd"] = actual_gd["gd_home"].fillna(0) + actual_gd["gd_away"].fillna(0)
        actual_gd = actual_gd[["team", "gd"]]

        actual_table = pd.merge(actual_points, actual_gd, on="team")
        actual_table = actual_table.sort_values(by=["points", "gd"], ascending=False).reset_index(drop=True)
        actual_table.index = actual_table.index + 1

        st.markdown("**Actual Table**")
        st.dataframe(actual_table)
