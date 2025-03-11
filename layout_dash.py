
import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np



def create_fighters_tab(fighters_df,results_df,stats_df):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("SELECT FIGHTER", className="text-danger"),
                html.Label('Select fighter name'),
                dcc.Dropdown(
                    id='fighter-dropdown',
                    options=[{'label': name, 'value': name} for name in fighters_df['Name']],
                    value=fighters_df['Name'][0],
                    className="custom_dropdown"
                ),
            ], width=4),
            # dbc.Col([
            #     html.H4("FILTER OPTIONS", className="text-danger"),
            #     dbc.Row([
            #         dbc.Col([
            #             html.Label("Weight Class"),
            #             dcc.Dropdown(
            #                 id='weight-class-filter',
            #                 options=[{'label': wc, 'value': wc} 
            #                         for wc in sorted(fighters_df['Weight_Class'].unique())],
            #                 multi=True,
            #                 placeholder="All Weight Classes"
            #             ),
            #         ], width=12),
            #     ]),
            # ], width=6),
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
                        dcc.Graph(id="fighter-radar-chart", style={"height": "400px",'backgroundColor':"rgba(50, 50, 50, 0.8)"})
                    )
                ]),
            ], width=8),
        ], className="mb-4"),
        

        
        dbc.Card([
            dbc.CardHeader(html.H5("Fighting Analysis", className="text-center")),  # Main title inside the card
            dbc.CardBody(
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Strike Distribution", className="text-center")),  # Title for the first column
                            dbc.CardBody(
                                dcc.Graph(id="fighter-strike-distribution", style={"height": "400px"})
                            )
                        ]),
                    ], width=6),  

                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Fighting Style Analysis", className="text-center")),  # Title for the second column
                            dbc.CardBody(
                                dcc.Graph(id="fighter-style-analysis", style={"height": "400px"})
                            )
                        ]),
                    ], width=6), 
                ])
            )
        ],className="mb-4"),
        
        dbc.Card([
            dbc.CardHeader(html.H5("FIGHT MOMENTUM ANALYSIS", className="text-center")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(dcc.Graph(id="momentum-gauge"), width=4),
                    dbc.Col(dcc.Graph(id="momentum-radar"), width=8),
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Label("Select Metrics Weighting:"),
                        dcc.Slider(
                            id='strike-weight',
                            min=0,
                            max=100,
                            value=40,
                            marks={0: 'Strikes', 100: 'Grappling'},
                            tooltip={"placement": "bottom"}
                        )
                    ], width=12)
                ]),
            ]),
        ],className="mb-4"),

        
        # dbc.Card(
        #     [
        #         dbc.CardHeader(
        #             html.H4("CAREER TIMELINE", className="text-danger mb-0"),
        #         ),
        #         dbc.CardBody([
        #             dbc.Row([
        #                 dbc.Col([
        #                     dcc.Graph(
        #                         id="career-timeline",
        #                         config={'displayModeBar': False},
        #                         className="border rounded-3",
        #                         style={'height': '400px'}
        #                     )
        #                 ])
        #             ]),
        #             dbc.Row([
        #                 dbc.Col([
        #                     html.Small(
        #                         "Hover over points to view fight details",
        #                         className="text-muted mt-2 d-block"
        #                     )
        #                 ], className="text-center")
        #             ])
        #         ])
        #     ]),
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

def create_matches_tab(fighters_df,stats_df,results_df):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("SELECT MATCH", className="text-danger"),
                dcc.Dropdown(
                    id='match-dropdown',
                    options=[{'label': match, 'value': match} for match in sorted(stats_df['BOUT'].unique())],
                    value=stats_df['BOUT'][0],
                    className="mb-4"
                ),
            ], width=4),
            # dbc.Col([
            #     html.H4("FILTER OPTIONS", className="text-danger"),
            #     dbc.Row([
            #         dbc.Col([
            #             html.Label("DATE Range"),
            #             dcc.DatePickerRange(
            #                 id='date-range',
            #                 min_date_allowed=min(pd.to_datetime(stats_df['DATE'])),
            #                 max_date_allowed=max(pd.to_datetime(stats_df['DATE'])),
            #                 start_date=min(pd.to_datetime(stats_df['DATE'])),
            #                 end_date=max(pd.to_datetime(stats_df['DATE'])),
            #             ),
            #         ], width=6),
            #     ]),
            # ], width=8),
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
                        dcc.Graph(id="match-stats-chart", style={"height": "372px"})
                    )
                ]),
            ], width=7),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("STRIKE DISTRIBUTION", className="text-center")),
                    dbc.CardBody(
                        dcc.Graph(id="strike-distribution", style={"height": "600px"})
                    )
                ]),
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Takedown Analysis", className="text-center")),
                    dbc.CardBody(
                        dcc.Graph(id="takedown-analysis", style={"height": "600px"})
                    )
                ]),
            ], width=6),
        
        
        
        ],className="mb-4"),
                
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("ROUND-BY-ROUND PROGRESSION", className="text-center")),
                    dbc.CardBody([
                        html.P("Select round to view progression:", className="text-white"),
                        dcc.Slider(
                            id='timeline-slider',
                            min=1,
                            max=5,  
                            step=1,
                            value=3,  
                            marks={i: {'label': f'R{i}', 'style': {'color': 'white'}} 
                                for i in range(1, 6)},
                            className="mb-4"
                        ),
                        dcc.Graph(id="fight-timeline", style={"height": "400px"}),
                        html.Hr(style={"background-color": "gray", "height": "2px"}),
                        html.H5("STRIKE DISTRIBUTION PER ROUND", className="text-center mt-3"),
                        dcc.Graph(id="fight-round-distribution", style={"height": "400px"})  
                    ])
                ]),
            ], width=12),
        ], className="mb-4"),
        
        
    ])

