import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

# --- Example data loading (replace with your actual data) ---
matches_df = pd.read_csv("statsbomb-matches.csv")
summary_stats_df = pd.read_csv("statsbomb-summary_stats.csv")
player_positions_df = pd.read_csv("statsbomb-player_positions.csv")  # avg_x, avg_y for each player
pass_network_df = pd.read_csv("statsbomb-passing_network.csv")       # pass counts between players

# --- Sidebar match selection ---
match_options = matches_df[["match_id", "home_team.home_team_name", "away_team.away_team_name", "match_date"]]
match_options["label"] = match_options.apply(lambda row: f"{row['home_team.home_team_name']} vs {row['away_team.away_team_name']} ({row['match_date']})", axis=1)

selected_label = st.sidebar.selectbox("Select Match", match_options["label"])
selected_match_id = match_options.loc[
    match_options["label"] == selected_label, "match_id"
].values[0]

# --- Tabs ---
tab1, tab2 = st.tabs(["📊 Summary", "🧠 Passing Network"])

with tab1:
    st.header("Match Summary Statistics")
    match_summary = summary_stats_df[summary_stats_df["match_id"] == selected_match_id]

    if match_summary.empty:
        st.warning("No summary data available for this match.")
    else:
        st.dataframe(match_summary)

with tab2:
    st.header("Passing Network (by team)")

    match_positions = player_positions_df[
        player_positions_df["match_id"] == selected_match_id
    ].copy()

    match_passes = pass_network_df[
        pass_network_df["match_id"] == selected_match_id
    ]

    if match_positions.empty or match_passes.empty:
        st.warning("No passing network data available for this match.")
    else:
        touch_scale = 20
        team_colors = ["skyblue", "lightcoral"]

        # Home / Away from matches_df
        home_team_name = matches_df.loc[
            matches_df["match_id"] == selected_match_id, "home_team.home_team_name"
        ].values[0]
        away_team_name = [t for t in match_positions["team_name"].unique() if t != home_team_name][0]

        # Flip away team x coords
        away_mask = match_positions["team_name"] == away_team_name
        match_positions.loc[away_mask, "average_x"] = 120 - match_positions.loc[away_mask, "average_x"]

        # Create pitch
        pitch = Pitch(pitch_type='statsbomb', line_color='black', pitch_color='white')
        fig, ax = pitch.draw(figsize=(10, 7))

        # Draw each team
        for i, team in enumerate([home_team_name, away_team_name]):
            team_positions = match_positions[match_positions["team_name"] == team]

            pitch.scatter(
                team_positions["average_x"],
                team_positions["average_y"],
                s=team_positions["touches"] * touch_scale,
                c=team_colors[i], edgecolors="black", linewidth=1, ax=ax, zorder=2
            )

            for _, row in team_positions.iterrows():
                pitch.annotate(
                    row["player_name"],
                    xy=(row["average_x"], row["average_y"]),
                    va="center", ha="center", fontsize=8, ax=ax, zorder=3
                )

            # Pass lines within same team
            team_passes = match_passes[
                match_passes["passer"].isin(team_positions["player_name"])
            ]
            for _, row in team_passes.iterrows():
                passer_pos = team_positions.loc[
                    team_positions["player_name"] == row["passer"], ["average_x", "average_y"]
                ].values
                receiver_pos = team_positions.loc[
                    team_positions["player_name"] == row["receiver"], ["average_x", "average_y"]
                ].values

                if passer_pos.size > 0 and receiver_pos.size > 0:
                    pitch.lines(
                        passer_pos[0][0], passer_pos[0][1],
                        receiver_pos[0][0], receiver_pos[0][1],
                        lw=row["pass_count"] * 0.5,
                        color=team_colors[i], alpha=0.6, ax=ax, zorder=1
                    )

        st.pyplot(fig)

        # ---- Players with most unique connections ----
        st.subheader("Players with Most Passing Connections")

        connections_df = match_passes.groupby("passer")["receiver"].nunique().reset_index()
        connections_df.columns = ["player_name", "unique_connections"]
        connections_df = connections_df.merge(
            match_positions[["player_name", "team_name"]],
            on="player_name",
            how="left"
        )

        # ---- Player combinations with most passes ----
        st.subheader("Top Passing Combinations")

        combinations_df = match_passes[["passer", "receiver", "pass_count"]].copy()
        combinations_df = combinations_df.merge(
            match_positions[["player_name", "team_name"]],
            left_on="passer", right_on="player_name", how="left"
        ).drop(columns=["player_name"])
        combinations_df.rename(columns={"team_name": "team"}, inplace=True)

        for team in [home_team_name, away_team_name]:
            st.markdown(f"**{team}**")
            team_conn = connections_df[connections_df["team_name"] == team] \
                .sort_values("unique_connections", ascending=False)
            st.markdown("*Players with most unique passing connections*")
            st.dataframe(team_conn, hide_index=True)

            team_combos = combinations_df[combinations_df["team"] == team] \
                .sort_values("pass_count", ascending=False)
            st.markdown("*Most frequent passing combinations*")
            st.dataframe(team_combos, hide_index=True)
