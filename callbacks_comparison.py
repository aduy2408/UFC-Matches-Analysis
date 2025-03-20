
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
            fillcolor='rgba(255, 0, 0, 0.5)',  
            line=dict(color='red', width=3),
            marker=dict(size=8),
            text=[f"{cat}: {fighter1[cat]:.2f}" for cat in categories],
            hoverinfo='text'
        ))

        # Fighter 2 trace
        fig.add_trace(go.Scatterpolar(
            r=values_2,
            theta=categories,
            fill='toself',
            name=fighter2_name,
            fillcolor='rgba(0, 0, 255, 0.5)',  
            line=dict(color='blue', width=3),
            marker=dict(size=8),
            text=[f"{cat}: {fighter2[cat]:.2f}" for cat in categories],
            hoverinfo='text'
        ))

        fig.update_layout(
            title=dict(
                text=f"<b>Fighter Comparison: {fighter1_name} vs. {fighter2_name}</b>",
                font=dict(size=20, color="white"),
                x=0.5
            ),
            polar=dict(
                bgcolor="rgba(0, 0, 0, 0)",
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    gridcolor="rgba(255, 255, 255, 0.1)",
                    linecolor="rgba(255, 255, 255, 0.2)",
                    showline=True,
                    linewidth=2,
                    tickfont=dict(size=12, color="white"),
                    tickwidth=2,
                    tickcolor="rgba(255, 255, 255, 0.4)"
                ),
                angularaxis=dict(
                    showline=True,
                    linewidth=2,
                    linecolor="rgba(255, 255, 255, 0.4)",
                    gridcolor="rgba(255, 255, 255, 0.2)",
                    tickfont=dict(size=12, color="white", weight="bold")
                )
            ),
            paper_bgcolor="rgba(0, 0, 0, 0)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            font=dict(color="white"),
            legend=dict(
                font=dict(size=14, color="white"),
                bgcolor="rgba(0, 0, 0, 0)",
                bordercolor="rgba(255, 255, 255, 0.2)",
                borderwidth=1
            ),
            margin=dict(t=60, l=40, r=40, b=40)
        )

        return fig

    @app.callback(
        Output("tale-of-tape-content", "children"),
        [Input("fighter1-dropdown", "value"),
         Input("fighter2-dropdown", "value")]
    )
    def update_tale_of_tape(fighter1_name, fighter2_name):
        if not fighter1_name or not fighter2_name:
            return html.Div("Please select two fighters")
        
        fighter1 = fighters_df[fighters_df['Name'] == fighter1_name].iloc[0]
        fighter2 = fighters_df[fighters_df['Name'] == fighter2_name].iloc[0]
        
        # Create comparison table
        table_rows = []
        
        # Calculate total fights
        f1_total_fights = fighter1['Wins'] + fighter1['Losses'] + fighter1['Draws']
        f2_total_fights = fighter2['Wins'] + fighter2['Losses'] + fighter2['Draws']
        
        comparison_data = [
            ("Weight Class", fighter1['Weight_Class'], fighter2['Weight_Class']),
            ("Total Fights", f"{f1_total_fights} ({fighter1['Wins']}-{fighter1['Losses']}-{fighter1['Draws']})", 
             f"{f2_total_fights} ({fighter2['Wins']}-{fighter2['Losses']}-{fighter2['Draws']})"),
            ("Place of Birth", fighter1['Place_of_Birth'] if pd.notna(fighter1['Place_of_Birth']) else "N/A", 
             fighter2['Place_of_Birth'] if pd.notna(fighter2['Place_of_Birth']) else "N/A"),
            ("Octagon Debut", fighter1['Octagon_Debut'], fighter2['Octagon_Debut']),
            ("Average Fight Time", f"{fighter1['Avg_Fight_Time']}s", f"{fighter2['Avg_Fight_Time']}s"),
            ("First Round Finishes", str(fighter1['First_Round_Finishes']), str(fighter2['First_Round_Finishes']))
        ]
        
        for label, val1, val2 in comparison_data:
            table_rows.append(
                html.Tr([
                    html.Td(label, className="text-center"),
                    html.Td(val1, className="text-center"),
                    html.Td(val2, className="text-center")
                ])
            )
        
        return dbc.Table([
            html.Thead(
                html.Tr([
                    html.Th("Attribute", className="text-center"),
                    html.Th(fighter1_name, className="text-center"),
                    html.Th(fighter2_name, className="text-center")
                ])
            ),
            html.Tbody(table_rows)
        ], bordered=True, dark=False, hover=True, responsive=True)

    @app.callback(
        Output("fighting-style-comparison", "figure"),
        [Input("fighter1-dropdown", "value"),
         Input("fighter2-dropdown", "value")]
    )
    def update_fighting_style(fighter1_name, fighter2_name):
        if not fighter1_name or not fighter2_name:
            return {}
        
        fighter1 = fighters_df[fighters_df['Name'] == fighter1_name].iloc[0]
        fighter2 = fighters_df[fighters_df['Name'] == fighter2_name].iloc[0]
        
        fig = make_subplots(rows=2, cols=1, 
                           subplot_titles=("Strike Target Distribution", "Strike Position Distribution"),
                           vertical_spacing=0.25)
        
        # Strike Target Distribution
        categories = ['Head', 'Body', 'Leg']
        f1_values = [fighter1['Sig_Strikes_Head_Percent'], 
                    fighter1['Sig_Strikes_Body_Percent'],
                    fighter1['Sig_Strikes_Leg_Percent']]
        f2_values = [fighter2['Sig_Strikes_Head_Percent'],
                    fighter2['Sig_Strikes_Body_Percent'],
                    fighter2['Sig_Strikes_Leg_Percent']]
        
        fig.add_trace(
            go.Bar(name=fighter1_name, x=categories, y=f1_values, marker_color='red'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(name=fighter2_name, x=categories, y=f2_values, marker_color='blue'),
            row=1, col=1
        )
        
        positions = ['Standing', 'Clinched', 'Grounded']
        f1_pos_values = [fighter1['Sig_Strikes_While_Standing_Percent'],
                        fighter1['Sig_Strikes_While_Clinched_Percent'],
                        fighter1['Sig_Strikes_While_Grounded_Percent']]
        f2_pos_values = [fighter2['Sig_Strikes_While_Standing_Percent'],
                        fighter2['Sig_Strikes_While_Clinched_Percent'],
                        fighter2['Sig_Strikes_While_Grounded_Percent']]
        
        fig.add_trace(
            go.Bar(name=fighter1_name, x=positions, y=f1_pos_values, marker_color='red', showlegend=False),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(name=fighter2_name, x=positions, y=f2_pos_values, marker_color='blue', showlegend=False),
            row=2, col=1
        )
        
        fig.update_layout(
            barmode='group',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.1,
                xanchor="center",
                x=0.5
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
   
        )
        
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.1)", range=[0, 1])
        fig.update_xaxes(gridcolor="rgba(255,255,255,0.1)")
        
        return fig

    @app.callback(
        Output("win-method-comparison", "figure"),
        [Input("fighter1-dropdown", "value"),
         Input("fighter2-dropdown", "value")]
    )
    def update_win_methods(fighter1_name, fighter2_name):
        if not fighter1_name or not fighter2_name:
            return {}
        
        fighter1 = fighters_df[fighters_df['Name'] == fighter1_name].iloc[0]
        fighter2 = fighters_df[fighters_df['Name'] == fighter2_name].iloc[0]
        
        categories = ['KO/TKO', 'Submission', 'Decision']
        f1_values = [fighter1['Win_by_KO/TKO_Percent'], 
                    fighter1['Win_by_Submission_Percent'],
                    fighter1['Win_by_Decision_Percent']]
        f2_values = [fighter2['Win_by_KO/TKO_Percent'],
                    fighter2['Win_by_Submission_Percent'],
                    fighter2['Win_by_Decision_Percent']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name=fighter1_name,
            x=categories,
            y=f1_values,
            marker_color='red'
        ))
        
        fig.add_trace(go.Bar(
            name=fighter2_name,
            x=categories,
            y=f2_values,
            marker_color='blue'
        ))
        
        fig.update_layout(
            barmode='group',
            title=dict(
                text="Win Method Distribution",
                font=dict(color="white"),
                x=0.5
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            yaxis=dict(
                title="Percentage",
                gridcolor="rgba(255,255,255,0.1)",
                range=[0, 1]
            ),
            xaxis=dict(
                gridcolor="rgba(255,255,255,0.1)"
            )
        )
        
        return fig

    @app.callback(
        [Output("fight-time-comparison", "children"),
         Output("first-round-comparison", "children")],
        [Input("fighter1-dropdown", "value"),
         Input("fighter2-dropdown", "value")]
    )
    def update_round_performance(fighter1_name, fighter2_name):
        if not fighter1_name or not fighter2_name:
            return "Please select two fighters", "Please select two fighters"
        
        fighter1 = fighters_df[fighters_df['Name'] == fighter1_name].iloc[0]
        fighter2 = fighters_df[fighters_df['Name'] == fighter2_name].iloc[0]
        
        # Average Fight Time
        f1_time = int(fighter1['Avg_Fight_Time'])
        f2_time = int(fighter2['Avg_Fight_Time'])
        f1_mins = f1_time // 60
        f1_secs = f1_time % 60
        f2_mins = f2_time // 60
        f2_secs = f2_time % 60
        
        fight_time = html.Div([
            html.Div([
                html.H3(f"{f1_mins}:{f1_secs:02d}", className="text-danger"),
                html.P(fighter1_name, className="text-muted")
            ], className="text-center"),
            html.Div([
                html.H3(f"{f2_mins}:{f2_secs:02d}", className="text-primary"),
                html.P(fighter2_name, className="text-muted")
            ], className="text-center")
        ])
        
        # First Round Finish Rate
        f1_total = fighter1['Wins'] + fighter1['Losses']
        f2_total = fighter2['Wins'] + fighter2['Losses']
        
        f1_first_round = fighter1['First_Round_Finishes']
        f2_first_round = fighter2['First_Round_Finishes']
        
        f1_rate = f1_first_round / f1_total if f1_total > 0 else 0
        f2_rate = f2_first_round / f2_total if f2_total > 0 else 0
        
        first_round = html.Div([
            html.Div([
                html.H3(f"{f1_rate:.0%}", className="text-danger"),
                html.P(f"{f1_first_round} of {f1_total} fights", className="text-muted")
            ], className="text-center"),
            html.Div([
                html.H3(f"{f2_rate:.0%}", className="text-primary"),
                html.P(f"{f2_first_round} of {f2_total} fights", className="text-muted")
            ], className="text-center")
        ])
        
        return fight_time, first_round

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
