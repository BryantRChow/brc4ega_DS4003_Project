#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import libraries
import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, callback
import folium


# In[2]:


crimes = pd.read_csv('data/data.csv')
crimes.head()


# In[3]:


# dc center point for folium
dc_lat = (crimes['Latitude'].min() + crimes['Latitude'].max())/2
dc_long = (crimes['Longitude'].min() + crimes['Longitude'].max())/2
dc_center = (dc_lat, dc_long)

# create a new map object
map = folium.Map(location=dc_center, zoom_start=12)

# save our map to an interactive html file
map.save('initial_dc_crimes_map.html')


# In[4]:


# load stylesheet
stylesheets = ['https://codepen.io/chriddyp/pen/dZVMbK.css']

# initialize app
app = Dash(__name__, external_stylesheets=stylesheets)
server = app.server


# In[5]:


app.layout = html.Div([
    # title row
    html.Div(
        html.H1(
            "Mapping of Washington D.C. Crime History",
            style = {"color": "light grey", "font-family": "serif"}),
        className = "row"
    ),

    # graph row
    html.Div(
        id = 'map graph', 
        children = html.Iframe(
            id='initial map graph',
            srcDoc = open('initial_dc_crimes_map.html','r').read(),
            style={'width': '100%', 'height':'400px','display': 'inline-block'},
        )
    ),
    
    # checklist row
    html.Div(
        dcc.Checklist(
            crimes['Offense'].unique(),
            crimes['Offense'].unique(),
            inline=True,
            style={'color': 'Gold', 'font-size': 15},
            id = 'offense',
        )
    ),

    # slider, and dropdowns row
    html.Div([

        # timeframe slider
        html.Div(
            children = [
                html.Label(
                    'Year',
                    style={"color": "light grey"}
                ),
                dcc.Slider(
                    min = crimes['Year'].min(), 
                    max = crimes['Year'].max(), 
                    step = 1.0, 
                    marks={i: '{}'.format(i) for i in range(crimes['Year'].min(), crimes['Year'].max())},
                    id = 'year',
                    tooltip = {"placement": "bottom", "always_visible": True},
                    included = False,
                    value = crimes['Year'].min(),
                ),
            ],
            className = "six columns"
        ),

        # wards dropdown
        html.Div(
            children = [
                html.Label(
                    'Wards',
                    style = {"color": "light grey"}
                ),
                dcc.Dropdown(
                    id = 'wards',
                    options = [{"label": x, "value": x} for x in sorted(crimes["Ward"].unique())],
                    multi = True,
                    value = [],
                    placeholder = 'Select Wards',
                )
            ], 
            className="five columns"
        ),

        # time of day dropdown
        html.Div(
            children = [
                html.Label(
                    'Time of Day',
                    style = {"color": "light grey"}
                ),
                dcc.Dropdown(
                    id = 'time of day',
                    options = crimes['Time of Day'].unique(),
                    value = 'DAY'
                )
            ], 
            className="one column"
        ),
    ]),
])

# define callbacks
@app.callback(
    Output('map graph', 'children'),
    Input('year', 'value'),
    Input('offense', 'value'),
    Input('wards', 'value'),
    Input('time of day', 'value'))
def update_figure(selected_year, selected_offense, selected_wards, selected_time_of_day):
    # create a filtered dataset
    filtered_df = crimes.loc[(crimes['Year'] == selected_year) & 
                             (crimes['Ward'].isin(selected_wards)) &
                             (crimes['Time of Day'] == selected_time_of_day) &
                             (crimes['Offense'].isin(selected_offense))]

    # dc center point for folium
    dc_lat = (crimes['Latitude'].min() + crimes['Latitude'].max())/2
    dc_long = (crimes['Longitude'].min() + crimes['Longitude'].max())/2
    dc_center = (dc_lat, dc_long)

    # create a new map object
    map = folium.Map(location=dc_center, zoom_start=12)

    # add crimes
    for i in range(len(filtered_df)):
        folium.Circle(
            location=[filtered_df.iloc[i]['Latitude'], filtered_df.iloc[i]['Longitude']],
            radius=16,
        ).add_to(map)

    # save our map to an interactive html file
    map_html = map.get_root().render()

    return html.Iframe(
            srcDoc = map_html,
            style={'width': '100%', 'height':'400px','display': 'inline-block'},
        )


# In[6]:


if __name__ == '__main__':
    app.run(debug=True)

