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

# Format matchday table probabilities
matches_display = df_filtered.copy()
matches_display["forcPH"] = (matches_display["forcPH"] * 100).round(1).astype(str) + "%"
matches_display["forcPD"] = (matches_display["forcPD"] * 100).round(1).astype(str) + "%"
matches_display["forcPA"] = (matches_display["forcPA"] * 100).round(1).astype(str) + "%"
matches_display["xG1"] = matches_display["xG1"].round(2)
matches_display["xG2"] = matches_display["xG2"].round(2)

# Get the full league name for the selected div
full_division_name = df_filtered["division"].iloc[0]

# ---------- MAIN TABS ----------
tab1, tab2 = st.tabs(["📅 Matches & Predictions", "📊 League Table"])

# ---------- TAB 1 ----------
with tab1:
    st.subheader(f"Matches — {full_division_name}, {selected_season}")
    # cols_to_show = ["date", "team1", "team2", "forcPH", "forcPD", "forcPA", "xG1", "xG2", "goals1", "goals2"]
    # st.dataframe(df_filtered[cols_to_show].sort_values("date"))
    st.dataframe(
        matches_display[["date", "team1", "team2", "forcPH", "forcPD", "forcPA", "xG1", "xG2", "goals1", "goals2"]],
        hide_index=True
    )

