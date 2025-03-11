
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import pandas as pd

def register_comparison_callbacks(app, fighters_df, results_df, stats_df):
    @app.callback(
        Output("fighters-comparison-chart", "figure"),
        [Input("fighter1-dropdown", "value"),
        Input("fighter2-dropdown", "value")]
    )
    def update_fighters_comparison(fighter1_name, fighter2_name):
        fighter1 = fighters_df[fighters_df['Name'] == fighter1_name].iloc[0]
        fighter2 = fighters_df[fighters_df['Name'] == fighter2_name].iloc[0]
        
        categories = ['Striking_Accuracy', 'Takedown_Accuracy', 'Sig_Str_Def', 'Takedown_Def', 'Knockdown_Avg', 'Sub_Avg_Per_Min']
        max_values = {
        'Striking_Accuracy': 1,
        'Takedown_Accuracy': 1,
        'Sig_Str_Def': 1,
        'Takedown_Def': 1,
        'Knockdown_Avg': fighters_df['Knockdown_Avg'].max(),
        'Sub_Avg_Per_Min': fighters_df['Sub_Avg_Per_Min'].max()
        }
        
        values_1 = [fighter1[cat]/max_values[cat] for cat in categories]
        values_2 = [fighter2[cat]/max_values[cat] for cat in categories]
        values_1 += values_1[:1]
        values_2 += values_2[:1]
        categories += categories[:1]

        # Create radar chart
        fig = go.Figure()

    # Fighter 1 trace
        fig.add_trace(go.Scatterpolar(
            r=values_1,
            theta=categories,
            fill='toself',
            name=fighter1_name,
            fillcolor='rgba(255, 0, 0, 0.3)',  # Red with transparency
            line=dict(color='red', width=3),
            marker=dict(size=6)
        ))

        # Fighter 2 trace
        fig.add_trace(go.Scatterpolar(
            r=values_2,
            theta=categories,
            fill='toself',
            name=fighter2_name,
            fillcolor='rgba(0, 0, 255, 0.3)',  # Blue with transparency
            line=dict(color='blue', width=3),
            marker=dict(size=6)
        ))

        fig.update_layout(
            title=dict(
                text=f"<b>Fighter Comparison: {fighter1_name} vs. {fighter2_name}</b>",
                font=dict(size=18, color="white"),
                x=0.5
            ),
            polar=dict(
                bgcolor="rgba(30, 30, 30, 1)",  
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    gridcolor="white",
                    gridwidth=1.5,
                    showline=True,
                    linewidth=1,
                    linecolor="white"
                ),
                angularaxis=dict(
                    showline=True,
                    linewidth=1,
                    linecolor="white",
                    tickfont=dict(size=14, color="white")
                )
            ),
            paper_bgcolor="rgba(20, 20, 20, 1)",  
            legend=dict(
                font=dict(size=14, color="white"),
                bgcolor="rgba(50, 50, 50, 0.5)"
            )
        )

        return fig
    @app.callback(
        Output("head-to-head-content", "children"),
        [Input("fighter1-dropdown", "value"),
        Input("fighter2-dropdown", "value")]
    )
    def update_head_to_head(fighter1_name, fighter2_name):
        if not fighter1_name or not fighter2_name:
            return html.Div("Please select two fighters")
        
        # Get all matches between the two fighters
        head_to_head = results_df[
            ((results_df['FIGHTER_1'] == fighter1_name) & (results_df['FIGHTER_2'] == fighter2_name)) |
            ((results_df['FIGHTER_1'] == fighter2_name) & (results_df['FIGHTER_2'] == fighter1_name))
        ].sort_values('DATE', ascending=False)  
        
        if head_to_head.empty:
            return html.Div([
                html.H4("No previous fights", className="text-center text-muted my-4"),
                html.P("These fighters have not faced each other.", className="text-center")
            ])
        
        fighter1_wins = head_to_head[head_to_head['fighter_1_result'] == 1].shape[0]
        fighter2_wins = head_to_head[head_to_head['fighter_2_result'] == 1].shape[0]
        
        return html.Div([
            html.H4("HEAD-TO-HEAD RECORD", className="text-center mb-3"),
            
            html.Div(className="d-flex justify-content-between mb-4", children=[
                html.Div(className="text-center", children=[
                    html.H2(fighter1_wins, className="text-danger m-0"),
                    html.P(fighter1_name, className="m-0")
                ]),
                
                html.Div(className="text-center", children=[
                    html.H2("-", className="text-light m-0"),
                ]),
                
                html.Div(className="text-center", children=[
                    html.H2(fighter2_wins, className="text-primary m-0"),
                    html.P(fighter2_name, className="m-0")
                ]),
            ]),
            
            html.H5("PREVIOUS FIGHTS", className="text-center mb-2"),
            
            html.Div([
                dbc.Table([
                    html.Tbody([
                        html.Tr([
                            html.Td([
                                html.Div(row['EVENT']),
                                html.Small(row['DATE'], className="text-muted")
                            ]),
                            html.Td([
                                html.Div(row['FIGHTER_1'] if row['fighter_1_result'] == 1 else row['FIGHTER_2'], className="text-success" if row['fighter_1_result'] == 1 else "text-danger"),
                                html.Small(f"{row['method_label']} (R{row['ROUND']})")
                            ])
                        ]) for _, row in head_to_head.iterrows()
                    ])
                ], borderless=True, className="mb-0")
            ])
        ])
        
        
    @app.callback(
        Output("fighter-1-overview", "children"),
        Input("fighter1-dropdown", "value")
    )
    def update_fighter_1_profile(fighter_name):
        fighter = fighters_df[fighters_df['Name'] == fighter_name].iloc[0]
        wins = fighter['Wins']
        losses = fighter['Losses']
        draws = fighter['Draws']   
        
        return html.Div([
            html.Div([
                html.Img(src=f"/assets/minh_2.jpg", 
                    style={'width': '150px', 'height': '150px', 'borderRadius': '10%'},
                    className="mx-auto d-block mb-3"),
                html.H4(fighter['Name'], className="text-center mb-3"),
                html.H6(f"{fighter['Weight_Class']}", className="text-center text-muted mb-2"),
                
                html.Div(className="d-flex justify-content-center mb-3", children=[
                    html.Div(className="text-center mx-2", children=[
                        html.H4(wins, className="text-success m-0"),
                        html.P("WINS", className="text-muted m-0")
                    ]),
                    html.Div(className="text-center mx-2", children=[
                        html.H4(losses, className="text-danger m-0"),
                        html.P("LOSSES", className="text-muted m-0")
                    ]),
                    html.Div(className="text-center mx-2", children=[
                        html.H4(draws, className="text-warning m-0"),
                        html.P("DRAWS", className="text-muted m-0")
                    ]),
                ]),
                
                html.H5("FINISH RATE", className="text-center mb-1"),
                html.Div(className="d-flex justify-content-center", children=[
                    html.Div(className="text-center mx-2", children=[
                        html.H4(fighter['Knockouts'], className="text-danger m-0"),
                        html.P("KO/TKO", className="text-muted m-0")
                    ]),
                    html.Div(className="text-center mx-2", children=[
                        html.H4(fighter['Submissions'], className="text-primary m-0"),
                        html.P("SUBMISSIONS", className="text-muted m-0")
                    ]),
                ]),
            ])
        ])
        
    @app.callback(
        Output("fighter-2-overview", "children"),
        Input("fighter2-dropdown", "value")
    )
    def update_fighter_2_profile(fighter_name):
        fighter = fighters_df[fighters_df['Name'] == fighter_name].iloc[0]
        wins = fighter['Wins']
        losses = fighter['Losses']
        draws = fighter['Draws']   
        
        return html.Div([
            html.Div([
                html.Img(src=f"/assets/minh_2.jpg", 
                    style={'width': '150px', 'height': '150px', 'borderRadius': '10%'},
                    className="mx-auto d-block mb-3"),
                html.H4(fighter['Name'], className="text-center mb-3"),
                html.H6(f"{fighter['Weight_Class']}", className="text-center text-muted mb-2"),
                
                html.Div(className="d-flex justify-content-center mb-3", children=[
                    html.Div(className="text-center mx-2", children=[
                        html.H4(wins, className="text-success m-0"),
                        html.P("WINS", className="text-muted m-0")
                    ]),
                    html.Div(className="text-center mx-2", children=[
                        html.H4(losses, className="text-danger m-0"),
                        html.P("LOSSES", className="text-muted m-0")
                    ]),
                    html.Div(className="text-center mx-2", children=[
                        html.H4(draws, className="text-warning m-0"),
                        html.P("DRAWS", className="text-muted m-0")
                    ]),
                ]),
                
                html.H5("FINISH RATE", className="text-center mb-1"),
                html.Div(className="d-flex justify-content-center", children=[
                    html.Div(className="text-center mx-2", children=[
                        html.H4(fighter['Knockouts'], className="text-danger m-0"),
                        html.P("KO/TKO", className="text-muted m-0")
                    ]),
                    html.Div(className="text-center mx-2", children=[
                        html.H4(fighter['Submissions'], className="text-primary m-0"),
                        html.P("SUBMISSIONS", className="text-muted m-0")
                    ]),
                ]),
            ])
        ])
