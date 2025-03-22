
import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Define common plot layout settings
plot_layout = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#ffffff"},
    "margin": dict(t=20, l=20, r=20, b=20),
}

# Define grid settings
grid_settings = {
    "gridcolor": "rgba(128, 128, 128, 0.1)",
    "zerolinecolor": "rgba(128, 128, 128, 0.2)"
}



def create_fighters_tab(fighters_df,results_df,stats_df):
    return dbc.Container([
        # Search and Filter Section
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H4("FIGHTER SELECTION", className="text-danger mb-3"),
                        dbc.InputGroup([
                            dbc.InputGroupText([
                                html.I(className="fas fa-search text-muted")
                            ]),
                            dcc.Dropdown(
                                id='fighter-dropdown',
                                options=[{'label': name.title(), 'value': name} for name in fighters_df['Name']],
                                value=fighters_df['Name'][0],
                                className="custom_dropdown",
                                placeholder="Search for a fighter..."
                            ),
                        ]),
                    ], width=6),
                    dbc.Col([
                        html.H4("QUICK STATS", className="text-danger mb-3 text-center"),
                        html.Div(id="quick-stats", className="d-flex justify-content-around")
                    ], width=6),
                ]),
            ])
        ], className="mb-4"),
        
        # Main Content Row
        dbc.Row([
            # Left Column - Fighter Profile
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("FIGHTER PROFILE", className="text-center mb-0"),
                        html.Div(className="card-header-icon text-danger text-center mt-2",
                                children=[html.I(className="fas fa-user-circle fa-2x")])
                    ], className="text-center"),
                    dbc.CardBody([
                        html.Div(id="fighter-profile-content", className="animated fadeIn")
                    ])
                ], className="h-100"),
            ], width=4),
            
            # Right Column - Performance Metrics
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("PERFORMANCE METRICS", className="text-center mb-0"),
                        html.Div(className="card-header-icon text-danger text-center mt-2",
                                children=[html.I(className="fas fa-chart-radar fa-2x")])
                    ], className="text-center"),
                    dbc.CardBody([
                        dbc.Spinner(
                            dcc.Graph(
                                id="fighter-radar-chart",
                                style={"height": "400px"},
                                config={'displayModeBar': False}
                            ),
                            color="danger",
                            type="border"
                        )
                    ])
                ], className="h-100"),
            ], width=8),
        ], className="mb-4"),
        

        
        dbc.Card([
            dbc.CardHeader([
                html.H5("FIGHTING ANALYSIS", className="text-center mb-0"),
                html.Div(className="card-header-icon text-danger text-center mt-2",
                        children=[html.I(className="fas fa-chart-bar fa-2x")])
            ], className="text-center"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                html.H5("STRIKE DISTRIBUTION", className="text-center mb-0"),
                            ),
                            dbc.CardBody([
                                dbc.Spinner(
                                    dcc.Graph(
                                        id="fighter-strike-distribution",
                                        style={"height": "400px", "backgroundColor": "transparent"},
                                        config={'displayModeBar': False}
                                    ),
                                    color="danger",
                                    type="border"
                                )
                            ])
                        ]),
                    ], width=6),

                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                html.H5("FIGHTING STYLE ANALYSIS", className="text-center mb-0"),
                            ),
                            dbc.CardBody([
                                dbc.Spinner(
                                    dcc.Graph(
                                        id="fighter-style-analysis",
                                        style={"height": "400px", "backgroundColor": "transparent"},
                                        config={'displayModeBar': False}
                                    ),
                                    color="danger",
                                    type="border"
                                )
                            ])
                        ]),
                    ], width=6),
                ])
            ])
        ], className="mb-4"),
        
        # Removed Fight Momentum Analysis Section

        dbc.Card([
            dbc.CardHeader([
                html.H5("RECENT FIGHT HISTORY", className="text-center mb-0"),
                html.Div(className="card-header-icon text-danger text-center mt-2",
                        children=[html.I(className="fas fa-history fa-2x")])
            ], className="text-center"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H6("LAST 5 FIGHTS", className="text-danger mb-3 text-center"),
                            dbc.Spinner(
                                html.Div(
                                    id="fighter-recent-fights",
                                    className="recent-fights-container"
                                ),
                                color="danger",
                                type="border",
                            )
                        ], className="p-2"),
                        html.Hr(className="my-4"),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H6("WIN STREAK", className="text-center mb-2"),
                                    html.Div(id="win-streak", className="text-center fs-4")
                                ])
                            ], width=4),
                            dbc.Col([
                                html.Div([
                                    html.H6("FINISH RATE", className="text-center mb-2"),
                                    html.Div(id="finish-rate", className="text-center fs-4")
                                ])
                            ], width=4),
                            dbc.Col([
                                html.Div([
                                    html.H6("AVG. FIGHT TIME", className="text-center mb-2"),
                                    html.Div(id="avg-fight-time", className="text-center fs-4")
                                ])
                            ], width=4),
                        ], className="text-muted"),
                    ], width=12)
                ])
            ])
        ], className="mb-4"),

    ])