# ---------- TAB 2 ----------
with tab2:
    st.subheader(f"League Table — {full_division_name}, {selected_season}")

    played = df_filtered.dropna(subset=["goals1", "goals2"])
    unplayed = df_filtered[df_filtered[["goals1", "goals2"]].isna().any(axis=1)]

    # --- Actual table ---
    if played.empty:
        actual_points = pd.DataFrame(columns=["team", "points"])
    else:
        actual_points_t1 = (
            played.groupby("team1")
            .apply(lambda x: (3*(x["goals1"] > x["goals2"]) + 1*(x["goals1"] == x["goals2"])).sum())
            .rename("points_home")
            .reset_index()
        )
    
        actual_points_t2 = (
            played.groupby("team2")
            .apply(lambda x: (3*(x["goals2"] > x["goals1"]) + 1*(x["goals2"] == x["goals1"])).sum())
            .rename("points_away")
            .reset_index()
        )
    
        actual_points = pd.merge(actual_points_t1, actual_points_t2, left_on="team1", right_on="team2", how="outer")
        actual_points["team"] = actual_points["team1"].combine_first(actual_points["team2"])
        actual_points["points"] = actual_points["points_home"].fillna(0) + actual_points["points_away"].fillna(0)
        actual_points = actual_points[["team", "points"]]
    
        actual_gd_t1 = played.groupby("team1").apply(lambda x: (x["goals1"] - x["goals2"]).sum()).reset_index(name="gd_home")
        actual_gd_t2 = played.groupby("team2").apply(lambda x: (x["goals2"] - x["goals1"]).sum()).reset_index(name="gd_away")
        actual_gd = pd.merge(actual_gd_t1, actual_gd_t2, left_on="team1", right_on="team2", how="outer")
        actual_gd["team"] = actual_gd["team1"].combine_first(actual_gd["team2"])
        actual_gd["gd"] = actual_gd["gd_home"].fillna(0) + actual_gd["gd_away"].fillna(0)
        actual_gd = actual_gd[["team", "gd"]]
    
        actual_table = pd.merge(actual_points, actual_gd, on="team").fillna(0)
        actual_table = actual_table.sort_values(by=["points", "gd"], ascending=False).reset_index(drop=True)
        actual_table.index = actual_table.index + 1

    st.markdown("**Actual Table (Played Matches So Far)**")
    st.dataframe(actual_table)

    # --- Predicted table (full season) ---
    pred_points_t1 = df_filtered.groupby("team1").apply(lambda x: (3 * x["forcPH"] + 1 * x["forcPD"]).sum()).reset_index(name="exp_points_home")
    pred_points_t2 = df_filtered.groupby("team2").apply(lambda x: (3 * x["forcPA"] + 1 * x["forcPD"]).sum()).reset_index(name="exp_points_away")
    pred_points = pd.merge(pred_points_t1, pred_points_t2, left_on="team1", right_on="team2", how="outer")
    pred_points["team"] = pred_points["team1"].combine_first(pred_points["team2"])
    pred_points["exp_points"] = pred_points["exp_points_home"].fillna(0) + pred_points["exp_points_away"].fillna(0)
    pred_points = pred_points[["team", "exp_points"]]

    exp_gd_t1 = df_filtered.groupby("team1").apply(lambda x: (x["xG1"] - x["xG2"]).sum()).reset_index(name="exp_gd_home")
    exp_gd_t2 = df_filtered.groupby("team2").apply(lambda x: (x["xG2"] - x["xG1"]).sum()).reset_index(name="exp_gd_away")
    exp_gd = pd.merge(exp_gd_t1, exp_gd_t2, left_on="team1", right_on="team2", how="outer")
    exp_gd["team"] = exp_gd["team1"].combine_first(exp_gd["team2"])
    exp_gd["exp_gd"] = exp_gd["exp_gd_home"].fillna(0) + exp_gd["exp_gd_away"].fillna(0)
    exp_gd = exp_gd[["team", "exp_gd"]]

    predicted_table = pd.merge(pred_points, exp_gd, on="team").fillna(0)
    predicted_table = predicted_table.sort_values(by=["exp_points", "exp_gd"], ascending=False).reset_index(drop=True)
    predicted_table.index = predicted_table.index + 1

    st.markdown("**Predicted Table (Full Season Forecast)**")
    st.dataframe(predicted_table)

    # --- Hybrid table: actual points so far + predicted points for unplayed matches ---
    # Actual points so far
    points_actual = actual_points.rename(columns={"points": "points_actual"})

    # Predicted points for unplayed matches
    pred_home = unplayed.groupby("team1").apply(lambda x: (3 * x["forcPH"] + 1 * x["forcPD"]).sum()).reset_index(name="points_home")
    pred_away = unplayed.groupby("team2").apply(lambda x: (3 * x["forcPA"] + 1 * x["forcPD"]).sum()).reset_index(name="points_away")
    points_pred = pd.merge(pred_home, pred_away, left_on="team1", right_on="team2", how="outer")
    points_pred["team"] = points_pred["team1"].combine_first(points_pred["team2"])
    points_pred["points_predicted"] = points_pred["points_home"].fillna(0) + points_pred["points_away"].fillna(0)
    points_pred = points_pred[["team", "points_predicted"]]

    # Actual goal difference so far
    gd_actual = actual_gd.rename(columns={"gd": "gd_actual"})

    # Predicted goal difference for unplayed matches
    gd_pred_home = unplayed.groupby("team1").apply(lambda x: (x["xG1"] - x["xG2"]).sum()).reset_index(name="gd_home")
    gd_pred_away = unplayed.groupby("team2").apply(lambda x: (x["xG2"] - x["xG1"]).sum()).reset_index(name="gd_away")
    gd_pred = pd.merge(gd_pred_home, gd_pred_away, left_on="team1", right_on="team2", how="outer")
    gd_pred["team"] = gd_pred["team1"].combine_first(gd_pred["team2"])
    gd_pred["gd_predicted"] = gd_pred["gd_home"].fillna(0) + gd_pred["gd_away"].fillna(0)
    gd_pred = gd_pred[["team", "gd_predicted"]]

    # Combine actual + predicted
    hybrid = pd.merge(points_actual, points_pred, on="team", how="outer").fillna(0)
    hybrid = pd.merge(hybrid, gd_actual, on="team", how="outer").fillna(0)
    hybrid = pd.merge(hybrid, gd_pred, on="team", how="outer").fillna(0)

    hybrid["total_points"] = hybrid["points_actual"] + hybrid["points_predicted"]
    hybrid["total_gd"] = hybrid["gd_actual"] + hybrid["gd_predicted"]

    hybrid = hybrid.sort_values(by=["total_points", "total_gd"], ascending=False).reset_index(drop=True)
    hybrid.index = hybrid.index + 1

    st.markdown("**Projected Final Table (Actual + Predicted)**")
    st.dataframe(hybrid[["team", "total_points", "total_gd"]].rename(columns={
        "total_points": "Points",
        "total_gd": "Goal Difference"
    }))
