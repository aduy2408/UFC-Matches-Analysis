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

def register_callbacks(app, fighters_df, results_df, stats_df):
    """Register all callbacks by calling individual registration functions"""
    # Import all callback modules
    from callbacks_fighters import register_fighter_callbacks
    from callbacks_matches import register_match_callbacks
    from callbacks_comparison import register_comparison_callbacks
    from callbacks_prediction import register_prediction_callbacks
    
    # Navigation callbacks
    @app.callback(
        Output("page-content", "children"),
        [Input("fighters-link", "n_clicks"),
         Input("matches-link", "n_clicks"),
         Input('comparison-link', 'n_clicks'),
         Input('prediction-link', 'n_clicks')]
    )
    def toggle_active_tab(fighters_clicks, matches_clicks, comparison_clicks, predict_clicks):
        from layout_dash import create_fighters_tab, create_matches_tab, create_comparison_tab, matches_predictions_tab
        if ctx.triggered:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if trigger_id == 'fighters-link':
                return create_fighters_tab(fighters_df=fighters_df, results_df=results_df, stats_df=stats_df)
            elif trigger_id == 'matches-link':
                return create_matches_tab(fighters_df=fighters_df, results_df=results_df, stats_df=stats_df)
            elif trigger_id == 'comparison-link':
                return create_comparison_tab(fighters_df=fighters_df, results_df=results_df, stats_df=stats_df)
            elif trigger_id == 'prediction-link':
                return matches_predictions_tab(fighters_df=fighters_df, results_df=results_df, stats_df=stats_df)
        return create_fighters_tab(fighters_df=fighters_df, results_df=results_df, stats_df=stats_df)
    
    @app.callback(
        Output('active-tab', 'data'),
        [Input("fighters-link", "n_clicks"),
         Input("matches-link", "n_clicks"),
         Input('comparison-link', 'n_clicks'),
         Input('prediction-link', 'n_clicks')]
    )
    def store_active_tab(fighters_clicks, matches_clicks, comparison_clicks, predict_clicks):
        if ctx.triggered:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if trigger_id == 'fighters-link':
                return 'fighters'
            elif trigger_id == 'matches-link':
                return 'matches'
            elif trigger_id == 'comparison-link':
                return 'comparison'
            elif trigger_id == 'prediction-link':
                return 'prediction'
        return 'fighters'  # Default value
    
    # Register all other callbacks
    register_fighter_callbacks(app, fighters_df, results_df, stats_df)
    register_match_callbacks(app, fighters_df, results_df, stats_df)
    register_comparison_callbacks(app, fighters_df, results_df, stats_df)
    register_prediction_callbacks(app, fighters_df, results_df, stats_df)

# def register_callbacks_2(app,fighters_df,results_df,stats_df):

#     @app.callback(
#         Output("page-content", "children"),
#         [Input("fighters-link", "n_clicks"),
#          Input("matches-link", "n_clicks"),
#          Input('comparison-link', 'n_clicks'),
#          Input('prediction-link', 'n_clicks')]
#     )
#     def toggle_active_tab(fighters_clicks, matches_clicks,comparison_clicks,predict_clicks):
#         from layout_dash import create_fighters_tab, create_matches_tab,create_comparison_tab ,matches_predictions_tab 
#         if ctx.triggered:
#             trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
#             if trigger_id == 'fighters-link':
#                 return create_fighters_tab(fighters_df=fighters_df,results_df=results_df,stats_df=stats_df)
#             elif trigger_id == 'matches-link':
#                 return create_matches_tab(fighters_df=fighters_df,results_df=results_df,stats_df=stats_df)
#             elif trigger_id == 'comparison-link':
#                 return create_comparison_tab(fighters_df=fighters_df,results_df=results_df,stats_df=stats_df)
#             elif trigger_id =='prediction-link':
#                 return matches_predictions_tab(fighters_df=fighters_df,results_df=results_df,stats_df=stats_df)
#         return create_fighters_tab(fighters_df=fighters_df,results_df=results_df,stats_df=stats_df)  
    
#     @app.callback(
#         Output('active-tab', 'data'),
#         [Input("fighters-link", "n_clicks"),
#          Input("matches-link", "n_clicks"),
#          Input('comparison-link', 'n_clicks'),
#          Input('prediction-link', 'n_clicks')]
#     )
#     def store_active_tab(fighters_clicks, matches_clicks,comparison_clicks,predict_clicks):
#         if ctx.triggered:
#             trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
#             if trigger_id == 'fighters-link':
#                 return 'fighters'
#             elif trigger_id == 'matches-link':
#                 return 'matches'
#             elif trigger_id == 'comparison-link':
#                 return 'comparison'
#             elif trigger_id == 'prediction-link':
#                 return 'prediction'
#         return 'fighters'  # Default value
    
    
#     @app.callback(
#         Output("fighter-profile-content", "children"),
#         Input("fighter-dropdown", "value")
#     )
#     def update_fighter_profile(fighter_name):
#         if not fighter_name:
#             return html.Div("Please select a fighter")
        
#         fighter = fighters_df[fighters_df['Name'] == fighter_name].iloc[0]
#         wins = fighter['Wins']
#         losses = fighter['Losses']
#         draws = fighter['Draws']    
    
        
#         return html.Div([
#             html.Div([
#                 html.Img(src=f"/assets/minh_2.jpg", 
#                     style={'width': '150px', 'height': '150px', 'borderRadius': '10%'},
#                     className="mx-auto d-block mb-3"),
#                 html.H4(fighter['Name'], className="text-center mb-3"),
#                 html.H6(f"{fighter['Weight_Class']}", className="text-center text-muted mb-2"),
                