def create_matches_tab(fighters_df,stats_df,results_df):
    return dbc.Container([
        # Match Selection Section
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H4("MATCH SELECTION", className="text-danger mb-3"),
                        dbc.InputGroup([
                            dbc.InputGroupText([
                                html.I(className="fas fa-trophy text-muted")
                            ], style={"border-right": "none"}),
                            dcc.Dropdown(
                                id='match-dropdown',
                                options=[{'label': match, 'value': match} for match in sorted(stats_df['BOUT'].unique())],
                                value=stats_df['BOUT'][0],
                                className="custom_dropdown",
                                placeholder="Search for a match..."
                            ),
                        ], className="align-items-center"),
                    ], width=6),
                    # dbc.Col([
                    #     html.H4("MATCH STATS", className="text-danger mb-3"),
                    #     html.Div(id="match-quick-stats", className="d-flex justify-content-around")
                    # ], width=6),
                ]),
            ])
        ], className="mb-4"),
        
        # Main Content
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("MATCH DETAILS", className="text-center mb-0"),
                        html.Div(className="card-header-icon text-danger text-center mt-2",
                                children=[html.I(className="fas fa-info-circle fa-2x")])
                    ], className="text-center"),
                    dbc.CardBody([
                        dbc.Spinner(
                            html.Div(id="match-details-content", className="animated fadeIn"),
                            color="danger",
                            type="border",
                        )
                    ])
                ], className="h-100")
            ], width=5),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("FIGHT STATISTICS", className="text-center mb-0"),
                        html.Div(className="card-header-icon text-danger text-center mt-2",
                                children=[html.I(className="fas fa-chart-bar fa-2x")])
                    ], className="text-center"),
                    dbc.CardBody([
                        dbc.Spinner(
                            dcc.Graph(
                                id="match-stats-chart",
                                style={"height": "372px", "backgroundColor": "transparent"},
                                config={'displayModeBar': False}
                            ),
                            color="danger",
                            type="border"
                        )
                    ])
                ], className="h-100")
            ], width=7)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("STRIKE DISTRIBUTION", className="text-center mb-0"),
                        html.Div(className="card-header-icon text-danger text-center mt-2",
                                children=[html.I(className="fas fa-fist-raised fa-2x")])
                    ], className="text-center"),
                    dbc.CardBody([
                        dbc.Spinner(
                            dcc.Graph(
                                id="strike-distribution",
                                style={"height": "600px", "backgroundColor": "transparent"},
                                config={'displayModeBar': False}
                            ),
                            color="danger",
                            type="border"
                        )
                    ])
                ], className="h-100")
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("TAKEDOWN ANALYSIS", className="text-center mb-0"),
                        html.Div(className="card-header-icon text-danger text-center mt-2",
                                children=[html.I(className="fas fa-hand-rock fa-2x")])
                    ], className="text-center"),
                    dbc.CardBody([
                        dbc.Spinner(
                            dcc.Graph(
                                id="takedown-analysis",
                                style={"height": "600px", "backgroundColor": "transparent"},
                                config={'displayModeBar': False}
                            ),
                            color="danger",
                            type="border"
                        )
                    ])
                ], className="h-100")
            ], width=6)
        ], className="mb-4"),
                
        dbc.Card([
            dbc.CardHeader([
                html.H5("ROUND-BY-ROUND ANALYSIS", className="text-center mb-0"),
                html.Div(className="card-header-icon text-danger text-center mt-2",
                        children=[html.I(className="fas fa-clock fa-2x")])
            ], className="text-center"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("SELECT ROUND", className="text-danger mb-2 d-block text-center"),
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Slider(
                                    id='timeline-slider',
                                    min=1,
                                    max=5,
                                    step=1,
                                    value=3,
                                    marks={
                                        i: {'label': f'ROUND {i}', 'style': {'color': '#ffffff'}}
                                        for i in range(1, 6)
                                    },
                                    className="mb-4"
                                )
                            ])
                        ], className="bg-transparent border-0 mb-4")
                    ], width=12),
                ]),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                html.H6("FIGHT PROGRESSION", className="text-center mb-0")
                            ),
                            dbc.CardBody([
                                dbc.Spinner(
                                    dcc.Graph(
                                        id="fight-timeline",
                                        style={"height": "400px", "backgroundColor": "transparent"},
                                        config={'displayModeBar': False}
                                    ),
                                    color="danger",
                                    type="border"
                                )
                            ])
                        ])
                    ], width=12),
                ], className="mb-4"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                html.H6("ROUND STATISTICS", className="text-center mb-0")
                            ),
                            dbc.CardBody([
                                dbc.Spinner(
                                    dcc.Graph(
                                        id="fight-round-distribution",
                                        style={"height": "400px", "backgroundColor": "transparent"},
                                        config={'displayModeBar': False}
                                    ),
                                    color="danger",
                                    type="border"
                                )
                            ])
                        ])
                    ], width=12)
                ])
            ])
        ], className="mb-4"),
        
        
    ])

