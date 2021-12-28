# --- import libraries ---
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Output, Input

import json
import requests

import plotly.io as pio
import plotly.offline as pyo

px.set_mapbox_access_token("pk.eyJ1IjoidG9ueXBhcmswMDEiLCJhIjoiY2t2dWVramFmODZqaDJucXBrbnhpZ2JreCJ9.-XXf1YI8YESgWbWODhZAZA")

from app import app
import os

# --- load data ---
df_h = pd.read_csv('map_assets/historical_cleaned.csv')
df_H = pd.read_csv('map_assets/df_h.csv')

#df_h['Date'] = pd.to_datetime(df_h['Date'])

df_s = pd.read_csv('map_assets/school_districts_greatschools_demographics.csv')

geo_df = pd.read_csv('map_assets/gdf.csv')
df_arima = pd.read_csv('map_assets/df_arima.csv')
df_arima['Date'] = pd.to_datetime(df_arima['Date'])
df_arima['Date'] = df_arima['Date'].dt.strftime('%Y-%m')
# df_arima i dont think this will be needed

options = []
for column in df_H.columns:
    options.append({'label': '{}'.format(column, column), 'value': column})
options = options[1:]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# # --- initialize the app ---
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# server = app.server

# --- layout the dashboard ---
mapping_layout = html.Div([
    html.Div([
        html.Div([
                html.H1('Historical Home Prices in Market vs existing SMH Properties', style = {'textAlign': 'center',
                                                                                 'color': '#FFFFFF',
                                                                                 'fontSize': '30px',
                                                                                 'padding-top': '0px'},
                        ),

                html.P('''An interactive dashboard and analysis displaying active and sold listings in SMH covered states for last three years. Marketing listings gathered from Redfin.com''',
                       style = {'textAlign': 'center',
                                'color': '#FFFFFF',
                                'fontSize': '16px'},
                    ),
                ],
            style = {'backgroundColor': '#1f3b4d',
                     'height': '200px',
                     'display': 'flex',
                     'flexDirection': 'column',
                     'justifyContent': 'center'},
            ),
        html.Div([
            html.Div([
            html.Label('Select a state to see home price data'),
            dcc.Dropdown(
                id = 'city-dropdown',
                options = options,
                value = 'Denver, CO',
                multi = False,
                clearable = True,
                searchable = True,
                placeholder = 'Choose a State...',
                ),
            ],
            style = {'width': '25%',
                     'display': 'inline-block',
                     'padding-left': '150px',
                     'padding-top': '20px'}
                ),
        html.Div(
            dcc.Graph(id = 'forecast-container',
                 style = {'padding': '25px'}),
            )
        ]),
        # html.Div([
        #     html.Div(
        #         dcc.Graph(id = 'graph-container',
        #          style = {'padding': '25px'}),
        #         ),
            html.Div(
                dcc.Graph(id = 'map-container',
                  style = {'padding': '50px'})
                ),
            html.Label('''Filter data in the first row of the table to see
                       changes on the map and graph! Example: > 100000 Population,
                       < 300000 Median Home price, etc.''',
                       style = {'padding-left': '5px'}),
            dash_table.DataTable(
                id = 'datatable',
                columns = [{'name': i, 'id': i,
                            'deletable': True, 'selectable': True,
                            'hideable': True} for i in df_h.columns],
                data = df_h.to_dict('records'), editable = False,
                filter_action = 'native', sort_action = 'native',
                sort_mode = 'multi', column_selectable = 'multi',
                row_selectable = 'multi', row_deletable = True,
                selected_columns = [],selected_rows = [],
                page_action = 'native', page_current = 0,
                page_size = 100, fill_width = False,
                style_table = {'padding': '50px',
                               'height': '300px',
                               'overflowY': 'auto'},
                style_cell_conditional = [
                    {'if': {'column_id': c},
                     'textAlign': 'center'}
                    for c in ['Population', 'Median Household Income ($USD)',
                              'Median Home Price ($USD, January 2021)']
                    ],
                style_data = {
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    }
                        ),
            html.Label('References:',
                       style = {'padding': '10px'}
                       ),
            html.Label('[1] Redfin, 2021, Download CSV of properties falling within zipcode from last 3 years, includes sold listings:',
                       style = {'padding-left': '25px'}),
            html.A('https://www.redfin.com/zipcode/{zipcode}/filter/include=forsale+mlsfsbo+construction+fsbo+sold-3yr',
                   style = {'padding-left': '25px'}),
            html.Label('[2] Stanley Martin Homes Projects, 2021:',
                       style = {'padding-left': '25px'}),
            html.A('Internal from SMH data team.',
                   style = {'padding-left': '25px',
                   'padding-bottom': '25px'}),
            # html.Label('[3] GeoNames API (Geocoders):',
            #            style = {'padding-left': '25px'}),
            # html.A('https://geocoder.readthedocs.io/providers/GeoNames.html',
            #        style = {'padding-left': '25px',
            #                 'padding-bottom': '25px'}),
                    ],
                    ),
                ],
            )