#                 html.Div(className="d-flex justify-content-center mb-3", children=[
#                     html.Div(className="text-center mx-2", children=[
#                         html.H4(wins, className="text-success m-0"),
#                         html.P("WINS", className="text-muted m-0")
#                     ]),
#                     html.Div(className="text-center mx-2", children=[
#                         html.H4(losses, className="text-danger m-0"),
#                         html.P("LOSSES", className="text-muted m-0")
#                     ]),
#                     html.Div(className="text-center mx-2", children=[
#                         html.H4(draws, className="text-warning m-0"),
#                         html.P("DRAWS", className="text-muted m-0")
#                     ]),
#                 ]),
                
#                 html.H5("FINISH RATE", className="text-center mb-1"),
#                 html.Div(className="d-flex justify-content-center", children=[
#                     html.Div(className="text-center mx-2", children=[
#                         html.H4(fighter['Knockouts'], className="text-danger m-0"),
#                         html.P("KO/TKO", className="text-muted m-0")
#                     ]),
#                     html.Div(className="text-center mx-2", children=[
#                         html.H4(fighter['Submissions'], className="text-primary m-0"),
#                         html.P("SUBMISSIONS", className="text-muted m-0")
#                     ]),
#                 ]),
#             ])
#         ])
#     @app.callback(
#         Output('fighter-radar-chart', 'figure'),
#         Input('fighter-dropdown', 'value')
#     )
#     def update_fighter_radar(selected_fighter):
#         fighter_data = fighters_df[fighters_df['Name'] == selected_fighter].iloc[0]
        
#         # Normalize 
#         categories = ['Striking_Accuracy', 'Takedown_Accuracy', 'Sig_Str_Def',
#                      'Takedown_Def', 'Knockdown_Avg', 'Sub_Avg_Per_Min']
        
#         #max values for normalization
#         max_values = {
#             'Striking_Accuracy': 1,
#             'Takedown_Accuracy': 1,
#             'Sig_Str_Def': 1,
#             'Takedown_Def': 1,
#             'Knockdown_Avg': fighters_df['Knockdown_Avg'].max(),
#             'Sub_Avg_Per_Min': fighters_df['Sub_Avg_Per_Min'].max()
#         }
        
#         values = [fighter_data[cat]/max_values[cat] for cat in categories]
#         display_values = [fighter_data[cat] for cat in categories]
        
#         # Rename categories for display
#         display_categories = [
#             'Strike Acc.', 'Takedown Acc.', 'Strike Defense',
#             'Takedown Def.', 'Knockdown Avg', 'Submission Avg'
#         ]
        
#         fig = go.Figure()
        
#         fig.add_trace(go.Scatterpolar(
#             r=values,
#             theta=display_categories,
#             fill='toself',
#             name=selected_fighter,
#             text=[f"{cat}: {val:.2f}" for cat, val in zip(display_categories, display_values)],
#             hoverinfo='text',
#             line_color='red',
#             fillcolor='rgba(255, 0, 0, 0.3)'
#         ))
        
#         fig.update_layout(
#             polar=dict(
#                 bgcolor="rgba(30, 30, 30, 1)",
#                 radialaxis=dict(
#                     visible=True,
#                     range=[0, 1.1]
#                 )
#             ),
#             showlegend=False,
#             title=f"{selected_fighter}'s Fighting Attributes",
#             title_x=0.5,
#             margin=dict(l=60, r=60, t=40, b=40),
#             paper_bgcolor='rgba(0, 0, 0, 0)',
#             plot_bgcolor='rgba(0, 0, 0, 0)',
#             font=dict(color='white')
#         )
        
#         return fig
    
    
        
#     @app.callback(
#         Output("fighter-recent-fights", "children"),
#         Input("fighter-dropdown", "value")
#     )
#     def update_recent_fights(fighter_name):
#         if not fighter_name:
#             return html.Div("Please select a fighter")
        

#         fighter_matches = results_df[
#             (results_df['FIGHTER_1'] == fighter_name) | (results_df['FIGHTER_2'] == fighter_name)
#         ].sort_values('DATE', ascending=False)
        
#         if fighter_matches.empty:
#             return html.Div("No fight data available")
        
#         return html.Div([
#             dbc.Table([
#                 html.Thead([
#                     html.Tr([
#                         html.Th("EVENT"),
#                         html.Th("DATE"),
#                         html.Th("OPPONENT"),
#                         html.Th("RESULT"),
#                         html.Th("METHOD"),
#                         html.Th("ROUND"),
#                     ])
#                 ]),
#                 html.Tbody([
#                     html.Tr([
#                         html.Td(row['EVENT']),
#                         html.Td(row['DATE']),
#                         html.Td(row['FIGHTER_2'] if row['FIGHTER_1'] == fighter_name else row['FIGHTER_1']),
#                         html.Td(
#                             html.Span("WIN", className="text-success") 
#                             if (row['FIGHTER_1'] == fighter_name and row['fighter_1_result'] == 1) or \
#                             (row['FIGHTER_2'] == fighter_name and row['fighter_2_result'] == 1) 
#                             else html.Span("LOSS", className="text-danger")
#                         ),
#                         html.Td(row['method_label']),
#                         html.Td(f"R{row['ROUND']} ({row['total_time_seconds']})")
#                     ]) for _, row in fighter_matches.iterrows()
#                 ])
#             ], striped=True, bordered=True, hover=True, responsive=True)
#         ])
    
