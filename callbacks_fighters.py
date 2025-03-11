from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd

def register_fighter_callbacks(app, fighters_df, results_df, stats_df):
    """Register callbacks for the fighters tab"""
    @app.callback(
        Output("fighter-profile-content", "children"),
        Input("fighter-dropdown", "value")
    )
    def update_fighter_profile(fighter_name):
        if not fighter_name:
            return html.Div("Please select a fighter")
        
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
        Output('fighter-radar-chart', 'figure'),
        Input('fighter-dropdown', 'value')
    )
    def update_fighter_radar(selected_fighter):
        fighter_data = fighters_df[fighters_df['Name'] == selected_fighter].iloc[0]
        
        # Normalize 
        categories = ['Striking_Accuracy', 'Takedown_Accuracy', 'Sig_Str_Def',
                     'Takedown_Def', 'Knockdown_Avg', 'Sub_Avg_Per_Min']
        
        #max values for normalization
        max_values = {
            'Striking_Accuracy': 1,
            'Takedown_Accuracy': 1,
            'Sig_Str_Def': 1,
            'Takedown_Def': 1,
            'Knockdown_Avg': fighters_df['Knockdown_Avg'].max(),
            'Sub_Avg_Per_Min': fighters_df['Sub_Avg_Per_Min'].max()
        }
        
        values = [fighter_data[cat]/max_values[cat] for cat in categories]
        display_values = [fighter_data[cat] for cat in categories]
        
        # Rename categories for display
        display_categories = [
            'Strike Acc.', 'Takedown Acc.', 'Strike Defense',
            'Takedown Def.', 'Knockdown Avg', 'Submission Avg'
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=display_categories,
            fill='toself',
            name=selected_fighter,
            text=[f"{cat}: {val:.2f}" for cat, val in zip(display_categories, display_values)],
            hoverinfo='text',
            line_color='red',
            fillcolor='rgba(255, 0, 0, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                bgcolor="rgba(30, 30, 30, 1)",
                radialaxis=dict(
                    visible=True,
                    range=[0, 1.1]
                )
            ),
            showlegend=False,
            title=f"{selected_fighter}'s Fighting Attributes",
            title_x=0.5,
            margin=dict(l=60, r=60, t=40, b=40),
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            font=dict(color='white')
        )
        
        return fig
    
    
        
    @app.callback(
        Output("fighter-recent-fights", "children"),
        Input("fighter-dropdown", "value")
    )
    def update_recent_fights(fighter_name):
        if not fighter_name:
            return html.Div("Please select a fighter")
        

        fighter_matches = results_df[
            (results_df['FIGHTER_1'] == fighter_name) | (results_df['FIGHTER_2'] == fighter_name)
        ].sort_values('DATE', ascending=False)
        
        if fighter_matches.empty:
            return html.Div("No fight data available")
        
        return html.Div([
            dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("EVENT"),
                        html.Th("DATE"),
                        html.Th("OPPONENT"),
                        html.Th("RESULT"),
                        html.Th("METHOD"),
                        html.Th("ROUND"),
                    ])
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td(row['EVENT']),
                        html.Td(row['DATE']),
                        html.Td(row['FIGHTER_2'] if row['FIGHTER_1'] == fighter_name else row['FIGHTER_1']),
                        html.Td(
                            html.Span("WIN", className="text-success") 
                            if (row['FIGHTER_1'] == fighter_name and row['fighter_1_result'] == 1) or \
                            (row['FIGHTER_2'] == fighter_name and row['fighter_2_result'] == 1) 
                            else html.Span("LOSS", className="text-danger")
                        ),
                        html.Td(row['method_label']),
                        html.Td(f"R{row['ROUND']} ({row['total_time_seconds']})")
                    ]) for _, row in fighter_matches.iterrows()
                ])
            ], striped=True, bordered=True, hover=True, responsive=True)
        ])
    
    @app.callback(
    Output('fighter-strike-distribution', 'figure'),
    Input('fighter-dropdown', 'value')
    )
    def update_fighter_strike_distribution(selected_fighter):
        fighter_data = fighters_df[fighters_df['Name'] == selected_fighter].iloc[0]
        colors = ["#636EFA", "#EF553B", "#00CC96"]  # Blue, Red, Green
        
        strike_data = {
        'Location': ['Head', 'Body', 'Leg'],
        'Percentage': [
        fighter_data['Sig_Strikes_Head_Percent'],
        fighter_data['Sig_Strikes_Body_Percent'],
        fighter_data['Sig_Strikes_Leg_Percent']
        ]}
        strike_df = pd.DataFrame(strike_data)
        
        fig = go.Figure()
        fig.add_trace(go.Pie(
            labels = strike_df['Location'],
            values = strike_df['Percentage'],
            hole = 0.1,
            name = "strike_pos",
            marker=dict(colors=colors, line=dict(color='white', width=1)),  
            textfont = dict(color='white')
        ))
        fig.update_layout(
            title = dict(text = 'Strike Distribution',
                         font=dict(size=20, color="white")),
            title_x = 0.5,
            paper_bgcolor="rgba(30, 30, 30, 1)",
            plot_bgcolor="rgba(30, 30, 30, 1)", 
            legend=dict(
                font=dict(size=14, color="white"),  
                bgcolor="rgba(50, 50, 50, 0.5)" ) 
        )
        return fig
    @app.callback(
    Output('fighter-style-analysis', 'figure'),
    Input('fighter-dropdown', 'value')
    )
    def update_fighter_strike_distribution(selected_fighter):
        fighter_data = fighters_df[fighters_df['Name'] == selected_fighter].iloc[0]
        colors = ["#636EFA", "#EF553B", "#00CC96"]  # Blue, Red, Green

        
        position_data = {
        'Position': ['Standing', 'Clinch', 'Ground'],        
        'Percentage': [
        fighter_data['Sig_Strikes_While_Standing_Percent'],
        fighter_data['Sig_Strikes_While_Clinched_Percent'],
        fighter_data['Sig_Strikes_While_Grounded_Percent']
        ]}
        position_df = pd.DataFrame(position_data)
        
        fig = go.Figure()
        fig.add_trace(go.Pie(
            labels = position_df['Position'],
            values = position_df['Percentage'],
            hole = 0.1,
            name = "Fighting style",
            marker=dict(colors=colors, line=dict(color='white', width=1)),  
        ))
        fig.update_layout(
            title = dict(text = 'Fighting style',
                         font=dict(size=20, color="white")),
            title_x = 0.5,
            paper_bgcolor="rgba(30, 30, 30, 1)",  
            plot_bgcolor="rgba(30, 30, 30, 1)",  
            legend=dict(
                font=dict(size=14, color="white"),  
                bgcolor="rgba(50, 50, 50, 0.5)" ) 
        )
        return fig
    
    
    @app.callback(
        [Output('momentum-gauge', 'figure'),
        Output('momentum-radar', 'figure')],
        [Input('fighter-dropdown', 'value'),
        Input('strike-weight', 'value')]
    )
    def update_momentum_analysis(selected_fighter, strike_weight):
        fighter_data = fighters_df[fighters_df['Name'] == selected_fighter].iloc[0]
        
        max_sig_strikes = fighters_df['Sig_Strikes_Per Min'].max()  
        max_takedowns = fighters_df['Takedown_Avg_Per Min'].max()   
        max_submissions = fighters_df['Sub_Avg_Per_Min'].max() 
        
        normalized_sig_strikes = (fighter_data['Sig_Strikes_Per Min'] / max_sig_strikes) * 100
        normalized_takedowns = (fighter_data['Takedown_Avg_Per Min'] / max_takedowns) * 100
        normalized_submissions = (fighter_data['Sub_Avg_Per_Min'] / max_submissions) * 100

        strike_score = normalized_sig_strikes * (strike_weight / 100)
        grapple_score = (normalized_takedowns + normalized_submissions) * ((100 - strike_weight) / 100)

        total_momentum = strike_score + grapple_score


        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_momentum,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {
                    'range': [0, 100],
                    'tickwidth': 1,
                    'tickcolor': 'white',
                    'tickfont': {'color': 'white'}
                },
                'bar': {'color': "#dc3545"},  
                'bgcolor': "rgba(30, 30, 30, 1)", 
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 40], 'color': "rgba(100, 100, 100, 0.5)"},
                    {'range': [40, 70], 'color': "rgba(70, 70, 70, 0.5)"},
                    {'range': [70, 100], 'color': "rgba(40, 40, 40, 0.5)"}
                ]
            }
        ))

        gauge_fig.update_layout(
            font={'color': 'white', 'family': "Arial"},
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            margin=dict(l=60, r=60, t=40, b=40)  
        )

        # Create radar chart
        radar_fig = go.Figure()
        radar_fig.add_trace(go.Scatterpolar(
            r=[fighter_data['Sig_Strikes_Per Min'],
            fighter_data['Takedown_Avg_Per Min'],
            fighter_data['Sub_Avg_Per_Min'],
            fighter_data['Knockdown_Avg'],
            fighter_data['Sig_Str_Def']],
            theta=['Strikes/Min', 'Takedowns/Min', 
                'Sub Attempts/Min', 'Knockdowns', 'Defense'],
            fill='toself',
            name='Momentum Factors'
        ))
        radar_fig.update_layout(
            polar=dict(
                bgcolor="rgba(30, 30, 30, 1)",
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )
            ),
            showlegend=False,
            title=f"{selected_fighter}",
            title_x=0.5,
            margin=dict(l=60, r=60, t=40, b=40),
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            font=dict(color='white')
        )     
        return gauge_fig, radar_fig