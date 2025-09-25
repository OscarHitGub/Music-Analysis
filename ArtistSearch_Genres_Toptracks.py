import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import plotly.express as px
import statsmodels.api as sm

st.set_page_config(page_title="Spotify Explorer", page_icon="🎧", layout="wide")

# login
CLIENT_ID = 'b87f7c4564b94a8482eb06c3b1c643fb'
CLIENT_SECRET = 'e9266877b0d64a73a9011127afb7a706'
auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

# func
def _first_artist_name(obj):
    try:
        return obj.get("artists", [{}])[0].get("name", "")
    except Exception:
        return ""

def _dedupe_name_artist(df, name_col="Album", artist_col="Artist"):
    key = (df[name_col].str.lower().str.strip() + " — " + df[artist_col].str.lower().str.strip())
    return df.loc[~key.duplicated()].copy()

def _chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def artist_search():
    # artists search
    q_artist = st.text_input("Search artist", placeholder="e.g., Kendrick Lamar", key="artist_q")
    if q_artist:
        try:
            res = sp.search(q=q_artist, type="artist", limit=10)
            artists = res.get("artists", {}).get("items", [])
        except Exception as e:
            st.error(f"Spotify error: {e}")
            artists = []
    
        if not artists:
            st.warning("No artists found.")
        else:
            choices = {f'{a["name"]} — followers: {a["followers"]["total"]:,}': a["id"] for a in artists}
            picked = st.selectbox("Pick an artist", list(choices.keys()))
            artist_id = choices[picked]
    
            try:
                top = sp.artist_top_tracks(artist_id, country="US").get("tracks", [])
            except Exception as e:
                st.error(f"Error fetching top tracks: {e}")
                top = []
    
            rows = []
            for t in top:
                imgs = t.get("album", {}).get("images") or []
                cover = imgs[0]["url"] if imgs else None
                rows.append({
                    "Track": t["name"],
                    "Album": t.get("album", {}).get("name"),
                    "Popularity": t.get("popularity", 0),
                    "Preview": t.get("preview_url"),
                    "Cover": cover,
                    "Track ID": t.get("id"),
                })
            df = pd.DataFrame(rows)
    
            c1, c2 = st.columns([1,1], gap="large")
            with c1:
                cols = st.columns(3)
                for i, r in df.iterrows():
                    col = cols[i % 3]  # afwisselend links/rechts
                    with col:
                        if r["Cover"]:
                            st.image(r["Cover"], width=140, caption=r["Track"])
                        if r["Preview"]:
                            st.audio(r["Preview"])
                        st.markdown("---")
            with c2:
                st.subheader("Top tracks")
                st.dataframe(df[["Track","Album","Popularity"]], width=100)
    else:
        st.info("Type an artist name above and press Enter.")

def genres():
    st.subheader("Popularity vs Duration by Genre")
    
    df = pd.read_csv("songs.csv")
    
    needed = {"track_popularity", "duration_ms", "playlist_genre"}
    missing = needed - set(df.columns)
    if missing:
        st.error(f"Missing columns in CSV: {missing}")
    else:
        df["track_popularity"] = pd.to_numeric(df["track_popularity"], errors="coerce")
        if df["track_popularity"].max() <= 1:
            df["track_popularity"] = df["track_popularity"] * 100
    
        df["duration_min"] = pd.to_numeric(df["duration_ms"], errors="coerce") / 60000.0
    
        min_max = st.slider("Duration range (minutes)", 0.0, 15.0, (0.5, 7.0), 0.5)
        dff = df[df["duration_min"].between(min_max[0], min_max[1])].copy()
    
        # Optional trendline
        show_trend = st.checkbox("Show trendline (OLS)", value=False)
    
        fig = px.scatter(
            dff,
            x="duration_min",
            y="track_popularity",
            color="playlist_genre",
            hover_data=["track_name", "track_artist", "track_popularity"],
            title="Song Popularity vs Duration",
            opacity=0.75,
            trendline="ols" if show_trend else None,
        )
        fig.update_layout(
            xaxis_title="Duration (minutes)",
            yaxis_title="Popularity (0–100)",
            legend_title_text="Genre"
        )
    
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Popularity distribution by Genre")
    fig_box = px.box(
        dff, x="playlist_genre", y="track_popularity",
        points="suspectedoutliers", title="Popularity by Genre", color="playlist_genre"
    )
    fig_box.update_layout(xaxis_title="Genre",
                          yaxis_title="Popularity (0–1)",
                          legend_title_text="Genre")
    st.plotly_chart(fig_box, use_container_width=True)
    
    # xd
    df["duration_bin"] = pd.cut(df["duration_ms"]/60000, bins=[0,3,5,8,15], labels=["<3m","3–5m","5–8m","8m+"])
    cat_order = ["<3m", "3–5m", "5–8m", "8m+"]
    fig = px.box(df, x="duration_bin", y="track_popularity", color="playlist_genre",
                 title="Popularity by Duration Bin and Genre", category_orders={"duration_bin": cat_order})
    fig.update_layout(
        xaxis_title="Song Duration (in minutes)",
        yaxis_title="Track Popularity (0–100)",
        legend_title_text="Genre"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # xd 2
    genre_stats = df.groupby("playlist_genre").agg(
        avg_pop=("track_popularity","mean"),
        avg_dur=("duration_ms","mean"),
        count=("track_name","count")
    ).reset_index()
    
    genre_stats["avg_dur_min"] = genre_stats["avg_dur"]/60000


def top_tracks():
    # top 10 ofzo
    q = st.text_input("Search songs (global top 10 by popularity)", placeholder="e.g., Drake")
    if q:
        results = sp.search(q=q, type="track", limit=50)  # fetch 50 tracks
        tracks = results.get("tracks", {}).get("items", [])
        
        rows = []
        for t in tracks:
            rows.append({
                "Track": t["name"],
                "Artist": ", ".join([ar["name"] for ar in t["artists"]]),
                "Album": t["album"]["name"],
                "Popularity": t["popularity"],
            })
        df = pd.DataFrame(rows)
    
        if not df.empty:
            top10 = df.sort_values("Popularity", ascending=False).head(10).reset_index(drop=True)
            st.subheader("🎶 Top 10 Tracks by Popularity")
            st.dataframe(top10, use_container_width=True)
        else:

            st.warning("No tracks found.")