#     @app.callback(
#     Output('fighter-strike-distribution', 'figure'),
#     Input('fighter-dropdown', 'value')
#     )
#     def update_fighter_strike_distribution(selected_fighter):
#         fighter_data = fighters_df[fighters_df['Name'] == selected_fighter].iloc[0]
#         colors = ["#636EFA", "#EF553B", "#00CC96"]  # Blue, Red, Green
        
#         strike_data = {
#         'Location': ['Head', 'Body', 'Leg'],
#         'Percentage': [
#         fighter_data['Sig_Strikes_Head_Percent'],
#         fighter_data['Sig_Strikes_Body_Percent'],
#         fighter_data['Sig_Strikes_Leg_Percent']
#         ]}
#         strike_df = pd.DataFrame(strike_data)
        
#         fig = go.Figure()
#         fig.add_trace(go.Pie(
#             labels = strike_df['Location'],
#             values = strike_df['Percentage'],
#             hole = 0.1,
#             name = "strike_pos",
#             marker=dict(colors=colors, line=dict(color='white', width=1)),  
#             textfont = dict(color='white')
#         ))
#         fig.update_layout(
#             title = dict(text = 'Strike Distribution',
#                          font=dict(size=20, color="white")),
#             title_x = 0.5,
#             paper_bgcolor="rgba(30, 30, 30, 1)",
#             plot_bgcolor="rgba(30, 30, 30, 1)", 
#             legend=dict(
#                 font=dict(size=14, color="white"),  
#                 bgcolor="rgba(50, 50, 50, 0.5)" ) 
#         )
#         return fig
#     @app.callback(
#     Output('fighter-style-analysis', 'figure'),
#     Input('fighter-dropdown', 'value')
#     )
#     def update_fighter_strike_distribution(selected_fighter):
#         fighter_data = fighters_df[fighters_df['Name'] == selected_fighter].iloc[0]
#         colors = ["#636EFA", "#EF553B", "#00CC96"]  # Blue, Red, Green

        
#         position_data = {
#         'Position': ['Standing', 'Clinch', 'Ground'],        
#         'Percentage': [
#         fighter_data['Sig_Strikes_While_Standing_Percent'],
#         fighter_data['Sig_Strikes_While_Clinched_Percent'],
#         fighter_data['Sig_Strikes_While_Grounded_Percent']
#         ]}
#         position_df = pd.DataFrame(position_data)
        
#         fig = go.Figure()
#         fig.add_trace(go.Pie(
#             labels = position_df['Position'],
#             values = position_df['Percentage'],
#             hole = 0.1,
#             name = "Fighting style",
#             marker=dict(colors=colors, line=dict(color='white', width=1)),  
#         ))
#         fig.update_layout(
#             title = dict(text = 'Fighting style',
#                          font=dict(size=20, color="white")),
#             title_x = 0.5,
#             paper_bgcolor="rgba(30, 30, 30, 1)",  
#             plot_bgcolor="rgba(30, 30, 30, 1)",  
#             legend=dict(
#                 font=dict(size=14, color="white"),  
#                 bgcolor="rgba(50, 50, 50, 0.5)" ) 
#         )
#         return fig
    
    
#     @app.callback(
#         [Output('momentum-gauge', 'figure'),
#         Output('momentum-radar', 'figure')],
#         [Input('fighter-dropdown', 'value'),
#         Input('strike-weight', 'value')]
#     )
#     def update_momentum_analysis(selected_fighter, strike_weight):
#         fighter_data = fighters_df[fighters_df['Name'] == selected_fighter].iloc[0]
        
#         max_sig_strikes = fighters_df['Sig_Strikes_Per Min'].max()  
#         max_takedowns = fighters_df['Takedown_Avg_Per Min'].max()   
#         max_submissions = fighters_df['Sub_Avg_Per_Min'].max() 
        
#         normalized_sig_strikes = (fighter_data['Sig_Strikes_Per Min'] / max_sig_strikes) * 100
#         normalized_takedowns = (fighter_data['Takedown_Avg_Per Min'] / max_takedowns) * 100
#         normalized_submissions = (fighter_data['Sub_Avg_Per_Min'] / max_submissions) * 100

#         strike_score = normalized_sig_strikes * (strike_weight / 100)
#         grapple_score = (normalized_takedowns + normalized_submissions) * ((100 - strike_weight) / 100)

#         total_momentum = strike_score + grapple_score


#         gauge_fig = go.Figure(go.Indicator(
#             mode="gauge+number",
#             value=total_momentum,
#             domain={'x': [0, 1], 'y': [0, 1]},
#             gauge={
#                 'axis': {
#                     'range': [0, 100],
#                     'tickwidth': 1,
#                     'tickcolor': 'white',
#                     'tickfont': {'color': 'white'}
#                 },
#                 'bar': {'color': "#dc3545"},  
#                 'bgcolor': "rgba(30, 30, 30, 1)", 
#                 'borderwidth': 2,
#                 'bordercolor': "gray",
#                 'steps': [
#                     {'range': [0, 40], 'color': "rgba(100, 100, 100, 0.5)"},
#                     {'range': [40, 70], 'color': "rgba(70, 70, 70, 0.5)"},
#                     {'range': [70, 100], 'color': "rgba(40, 40, 40, 0.5)"}
#                 ]
#             }
#         ))

#         gauge_fig.update_layout(
#             font={'color': 'white', 'family': "Arial"},
#             paper_bgcolor='rgba(0, 0, 0, 0)',
#             plot_bgcolor='rgba(0, 0, 0, 0)',
#             margin=dict(l=60, r=60, t=40, b=40)  
#         )

