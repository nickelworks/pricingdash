import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

import fiona
import geopandas as gpd
import pandas as pd

from dash.dependencies import Input, Output

#initializing the dash app
app = dash.Dash(__name__)

#reading the school boundaries dataset
data = pd.read_json("https://nycdsacapstone2021.blob.core.windows.net/geojsons/school_districts_simplified.json")
gdf = gpd.GeoDataFrame.from_features(data["features"])

#reading the greatschools.org agg dataset
schools_df = pd.read_csv('https://nycdsacapstone2021.blob.core.windows.net/mapping/school_districts_greatschools_demographics.csv', index_col= 0).drop(['first_word'], axis = 1)
schools_df['GEOID'] = schools_df['GEOID'].astype('int')

# app.layout = html.Div([
#     html.P("Candidate:"),
#     dcc.RadioItems(
#         id='candidate',
#         options=[{'value': x, 'label': x}
#                  for x in candidates],
#         value=candidates[0],
#         labelStyle={'display': 'inline-block'}
#     ),
#     dcc.Graph(id="choropleth"),
# ])

# @app.callback(
#     Output("choropleth", "figure"),
#     [Input("candidate", "value")])

# def display_choropleth(candidate):
    # fig = px.choropleth(
    #     df, geojson=geojson, color=candidate,
    #     locations="district", featureidkey="properties.district",
    #     projection="mercator", range_color=[0, 6500])
    # fig.update_geos(fitbounds="locations", visible=False)
    # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

fig = px.choropleth_mapbox(
    schools_df, geojson=gdf, color="avg_rating",
    locations="GEOID", featureidkey="properties.GEOID",
    hover_name = "school_district_id",
    mapbox_style="open-street-map", opacity=0.7, zoom=2)

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# return fig

app.layout = html.Div(style = {
  'backgroundColor': '#111111'
}, children = [
    html.H1(
    children = 'Hello Dash',
    style = {
      'textAlign': 'center',
      'color': '#7FDBFF'
    }
  ),

    html.Div(children = 'Nicoles first graph on her app.', style = {
    'textAlign': 'center',
    'color': '#7FDBFF'
  }),

    dcc.Graph(
    id = 'choropleth',
    figure = fig
  )
])

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port=8060, debug=True)
