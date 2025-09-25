# -*- coding: utf-8 -*-
"""
Created on Wed Sep 24 15:58:34 2025

@author: Groep 8
"""
# FILE IMPORT #
import read_ArtistData as ra
import ArtistSearch_Genres_Toptracks as agt
import lastfm_charts as lc
import streamlit as st

st.set_page_config(page_title="Music Analysis", page_icon="🎧")
App_selection = st.sidebar.radio(
        "Select Data:",
        ("Spotify Data", "Last.fm Charts")
        )

if App_selection == "Spotify Data":  
    # Maak een selection box in de sidebar
    sortside_selectbox = st.sidebar.selectbox(
        'Sort Method:',
        ('Per Artist', 'Per Genre', 'Per Track')
    )
    
    # Run de code voor de data van Artists
    st.title("🎧 Spotify Explorer")
    st.info("The popularity score is a score assigned by spotify to an artist/album/track/ect.\n"
            "This stat is based on a variëty of factors.\n"
            "The artist's popularity is calculated from the popularity of all the artist's tracks.\n"
            "The popularity of a track is a value between 0 and 100, with 100 being the most popular.\n"
            "The popularity is calculated by algorithm and is based, in the most part, "
            "on the total number of plays the track has had and how recent those plays are. ", icon="❗")
        
    if sortside_selectbox == "Per Artist":
        agt.artist_search()
        ra.Artist_tab()
    
    if sortside_selectbox == "Per Track":
        agt.top_tracks()
    
    if sortside_selectbox == "Per Genre":
        agt.genres()
        
elif App_selection == "Last.fm Charts":
     lc




