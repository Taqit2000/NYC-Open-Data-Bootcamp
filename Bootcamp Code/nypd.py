import numpy as np
import pandas as pd
import requests as re
import seaborn as sns
from tqdm.auto import tqdm
import matplotlib.pyplot as plt
from tqdm import tqdm


import plotly
import plotly.offline as py
import plotly.graph_objs as go
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

LIMIT= 1000000
URLYTD = f"{'https://data.cityofnewyork.us/resource/uip8-fykc.json'}?$limit={LIMIT}"
URLHIS = f"{'https://data.cityofnewyork.us/resource/8h9b-rp9u.json'}?$limit={LIMIT}"
URLSUBWAY = f"{'https://data.cityofnewyork.us/resource/he7q-3hwy.json'}?$limit={LIMIT}"


YTD = re.get(URLYTD)
NYPDYTD = pd.read_json(YTD.text)

HIS = re.get(URLHIS)
NYPDHIS = pd.read_json(HIS.text)

SUBWAY = re.get(URLSUBWAY)
SUBWAY = pd.read_json(SUBWAY.text)


NYPD = pd.concat([NYPDYTD, NYPDHIS], ignore_index=True)
NYPD['arrest_date'] = pd.to_datetime(NYPD['arrest_date'])
NYPD['time'] = NYPD['arrest_date'].dt.hour + NYPD['arrest_date'].dt.minute + NYPD['arrest_date'].dt.second
NYPD['year'] = NYPD['arrest_date'].dt.year
NYPD['month'] = NYPD['arrest_date'].dt.month
NYPD['day'] = NYPD['arrest_date'].dt.day

# Extract coordinates from the 'the_geom' field
SUBWAY['coordinates'] = SUBWAY['the_geom'].apply(lambda x: x['coordinates'])

# Split the coordinates into latitude and longitude
SUBWAY['latitude'] = SUBWAY['coordinates'].apply(lambda x: x[1])
SUBWAY['longitude'] = SUBWAY['coordinates'].apply(lambda x: x[0])

# Concatenate 'name' and 'line' into a single column
SUBWAY['info'] = 'Line: ' + SUBWAY['line'] + ', Street Entrance: ' + SUBWAY['name']

# Creating subway data plot
subway_stations = go.Scattermapbox(
    lat=SUBWAY['latitude'],
    lon=SUBWAY['longitude'],
    mode='markers',
    marker=go.scattermapbox.Marker(
        size=5,
        color='rgb(255, 0, 0)',
        opacity=1),
    text=SUBWAY['info'],  # Set 'text' to the new column
    hoverinfo='text'  # Show the 'text' when hovering over the points
)


NYPD['Number of People Arrested'] = 1


fig = px.density_mapbox(NYPD,
                        lat='latitude',
                        lon='longitude',
                        z='Number of People Arrested',
                        radius=10,
                        hover_name='arrest_boro',
                        hover_data=['arrest_date', 'pd_desc', 'arrest_boro', 'arrest_precinct', 'ofns_desc', 'law_code', 'age_group', 'perp_sex', 'perp_race', 'lon_lat', 'law_cat_cd'],
                        mapbox_style='carto-positron',
                        zoom=10,
                        center={'lat': 40.7128, 'lon': -74.0060},  # Coordinates for New York City
                        color_continuous_scale=px.colors.sequential.Viridis,
                        title='Arrest Data (Heatmap)')


# Change the height of the map
fig.update_layout(height=1000)

# Add Subway Station data to arrest heatmap
fig.add_trace(subway_stations)


unique_years = NYPD['year'].unique()
unique_ofns = NYPD['ofns_desc'].dropna().unique()
available_subway_lines = SUBWAY['line'].unique()
subway_options = [{'label': line, 'value': line} for line in available_subway_lines]

# Create dropdown options
year_options = [{'label': year, 'value': year} for year in unique_years]
ofns_options = [{'label': ofns, 'value': ofns} for ofns in unique_ofns]

app = dash.Dash(__name__)
server = app.server
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


index_page = html.Div([
    html.Title('NYPD Subway Entrance and Arrest Data'),
    html.Div([
        html.A('Home', href='http://flame.zapto.org:42420/', target='_blank'),
        html.Br(),
        html.A('About us', href='http://flame.zapto.org:420/about-us.html', target='_blank'),
        html.Br(),
        html.A('Google Site', href='https://sites.google.com/view/nypd-subway-entrance-and-arrest/home', target='_blank'),
    ], style={'backgroundColor': '#f0f0f0', 'padding': '10px', 'border':'10px clear'}),
    dcc.Dropdown(id='year_dropdown', options=year_options, multi=True, value=2023, placeholder='Select a year to filter by'),
    dcc.Dropdown(id='ofns_dropdown', options=ofns_options, multi=True, placeholder='Select an offense to filter by'),
    dcc.Dropdown(id='subway_dropdown', options=subway_options, multi=True, placeholder='Select a subway line to filter by'),
    dcc.Graph(id='heatmap')
])

about_us_page = html.Div([
    html.H1('About Us'),
    html.P('Here is some information about us...'),  # replace with your own content
    dcc.Link('Go back to home', href='/')
])

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/about-us':
        return about_us_page
    else:
        return index_page
@app.callback(
    Output('heatmap', 'figure'),
    [Input('year_dropdown', 'value'),
     Input('ofns_dropdown', 'value'),
     Input('subway_dropdown', 'value')]  # Add the subway line as an input
)
def update_heatmap(selected_years, selected_ofns, selected_subway_lines):  
    if selected_years is not None:
        if not isinstance(selected_years, list):
            selected_years = [selected_years]
        NYPD_filtered = NYPD[NYPD['year'].isin(selected_years)]
    else:
        NYPD_filtered = NYPD.copy()
    
    if selected_ofns is not None:
        if not isinstance(selected_ofns, list):
            selected_ofns = [selected_ofns]
        NYPD_filtered = NYPD_filtered[NYPD_filtered['ofns_desc'].isin(selected_ofns)]

    # Filter subway stations, or use all if no line selected
    if selected_subway_lines is not None:
        if not isinstance(selected_subway_lines, list):
            selected_subway_lines = [selected_subway_lines]
        SUBWAY_filtered = SUBWAY[SUBWAY['line'].isin(selected_subway_lines)]
    else:
        SUBWAY_filtered = SUBWAY.copy()

    subway_stations = go.Scattermapbox(
        lat=SUBWAY_filtered['latitude'],
        lon=SUBWAY_filtered['longitude'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=5,
            color='rgb(48, 213, 200)',
            opacity=1),
        text=SUBWAY_filtered['info'],
        hoverinfo='text'
    )
    
    fig = px.density_mapbox(NYPD_filtered,
                            lat='latitude',
                            lon='longitude',
                            z='Number of People Arrested',
                            radius=10,
                            hover_name='arrest_boro',
                            hover_data=['arrest_date', 'pd_desc', 'arrest_boro', 'arrest_precinct', 'ofns_desc', 'law_code', 'age_group', 'perp_sex', 'perp_race', 'lon_lat', 'law_cat_cd'],
                            mapbox_style='carto-positron',
                            zoom=10,
                            center={'lat': 40.7128, 'lon': -74.0060},
                            color_continuous_scale=px.colors.sequential.Agsunset,
                            title='Subway Entrances and Arrest Data (Heatmap)')

    fig.update_layout(height=1000)

    fig.add_trace(subway_stations)

    return fig



if __name__ == '__main__':
    app.run_server()