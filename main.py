import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go

import numpy as np
import pandas as pd


def polygon_sort(corners):
    n = len(corners)
    cx = float(sum(x for x, y in corners)) / n
    cy = float(sum(y for x, y in corners)) / n
    corners_with_angles = []
    for x, y in corners:
        an = (np.arctan2(y - cy, x - cx) + 2.0 * np.pi) % (2.0 * np.pi)
        corners_with_angles.append((x, y, an))
    corners_with_angles.sort(key=lambda tup: tup[2])

    return list(map(lambda item: (item[0], item[1]), corners_with_angles))


def get_raw_polygon(df: pd.DataFrame):
    trace = go.Scatter(
        x=df[0],
        y=df[1],
        mode='markers+lines',
        text=list(range(len(df)))
    )

    return go.Figure(data=trace)


def get_sorted_polygon(df: pd.DataFrame):
    corners_sorted = polygon_sort(df.values)

    trace = go.Scatter(
        x=[corner[0] for corner in corners_sorted] + [corners_sorted[0][0]],
        y=[corner[1] for corner in corners_sorted] + [corners_sorted[0][1]],
        mode='markers+lines',
        text=list(range(len(df))),
        fill='tonexty'
    )

    return go.Figure(data=trace)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
init_df = pd.read_json('dataset1.json', orient='values')

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        }
    ),

    html.Div([
        dcc.Graph(id='raw-polygon-graph', figure=get_raw_polygon(init_df)),
    ],
        style={'display': 'inline-block', 'width': '49%'}
    ),

    html.Div([
        dcc.Graph(id='sorted-polygon-graph', figure=get_sorted_polygon(init_df)),
    ],
        style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}
    ),

    html.Div(id='output-data-upload'),
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'json' in filename:
            df = pd.read_json(io.StringIO(decoded.decode('utf-8')), orient='values')
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': str(i), 'id': str(i)} for i in df.columns]
        ),
    ])


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(content, name, date):
    if content is not None:
        children = [parse_contents(content, name, date)]
        return children


if __name__ == '__main__':
    app.run_server(debug=True)
