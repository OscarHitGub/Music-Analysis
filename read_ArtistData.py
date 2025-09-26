# -*- coding: utf-8 -*-
"""
Created on Tue Sep 23 14:57:20 2025

@author: oscar
"""
import streamlit as st
import plotly.express as px
import pandas as pd
import statsmodels.api as sm

def Artist_tab():
    # Import de CSV file van artist data
    ArtistData = pd.read_csv('Artist_Data.csv')
    st.set_page_config(layout="wide")
        
    # Artist data in een tabel
    st.title("Data of 500+ spotify artists")
    st.dataframe(ArtistData, hide_index=True)
    
    ## HISTOGRAMMEN MET SELECTIONBOX ##
    
    st.subheader("Histogram of selected column", divider=True)
    # Maak de selectbox eerst
    hist_selectbox = st.selectbox(
        "Select column:", 
        ("Popularity", "Followers", "Average song length")
    )
    
    # Maak een histogram die zich aanpast op de data
    if hist_selectbox == "Popularity":
        fig_pop = px.histogram(ArtistData, x="Popularity",
                   color_discrete_sequence=['#d62728'], nbins=40)
        st.plotly_chart(fig_pop)
        
    elif hist_selectbox == "Followers":
        fig_fol = px.histogram(ArtistData, x="Followers",
                   color_discrete_sequence=['#1f77b4'], nbins=40)
        st.plotly_chart(fig_fol)

    elif hist_selectbox == "Average song length":
        fig_len = px.histogram(ArtistData,
                           x="Average_top_song_length_in_min",
                           labels={"Average_top_song_length_in_min":"Average song length in min"},
                           color_discrete_sequence=['#bcbd22'], nbins=40
                           )
        st.plotly_chart(fig_len)
    
    ## BOXPLOTS ##
    
    # Verdeel de pagina in drieeën
    col1, col2, col3 = st.columns(3)
    
    with col2:
        # Plot de Followers
        st.subheader("Followers", divider=False)
        
        # Checkbox die automatisch session_state bijwerkt
        st.checkbox("Logaritmische schaal", key='log_scale_f', value=True)
        
        fig_F = px.box(ArtistData,
                         y="Followers",
                         hover_data="Name", 
                         color_discrete_sequence=['#1f77b4']
                         )
        fig_F.update_yaxes(type="log" if st.session_state.log_scale_f else "linear")
        st.plotly_chart(fig_F, use_container_width=True)
    
    with col1:
        # Plot de Popularity
        st.subheader("Popularity", divider=False)
        fig_P = px.box(ArtistData,
                         y="Popularity",
                         hover_data="Name", 
                         color_discrete_sequence=['#d62728']  
                         )
        st.plotly_chart(fig_P, use_container_width=True)

    with col3:
        # Plot de Average_top_song_length_in_min
        st.subheader("Average song length in min", divider=False)
        fig_P = px.box(ArtistData,
                         y="Average_top_song_length_in_min",
                         hover_data="Name", 
                         color_discrete_sequence=['#bcbd22']
                         )
        st.plotly_chart(fig_P, use_container_width=True)
    
    ## SCATTERPLOTS ##
    st.subheader("Scatterplots", divider=True)
        
    # Verdeel de pagina in tweeën
    col1, col2 = st.columns(2)
    
    with col1:
        # Plot de Popularity tegen de Followers
        st.subheader("Popularity v Followers", divider=False)
        
        # Checkbox die automatisch session_state bijwerkt
        st.checkbox("Logaritmische schaal", key='log_scale_pvf', value=True)

        # Plot de Popularity tegen de Followers
        fig_PvF = px.scatter(ArtistData,
                             x="Popularity",
                             y="Followers",
                             hover_data="Name",
                             color="Average_top_song_length_in_min",
                             color_continuous_scale="sunsetdark",
                             trendline="ols",
                             trendline_options=dict(log_y=True),
                             trendline_color_override="white",
                             labels={"Average_top_song_length_in_min":"Average song<br>length in min"}
                             )
        fig_PvF.update_yaxes(type="log" if st.session_state.log_scale_pvf else "linear")
        st.plotly_chart(fig_PvF, use_container_width=True)

    with col2:
        st.subheader("Followers v Average song length", divider=False)
                
        # Checkbox die automatisch session_state bijwerkt
        st.checkbox("Logaritmische schaal", key='log_scale_avf', value=True)
            
        # Plot de Popularity tegen de Average song length
        fig_AvF = px.scatter(ArtistData,
                             x="Average_top_song_length_in_min",
                             y="Followers",
                             hover_data="Name",
                             color="Popularity",
                             color_continuous_scale="sunset",
                             labels={"Average_top_song_length_in_min":"Average song length in min"}
                             )
        fig_AvF.update_yaxes(type="log" if st.session_state.log_scale_avf else "linear")
        st.plotly_chart(fig_AvF)

    st.subheader("Popularity v Average song length", divider=False)

    # Plot de Popularity tegen de Average song length
    fig_PvA = px.scatter(ArtistData,
                         x="Popularity",
                         y="Average_top_song_length_in_min",
                         hover_data="Name",
                         color="Followers",
                         color_continuous_scale="Tealgrn",
                         trendline="ols",
                         trendline_color_override="white",
                         labels={"Average_top_song_length_in_min":"Average song length in min"}
                         )
    fig_PvA.update_layout()
    st.plotly_chart(fig_PvA, use_container_width=False)

