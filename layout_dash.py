# layout_dash.py
import dash
from dash import dcc, html
from plotly.subplots import make_subplots

def create_layout(fighters_df,results_df):
    layout = html.Div([
        html.Div([
            html.H1("UFC Fighter Analytics Dashboard", 
                    style={'textAlign': 'center', 'color': '#d20a0a', 'marginBottom': 30})
        ]),
        
        dcc.Tabs([
            dcc.Tab(label='Fighter Analysis', children=[
                html.Div([
                    html.Div([
                        html.H3("Select Fighter",style={'textAlign': 'center', 'color': '#d20a0a', 'marginBottom': 30}),
                        dcc.Dropdown(
                            id='fighter-dropdown',
                            options=[{'label': name, 'value': name} for name in fighters_df['Name'].unique()],
                            value=fighters_df['Name'].iloc[0]  
                        ),
                        html.Div(id='fighter-info-card', className='stats-card')
                    ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),
                    
                    html.Div([
                        html.H3("Fighter Statistics",style={'textAlign': 'center', 'color': '#d20a0a', 'marginBottom': 30}),
                        dcc.Graph(id='fighter-stats-radar')
                    ], style={'width': '35%', 'display': 'inline-block'}),
                    
                    html.Div([
                        html.H3("Career Record",style={'textAlign': 'center', 'color': '#d20a0a', 'marginBottom': 30}),
                        dcc.Graph(id='fighter-win-loss-pie')
                    ], style={'width': '35%', 'display': 'inline-block'})
                ]),
                
                html.Div([
                    html.H3("Fighting Style Breakdown",style={'textAlign': 'center', 'color': '#d20a0a', 'marginBottom': 30}),
                    dcc.Graph(id='fighter-style-breakdown')
                ])
            ]),
            
        dcc.Tab(label='Match Analysis', children=[
            html.Div([
                html.Div([
                    html.H3("Select Match",style={'textAlign': 'center', 'color': '#d20a0a', 'marginBottom': 30}),
                    dcc.Dropdown(
                        id='match-dropdown',
                        options=[{'label': bout, 'value':bout} for bout in results_df['BOUT'].unique()],  
                        value=results_df['BOUT'].iloc[0]  
                    ),
                    html.Div(id='match-info-card', className='stats-card'),
                ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                        
                html.Div([
                        html.H3("Fighters",style={'textAlign': 'center', 'color': '#d20a0a', 'marginBottom': 30}),
                        html.Div([
                            html.Div([
                                html.Img(id='fighter-1-image', src='', 
                                        style={'width': '300px', 'height': 'auto', 'borderRadius': '5px','display':'block','margin':'auto'}),
                                html.P(id='fighter-1-name', style={'textAlign': 'center'})
                            ], style={'width': '45%'}),
                            html.Div(style={'width': '45%', 'textAlign': 'center', 'alignSelf': 'center'},children=[
                                html.Img(src='https://res.cloudinary.com/da7h9bpnj/image/upload/v1740722018/Pngtree_vs_624541_ty55wp.png', 
                                        style={'width': '300px', 'height': 'auto', 'borderRadius': '5px','display':'block','margin':'auto'}),
                            ]),                           
                            html.Div([
                                html.Img(id='fighter-2-image', src='', 
                                        style={'width': '300px', 'height': 'auto', 'borderRadius': '5px','display':'block','margin':'auto'}),
                                html.P(id='fighter-2-name', style={'textAlign': 'center'})
                            ], style={'width': '45%'})
                        ], style={'display': 'flex', 'justifyContent': 'space-between', 'width': '100%'})
                    ], style={'width': '65%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingLeft': '20px'})
                ], style={'display': 'flex', 'marginBottom': '20px'}),    
                        
                        
                html.Div([
                    html.Div([
                        html.H3("Round Performance"),
                        dcc.Graph(id='round-stats')
                    ], style={'width': '70%', 'display': 'inline-block'}),
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
        
            dcc.Tab(label='Fighter Comparison', children=[
                html.Div([
                    html.H3("Compare Fighters", style={'textAlign': 'center'}),
                    
                    html.Div([
                        html.Div([
                            dcc.Dropdown(
                                id='fighter-dropdown-1',
                                options=[{'label': name, 'value': name} for name in fighters_df['Name'].unique()],
                                value=fighters_df['Name'].iloc[0]  
                            ),
                            html.Div(id='fighter-1-info-card', className='stats-card'),
                        ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                        
                        html.Div([
                            dcc.Dropdown(
                                id='fighter-dropdown-2',
                                options=[{'label': name, 'value': name} for name in fighters_df['Name'].unique()],
                                value=fighters_df['Name'].iloc[1]  
                            ),
                            html.Div(id='fighter-2-info-card', className='stats-card')
                        ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                        
                    ], style={'display': 'flex', 'justifyContent': 'space-between'}), 
                    
                    html.Div([
                            html.H3("Stats comparing",style={'textAlign': 'center'}),
                            
                            dcc.Graph(id='fighter-comparison-piechart'),
                            
                            dcc.Graph(id= 'fighter-comparison-radar')
                        
                    ])
            ]),
        ])
    ])

]) 
    return layout