#         # Create radar chart
#         radar_fig = go.Figure()
#         radar_fig.add_trace(go.Scatterpolar(
#             r=[fighter_data['Sig_Strikes_Per Min'],
#             fighter_data['Takedown_Avg_Per Min'],
#             fighter_data['Sub_Avg_Per_Min'],
#             fighter_data['Knockdown_Avg'],
#             fighter_data['Sig_Str_Def']],
#             theta=['Strikes/Min', 'Takedowns/Min', 
#                 'Sub Attempts/Min', 'Knockdowns', 'Defense'],
#             fill='toself',
#             name='Momentum Factors'
#         ))
#         radar_fig.update_layout(
#             polar=dict(
#                 bgcolor="rgba(30, 30, 30, 1)",
#                 radialaxis=dict(
#                     visible=True,
#                     range=[0, 10]
#                 )
#             ),
#             showlegend=False,
#             title=f"{selected_fighter}",
#             title_x=0.5,
#             margin=dict(l=60, r=60, t=40, b=40),
#             paper_bgcolor='rgba(0, 0, 0, 0)',
#             plot_bgcolor='rgba(0, 0, 0, 0)',
#             font=dict(color='white')
#         )     
#         return gauge_fig, radar_fig
    
    

    
# ### ---------------------MATCHES CALLBACKS----------------------------------- ###
# ### ------------------------------------------------------------------------- ###


#     @app.callback(
#         Output("match-details-content", "children"),
#         Input("match-dropdown", "value")
#     )
#     def update_match_details(match_name):
#         if not match_name:
#             return html.Div("Please select an event")
#         match_data = results_df[results_df['BOUT'] == match_name].iloc[0]
        
#         fighter_1 = match_data['FIGHTER_1']
#         fighter_2 = match_data['FIGHTER_2']

#         # Determine winner
#         if match_data['fighter_1_result'] == 1:
#             winner = fighter_1
#             loser = fighter_2
#         else:
#             winner = fighter_2
#             loser = fighter_1
            
#         method_mapping = {0: "ko/tko/could not continue", 1: "submission", 2: "decision", 3:"dq", 4:"overturned"}
#         method = method_mapping.get(match_data['method_label'], "Unknown")

  
#         return html.Div([
#             html.H4(match_data['EVENT'], className="text-center mb-3"),
#             html.P(f"Date: {match_data['DATE']}", className="text-center text-muted mb-4"),
            
#             html.Div(className="d-flex justify-content-between align-items-center mb-4", children=[
#                 html.Div(className="text-center", children=[
#                     # html.Img(src=f"assets/{match['FIGHTER_1'].lower().replace(' ', '_')}.jpg", 
#                     #     style={'width': '100px', 'height': '100px', 'borderRadius': '50%'}),
#                     html.H5(fighter_1, className="mt-2"),
#                     html.P(match_data['weight_class'], 
#                         className="text-muted")
#                 ]),
                
#                 html.Div(className="text-center", children=[
#                     html.H3("VS", className="text-danger")
#                 ]),
                
#                 html.Div(className="text-center", children=[
#                     # html.Img(src=f"assets/{match['FIGHTER_2'].lower().replace(' ', '_')}.jpg", 
#                     #     style={'width': '100px', 'height': '100px', 'borderRadius': '50%'}),
#                     html.H5(fighter_2, className="mt-2"),
#                     html.P(match_data['weight_class'], 
#                         className="text-muted")
#                 ]),
#             ]),
            
#             html.Div(className="text-center mb-3", children=[
#                 html.H5("RESULT"),
#                 html.H4([
#                     html.Span(f"Winner: {winner}", className="text-success"),
#                 ]),
#                 html.P(f"via {method} - Round {match_data['ROUND']} ({match_data['total_time_seconds']}s)")
#             ])
#         ])
#     @app.callback(
#         Output("match-stats-chart", "figure"),
#         Input("match-dropdown", "value")
#     )
    
#     def update_match_stats(match_name):
#         if not match_name:
#             return {}

#         bout_stats = stats_df[stats_df['BOUT'] == match_name]
#         if bout_stats.empty:
#             return {} 

#         fig = go.Figure()
        
#         # Define modern colors
#         color_palette = ["#1f77b4","#d62728"]
        
#         for i, fighter in enumerate(bout_stats['FIGHTER'].unique()):
#             fighter_stats = bout_stats[bout_stats['FIGHTER'] == fighter]
            
#             # Line chart for Significant Strike Accuracy
#             fig.add_trace(go.Scatter(
#                 x=fighter_stats['ROUND'],
#                 y=fighter_stats['SIG.STR. %'],
#                 name=f"{fighter} Sig Strike Accuracy",
#                 mode='lines+markers',
#                 line=dict(width=3, color=color_palette[i % len(color_palette)]),  #s
#                 marker=dict(size=8, symbol="circle"),
#                 yaxis='y2'
#             ))

