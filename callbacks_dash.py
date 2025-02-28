# callbacks.py
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
from dash import dcc, html
from plotly.subplots import make_subplots

import numpy as np
# Load your data
fighters_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fighters_processed.csv')
stats_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fight_stats_with_weghtclass_date_location.csv')
results_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fight_results_with_locale.csv')

def register_callbacks(app,fighters_df, stats_df, results_df):

## -------------------------------------- FIGHTER ANALYSIS CALLBACKS -------------------------------------- ##
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
    
    
    
    # Fighter Radar Chart
    @app.callback(
        Output('fighter-stats-radar', 'figure'),
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
            title=f"{selected_fighter}'s Fighting Attributes",
            title_x=0.5
        )
        
        return fig

    # Win-Loss Pie Chart
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
        fig.update_layout(title=f"{selected_fighter}'s Record",title_x=0.5, showlegend=True)
        
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
                            subplot_titles=('Striking distribution', 'Fighting position Distribution'))
        
        fig.add_trace(
            go.Pie(
                labels=strike_df['Location'],
                values=strike_df['Percentage'],
                name="Strk pos"
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Pie(
                labels=position_df['Position'],
                values=position_df['Percentage'],
                name="Fighting pos"
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text=f"{selected_fighter}'s Fighting style analysis",
            title_x=0.5,
            height=500
        )
        
        return fig


## -------------------------------------- MATCH ANALYSIS CALLBACKS -------------------------------------- ##
## -------------------------------------- MATCH ANALYSIS CALLBACKS -------------------------------------- ##

    # Match Info Card Callback
    @app.callback(
        [Output('match-info-card', 'children'),
        Output('fighter-1-image', 'src'),
        Output('fighter-2-image', 'src'),
        Output('fighter-1-name', 'children'),
        Output('fighter-2-name', 'children')],
        [Input('match-dropdown', 'value')]
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
        
        fighter_1_info = fighters_df[fighters_df['Name'] == fighter1].iloc[0]
        fighter_2_info = fighters_df[fighters_df['Name'] == fighter2].iloc[0]
        
        # Get method
        method_mapping = {0: "ko/tko/could not continue", 1: "submission", 2: "decision", 3:"dq", 4:"overturned"}
        method = method_mapping.get(match_data['method_label'], "Unknown")
        
        # Image URLs
        img_url_1 = 'https://res.cloudinary.com/da7h9bpnj/image/upload/v1740706726/q7aeoc2wkh12vfylaprk.png'
        #fighter_1_info['img']
        
        img_url_2 = 'https://res.cloudinary.com/da7h9bpnj/image/upload/v1740706726/q7aeoc2wkh12vfylaprk.png'
        #fighter_2_info['img']
        
        match_info = html.Div([
            html.H4(selected_bout),
            html.P(f"Event: {match_data['EVENT']}"),
            html.P(f"Date: {match_data['DATE'].strftime('%B %d, %Y')}"),
            html.P(f"Location: {match_data['LOCATION'].title()}"),
            html.P(f"Weight Class: {match_data['weight_class'].title()}"),
            html.Hr(),
            html.P(f"Winner: {winner}", style={'color': 'green', 'fontWeight': 'bold'}),
            html.P(f"Loser: {loser}",style={'color': 'red', 'fontWeight': 'bold'}),
            html.P(f"Method: {method}"),
            html.P(f"Round: {match_data['ROUND']}"),
            html.P(f"Time: {match_data['TIME']}(s)"),
            html.P(f"Total time: {match_data['total_time_seconds']}(s)")
        ])
        
        return match_info, img_url_1, img_url_2, fighter1, fighter2

    # Round Stats Callback
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
                opacity=0.5,
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

        # Determine number of fighters to display
        fighters = bout_stats['FIGHTER'].unique()
        num_fighters = len(fighters)

        # Create subplots
        fig = make_subplots(
            rows=num_fighters,
            cols=1,
            subplot_titles=[fighter for fighter in fighters],
            specs=[[{'type': 'bar'}] for _ in range(num_fighters)]  # Specify bar type for each subplot
        )

        for i, fighter in enumerate(fighters):
            fighter_stats = bout_stats[bout_stats['FIGHTER'] == fighter]

            head_strikes = fighter_stats['total_head_land'].sum()
            body_strikes = fighter_stats['total_body_land'].sum()
            leg_strikes = fighter_stats['total_leg_land'].sum()

            fig.add_trace(go.Bar(
                x=['Head', 'Body', 'Leg'],
                y=[head_strikes, body_strikes, leg_strikes],
                name=f"{fighter} - Landed",
                legendgroup=fighter,
                marker_color='blue'
            ), row=i + 1, col=1)

            head_strikes_attempt = fighter_stats['total_head_attempt'].sum()
            body_strikes_attempt = fighter_stats['total_body_attempt'].sum()
            leg_strikes_attempt = fighter_stats['total_leg_attempt'].sum()

            fig.add_trace(go.Bar(
                x=['Head', 'Body', 'Leg'],
                y=[head_strikes_attempt, body_strikes_attempt, leg_strikes_attempt],
                name=f"{fighter} - Attempted",
                legendgroup=fighter,
                marker_color='red'
            ), row=i + 1, col=1)           


        fig.update_layout(
                title=f"Strike Distribution: {selected_bout}",
                xaxis_title="Target Area",
                yaxis_title="Count",
                barmode='group',
                height=300 * num_fighters 
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
    
    
    
    ## -------------------------------------- FIGHTER COMPARISON CALLBACKS -------------------------------------- ##

    

    @app.callback(
        [Output('fighter-1-info-card', 'children'),
         Output('fighter-2-info-card', 'children')],
        [Input('fighter-dropdown-1', 'value'),
         Input('fighter-dropdown-2', 'value')]
    )
    def update_fighter_comparison(selected_fighter_1, selected_fighter_2):
        if selected_fighter_1 == selected_fighter_2:
            return "Please select two different fighters for comparison.",
        
        # Fetch data for fighter 1
        fighter_data_1 = fighters_df[fighters_df['Name'] == selected_fighter_1].iloc[0]
        img_url_1 = fighter_data_1['img'] 
        fighter_info_1 = html.Div([
            html.H4(selected_fighter_1),
            html.Img(src=img_url_1, style={'width': '150px', 'height': 'auto', 'borderRadius': '5px'}),
            html.P(f"Nickname: {fighter_data_1['Nickname'] if pd.notna(fighter_data_1['Nickname']) else 'N/A'}"),
            html.P(f"Weight Class: {fighter_data_1['Weight_Class']}"),
            html.P(f"Wins: {fighter_data_1['Wins']}"),
            html.P(f"Losses: {fighter_data_1['Losses']}"),
            html.P(f"Knockouts: {fighter_data_1['Knockouts']}"),
            html.P(f"Submissions: {fighter_data_1['Submissions']}")
        ],style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'margin': '10px', 'border': '1px solid #d20a0a', 'padding': '10px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'})

        # Fetch data for fighter 2
        fighter_data_2 = fighters_df[fighters_df['Name'] == selected_fighter_2].iloc[0]
        img_url_2 = fighter_data_2['img']
        
        fighter_info_2 = html.Div([
            html.H4(selected_fighter_2),
            html.Img(src=img_url_2, style={'width': '140px', 'height': 'auto', 'borderRadius': '5px'}),
            html.P(f"Nickname: {fighter_data_2['Nickname'] if pd.notna(fighter_data_2['Nickname']) else 'N/A'}"),
            html.P(f"Weight Class: {fighter_data_2['Weight_Class']}"),
            html.P(f"Wins: {fighter_data_2['Wins']}"),
            html.P(f"Losses: {fighter_data_2['Losses']}"),
            html.P(f"Knockouts: {fighter_data_2['Knockouts']}"),
            html.P(f"Submissions: {fighter_data_2['Submissions']}")
        ],style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'margin': '10px', 'border': '1px solid #d20a0a', 'padding': '10px', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'})
        return fighter_info_1, fighter_info_2
    
    @app.callback(
        Output('fighter-comparison-piechart', 'figure'),
        Output('fighter-comparison-radar', 'figure'),
        [Input('fighter-dropdown-1', 'value'),
         Input('fighter-dropdown-2', 'value')]  
    )
        
    def update_piechart_radar(selected_fighter_1, selected_fighter_2):
        fighter_data_1 = fighters_df[fighters_df['Name'] == selected_fighter_1].iloc[0]
        fighter_data_2 = fighters_df[fighters_df['Name'] == selected_fighter_2].iloc[0]
        

        win_loss_values_p1 = [fighter_data_1['Wins'], fighter_data_1['Losses'], fighter_data_1['Draws']]
        win_loss_values_p2 = [fighter_data_2['Wins'], fighter_data_2['Losses'], fighter_data_2['Draws']]
        win_loss_labels = ["Wins", "Losses", " Draws"]
        
        fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]],
                            subplot_titles=(f'{fighter_data_1['Name']} stats', f'{fighter_data_2['Name']} stats'))
        
        fig.add_trace(
            go.Pie(
                labels=win_loss_labels,
                values=win_loss_values_p1,
                name="nothing to see here"
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Pie(
                labels=win_loss_labels,
                values=win_loss_values_p2,
                name="blba bla"
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text=f"{fighter_data_1['Name']} & {fighter_data_2['Name']} Records",
            height=500

        )
        categories = ['Striking_Accuracy', 'Takedown_Accuracy', 'Sig_Str_Def', 'Takedown_Def', 'Knockdown_Avg', 'Sub_Avg_Per_Min']

        
        #max values for normalization
        max_values = {
            'Striking_Accuracy': 1,
            'Takedown_Accuracy': 1,
            'Sig_Str_Def': 1,
            'Takedown_Def': 1,
            'Knockdown_Avg': fighters_df['Knockdown_Avg'].max(),
            'Sub_Avg_Per_Min': fighters_df['Sub_Avg_Per_Min'].max()
        }
        
        values_1 = [fighter_data_1[cat]/max_values[cat] for cat in categories]
        values_2 = [fighter_data_2[cat]/max_values[cat] for cat in categories]

        
     
        display_categories = [
            'Strike Acc.', 'Takedown Acc.', 'Strike Defense',
            'Takedown Def.', 'Knockdown Avg', 'Submission Avg'
        ]
        radar_fig = make_subplots(rows=1, cols=2, subplot_titles=(fighter_data_1['Name'], fighter_data_2['Name']),specs=[[{'type': 'polar'}, {'type': 'polar'}]])

        radar_fig.add_trace(go.Scatterpolar(
            r=values_1 ,  
            theta=display_categories,  
            fill='toself',
            name=selected_fighter_1
        ), row=1, col=1)

        radar_fig.add_trace(go.Scatterpolar(
            r=values_2,  
            theta=display_categories,  
            fill='toself',
            name=selected_fighter_2
        ), row=1, col=2)

        radar_fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1.1]  
                )
            )
        )
        return fig, radar_fig