def create_comparison_tab(fighters_df,results_df,stats_df):
    return dbc.Container([
        # Fighter Selection Section
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H4("FIGHTER 1 SELECTION", className="text-danger mb-3"),
                        dbc.InputGroup([
                            dbc.InputGroupText([
                                html.I(className="fas fa-user text-muted")
                            ]),
                            dcc.Dropdown(
                                id='fighter1-dropdown',
                                options=[{'label': name.title(), 'value': name} for name in fighters_df['Name']],
                                value=fighters_df['Name'][0],
                                className="custom_dropdown",
                                placeholder="Select first fighter..."
                            ),
                        ]),
                    ], width=5),
                    dbc.Col([
                        html.Div([
                            html.H4("VS", className="text-danger text-center"),
                            html.I(className="fas fa-exchange-alt fa-2x text-muted text-center")
                        ], className="h-100 d-flex flex-column justify-content-center align-items-center")
                    ], width=2),
                    dbc.Col([
                        html.H4("FIGHTER 2 SELECTION", className="text-danger mb-3"),
                        dbc.InputGroup([
                            dbc.InputGroupText([
                                html.I(className="fas fa-user text-muted")
                            ]),
                            dcc.Dropdown(
                                id='fighter2-dropdown',
                                options=[{'label': name.title(), 'value': name} for name in fighters_df['Name']],
                                value=fighters_df['Name'][1],
                                className="custom_dropdown",
                                placeholder="Select second fighter..."
                            ),
                        ]),
                    ], width=5),
                ], className="align-items-center"),
            ])
        ], className="mb-4"),


        
        # Fighters Overview Section
        dbc.Card([
            dbc.CardHeader([
                html.H5("FIGHTERS OVERVIEW", className="text-center mb-0"),
                html.Div(className="card-header-icon text-danger text-center mt-2",
                        children=[html.I(className="fas fa-users fa-2x")])
            ], className="text-center"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("FIGHTER 1", className="text-center")),
                            dbc.CardBody([
                                dbc.Spinner(
                                    html.Div(id="fighter-1-overview", className="animated fadeIn"),
                                    color="danger",
                                    type="border"
                                )
                            ])
                        ])
                    ], width=4),
                    dbc.Col([
                        html.Div([
                            html.Img(
                                src='https://res.cloudinary.com/da7h9bpnj/image/upload/v1740722018/Pngtree_vs_624541_ty55wp.png',
                                className="img-fluid animate__animated animate__pulse animate__infinite",
                                style={"max-width": "60%", "height": "auto"}
                            )
                        ], className="d-flex h-100 align-items-center justify-content-center")
                    ], width=4),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("FIGHTER 2", className="text-center")),
                            dbc.CardBody([
                                dbc.Spinner(
                                    html.Div(id="fighter-2-overview", className="animated fadeIn"),
                                    color="danger",
                                    type="border"
                                )
                            ])
                        ])
                    ], width=4)
                ])
            ])
        ], className="mb-4-1"),

        
        # Stats Comparison Section
        dbc.Card([
            dbc.CardHeader([
                html.H5("STATS COMPARISON", className="text-center mb-0"),
                html.Div(className="card-header-icon text-danger text-center mt-2",
                        children=[html.I(className="fas fa-chart-bar fa-2x")])
            ], className="text-center"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("COMPARISON METRICS", className="text-danger mb-2 d-block text-center"),
                        dbc.ButtonGroup([
                            dbc.Button("Overall Stats", id="stats-type-overall", color="danger", outline=True, active=True, className="me-1"),
                            dbc.Button("Strike Stats", id="stats-type-strikes", color="danger", outline=True, className="me-1"),
                            dbc.Button("Grappling", id="stats-type-grappling", color="danger", outline=True),
                        ], className="d-flex justify-content-center mb-4")
                    ], width=12),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Spinner(
                            dcc.Graph(
                                id="fighters-comparison-chart",
                                style={"height": "400px", "backgroundColor": "transparent"},
                                config={'displayModeBar': False}
                            ),
                            color="danger",
                            type="border"
                        )
                    ], width=12)
                ])
            ])
        ], className="mb-4"),

        # Tale of the Tape Section
        dbc.Card([
            dbc.CardHeader([
                html.H5("TALE OF THE TAPE", className="text-center mb-0"),
                html.Div(className="card-header-icon text-danger text-center mt-2",
                        children=[html.I(className="fas fa-file-alt fa-2x")])
            ], className="text-center"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("COMPARE STATS", className="text-danger mb-2 d-block text-center"),
                        dbc.ButtonGroup([
                            dbc.Button("Physical Stats", id="tape-type-physical", color="danger", outline=True, active=True, className="me-1"),
                            dbc.Button("Career Stats", id="tape-type-career", color="danger", outline=True, className="me-1"),
                            dbc.Button("Form Guide", id="tape-type-form", color="danger", outline=True),
                        ], className="d-flex justify-content-center mb-4")
                    ], width=12),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Spinner(
                            html.Div(id="tale-of-tape-content", className="animated fadeIn"),
                            color="danger",
                            type="border"
                        )
                    ], width=12)
                ])
            ])
        ], className="mb-4"),
        
        # Fighting Analysis Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("FIGHTING STYLE BREAKDOWN", className="text-center mb-0"),
                        html.Div(className="card-header-icon text-danger text-center mt-2",
                                children=[html.I(className="fas fa-fist-raised fa-2x")])
                    ], className="text-center"),
                    dbc.CardBody([
                        html.Label("SELECT ANALYSIS TYPE", className="text-danger mb-2 d-block text-center"),
                        dbc.ButtonGroup([
                            dbc.Button("Striking", id="style-type-striking", color="danger", outline=True, active=True, className="me-1"),
                            dbc.Button("Ground Game", id="style-type-ground", color="danger", outline=True),
                        ], className="d-flex justify-content-center mb-4"),
                        dbc.Spinner(
                            dcc.Graph(
                                id="fighting-style-comparison",
                                style={"height": "400px", "backgroundColor": "transparent"},
                                config={'displayModeBar': False}
                            ),
                            color="danger",
                            type="border"
                        )
                    ])
                ]),
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("WIN METHOD DISTRIBUTION", className="text-center mb-0"),
                        html.Div(className="card-header-icon text-danger text-center mt-2",
                                children=[html.I(className="fas fa-trophy fa-2x")])
                    ], className="text-center"),
                    dbc.CardBody([
                        html.Label("VICTORY BREAKDOWN", className="text-danger mb-2 d-block text-center"),
                        dbc.ButtonGroup([
                            dbc.Button("Method", id="win-type-method", color="danger", outline=True, active=True, className="me-1"),
                            dbc.Button("Round", id="win-type-round", color="danger", outline=True),
                        ], className="d-flex justify-content-center mb-4"),
                        dbc.Spinner(
                            dcc.Graph(
                                id="win-method-comparison",
                                style={"height": "400px", "backgroundColor": "transparent"},
                                config={'displayModeBar': False}
                            ),
                            color="danger",
                            type="border"
                        )
                    ])
                ]),
            ], width=6),
        ], className="mb-4"),

        # Round Performance Analysis Section
        dbc.Card([
            dbc.CardHeader([
                html.H5("ROUND PERFORMANCE ANALYSIS", className="text-center mb-0"),
                html.Div(className="card-header-icon text-danger text-center mt-2",
                        children=[html.I(className="fas fa-stopwatch fa-2x")])
            ], className="text-center"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H6("FIGHT TIME METRICS", className="text-center mb-0")),
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        html.Div([
                                            html.H6("AVERAGE FIGHT TIME", className="text-center mb-2"),
                                            dbc.Spinner(
                                                html.Div(id="fight-time-comparison", className="text-center fs-4"),
                                                color="danger",
                                                type="border",
                                            )
                                        ])
                                    ], width=6),
                                    dbc.Col([
                                        html.Div([
                                            html.H6("FIRST ROUND FINISH RATE", className="text-center mb-2"),
                                            dbc.Spinner(
                                                html.Div(id="first-round-comparison", className="text-center fs-4"),
                                                color="danger",
                                                type="border",
                                            )
                                        ])
                                    ], width=6),
                                ])
                            ])
                        ], className="h-100")
                    ], width=12),
                ])
            ])
        ], className="mb-4"),

        # Head-to-Head Analysis Section
        dbc.Card([
            dbc.CardHeader([
                html.H5("HEAD-TO-HEAD ANALYSIS", className="text-center mb-0"),
                html.Div(className="card-header-icon text-danger text-center mt-2",
                        children=[html.I(className="fas fa-handshake fa-2x")])
            ], className="text-center"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("HISTORICAL MATCHUP", className="text-danger mb-2 d-block text-center"),
                        dbc.Spinner(
                            html.Div(id="head-to-head-content", className="animated fadeIn text-center"),
                            color="danger",
                            type="border"
                        )
                    ], width=12)
                ])
            ])
        ], className="mb-4"),
    ])