#             # Bar chart for Significant Strikes Landed
#             fig.add_trace(go.Bar(
#                 x=fighter_stats['ROUND'],
#                 y=fighter_stats['sig_str_land'],
#                 name=f"{fighter} Sig Strikes Landed",
#                 marker=dict(color=color_palette[i % len(color_palette)], opacity=0.6),  
#             ))

    
#         fig.update_layout(
#             title=dict(
#                 text=f"<b>Round Performance: {match_name}</b>",
#                 y=0.94,
#                 x=0.5,
#                 font=dict(size=20, color="white"),
#             ),
#             xaxis=dict(
#                 title="<b>Round</b>",
#                 tickmode="linear",
#                 tick0=1,
#                 dtick=1,
#                 title_font=dict(size=16, color="white"),
#                 tickfont=dict(size=14, color="white"),
#                 showgrid=True,
#                 gridcolor="gray",
#             ),
#             yaxis=dict(
#                 title="<b>Significant Strikes Landed</b>",
#                 title_font=dict(size=16, color="white"),
#                 tickfont=dict(size=14, color="white"),
#                 showgrid=True,
#                 gridcolor="gray",
#             ),
#             yaxis2=dict(
#                 title="<b>Significant Strike Accuracy (%)</b>",
#                 title_font=dict(size=16, color="white"),
#                 tickfont=dict(size=14, color="white"),
#                 overlaying='y',
#                 side='right',
#                 range=[0, 1],
#                 showgrid=False,
#                 tickformat=".0%",  
#             ),
#             barmode='group',
#             legend=dict(
#                 x=0.5,
#                 y=1,
#                 orientation="h",
#                 bgcolor="rgba(50, 50, 50, 0.5)",
#                 font=dict(size=14, color="white"),
#                 xanchor="center",
#                 yanchor="bottom"
#             ),
#             paper_bgcolor="rgba(20, 20, 20, 1)",  
#             plot_bgcolor="rgba(30, 30, 30, 1)",  
#         )
                    
            
#         return fig
#     @app.callback(
#         Output('strike-distribution', 'figure'),
#         Input('match-dropdown', 'value')
#     )
#     def update_strike_distribution(match_name):
#         if not match_name:
#             return {}
            
#         bout_stats = stats_df[stats_df['BOUT'] == match_name]
#         fighters = bout_stats['FIGHTER'].unique()
        
 
#         fig = make_subplots(
#             rows=2, 
#             cols=2,
#             specs=[[{'type': 'pie'}, {'type': 'pie'}],
#                 [{'type': 'pie'}, {'type': 'pie'}]],
#             subplot_titles=[
#                 f"{fighters[0]} - Attempted", f"{fighters[0]} - Landed",
#                 f"{fighters[1]} - Attempted", f"{fighters[1]} - Landed"
#             ]
#         )
        
#         colors = ["#636EFA", "#EF553B", "#00CC96"]  
        
#         for i, fighter in enumerate(fighters):
#             fighter_stats = bout_stats[bout_stats['FIGHTER'] == fighter]
            
  
#             head_strikes = fighter_stats['total_head_attempt'].sum()
#             body_strikes = fighter_stats['total_body_attempt'].sum()
#             leg_strikes = fighter_stats['total_leg_attempt'].sum()
            
#             head_strikes_land = fighter_stats['total_head_land'].sum()
#             body_strikes_land = fighter_stats['total_body_land'].sum()
#             leg_strikes_land = fighter_stats['total_leg_land'].sum()
            

#             fig.add_trace(
#                 go.Pie(
#                     labels=['Head', 'Body', 'Leg'],
#                     values=[head_strikes, body_strikes, leg_strikes],
#                     name=f"{fighter} Attempts",
#                     marker=dict(colors=colors),
#                     textinfo='percent',
#                     hoverinfo='label+value+percent',
#                     hole=0.3,
#                 ),
#                 row=i+1, col=1
#             )
            
   
#             fig.add_trace(
#                 go.Pie(
#                     labels=['Head', 'Body', 'Leg'],
#                     values=[head_strikes_land, body_strikes_land, leg_strikes_land],
#                     name=f"{fighter} Landed",
#                     marker=dict(colors=colors),
#                     textinfo='percent',
#                     hoverinfo='label+value+percent',
#                     hole=0.3,
#                 ),
#                 row=i+1, col=2
#             )
        
#         fig.update_layout(
#             title=f"Strike Distribution: {match_name}",
#             height=600,
#             paper_bgcolor="rgba(20, 20, 20, 1)",
#             plot_bgcolor="rgba(30, 30, 30, 1)",
#             font=dict(color="white"),
#             showlegend=False
#         )
        
#         return fig
    
#     @app.callback(
#     Output('takedown-analysis', 'figure'),
#     Input('match-dropdown', 'value')
#     )
#     def update_strike_distribution(match_name):
#         if not match_name:
#             return {}
#         attempt_color = "#1f77b4"  
#         landed_color = "#d62728"   
#         bout_stats = stats_df[stats_df['BOUT'] == match_name]
#         fighters = bout_stats['FIGHTER'].unique()
#         fig = go.Figure()
#         for fighter in fighters:
#             fighter_stats = bout_stats[bout_stats['FIGHTER'] == fighter]
#             takedown_attempts = fighter_stats['touchdown_attempt'].sum()
#             takedown_land = fighter_stats['takedown_land'].sum()

            
#             fig.add_trace(go.Bar(
#                 x = ['Attempt','Landed'],
#                 y = [takedown_attempts, takedown_land],
#                 name = fighter,
#             ))
#         fig.update_layout(
#         title=f"Takedown Success: {match_name}",
#         xaxis_title="Takedowns",
#         yaxis_title="Count",
#         barmode='group',
#         paper_bgcolor="rgba(20, 20, 20, 1)",  
#         plot_bgcolor="rgba(30, 30, 30, 1)",  
#             font=dict(color="white"),  
#         legend=dict(
#             font=dict(size=14, color="white"),
#             bgcolor="rgba(50, 50, 50, 0.5)"  
#         )
#         )
#         return fig
    
