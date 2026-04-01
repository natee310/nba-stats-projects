"""
LeBron James - Top 5 Most Efficient Career Games
=================================================
Data source: NBA API (official, no scraping needed)
Efficiency metric: Game Score (John Hollinger)
  GmSc = PTS + 0.4*FG - 0.7*FGA - 0.4*(FTA-FT) + 0.7*ORB + 0.3*DRB
         + STL + 0.7*AST + 0.7*BLK - 0.4*PF - TOV

Install dependencies:
    pip install nba_api pandas
"""

import time
import pandas as pd
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players

# ── Config ────────────────────────────────────────────────────────────────────
PLAYER_NAME = "LeBron James"
SEASONS = [
    "2003-04", "2004-05", "2005-06", "2006-07", "2007-08",
    "2008-09", "2009-10", "2010-11", "2011-12", "2012-13",
    "2013-14", "2014-15", "2015-16", "2016-17", "2017-18",
    "2018-19", "2019-20", "2020-21", "2021-22", "2022-23",
    "2023-24", "2024-25",
]


def get_player_id(name: str) -> int:
    match = players.find_players_by_full_name(name)
    if not match:
        raise ValueError(f"Player '{name}' not found.")
    return match[0]["id"]


def fetch_season_log(player_id: int, season: str) -> pd.DataFrame:
    log = playergamelog.PlayerGameLog(
        player_id=player_id,
        season=season,
        season_type_all_star="Regular Season",
        timeout=30,
    )
    df = log.get_data_frames()[0]
    df["SEASON"] = season
    return df


def compute_game_score(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["GAME_SCORE"] = (
        df["PTS"]
        + 0.4  * df["FGM"]
        - 0.7  * df["FGA"]
        - 0.4  * (df["FTA"].fillna(0) - df["FTM"].fillna(0))
        + 0.7  * df["OREB"].fillna(0)
        + 0.3  * df["DREB"].fillna(0)
        + 1.0  * df["STL"].fillna(0)
        + 0.7  * df["AST"].fillna(0)
        + 0.7  * df["BLK"].fillna(0)
        - 0.4  * df["PF"].fillna(0)
        - 1.0  * df["TOV"].fillna(0)
    ).round(1)
    return df


def main():
    print(f"Looking up player ID for '{PLAYER_NAME}'...")
    player_id = get_player_id(PLAYER_NAME)
    print(f"Found: ID = {player_id}\n")

    all_logs = []

    for season in SEASONS:
        print(f"  -> Fetching {season}...", end=" ", flush=True)
        try:
            df = fetch_season_log(player_id, season)
            if df.empty:
                print("no data.")
            else:
                all_logs.append(df)
                print(f"{len(df)} games.")
        except Exception as e:
            print(f"error: {e}")
        time.sleep(1)

    if not all_logs:
        print("\nNo data collected. Check your internet connection.")
        return

    career = pd.concat(all_logs, ignore_index=True)
    career = compute_game_score(career)

    display_cols = {
        "SEASON": "Season", "GAME_DATE": "Date", "MATCHUP": "Matchup",
        "WL": "W/L", "PTS": "PTS", "REB": "REB", "AST": "AST",
        "STL": "STL", "BLK": "BLK", "TOV": "TOV", "FGM": "FGM",
        "FGA": "FGA", "FTM": "FTM", "FTA": "FTA", "OREB": "OREB",
        "DREB": "DREB", "PF": "PF", "GAME_SCORE": "GameScore",
    }

    top5 = (
        career[list(display_cols.keys())]
        .rename(columns=display_cols)
        .sort_values("GameScore", ascending=False)
        .head(5)
        .reset_index(drop=True)
    )
    top5.index += 1

    print("\n" + "=" * 75)
    print("  LeBron James - Top 5 Most Efficient Career Games (Game Score)")
    print("=" * 75)
    print(top5.to_string())
    print("=" * 75)
    print("\nGame Score formula (Hollinger):")
    print("  GmSc = PTS + 0.4*FGM - 0.7*FGA - 0.4*(FTA-FTM)")
    print("         + 0.7*OREB + 0.3*DREB + STL + 0.7*AST + 0.7*BLK - 0.4*PF - TOV\n")

    out_path = "lebron_top5_efficient_games.csv"
    top5.to_csv(out_path, index_label="Rank")
    print(f"Results saved to: {out_path}")

    return top5


if __name__ == "__main__":
    main()