def matches_predictions_tab(fighters_df,stats_df,results_df):
    return dbc.Container([
        # Fighter Selection Section
        dbc.Card([
            dbc.CardHeader([
                html.H5("MATCH PREDICTION", className="text-center mb-0"),
                html.Div(className="card-header-icon text-danger text-center mt-2",
                        children=[html.I(className="fas fa-robot fa-2x")])
            ], className="text-center"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H4("FIGHTER 1", className="text-danger text-center mb-3"),
                        dbc.InputGroup([
                            dbc.InputGroupText([
                                html.I(className="fas fa-user text-muted")
                            ]),
                            dcc.Dropdown(
                                id='predict-fighter1-dropdown',
                                options=[{'label': name.title(), 'value': name} for name in fighters_df['Name']],
                                value=fighters_df['Name'][0],
                                className="custom_dropdown",
                                placeholder="Select first fighter..."
                            ),
                        ]),
                    ], width=5),
                    dbc.Col([
                        html.Div([
                            html.H4("VS", className="text-danger text-center mb-3"),
                            dbc.Button(
                                "PREDICT WINNER",
                                id="predict-button",
                                color="danger",
                                size="lg",
                                className="mt-2 w-100"
                            ),
                        ], className="h-100 d-flex flex-column justify-content-center align-items-center")
                    ], width=2),
                    dbc.Col([
                        html.H4("FIGHTER 2", className="text-danger text-center mb-3"),
                        dbc.InputGroup([
                            dbc.InputGroupText([
                                html.I(className="fas fa-user text-muted")
                            ]),
                            dcc.Dropdown(
                                id='predict-fighter2-dropdown',
                                options=[{'label': name.title(), 'value': name} for name in fighters_df['Name']],
                                value=fighters_df['Name'][1],
                                className="custom_dropdown",
                                placeholder="Select second fighter..."
                            ),
                        ]),
                    ], width=5),
                ], className="align-items-center"),
            ])
        ], className="mb-4 "),
        
        dbc.Card([
            dbc.CardHeader(html.H5("FIGHTERS TO PREDICT", className="text-center")), 
            dbc.CardBody(
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Fighter 1", className="text-center")),  
                        dbc.CardBody(
                            html.Div(id="fighter-1-overview-predict")
                            )
                        ]),
                    ], width=4),  
                    
                    
                    dbc.Col([
                        html.Div([
                            html.Img(src='https://res.cloudinary.com/da7h9bpnj/image/upload/v1740722018/Pngtree_vs_624541_ty55wp.png', className="img-fluid",
                                     style={"max-width": "60%", "height": "auto"})
                        ],style={
                            "display": "flex",
                            "height": "100%",
                            "align-items": "center",
                            "justify-content": "center"}),  
                    ], width=4), 
                    
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Fighter 2", className="text-center")),  
                        dbc.CardBody(
                            html.Div(id="fighter-2-overview-predict")
                            )
                        ]),
                    ], width=4), 
                ])
            )
        ],className="h-100"),
        
        # Fight Predictions Section
        dbc.Card([
            dbc.CardHeader([
                html.H5("FIGHT PREDICTIONS", className="text-center mb-0"),
                html.Div(className="card-header-icon text-danger text-center mt-2",
                        children=[html.I(className="fas fa-brain fa-2x")]),
                html.P("AI-Powered Fight Outcome Analysis", 
                    className="text-center text-muted mb-0 mt-2")
            ], className="text-center"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H6("PREDICTION RESULT", className="text-center mb-0")),
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Spinner(
                                            html.Div(id="consensus-prediction", className="text-center fs-4"),
                                            color="danger",
                                            type="border"
                                        ),
                                        dbc.Progress(
                                            [
                                                dbc.Progress(value=0, color="danger", bar=True, id="prediction-progress"),
                                            ],
                                            className="my-3",
                                            style={"height": "4px"}
                                        ),
                                        html.Div(id="prediction-loading", className="text-center text-muted small mb-3")
                                    ], width=12),
                                    dbc.Col([
                                        html.Hr(className="my-3"),
                                        html.Div([
                                            html.H6("MODEL CONFIDENCE", className="text-center mb-3"),
                                            dbc.Spinner(
                                                html.Div(id="model-predictions", className="text-center fs-4"),
                                                color="danger",
                                                type="border"
                                            )
                                        ])
                                    ], width=12)
                                ])
                            ])
                        ])
                    ], width=12),
                ])
            ])
        ], className="mb-4"),
        # Model Information Section
        dbc.Card([
            dbc.CardHeader([
                html.H5("MODEL INFORMATION", className="text-center mb-0"),
                html.Div(className="card-header-icon text-danger text-center mt-2",
                        children=[html.I(className="fas fa-microchip fa-2x")])
            ], className="text-center"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H6("MODEL ENSEMBLE", className="text-center mb-0")),
                            dbc.CardBody([
                                html.P([
                                    "Utilizing advanced ML models including ",
                                    html.Span("Random Forest", className="text-danger"),
                                    ", ",
                                    html.Span("XGBoost", className="text-danger"),
                                    ", ",
                                    html.Span("LightGBM", className="text-danger"),
                                    ", and ensemble methods"
                                ], className="text-center mb-3"),
                                dbc.ListGroup([
                                    dbc.ListGroupItem([
                                        html.I(className="fas fa-check-circle text-success me-2"),
                                        "Historical data from 1000+ UFC fights"
                                    ], className="d-flex align-items-center"),
                                    dbc.ListGroupItem([
                                        html.I(className="fas fa-check-circle text-success me-2"),
                                        "Advanced feature engineering"
                                    ], className="d-flex align-items-center"),
                                    dbc.ListGroupItem([
                                        html.I(className="fas fa-check-circle text-success me-2"),
                                        "Cross-validation techniques"
                                    ], className="d-flex align-items-center"),
                                ])
                            ])
                        ], className="mb-3")
                    ], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H6("MODEL METRICS", className="text-center mb-0")),
                            dbc.CardBody([
                                html.Div([
                                    html.H6("Model Agreement", className="text-center mb-2"),
                                    dbc.Spinner(
                                        html.Div(id="model-agreement", className="text-center fs-4 text-danger"),
                                        color="danger",
                                        type="border"
                                    )
                                ], className="mb-3"),
                                dbc.Progress(
                                    [
                                        dbc.Progress(value=63.2, color="success", bar=True, 
                                                   label="Accuracy: 63.2%"),
                                    ],
                                    className="mb-2",
                                ),
                                # dbc.Progress(
                                #     [
                                #         dbc.Progress(value=82, color="info", bar=True, 
                                #                    label="Precision: 82%"),
                                #     ],
                                #     className="mb-2",
                                # ),
                                # dbc.Progress(
                                #     [
                                #         dbc.Progress(value=88, color="warning", bar=True, 
                                #                    label="Recall: 88%"),
                                #     ],
                                # ),
                            ])
                        ])
                    ], width=6),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Alert([
                            html.I(className="fas fa-exclamation-triangle me-2"),
                            "Disclaimer: These predictions are for informational purposes only and should not be used for betting.",
                        ], color="warning", className="text-center mb-0 mt-3")
                    ], width=12)
                ])
            ],className='mb-4')
        ])
    ])