#     @app.callback(
#         [Output("timeline-slider", "max"),
#         Output("timeline-slider", "value"),
#         Output("timeline-slider", "marks")],
#         Input("match-dropdown", "value")
#     )
#     def update_timeline_slider_props(match_name):
#         if not match_name or match_name not in stats_df['BOUT'].unique():
#             max_round = 3
#         else:
#             bout_stats = stats_df[stats_df['BOUT'] == match_name]
#             max_round = int(bout_stats['ROUND'].max()) if not bout_stats.empty else 3
        
      
#         marks = {i: {'label': f'R{i}', 'style': {'color': 'white'}} for i in range(1, max_round + 1)}
        
#         return max_round, max_round, marks
    
#     @app.callback(
#         Output("fight-timeline", "figure"),
#         [Input("match-dropdown", "value"),
#         Input("timeline-slider", "value")],
#     )
#     def update_fight_timeline(match_name, selected_round):
#         if not match_name:
#             return {}
            
#         bout_stats = stats_df[stats_df['BOUT'] == match_name].copy()
#         if bout_stats.empty:
#             return {}
            
#         fighters = bout_stats['FIGHTER'].unique()
#         if len(fighters) != 2:
#             return {}
        
#         bout_stats['ROUND'] = pd.to_numeric(bout_stats['ROUND'], errors='coerce')
#         bout_stats = bout_stats.dropna(subset=['ROUND'])
#         bout_stats['ROUND'] = bout_stats['ROUND'].astype(int)
        
#         if selected_round is not None:
#             selected_round = int(selected_round)
#         else:
#             selected_round = bout_stats['ROUND'].max()
        
#         filtered_stats = bout_stats[bout_stats['ROUND'] <= selected_round]
        
#         fig = go.Figure()
        
#         for fighter_idx, fighter in enumerate(fighters):
#             fighter_stats = filtered_stats[filtered_stats['FIGHTER'] == fighter]
            
#             if fighter_stats.empty:
#                 continue
                

#             round_stats = fighter_stats.groupby('ROUND').agg({
#                 'sig_str_land': 'sum',
#                 'sig_str_attempt': 'sum',
#                 'total_str_land': 'sum',
#                 'takedown_land': 'sum',
#                 'touchdown_attempt': 'sum' 
#             }).reset_index()
            
#             round_stats['cum_sig_strikes'] = round_stats['sig_str_land'].cumsum()
#             round_stats['cum_takedowns'] = round_stats['takedown_land'].cumsum()
            
#             fig.add_trace(go.Scatter(
#                 x=round_stats['ROUND'],
#                 y=round_stats['cum_sig_strikes'],
#                 mode='lines+markers',
#                 name=f"{fighter} - Sig. Strikes",
#                 line=dict(width=3, color='red' if fighter_idx == 0 else 'blue'),
#                 marker=dict(size=8)
#             ))
            
#             fig.add_trace(go.Scatter(
#                 x=round_stats['ROUND'],
#                 y=round_stats['cum_takedowns'] * 5,  
#                 mode='lines+markers',
#                 name=f"{fighter} - Takedowns (×5)",
#                 line=dict(width=2, dash='dot', color='darkred' if fighter_idx == 0 else 'darkblue'),
#                 marker=dict(symbol='diamond', size=8)
#             ))
        
#         fig.update_layout(
#             title=f"Fight Progression: {match_name}",
#             xaxis=dict(
#                 title="Round",
#                 tickmode='array',
#                 tickvals=list(range(1, int(bout_stats['ROUND'].max()) + 1)),
#                 ticktext=[f"R{r}" for r in range(1, int(bout_stats['ROUND'].max()) + 1)],
#             ),
#             yaxis=dict(title="Cumulative Stats"),
#             paper_bgcolor="rgba(20, 20, 20, 1)",
#             plot_bgcolor="rgba(30, 30, 30, 1)",
#             font=dict(color="white"),
#             legend=dict(
#                 font=dict(color="white")
#             ),
#         )
        
#         return fig
    
    
#     @app.callback(
#         Output("fight-round-distribution", "figure"),
#         [Input("match-dropdown", "value"),
#         Input("timeline-slider", "value")],
#     )
#     def update_round_strike_distribution(match_name, selected_round):
#         if not match_name:
#             return {}
            
#         # Get fight stats for the selected match
#         bout_stats = stats_df[stats_df['BOUT'] == match_name].copy()
#         if bout_stats.empty:
#             return {}
                
#         fighters = bout_stats['FIGHTER'].unique()
#         if len(fighters) != 2:
#             return {}
        
#         bout_stats['ROUND'] = pd.to_numeric(bout_stats['ROUND'], errors='coerce')
#         bout_stats = bout_stats.dropna(subset=['ROUND'])
#         bout_stats['ROUND'] = bout_stats['ROUND'].astype(int)
        
#         if selected_round is not None:
#             selected_round = int(selected_round)
#         else:
#             selected_round = bout_stats['ROUND'].max()
        
#         fig = make_subplots(
#             rows=1, cols=2,
#             specs=[[{"type": "pie"}, {"type": "pie"}]],
#             subplot_titles=(f"{fighters[0]} - Round {selected_round}", f"{fighters[1]} - Round {selected_round}")
#         )
        
#         for fighter_idx, fighter in enumerate(fighters):
#             selected_round_stats = bout_stats[(bout_stats['FIGHTER'] == fighter) & (bout_stats['ROUND'] == selected_round)]
            
#             if not selected_round_stats.empty:
#                 head_strikes = selected_round_stats['total_head_land'].sum()
#                 body_strikes = selected_round_stats['total_body_land'].sum()
#                 leg_strikes = selected_round_stats['total_leg_land'].sum()
                
#                 colors = ["#636EFA", "#EF553B", "#00CC96"]  # Blue, Red, Green
                
