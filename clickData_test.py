from jupyter_dash import JupyterDash
import json
import dash
import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly
import plotly.express as px
import dash_bootstrap_components as dbc

# import data
df = pd.read_csv('dummy_data_test.csv')

with open('geo_gemeenten.json') as json_data:
     geo_muni = json.load(json_data)
with open('geo_wijken.json') as json_data:
     geo_neigh = json.load(json_data)
        
# mapbox token
token = 'pk.eyJ1IjoiY2FzcGFyLWVnYXMiLCJhIjoiY2poc3QwazFkMDNiaTNxbG1vMmJvZmVwcCJ9.Yy65IKfEEM015SvKt8OBqw'

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

colors = {'background': '#979797','text': '#ffffff'}

# primary choro_figure with dummy data on municipality level
choro_figure = px.choropleth_mapbox(
    df, geojson=geo_muni, color='prevalentie', color_continuous_scale=px.colors.sequential.Viridis_r,
    locations="GM_NAAM", featureidkey="properties.GM_NAAM",
    center={"lat": 52.0907, "lon": 5.1214}, 
    zoom=6, range_color=[0, 131])

choro_figure.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text'],
    mapbox = dict(
        accesstoken = token,
        style = 'mapbox://styles/caspar-egas/cl1yy8qvz001o15mujg2i3kzr'))

choro_layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    dcc.Graph(id="choro_graph", figure=choro_figure, config={'displayModeBar':False}),
])

# secondary choro_figure with dummy data on neighborhood level 
def create_choro2(df_function):
    municipal_code = df_function[df_function["geo"] == "GEM"].iloc[0]["code"]
    municipal_feature = next((x for x in geo_muni["features"] if x["properties"]["GM_CODE"] == municipal_code), None)
    
    choro_figure2 = px.choropleth_mapbox(
        df_function, geojson=geo_neigh, color='prevalentie', color_continuous_scale=px.colors.sequential.Viridis_r,
        locations="WK_NAAM", featureidkey="properties.WK_NAAM",
        center= {"lat": municipal_feature["properties"]["centroid_y"], "lon": municipal_feature["properties"]["centroid_x"]},
        zoom=9.5, range_color=[0, 600])

    choro_figure2.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        mapbox = dict(
            accesstoken = token,
            style = 'mapbox://styles/caspar-egas/cl1yy8qvz001o15mujg2i3kzr'))
    
    return choro_figure2

default_selection = df[df['GM_NAAM'] == 'Utrecht']

choro_layout2 = html.Div(style={'backgroundColor': colors['background']}, children=[
    dcc.Graph(id="choro_graph2", figure=create_choro2(default_selection), config={'displayModeBar':False}),
])

@app.callback(
    Output('choro_graph2', 'figure'),
    Input('choro_graph', 'clickData'))
def update_choro2(clickData):
    if clickData:
        location = clickData['points'][0]['location']
        dff = df[df['GM_NAAM'] == location]
    else:
        dff = df[df['GM_NAAM'] == 'Utrecht']
    return create_choro2(dff)

dashlayout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(html.Div(children=[choro_layout]),style={'height': '400px'}, width=6),
                dbc.Col(html.Div(children=[choro_layout2]),style={'height': '400px'}, width=6),
            ],
            className="g-0",
            style={"height": "100vh", "background-color": colors['background']},
                ),
    ],
            
)


app.layout = dashlayout

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
