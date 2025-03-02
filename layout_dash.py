
import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np



def create_fighters_tab(fighters_df):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("SELECT FIGHTER", className="text-danger"),
                html.Label('Select fighter name'),
                dcc.Dropdown(
                    id='fighter-dropdown',
                    options=[{'label': name, 'value': name} for name in fighters_df['Name']],
                    value=fighters_df['Name'][0],
                    className="mb-4"
                ),
            ], width=4),
            dbc.Col([
                html.H4("FILTER OPTIONS", className="text-danger"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Weight Class"),
                        dcc.Dropdown(
                            id='weight-class-filter',
                            options=[{'label': wc, 'value': wc} 
                                    for wc in sorted(fighters_df['Weight_Class'].unique())],
                            multi=True,
                            placeholder="All Weight Classes"
                        ),
                    ], width=12),
                ]),
            ], width=6),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("FIGHTER PROFILE", className="text-center")),
                    dbc.CardBody(
                        html.Div(id="fighter-profile-content")
                    )
                ]),
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("PERFORMANCE METRICS", className="text-center")),
                    dbc.CardBody(
                        dcc.Graph(id="fighter-radar-chart", style={"height": "400px"})
                    )
                ]),
            ], width=8),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("RECENT FIGHTS", className="text-center")),
                    dbc.CardBody(
                        html.Div(id="fighter-recent-fights")
                    )
                ]),
            ]),
        ]),
    ])

def create_matches_tab(results_df):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("SELECT EVENT", className="text-danger"),
                dcc.Dropdown(
                    id='event-dropdown',
                    options=[{'label': event, 'value': event} for event in sorted(results_df['EVENT'].unique())],
                    value=results_df['EVENT'][0],
                    className="mb-4"
                ),
            ], width=4),
            dbc.Col([
                html.H4("FILTER OPTIONS", className="text-danger"),
                dbc.Row([
                    dbc.Col([
                        html.Label("DATE Range"),
                        dcc.DatePickerRange(
                            id='date-range',
                            min_date_allowed=min(pd.to_datetime(results_df['DATE'])),
                            max_date_allowed=max(pd.to_datetime(results_df['DATE'])),
                            start_date=min(pd.to_datetime(results_df['DATE'])),
                            end_date=max(pd.to_datetime(results_df['DATE'])),
                        ),
                    ], width=6),
                ]),
            ], width=8),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("MATCH DETAILS", className="text-center")),
                    dbc.CardBody(
                        html.Div(id="match-details-content")
                    )
                ]),
            ], width=5),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("FIGHT STATISTICS", className="text-center")),
                    dbc.CardBody(
                        dcc.Graph(id="match-stats-chart", style={"height": "400px"})
                    )
                ]),
            ], width=7),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("FINISH DISTRIBUTION", className="text-center")),
                    dbc.CardBody(
                        dcc.Graph(id="finish-distribution", style={"height": "300px"})
                    )
                ]),
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("ROUND FINISHES", className="text-center")),
                    dbc.CardBody(
                        dcc.Graph(id="round-finishes", style={"height": "300px"})
                    )
                ]),
            ], width=6),
        ]),
    ])

def create_layout_2(fighters_df, results_df):
    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/UFC_Logo.svg/2560px-UFC_Logo.svg.png", height="50px")),
                            dbc.Col(html.H3("UFC ANALYTICS", className="ms-3 text-light")),
                        ],
                        align="center",
                    ),
                    style={"textDecoration": "none"},
                ),
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("FIGHTER STATS", href="#fighters", id="fighters-link")),
                        dbc.NavItem(dbc.NavLink("MATCH ANALYSIS", href="#matches", id="matches-link")),
                        dbc.NavItem(dbc.NavLink("FIGHTER COMPARISON", href="#comparison", id="comparison-link")),
                    ],
                    className="ms-auto",
                    navbar=True,
                ),
            ]
        ),
        color="dark",
        dark=True,
        className="mb-4",
    )

    content = html.Div(
        create_fighters_tab(fighters_df),  # Default to fighter stats tab
        id="page-content"
    )

    layout = html.Div([
        navbar,
        content,
        dcc.Store(id='active-tab', data='fighters')
    ])
    
    return layout