#                 fig.add_trace(
#                     go.Pie(
#                         labels=['Head', 'Body', 'Leg'],
#                         values=[head_strikes, body_strikes, leg_strikes],
#                         textinfo='percent',
#                         hoverinfo='label+value+percent',
#                         marker=dict(colors=colors),
#                         hole=0.3,
#                     ),
#                     row=1, col=fighter_idx+1
#                 )
        
        
#         fig.update_layout(
#             title=f"Strike Distribution in Round {selected_round}",
#             height=350,
#             paper_bgcolor="rgba(20, 20, 20, 1)",
#             plot_bgcolor="rgba(30, 30, 30, 1)",
#             font=dict(color="white"),
#             showlegend=True,
#             legend=dict(

#                 font=dict(color="white"),
#                 bgcolor="rgba(50, 50, 50, 0.5)"
#             )
#         )
        
#         return fig
# ### ---------------------COMPARISON CALLBACKS----------------------------------- ###
# ### ------------------------------------------------------------------------- ###

#     @app.callback(
#         Output("fighters-comparison-chart", "figure"),
#         [Input("fighter1-dropdown", "value"),
#         Input("fighter2-dropdown", "value")]
#     )
#     def update_fighters_comparison(fighter1_name, fighter2_name):
#         fighter1 = fighters_df[fighters_df['Name'] == fighter1_name].iloc[0]
#         fighter2 = fighters_df[fighters_df['Name'] == fighter2_name].iloc[0]
        
#         categories = ['Striking_Accuracy', 'Takedown_Accuracy', 'Sig_Str_Def', 'Takedown_Def', 'Knockdown_Avg', 'Sub_Avg_Per_Min']
#         max_values = {
#         'Striking_Accuracy': 1,
#         'Takedown_Accuracy': 1,
#         'Sig_Str_Def': 1,
#         'Takedown_Def': 1,
#         'Knockdown_Avg': fighters_df['Knockdown_Avg'].max(),
#         'Sub_Avg_Per_Min': fighters_df['Sub_Avg_Per_Min'].max()
#         }
        
#         values_1 = [fighter1[cat]/max_values[cat] for cat in categories]
#         values_2 = [fighter2[cat]/max_values[cat] for cat in categories]
#         values_1 += values_1[:1]
#         values_2 += values_2[:1]
#         categories += categories[:1]

#         # Create radar chart
#         fig = go.Figure()

#     # Fighter 1 trace
#         fig.add_trace(go.Scatterpolar(
#             r=values_1,
#             theta=categories,
#             fill='toself',
#             name=fighter1_name,
#             fillcolor='rgba(255, 0, 0, 0.3)',  # Red with transparency
#             line=dict(color='red', width=3),
#             marker=dict(size=6)
#         ))

#         # Fighter 2 trace
#         fig.add_trace(go.Scatterpolar(
#             r=values_2,
#             theta=categories,
#             fill='toself',
#             name=fighter2_name,
#             fillcolor='rgba(0, 0, 255, 0.3)',  # Blue with transparency
#             line=dict(color='blue', width=3),
#             marker=dict(size=6)
#         ))

#         fig.update_layout(
#             title=dict(
#                 text=f"<b>Fighter Comparison: {fighter1_name} vs. {fighter2_name}</b>",
#                 font=dict(size=18, color="white"),
#                 x=0.5
#             ),
#             polar=dict(
#                 bgcolor="rgba(30, 30, 30, 1)",  
#                 radialaxis=dict(
#                     visible=True,
#                     range=[0, 1],
#                     gridcolor="white",
#                     gridwidth=1.5,
#                     showline=True,
#                     linewidth=1,
#                     linecolor="white"
#                 ),
#                 angularaxis=dict(
#                     showline=True,
#                     linewidth=1,
#                     linecolor="white",
#                     tickfont=dict(size=14, color="white")
#                 )
#             ),
#             paper_bgcolor="rgba(20, 20, 20, 1)",  
#             legend=dict(
#                 font=dict(size=14, color="white"),
#                 bgcolor="rgba(50, 50, 50, 0.5)"
#             )
#         )

#         return fig
#     @app.callback(
#         Output("head-to-head-content", "children"),
#         [Input("fighter1-dropdown", "value"),
#         Input("fighter2-dropdown", "value")]
#     )
#     def update_head_to_head(fighter1_name, fighter2_name):
#         if not fighter1_name or not fighter2_name:
#             return html.Div("Please select two fighters")
        
#         # Get all matches between the two fighters
#         head_to_head = results_df[
#             ((results_df['FIGHTER_1'] == fighter1_name) & (results_df['FIGHTER_2'] == fighter2_name)) |
#             ((results_df['FIGHTER_1'] == fighter2_name) & (results_df['FIGHTER_2'] == fighter1_name))
#         ].sort_values('DATE', ascending=False)  
        
#         if head_to_head.empty:
#             return html.Div([
#                 html.H4("No previous fights", className="text-center text-muted my-4"),
#                 html.P("These fighters have not faced each other.", className="text-center")
#             ])
        
#         fighter1_wins = head_to_head[head_to_head['fighter_1_result'] == 1].shape[0]
#         fighter2_wins = head_to_head[head_to_head['fighter_2_result'] == 1].shape[0]
        
#         return html.Div([
#             html.H4("HEAD-TO-HEAD RECORD", className="text-center mb-3"),
            
#             html.Div(className="d-flex justify-content-between mb-4", children=[
#                 html.Div(className="text-center", children=[
#                     html.H2(fighter1_wins, className="text-danger m-0"),
#                     html.P(fighter1_name, className="m-0")
#                 ]),
                