def create_comparison_tab(fighters_df,results_df,stats_df):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("SELECT FIGHTER 1", className="text-danger"),
                dcc.Dropdown(
                    id='fighter1-dropdown',
                    options=[{'label': name, 'value': name} for name in fighters_df['Name']],
                    value=fighters_df['Name'][0],
                    className="mb-4"
                ),
            ], width=4),
        dbc.Col([
            html.H4("SELECT FIGHTER 2", className="text-danger"),
            dcc.Dropdown(
                id='fighter2-dropdown',
                options=[{'label': name, 'value': name} for name in fighters_df['Name']],
                value=fighters_df['Name'][1],
                className="mb-4"
            ),
                ], width=4),
            ], className="mb-4"),
        
        dbc.Card([
            dbc.CardHeader(html.H5("Fighters Overview", className="text-center")), 
            dbc.CardBody(
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Fighter 1", className="text-center")),  
                        dbc.CardBody(
                            html.Div(id="fighter-1-overview")
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
                            html.Div(id="fighter-2-overview")
                            )
                        ]),
                    ], width=4), 
                ])
            )
        ],className="mb-4"),

        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("STATS COMPARISON", className="text-center")),
                    dbc.CardBody(
                        dcc.Graph(id="fighters-comparison-chart", style={"height": "400px"})
                    )
                ]),
            ]),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("HEAD-TO-HEAD", className="text-center")),
                    dbc.CardBody(
                        html.Div(id="head-to-head-content")
                    )
                ]),
            ], width=100),
            # dbc.Col([
            #     dbc.Card([
            #         dbc.CardHeader(html.H5("PLACE HOLDER", className="text-center")),
            #         dbc.CardBody(
            #             dcc.Graph(id="IDK", style={"height": "300px"})
            #         )
            #     ]),
            # ], width=8),
        ]),
    ])

def matches_predictions_tab(fighters_df,stats_df,results_df):
    return dbc.Container([
        
        dbc.Row([
            dbc.Col([
                html.H4("SELECT FIGHTER 1", className="text-danger"),
                dcc.Dropdown(
                    id='predict-fighter1-dropdown',
                    options=[{'label': name, 'value': name} for name in fighters_df['Name']],
                    value=fighters_df['Name'][0],
                    className="mb-4"
                ),
            ], width=4),
        dbc.Col([
            html.H4("SELECT FIGHTER 2", className="text-danger"),
            dcc.Dropdown(
                id='predict-fighter2-dropdown',
                options=[{'label': name, 'value': name} for name in fighters_df['Name']],
                value=fighters_df['Name'][1],
                className="mb-4"
            ),
                ], width=4),
        dbc.Col([
            html.Div([
                html.H4("\u00A0", className="text-danger"),
                dbc.Button(
                    "PREDICT WINNER", 
                    id="predict-button", 
                    color="danger", 
                    size="lg",
                    className="mb-4"
                ),
            ], className="d-flex flex-column")
            ], width=4),
        ], className="mb-4"),
        
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
        ],className="mb-4"),
        
        dbc.Card([
            dbc.CardHeader([
                html.H5("FIGHT PREDICTION", className="text-center"),
                html.P("Prediction is based on historical UFC data, output is the result of fighter 1", className="text-center text-muted mb-0")
            ]), 
            dbc.CardBody([
                html.Div(id="prediction-output", className="mb-4"),
                
                dbc.Spinner(
                    html.Div(id="prediction-loading", style={"height": "20px"}),
                    color="danger",
                    type="grow",
                    fullscreen=False,
                ),
                
            ])
        ], className="mb-4"),
        dbc.Card([
            dbc.CardHeader(html.H5("MODEL INFORMATION", className="text-center")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H6("Model Type:", className="text-center mb-2"),
                        html.P(id="model-type-info", className="text-center text-muted"),
                    
                    ], width=6),
                    dbc.Col([
                        html.H6("Model Accuracy:", className="text-center mb-2"),
                        html.P(id="model-accuracy-info", className="text-center text-muted"),
                        

                    ], width=6),
                ]),
                dbc.Row([
                    dbc.Col([
                        html.H6("Disclaimer:", className="text-center mb-2 mt-3"),
                        html.P("Predictions are for entertainment purposes only and should not be used for betting(or..)", 
                              className="text-center text-muted fst-italic")
                ],width=100),
                ])
            ])
        ])
    ])


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
        create_fighters_tab(fighters_df=fighters_df,results_df=results_df,stats_df=stats_df), 
        id="page-content"
    )

    layout = html.Div([
        html.Link(
            rel = 'stylesheet',
            href = '/assets/style.css'
        ),
        navbar,
        content,
        dcc.Store(id='active-tab', data='fighters')
    ])
    
    return layout