# --- dropdown callback ---
@app.callback(
    Output('forecast-container', 'figure'),
    Input('city-dropdown', 'value'))
def update_figure(selected_city):
    dff = df_H[['Date', selected_city]]
    # dff[selected_city] = dff[selected_city].round(0)
    dfa = df_arima[df_arima['City'] == selected_city]

    fig = px.line(dff, x = 'Date', y = selected_city,
                  hover_data = {selected_city: ':$,f'}).update_traces(
                      line = dict(color = '#1f3b4d', width = 2))

    # fig.add_scatter(x = dfa.Date, y = dfa.Mean,
    #                 line_color = 'orange', name = 'Forecast Mean',
    #                 hovertemplate = 'Forecast Mean: %{y:$,f}<extra></extra>')
    #
    # fig.add_scatter(x = dfa.Date, y = dfa.Lower_ci,
    #                 fill = 'tonexty', fillcolor = 'rgba(225,225,225, 0.3)',
    #                 marker = {'color': 'rgba(225,225,225, 0.9)'},
    #                 name = 'Lower 95% Confidence Interval',
    #                 hovertemplate = 'Lower 95% Confidence Interval: %{y:$,f}<extra></extra>')
    #
    # fig.add_scatter(x = dfa.Date, y = dfa.Upper_ci,
    #                 fill = 'tonexty', fillcolor = 'rgba(225,225,225, 0.3)',
    #                 marker = {'color': 'rgba(225,225,225, 0.9)'},
    #                 name = 'Upper 95% Confidence Interval',
    #                 hovertemplate = 'Upper 95% Confidence Interval: %{y:$,f}<extra></extra>')

    fig.update_layout(template = 'xgridoff',
                      yaxis = {'title': 'Median Home Price by State ($)'},
                      xaxis = {'title': 'Year Sold'},
                      title = {'text': 'Home Prices vs. Year for {}'.format(selected_city),
                               'font': {'size': 24}, 'x': 0.5, 'xanchor': 'center'}
                      )

    return fig

#--- choropleth callback ---
@app.callback(
    Output('graph-container', 'figure'),
    Input('datatable', 'derived_virtual_data'))

def update_scatter(all_rows_data):
    dff = pd.DataFrame(all_rows_data)
    dffm = df_s

    fig = px.choropleth_mapbox(dffm, geojson=geo_df, color="avg_pct_low_income",locations="GEOID",
                                featureidkey="properties.GEOID",hover_name = "school_district_id" ,opacity=0.7, zoom=2)

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_geos(fitbounds="locations", visible=False)

    return fig


# --- map callback ---
@app.callback(
    Output('map-container', 'figure'),
    Input('datatable', 'derived_virtual_data'))
def update_map(all_rows_data):
    dffm = pd.DataFrame(all_rows_data)

    fig = (px.scatter_mapbox(dffm[dffm['PRICE']<500000], lat="LATITUDE", lon="LONGITUDE", color="PRICE"))
    fig.update_traces(marker={"size": 10})

    fig.update_layout(title_text = 'Visualizing Home Sale Data on Map',
                      title_font_size = 24,
                      #title_xref = 'container',
                      title_y = 0.99,
                      title_x = 0.5, mapbox={"style": "open-street-map","zoom": 5,"layers": [
                {
                    "source": json.loads(geo_df.geometry.to_json()),
                    "below": "traces",
                    "type": "line",
                    "color": "blue",
                    "line": {"width": 1.5},
                }
            ],
        },
        margin={"l": 0, "r": 0, "t": 0, "b": 0}, )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