#                 html.Div(className="text-center", children=[
#                     html.H2("-", className="text-light m-0"),
#                 ]),
                
#                 html.Div(className="text-center", children=[
#                     html.H2(fighter2_wins, className="text-primary m-0"),
#                     html.P(fighter2_name, className="m-0")
#                 ]),
#             ]),
            
#             html.H5("PREVIOUS FIGHTS", className="text-center mb-2"),
            
#             html.Div([
#                 dbc.Table([
#                     html.Tbody([
#                         html.Tr([
#                             html.Td([
#                                 html.Div(row['EVENT']),
#                                 html.Small(row['DATE'], className="text-muted")
#                             ]),
#                             html.Td([
#                                 html.Div(row['FIGHTER_1'] if row['fighter_1_result'] == 1 else row['FIGHTER_2'], className="text-success" if row['fighter_1_result'] == 1 else "text-danger"),
#                                 html.Small(f"{row['method_label']} (R{row['ROUND']})")
#                             ])
#                         ]) for _, row in head_to_head.iterrows()
#                     ])
#                 ], borderless=True, className="mb-0")
#             ])
#         ])
        
        
#     @app.callback(
#         Output("fighter-1-overview", "children"),
#         Input("fighter1-dropdown", "value")
#     )
#     def update_fighter_1_profile(fighter_name):
#         fighter = fighters_df[fighters_df['Name'] == fighter_name].iloc[0]
#         wins = fighter['Wins']
#         losses = fighter['Losses']
#         draws = fighter['Draws']   
        
#         return html.Div([
#             html.Div([
#                 html.Img(src=f"/assets/minh_2.jpg", 
#                     style={'width': '150px', 'height': '150px', 'borderRadius': '10%'},
#                     className="mx-auto d-block mb-3"),
#                 html.H4(fighter['Name'], className="text-center mb-3"),
#                 html.H6(f"{fighter['Weight_Class']}", className="text-center text-muted mb-2"),
                
#                 html.Div(className="d-flex justify-content-center mb-3", children=[
#                     html.Div(className="text-center mx-2", children=[
#                         html.H4(wins, className="text-success m-0"),
#                         html.P("WINS", className="text-muted m-0")
#                     ]),
#                     html.Div(className="text-center mx-2", children=[
#                         html.H4(losses, className="text-danger m-0"),
#                         html.P("LOSSES", className="text-muted m-0")
#                     ]),
#                     html.Div(className="text-center mx-2", children=[
#                         html.H4(draws, className="text-warning m-0"),
#                         html.P("DRAWS", className="text-muted m-0")
#                     ]),
#                 ]),
                
#                 html.H5("FINISH RATE", className="text-center mb-1"),
#                 html.Div(className="d-flex justify-content-center", children=[
#                     html.Div(className="text-center mx-2", children=[
#                         html.H4(fighter['Knockouts'], className="text-danger m-0"),
#                         html.P("KO/TKO", className="text-muted m-0")
#                     ]),
#                     html.Div(className="text-center mx-2", children=[
#                         html.H4(fighter['Submissions'], className="text-primary m-0"),
#                         html.P("SUBMISSIONS", className="text-muted m-0")
#                     ]),
#                 ]),
#             ])
#         ])
        
#     @app.callback(
#         Output("fighter-2-overview", "children"),
#         Input("fighter2-dropdown", "value")
#     )
#     def update_fighter_2_profile(fighter_name):
#         fighter = fighters_df[fighters_df['Name'] == fighter_name].iloc[0]
#         wins = fighter['Wins']
#         losses = fighter['Losses']
#         draws = fighter['Draws']   
        
#         return html.Div([
#             html.Div([
#                 html.Img(src=f"/assets/minh_2.jpg", 
#                     style={'width': '150px', 'height': '150px', 'borderRadius': '10%'},
#                     className="mx-auto d-block mb-3"),
#                 html.H4(fighter['Name'], className="text-center mb-3"),
#                 html.H6(f"{fighter['Weight_Class']}", className="text-center text-muted mb-2"),
                
#                 html.Div(className="d-flex justify-content-center mb-3", children=[
#                     html.Div(className="text-center mx-2", children=[
#                         html.H4(wins, className="text-success m-0"),
#                         html.P("WINS", className="text-muted m-0")
#                     ]),
#                     html.Div(className="text-center mx-2", children=[
#                         html.H4(losses, className="text-danger m-0"),
#                         html.P("LOSSES", className="text-muted m-0")
#                     ]),
#                     html.Div(className="text-center mx-2", children=[
#                         html.H4(draws, className="text-warning m-0"),
#                         html.P("DRAWS", className="text-muted m-0")
#                     ]),
#                 ]),
                
#                 html.H5("FINISH RATE", className="text-center mb-1"),
#                 html.Div(className="d-flex justify-content-center", children=[
#                     html.Div(className="text-center mx-2", children=[
#                         html.H4(fighter['Knockouts'], className="text-danger m-0"),
#                         html.P("KO/TKO", className="text-muted m-0")
#                     ]),
#                     html.Div(className="text-center mx-2", children=[
#                         html.H4(fighter['Submissions'], className="text-primary m-0"),
#                         html.P("SUBMISSIONS", className="text-muted m-0")
#                     ]),
#                 ]),
#             ])
#         ])


# ####-------------------------- PREDICTIONS CALLBACKS---------------------------------------------------- ###
# ####-------------------------- PREDICTIONS CALLBACKS---------------------------------------------------- ###

#     # @app.callback(  
        