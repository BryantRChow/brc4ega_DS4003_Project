#!/usr/bin/env python
# coding: utf-8

# In[294]:


# import libraries
import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, callback
import folium


# In[295]:


crimes = pd.read_csv('data/data.csv')
crimes.head()


# In[296]:


# dc center point for folium
dc_lat = (crimes['Latitude'].min() + crimes['Latitude'].max())/2
dc_long = (crimes['Longitude'].min() + crimes['Longitude'].max())/2
dc_center = (dc_lat, dc_long)

# create a new map object
map = folium.Map(location=dc_center, zoom_start=12)

# save our map to an interactive html file
map.save('initial_dc_crimes_map.html')


# In[297]:


# load stylesheet
stylesheets = ['https://codepen.io/chriddyp/pen/dZVMbK.css']

# initialize app
app = Dash(__name__, external_stylesheets=stylesheets, suppress_callback_exceptions=True)
server = app.server


# In[298]:


app.layout = html.Div([
    # title row
    html.Div([
        html.H1(
            "Washington D.C. Crime History",
            style = {"color": "white", "font-family": "serif", "text-align": "center"})],
        style={"background-image": "url('assets/usa.avif')"}
    ),

    dcc.Tabs(id="tabs", value='map', children=[
        dcc.Tab(label='Yearly Mapping', value='map'),
        dcc.Tab(label='Change Over Time', value='graph'),
    ]),

    html.Div(id='tab-content'),
])

@callback(Output('tab-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'map':
        return html.Div([ 
        # graph row
        html.Div(
            id = 'map graph', 
            children = html.Iframe(
                id='initial map graph',
                srcDoc = open('initial_dc_crimes_map.html','r').read(),
                style={'width': '100%', 'height':'600px','display': 'inline-block'},
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
                        marks={i: '{}'.format(i) for i in range(crimes['Year'].min(), crimes['Year'].max()+1)},
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
        ]),])
    elif tab == 'graph':
        return html.Div([
        # graph
        html.Div(id='graph_over_time'),

        # slider, and dropdowns row
        html.Div([

            # timeframe slider
            html.Div(
                children = [
                    html.Label(
                        'Year',
                        style={"color": "light grey"}
                    ),
                    dcc.RangeSlider(
                        min = crimes['Year'].min(), 
                        max = crimes['Year'].max(), 
                        step = 1.0, 
                        marks={i: '{}'.format(i) for i in range(crimes['Year'].min(), crimes['Year'].max()+1)},
                        id = 'year_range',
                        tooltip = {"placement": "bottom", "always_visible": True},
                        value = [crimes['Year'].min(), crimes['Year'].max()]
                    ),
                ],
                className = "four columns"
            ),

            # wards dropdown
            html.Div(
                children = [
                    html.Label(
                        'Wards',
                        style = {"color": "light grey"}
                    ),
                    dcc.Dropdown(
                        id = 'wards_graph',
                        options = [{"label": x, "value": x} for x in sorted(crimes["Ward"].unique())],
                        multi = True,
                        value = [x for x in sorted(crimes["Ward"].unique())],
                        placeholder = 'Select Wards',
                    )
                ], 
                className="six columns"
            ),
            # violent
            html.Div(
                children = [
                    html.Label(
                        'Severity',
                        style = {"color": "light grey"}
                    ),
                    dcc.Checklist(
                        crimes['Violence'].unique(),
                        crimes['Violence'].unique(),
                        inline=True,
                        style={'color': 'Gold', 'font-size': 15},
                        id = 'violence',
                    )
                ]
            )
            
        ])
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

    # colors for different wards
    colors = {1:'#F32020', 2:'#37E0EE', 3:'#3D20F3', 4:'#8620F3', 5:'#F38920', 6:'#4AB45B', 7:'#D6D136', 8:'#69E1CD'}

    # add crimes
    for i in range(len(filtered_df)):
        folium.Circle(
            location=[filtered_df.iloc[i]['Latitude'], filtered_df.iloc[i]['Longitude']],
            radius=16,
            fill=True,
            color=colors[filtered_df.iloc[i]['Ward']],
            tooltip='<b>Offense: %s</b><br><b>%s</b><br><b>Date: %s</b><br><b>Police District: %s</b>'
              % (filtered_df.iloc[i]['Offense'], filtered_df.iloc[i]['Violence'],filtered_df.iloc[i]['Date'], filtered_df.iloc[i]['Police District'])
        ).add_to(map)

    # save our map to an interactive html file
    map_html = map.get_root().render()

    return html.Iframe(
            srcDoc = map_html,
            style={'width': '100%', 'height':'400px','display': 'inline-block'},
        )

@app.callback(
    Output('graph_over_time', 'children'),
    Input('year_range', 'value'),
    Input('wards_graph', 'value'),
    Input('violence', 'value'))
def update_figure(selected_years, selected_wards, selected_violence):
    # create a filtered dataset
    filtered_df = crimes.loc[(crimes['Year'] >= selected_years[0]) & 
                             (crimes['Year'] <= selected_years[1]) &
                             (crimes['Ward'].isin(selected_wards)) & 
                             (crimes['Violence'].isin(selected_violence))]
    
    grouped_df = filtered_df.groupby(['Year','Ward'], as_index=False).size()
    grouped_df.columns = ['Year', 'Ward', 'Count']
    
    fig = px.line(grouped_df, x="Year", y="Count", color='Ward')
    fig.update_layout(xaxis={'tickformat':'d'}, title="Yearly Count of Crimes Per Ward")

    return dcc.Graph(figure = fig)


# In[299]:


crimes['Counter'] = 1
grouped_df = crimes.groupby(['Year','Ward'], as_index=False).size()
grouped_df.head()


# In[300]:


if __name__ == '__main__':
    app.run(debug=True)

