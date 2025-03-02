# callbacks.py
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
from dash import dcc, html
from plotly.subplots import make_subplots
from dash import dcc, html, callback, Input, Output, ctx
import dash_bootstrap_components as dbc

import numpy as np
# Load your data
fighters_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fighters_processed.csv')
results_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fight_stats_with_weghtclass_date_location.csv')
results_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fight_results_with_locale.csv')



def register_callbacks_2(app,fighters_df,results_df,stats_df):

    @app.callback(
        Output("page-content", "children"),
        [Input("fighters-link", "n_clicks"),
         Input("matches-link", "n_clicks")]
    )
    def toggle_active_tab(fighters_clicks, matches_clicks):
        from layout_dash import create_fighters_tab, create_matches_tab  # Local import
        if ctx.triggered:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if trigger_id == 'fighters-link':
                return create_fighters_tab(fighters_df)
            elif trigger_id == 'matches-link':
                return create_matches_tab(results_df)
        return create_fighters_tab(fighters_df)  # Default

    @app.callback(
        Output('active-tab', 'data'),
        [Input("fighters-link", "n_clicks"),
         Input("matches-link", "n_clicks")]
    )
    def store_active_tab(fighters_clicks, matches_clicks):
        if ctx.triggered:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if trigger_id == 'fighters-link':
                return 'fighters'
            elif trigger_id == 'matches-link':
                return 'matches'
        return 'fighters'  # Default value
    
    
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
                html.Img(src=f"assets/{fighter['Name'].lower().replace(' ', '_')}.jpg", 
                    style={'width': '150px', 'height': '150px', 'borderRadius': '50%'},
                    className="mx-auto d-block mb-3"),
                html.H3(fighter['Name'], className="text-center mb-3"),
                html.H5(f"Weight Class: {fighter['Weight_Class']}", className="text-center text-muted mb-2"),
                
                html.Div(className="d-flex justify-content-center mb-3", children=[
                    html.Div(className="text-center mx-2", children=[
                        html.H2(wins, className="text-success m-0"),
                        html.P("WINS", className="text-muted m-0")
                    ]),
                    html.Div(className="text-center mx-2", children=[
                        html.H2(losses, className="text-danger m-0"),
                        html.P("LOSSES", className="text-muted m-0")
                    ]),
                    html.Div(className="text-center mx-2", children=[
                        html.H2(draws, className="text-warning m-0"),
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
        
        # Get all fights where the fighter participated
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
        Output("match-details-content", "children"),
        Input("event-dropdown", "value")
    )
    def update_match_details(event_name):
        if not event_name:
            return html.Div("Please select an event")
        
        # Get all matches for the selected event
        event_matches = results_df[results_df['EVENT'] == event_name]
        
        if event_matches.empty:
            return html.Div("No match data available")
        
        # For simplicity, take the first match from the event
        match = event_matches.iloc[0]
        
        return html.Div([
            html.H4(match['EVENT'], className="text-center mb-3"),
            html.P(f"Date: {match['DATE']}", className="text-center text-muted mb-4"),
            
            html.Div(className="d-flex justify-content-between align-items-center mb-4", children=[
                html.Div(className="text-center", children=[
                    html.Img(src=f"assets/{match['FIGHTER_1'].lower().replace(' ', '_')}.jpg", 
                        style={'width': '100px', 'height': '100px', 'borderRadius': '50%'}),
                    html.H5(match['FIGHTER_1'], className="mt-2"),
                    html.P(match['weight_class'], 
                        className="text-muted")
                ]),
                
                html.Div(className="text-center", children=[
                    html.H3("VS", className="text-danger")
                ]),
                
                html.Div(className="text-center", children=[
                    html.Img(src=f"assets/{match['FIGHTER_2'].lower().replace(' ', '_')}.jpg", 
                        style={'width': '100px', 'height': '100px', 'borderRadius': '50%'}),
                    html.H5(match['FIGHTER_2'], className="mt-2"),
                    html.P(match['weight_class'], 
                        className="text-muted")
                ]),
            ]),
            
            html.Div(className="text-center mb-3", children=[
                html.H5("RESULT"),
                html.H4([
                    html.Span(f"Winner: {match['FIGHTER_1'] if match['fighter_1_result'] ==1 else match['FIGHTER_2']}", 
                            className="text-success" if match['fighter_1_result'] == 1 else "text-danger"),
                ]),
                html.P(f"via {match['method_label']} - Round {match['ROUND']} ({match['total_time_seconds']}s)")
            ])
        ])
    @app.callback(
        Output("match-stats-chart", "figure"),
        Input("event-dropdown", "value")
    )
    
    def update_match_stats(event_name):
        if not event_name:
            return {}

        # Filter matches for the selected event
        event_bouts = results_df[results_df['EVENT'] == event_name]
        if event_bouts.empty:
            return {} 

        # Initialize statistics categories
        stats_categories = [
            'sig_str_land', 'total_str_land', 'takedown_land', 
            'KD', 'CTRL'  # Adjust the names to match your DataFrame
        ]
        
        fighters = event_bouts['FIGHTER'].unique()
        print(fighters)
        # Initialize statistics categories
        stats_categories = [
            'sig_str_land', 'total_str_land', 'takedown_land', 
            'KD', 'CTRL'  # Adjust these based on your DataFrame's actual column names
        ]

        # Initialize dictionaries to hold stats for each fighter
        fighter_stats = {fighter: {cat: 0 for cat in stats_categories} for fighter in fighters}

        # Aggregate statistics for each fighter
        for _, row in event_bouts.iterrows():
            fighter_stats[row['FIGHTER']]['sig_str_land'] += row['sig_str_land']
            fighter_stats[row['FIGHTER']]['total_str_land'] += row['total_str_land']
            fighter_stats[row['FIGHTER']]['takedown_land'] += row['takedown_land']
            fighter_stats[row['FIGHTER']]['KD'] += row['KD']
            fighter_stats[row['FIGHTER']]['CTRL'] += row['CTRL']

        # Prepare data for plotting
        fig = go.Figure()
        
        for fighter, stats in fighter_stats.items():
            fig.add_trace(go.Bar(
                x=stats_categories,
                y=list(stats.values()),
                name=fighter,
                marker_color='red' if fighter == fighters[0] else 'blue'  # Alternate colors or use a color map
            ))

        fig.update_layout(
            barmode='group',
            title='Fight Statistics',
            xaxis_title='Statistics',
            yaxis_title='Count',
            legend_title='Fighter',
            margin=dict(l=40, r=40, t=40, b=40),
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            font=dict(color='white')
        )
        
        return fig