def create_landing_page():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                # Hero Section
                html.Div([
                    html.H1("SOI KEO` SPORTS MMA", 
                        className="text-center display-1 gradient-text mt-8 pt-5 mb-4"),
                    html.Div(
                        "F88 AI18D02", 
                        className="text-center typewriter-text fs-3 mb-5"
                    ),
                ], className="mb-5"),

                # Features Grid
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            html.Div([
                                html.I(className="fas fa-chart-line fa-2x text-danger mb-3"),
                                html.H4("Fighter Analysis", className="mb-3"),
                                html.P("Detailed statistics and performance metrics for every UFC fighter", 
                                    className="text-muted")
                            ], className="text-center p-4")
                        ], className="h-100")
                    ], width=12, md=3, className="mb-4"),
                    
                    dbc.Col([
                        dbc.Card([
                            html.Div([
                                html.I(className="fas fa-fist-raised fa-2x text-danger mb-3"),
                                html.H4("Match Analysis", className="mb-3"),
                                html.P("In-depth fight breakdowns and historical bout data", 
                                    className="text-muted")
                            ], className="text-center p-4")
                        ], className="h-100")
                    ], width=12, md=3, className="mb-4"),
                    
                    dbc.Col([
                        dbc.Card([
                            html.Div([
                                html.I(className="fas fa-users fa-2x text-danger mb-3"),
                                html.H4("Fighter Comparison", className="mb-3"),
                                html.P("Head-to-head analysis and style matchup insights", 
                                    className="text-muted")
                            ], className="text-center p-4")
                        ], className="h-100")
                    ], width=12, md=3, className="mb-4"),
                    
                    dbc.Col([
                        dbc.Card([
                            html.Div([
                                html.I(className="fas fa-robot fa-2x text-danger mb-3"),
                                html.H4("AI Predictions", className="mb-3"),
                                html.P("Machine learning-powered fight outcome predictions", 
                                    className="text-muted")
                            ], className="text-center p-4")
                        ], className="h-100")
                    ], width=12, md=3, className="mb-4"),
                ], className="mb-5"),

                # Info Section
                html.Div([
                    html.P([
                        "Welcome to the future of UFC fight analysis. Our dashboard combines ",
                        html.Span("advanced statistics", className="text-danger"),
                        ", ",
                        html.Span("machine learning", className="text-danger"),
                        ", and ",
                        html.Span("data visualization", className="text-danger"),
                        " to provide unparalleled insights into the world of mixed martial arts."
                    ], className="text-center fs-5 mb-4"),
                    
                    html.P([
                        "Explore fighter profiles, analyze matchups, and get AI-powered predictions for upcoming fights.",
                    ], className="text-center fs-5 text-muted")
                ], className="overview-text mt-4")
            ], width=12)
        ], className="justify-content-center align-items-center min-vh-80 pt-5")
    ], fluid=True, className="h-100 pt-5")

def create_layout_2(fighters_df, results_df,stats_df):
    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/UFC_Logo.svg/2560px-UFC_Logo.svg.png", height="50px")),
                            # dbc.Col(html.H3("UFC ANALYTICS", className="ms-3 text-light"), width='auto',style = {"white-space": "nowrap","color":"#ff0000"}),
                        ],
                        align="center",
                    ),
                    style={"textDecoration": "none"},
                ),
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("HOME", href="#home", id="home-link")),
                        dbc.NavItem(dbc.NavLink("FIGHTER STATS", href="#fighters", id="fighters-link")),
                        dbc.NavItem(dbc.NavLink("MATCH ANALYSIS", href="#matches", id="matches-link")),
                        dbc.NavItem(dbc.NavLink("FIGHTER COMPARISON", href="#comparison", id="comparison-link")),
                        dbc.NavItem(dbc.NavLink("MATCH PREDICTIONS", href="#prediction", id="prediction-link")),
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
        create_landing_page(), 
        id="page-content"
    )

    layout = html.Div([
        html.Link(
            rel = 'stylesheet',
            href = '/assets/style.css'
        ),
        navbar,
        content,
        dcc.Store(id='active-tab', data='home')
    ])
    
    return layout
