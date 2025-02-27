# layout.py
import dash
from dash import dcc, html

def create_layout():
    layout = html.Div([
        html.Div([
            html.H1("UFC Fighter Analytics Dashboard", 
                    style={'textAlign': 'center', 'color': '#d20a0a', 'marginBottom': 30})
        ]),
        
        # Tabs for different dashboard views
        dcc.Tabs([
            # Fighter Analysis Tab
            dcc.Tab(label='Fighter Analysis', children=[
                html.Div([
                    html.Div([
                        html.H3("Select Fighter"),
                        dcc.Dropdown(
                            id='fighter-dropdown',
                            options=[],
                            value=None  # Placeholder for fighter selection
                        ),
                        html.Div(id='fighter-info-card', className='stats-card')
                    ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),
                    
                    html.Div([
                        html.H3("Fighter Statistics"),
                        dcc.Graph(id='fighter-stats-radar')
                    ], style={'width': '35%', 'display': 'inline-block'}),
                    
                    html.Div([
                        html.H3("Career Record"),
                        dcc.Graph(id='fighter-win-loss-pie')
                    ], style={'width': '35%', 'display': 'inline-block'})
                ]),
                
                html.Div([
                    html.H3("Fighting Style Breakdown"),
                    dcc.Graph(id='fighter-style-breakdown')
                ])
            ]),
            
            # Match Analysis Tab
            dcc.Tab(label='Match Analysis', children=[
                html.Div([
                    html.Div([
                        html.H3("Select Match"),
                        dcc.Dropdown(
                            id='match-dropdown',
                            options=[],
                            value=None  # Placeholder for match selection
                        ),
                        html.Div(id='match-info-card', className='stats-card')
                    ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),
                    
                    html.Div([
                        html.H3("Round Performance"),
                        dcc.Graph(id='round-stats')
                    ], style={'width': '70%', 'display': 'inline-block'})
                ]),
                
                html.Div([
                    html.Div([
                        html.H3("Strike Distribution"),
                        dcc.Graph(id='strike-distribution')
                    ], style={'width': '50%', 'display': 'inline-block'}),
                    
                    html.Div([
                        html.H3("Takedown Success"),
                        dcc.Graph(id='takedown-success')
                    ], style={'width': '50%', 'display': 'inline-block'})
                ])
            ]),
        ])
    ])
    
    return layout
