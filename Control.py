# -*- coding: utf-8 -*-
"""
Created on Wed Sep 24 15:58:34 2025

@author: Groep 8
"""
# FILE IMPORT #
import read_ArtistData as ra
import ArtistSearch_Genres_Toptracks as agt

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
    if sortside_selectbox == "Per Artist":
        agt.artist_search()
        ra.Artist_tab()
    
    if sortside_selectbox == "Per Track":
        agt.top_tracks()
    
    if sortside_selectbox == "Per Genre":
        agt.genres()
        
elif App_selection == "Last.fm Charts":
    print("Hello Last.fm")