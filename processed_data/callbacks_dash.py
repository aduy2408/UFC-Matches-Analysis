# callbacks.py
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
from layout import create_layout

# Load your data
fighters_df = pd.read_csv('processed_data/fighters_processed.csv')
stats_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fight_stats_with_weghtclass_date_location.csv')
results_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fight_results_with_locale.csv')

def register_callbacks(app):
    # Fighter Info Callback
    @app.callback(
        Output('fighter-info-card', 'children'),
        Input('fighter-dropdown', 'value')
    )
    def update_fighter_info(selected_fighter):
        fighter_data = fighters_df[fighters_df['Name'] == selected_fighter].iloc[0]
        
        return html.Div([
            html.H4(selected_fighter),
            html.P(f"Nickname: {fighter_data['Nickname'] if pd.notna(fighter_data['Nickname']) else 'N/A'}"),
            html.P(f"Weight Class: {fighter_data['Weight_Class']}"),
            html.P(f"From: {fighter_data['Place_of_Birth'] if pd.notna(fighter_data['Place_of_Birth']) else 'Unknown'}"),
            html.P(f"UFC Debut: {fighter_data['Octagon_Debut']}"),
            html.Hr(),
            html.P(f"Record: {int(fighter_data['Wins'])}-{int(fighter_data['Losses'])}-{int(fighter_data['Draws'])}"),
            html.P(f"KOs: {int(fighter_data['Knockouts'])}"),
            html.P(f"Submissions: {int(fighter_data['Submissions'])}")
        ])
    
    # Enhanced Fighter Radar Chart
    @app.callback(
        Output('fighter-stats-radar', 'figure'),
        Input('fighter-dropdown', 'value')
    )
    def update_fighter_radar(selected_fighter):
        fighter_data = fighters_df[fighters_df['Name'] == selected_fighter].iloc[0]
        
        # Normalize values for better radar chart presentation
        categories = ['Striking_Accuracy', 'Takedown_Accuracy', 'Sig_Str_Def',
                     'Takedown_Def', 'Knockdown_Avg', 'Sub_Avg_Per_Min']
        
        # Get max values for normalization
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
            hoverinfo='text'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=False,
            title=f"{selected_fighter}'s Fighting Attributes"
        )
        
        return fig

    # Win-Loss Pie Chart Callback
    @app.callback(
        Output('fighter-win-loss-pie', 'figure'),
        Input('fighter-dropdown', 'value')
    )
    def update_win_loss_pie(selected_fighter):
        fighter_data = fighters_df[fighters_df['Name'] == selected_fighter].iloc[0]
        
        # Values for the pie chart
        values = [fighter_data['Wins'], fighter_data['Losses'], fighter_data['Draws']]
        labels = ['Wins', 'Losses', 'Draws']
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4)])
        fig.update_layout(title=f"{selected_fighter}'s Record", showlegend=True)
        
        return fig

    # Fighter Style Breakdown Callback
    @app.callback(
        Output('fighter-style-breakdown', 'figure'),
        Input('fighter-dropdown', 'value')
    )
    def update_style_breakdown(selected_fighter):
        fighter_data = fighters_df[fighters_df['Name'] == selected_fighter].iloc[0]
        
        # Create data for strike distribution
        strike_data = {
            'Location': ['Head', 'Body', 'Leg'],
            'Percentage': [
                fighter_data['Sig_Strikes_Head_Percent'],
                fighter_data['Sig_Strikes_Body_Percent'],
                fighter_data['Sig_Strikes_Leg_Percent']
            ]
        }
        
        strike_df = pd.DataFrame(strike_data)
        
        # Create data for position distribution
        position_data = {
            'Position': ['Standing', 'Clinch', 'Ground'],
            'Percentage': [
                fighter_data['Sig_Strikes_While_Standing_Percent'],
                fighter_data['Sig_Strikes_While_Clinched_Percent'],
                fighter_data['Sig_Strikes_While_Grounded_Percent']
            ]
        }
        
        position_df = pd.DataFrame(position_data)
        
        fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]],
                            subplot_titles=('Strike Target Distribution', 'Fighting Position Distribution'))
        
        fig.add_trace(
            go.Pie(
                labels=strike_df['Location'],
                values=strike_df['Percentage'],
                name="Strike Targets"
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Pie(
                labels=position_df['Position'],
                values=position_df['Percentage'],
                name="Fighting Positions"
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text=f"{selected_fighter}'s Fighting Style Analysis",
            height=500
        )
        
        return fig

    # Match Info Card Callback
    @app.callback(
        Output('match-info-card', 'children'),
        Input('match-dropdown', 'value')
    )
    def update_match_info(selected_bout):
        match_data = results_df[results_df['BOUT'] == selected_bout].iloc[0]
        
        # Get fighter names
        fighter1 = match_data['FIGHTER_1']
        fighter2 = match_data['FIGHTER_2']
        
        # Determine winner
        if match_data['fighter_1_result'] == 1:
            winner = fighter1
            loser = fighter2
        else:
            winner = fighter2
            loser = fighter1
        
        # Get method of victory
        method_mapping = {0: "Decision", 1: "KO/TKO", 2: "Submission"}
        method = method_mapping.get(match_data['method_label'], "Unknown")
        
        return html.Div([
            html.H4(selected_bout),
            html.P(f"Event: {match_data['EVENT']}"),
            html.P(f"Date: {match_data['DATE'].strftime('%B %d, %Y')}"),
            html.P(f"Location: {match_data['LOCATION'].title()}"),
            html.P(f"Weight Class: {match_data['weight_class'].title()}"),
            html.Hr(),
            html.P(f"Winner: {winner}", style={'color': 'green', 'fontWeight': 'bold'}),
            html.P(f"Loser: {loser}"),
            html.P(f"Method: {method}"),
            html.P(f"Round: {match_data['ROUND']}"),
            html.P(f"Time: {int(match_data['TIME'] // 60)}:{int(match_data['TIME'] % 60):02d}")
        ])

    # Enhanced Round Stats Callback
    @app.callback(
        Output('round-stats', 'figure'),
        Input('match-dropdown', 'value')
    )
    def update_round_stats(selected_bout):
        bout_stats = stats_df[stats_df['BOUT'] == selected_bout]
        
        fig = go.Figure()
        
        for fighter in bout_stats['FIGHTER'].unique():
            fighter_stats = bout_stats[bout_stats['FIGHTER'] == fighter]
            
            # Significant strikes accuracy
            fig.add_trace(go.Scatter(
                x=fighter_stats['ROUND'],
                y=fighter_stats['SIG.STR. %'],
                name=f"{fighter} - Sig. Strike Accuracy",
                mode='lines+markers',
                line=dict(width=3)
            ))
            
            # Significant strikes landed
            fig.add_trace(go.Bar(
                x=fighter_stats['ROUND'],
                y=fighter_stats['sig_str_land'],
                name=f"{fighter} - Sig. Strikes Landed",
                opacity=0.7,
                yaxis="y2"
            ))
        
        fig.update_layout(
            title=f"Round Performance: {selected_bout}",
            xaxis_title="Round",
            yaxis=dict(
                title="Significant Strike Accuracy (%)",
                range=[0, 1]
            ),
            yaxis2=dict(
                title="Significant Strikes Landed",
                overlaying="y",
                side="right"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig

    # Strike Distribution Callback
    @app.callback(
        Output('strike-distribution', 'figure'),
        Input('match-dropdown', 'value')
    )
    def update_strike_distribution(selected_bout):
        bout_stats = stats_df[stats_df['BOUT'] == selected_bout]
        
        fig = go.Figure()
        
        for fighter in bout_stats['FIGHTER'].unique():
            fighter_stats = bout_stats[bout_stats['FIGHTER'] == fighter]
            
            # Sum up the stats across all rounds
            head_strikes = fighter_stats['total_head_land'].sum()
            body_strikes = fighter_stats['total_body_land'].sum()
            leg_strikes = fighter_stats['total_leg_land'].sum()
            
            fig.add_trace(go.Bar(
                x=['Head', 'Body', 'Leg'],
                y=[head_strikes, body_strikes, leg_strikes],
                name=fighter
            ))
        
        fig.update_layout(
            title=f"Strike Distribution: {selected_bout}",
            xaxis_title="Target Area",
            yaxis_title="Strikes Landed",
            barmode='group'
        )
        
        return fig

    # Takedown Success Callback
    @app.callback(
        Output('takedown-success', 'figure'),
        Input('match-dropdown', 'value')
    )
    def update_takedown_success(selected_bout):
        bout_stats = stats_df[stats_df['BOUT'] == selected_bout]
        
        fig = go.Figure()
        
        for fighter in bout_stats['FIGHTER'].unique():
            fighter_stats = bout_stats[bout_stats['FIGHTER'] == fighter]
            
            # Sum up the stats across all rounds
            takedowns_attempted = fighter_stats['touchdown_attempt'].sum()
            takedowns_landed = fighter_stats['takedown_land'].sum()
            
            fig.add_trace(go.Bar(
                x=['Attempted', 'Landed'],
                y=[takedowns_attempted, takedowns_landed],
                name=fighter
            ))
        
        fig.update_layout(
            title=f"Takedown Success: {selected_bout}",
            xaxis_title="Takedowns",
            yaxis_title="Count",
            barmode='group'
        )
        
        return fig
