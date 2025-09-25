import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

def lastfm():
    # ---- SETTINGS ----
    API_KEY = "b25b959554ed76058ac220b7b2e0a026"
    BASE_URL = "http://ws.audioscrobbler.com/2.0/"
    COLOR_PALETTE = px.colors.qualitative.Set2
    
    st.set_page_config(page_title="Last.fm Charts", layout="wide")
    st.title("🎶 Last.fm Charts")
    
    # ---- CACHED API FUNCTIES ----
    @st.cache_data(ttl=3600)
    def get_artist_info_cached(artist_name):
        params_info = {"method": "artist.getInfo", "artist": artist_name, "api_key": API_KEY, "format": "json"}
        r_info = requests.get(BASE_URL, params=params_info)
        info = r_info.json().get("artist", {})
        listeners = int(info.get("stats", {}).get("listeners", 0))
        playcount = int(info.get("stats", {}).get("playcount", 0))
        return listeners, playcount
    
    @st.cache_data(ttl=3600)
    def get_track_info_cached(artist_name, track_name):
        params = {"method": "track.getInfo", "artist": artist_name, "track": track_name, "api_key": API_KEY, "format": "json"}
        r = requests.get(BASE_URL, params=params)
        data = r.json().get("track", {})
        playcount = int(data.get("playcount", 0))
        listeners = int(data.get("listeners", 0))
        return playcount, listeners
    
    # ---- HELPER FUNCTIES ----
    def get_global_top_artists(limit=10):
        params = {"method": "chart.getTopArtists", "api_key": API_KEY, "format": "json", "limit": limit}
        r = requests.get(BASE_URL, params=params)
        data = r.json()["artists"]["artist"]
        return pd.DataFrame([{"artist": a["name"], "listeners": int(a["listeners"])} for a in data])
    
    def get_global_top_tracks(limit=500):
        params = {"method": "chart.getTopTracks", "api_key": API_KEY, "format": "json", "limit": limit}
        r = requests.get(BASE_URL, params=params)
        data = r.json()["tracks"]["track"]
        return pd.DataFrame([{"track": f"{t['name']} ({t['artist']['name']})", "playcount": int(t["playcount"])} for t in data])
    
    def get_local_top_artists(country="Netherlands", limit=10):
        params = {"method": "geo.getTopArtists", "country": country, "api_key": API_KEY, "format": "json", "limit": limit}
        r = requests.get(BASE_URL, params=params)
        data = r.json()["topartists"]["artist"]
        return pd.DataFrame([{"artist": a["name"], "listeners": int(a["listeners"])} for a in data])
    
    def style_bar(df, x_col, y_col, title=None):
        df[x_col] = pd.to_numeric(df[x_col], errors='coerce').fillna(0)
        df_sorted = df.sort_values(x_col, ascending=True)
        fig = px.bar(df_sorted, x=x_col, y=y_col, orientation='h',
                     color=y_col, color_discrete_sequence=COLOR_PALETTE,
                     text=x_col, title=title)
        fig.update_traces(texttemplate='%{text:,}', textposition='outside', showlegend=False)
        fig.update_layout(xaxis_title=None, yaxis_title=None,
                          margin=dict(l=10, r=10, t=40, b=10),
                          xaxis=dict(showgrid=False),
                          yaxis=dict(showgrid=False, autorange="reversed"),
                          font=dict(size=13))
        return fig
    
    def style_scatter(fig):
        fig.update_layout(margin=dict(l=10,r=10,t=40,b=10), font=dict(size=13), showlegend=False)
        return fig
    
    # ---- TABS ----
    tab1, tab2 = st.tabs(["Charts", "Genres"])
    
    # ---- TAB 1: GLOBAL & LOCAL CHARTS ----
    with tab1:
        st.header("Algemene instellingen")
        limit = st.slider("Aantal resultaten", 5, 30, 10)
        country_choice = st.text_input("Land voor lokale top artiesten", "Netherlands")
    
        st.header("🎶 Globale en lokale charts")
        df_global_artists = get_global_top_artists(limit)
        df_local_artists = get_local_top_artists(country_choice, limit)
        df_global_tracks = get_global_top_tracks(limit)
    
        # Voeg rang toe
        df_global_artists['rank_global'] = df_global_artists['listeners'].rank(ascending=False, method='first').astype(int)
        df_local_artists['rank_local'] = df_local_artists['listeners'].rank(ascending=False, method='first').astype(int)
    
        # Plot globale en lokale artiesten
        col1, col2 = st.columns(2)
        with col1:
            fig_global_artists = style_bar(df_global_artists.sort_values("rank_global"), "listeners", "artist", "🔥 Globale top artiesten")
            st.plotly_chart(fig_global_artists, use_container_width=True, key="global_artists_bar")
        with col2:
            fig_local_artists = style_bar(df_local_artists.sort_values("rank_local"), "listeners", "artist", f"📍 Top artiesten in {country_choice}")
            st.plotly_chart(fig_local_artists, use_container_width=True, key="local_artists_bar")
    
        # Scatterplot rangen
        merged = pd.merge(df_local_artists, df_global_artists, on="artist", how="inner")
        if not merged.empty:
            fig_scatter = px.scatter(
                merged,
                x="rank_global",
                y="rank_local",
                text="artist",
                color="rank_global",
                color_continuous_scale="Viridis",
                labels={"rank_global": "Globale rang", "rank_local": "Lokale rang"},
                title="📊 Vergelijking chartpositie lokaal vs globaal"
            )
            fig_scatter.update_xaxes(autorange="reversed")  # rank 1 links
            fig_scatter.update_yaxes(autorange="reversed")  # rank 1 boven
            fig_scatter.update_traces(textposition="top center")
            fig_scatter.update_coloraxes(showscale=False)
            fig_scatter = style_scatter(fig_scatter)
            st.plotly_chart(fig_scatter, use_container_width=True, key="scatter_rank")
        else:
            st.info("Geen overlappende artiesten gevonden.")
    
        # Globale top tracks
        fig_global_tracks = style_bar(df_global_tracks.sort_values("playcount"), "playcount", "track", "🎵 Globale top tracks")
        st.plotly_chart(fig_global_tracks, use_container_width=True, key="global_tracks_bar")
    
        # Voeg playcount toe aan df_global_artists
        playcounts = []
        for artist in df_global_artists['artist']:
            _, playcount = get_artist_info_cached(artist)
            playcounts.append(playcount)
    
        df_global_artists['playcount'] = playcounts
    
    
        # Globale artiesten: Listeners vs Playcount
        if not df_global_artists.empty:
            fig_corr_artists = px.scatter(
                df_global_artists,
                x="playcount",
                y="listeners",
                text="artist",
                size="playcount",
                color="listeners",
                color_continuous_scale="Viridis",
                labels={"playcount": "Playcount", "listeners": "Listeners"},
                title="🌟 Globale artiesten: Playcount vs Listeners"
            )
            fig_corr_artists.update_traces(textposition="top center")
            st.plotly_chart(fig_corr_artists, use_container_width=True)
    
    
    # ---- TAB 2: GENRES ----
    with tab2:
        st.header("🎼 Genre Insights")
        
        genre_mode = st.radio("Selecteer weergave", ["Genre Charts", "Genre Populariteit"])
    
        if genre_mode == "Genre Charts":
            st.subheader("Top artiesten en tracks per genre")
            genre_choice = st.text_input("Voer een genre in", "rock", key="genre_choice_charts")
            limit_genre = st.slider("Aantal resultaten per genre", 5, 30, 10, key="genre_limit_charts")
    
            try:
                # Genre top-artists
                params_artists = {"method": "tag.getTopArtists", "tag": genre_choice, "api_key": API_KEY, "format": "json", "limit": 50}
                r_artists = requests.get(BASE_URL, params=params_artists)
                data_artists = r_artists.json().get("topartists", {}).get("artist", [])
                artists_info = []
                for a in data_artists:
                    name = a.get("name", "Onbekend")
                    listeners, playcount = get_artist_info_cached(name)
                    artists_info.append({"artist": name, "listeners": listeners, "playcount": playcount})
                df_genre_artists = pd.DataFrame(artists_info).sort_values("listeners", ascending=False).head(limit_genre)
    
                # Genre top-tracks
                params_tracks = {"method": "tag.getTopTracks", "tag": genre_choice, "api_key": API_KEY, "format": "json", "limit": limit_genre}
                r_tracks = requests.get(BASE_URL, params=params_tracks)
                data_tracks = r_tracks.json().get("tracks", {}).get("track", [])
                tracks_info = []
                for t in data_tracks:
                    track_name = t.get("name", "Onbekend")
                    artist_name = t.get("artist", {}).get("name", "Onbekend")
                    playcount, listeners = get_track_info_cached(artist_name, track_name)
                    tracks_info.append({"track": f"{track_name} ({artist_name})", "playcount": playcount, "listeners": listeners})
                df_genre_tracks = pd.DataFrame(tracks_info).sort_values("playcount", ascending=False)
    
                # Plot genre charts
                col1, col2 = st.columns(2)
                with col1:
                    if not df_genre_artists.empty:
                        fig_genre_artists = style_bar(df_genre_artists, "listeners", "artist", f"🔥 Top artiesten in {genre_choice}")
                        st.plotly_chart(fig_genre_artists, use_container_width=True)
                with col2:
                    if not df_genre_tracks.empty:
                        fig_genre_tracks = style_bar(df_genre_tracks, "playcount", "track", f"🎵 Top tracks in {genre_choice}")
                        st.plotly_chart(fig_genre_tracks, use_container_width=True)
    
                # Treemap artiesten
                if not df_genre_artists.empty:
                    fig_treemap = px.treemap(
                        df_genre_artists,
                        path=['artist'],
                        values='listeners',
                        color='listeners',
                        color_continuous_scale='Viridis',
                        title=f"📦Populariteit van artiesten in {genre_choice}"
                    )
                    st.plotly_chart(fig_treemap, use_container_width=True)
    
                # ---- CORRELATIEPLOT TAB 2 ----
                if not df_genre_artists.empty:
                    fig_genre_corr = px.scatter(
                        df_genre_artists,
                        x="playcount",
                        y="listeners",
                        text="artist",
                        color="listeners",
                        size="playcount",
                        color_continuous_scale="Viridis",
                        labels={"listeners": "Listeners", "playcount": "Playcount"},
                        title=f"🎶 Genre {genre_choice}: Listeners vs Playcount (Artiesten)"
                    )
                    fig_genre_corr.update_traces(textposition="top center")
                    st.plotly_chart(fig_genre_corr, use_container_width=True)
    
            except Exception as e:
                st.error(f"Fout bij ophalen van genre '{genre_choice}': {e}")
    
        elif genre_mode == "Genre Populariteit":
            st.subheader("Populairste genres wereldwijd")
            try:
                # Top tags / genres wereldwijd
                params_tags = {"method": "chart.getTopTags", "api_key": API_KEY, "format": "json", "limit": 10}
                r_tags = requests.get(BASE_URL, params=params_tags)
                data_tags = r_tags.json().get("tags", {}).get("tag", [])
                df_tags = pd.DataFrame([{"tag": t["name"], "count": int(t["reach"])} for t in data_tags])
    
                fig_tags = px.bar(df_tags.sort_values("count"), x="count", y="tag", orientation="h",
                                color="count", color_discrete_sequence=COLOR_PALETTE,
                                text="count", title="🔥 Populairste genres wereldwijd")
                fig_tags.update_traces(texttemplate='%{text:,}', textposition='outside', showlegend=False)
                st.plotly_chart(fig_tags, use_container_width=True)
    
            except Exception as e:
                st.error(f"Fout bij ophalen van genre populariteit: {e}")


