# callbacks.py
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
from dash import dcc, html
from plotly.subplots import make_subplots
from dash import dcc, html, callback, Input, Output, ctx
import dash_bootstrap_components as dbc

def register_callbacks(app, fighters_df, results_df, stats_df):
    # Import all callback modules
    from callbacks_fighters import register_fighter_callbacks
    from callbacks_matches import register_match_callbacks
    from callbacks_comparison import register_comparison_callbacks
    from callbacks_prediction import register_prediction_callbacks
    from layout_dash import create_landing_page, create_fighters_tab, create_matches_tab, create_comparison_tab, matches_predictions_tab
    
    # Navigation callbacks
    @app.callback(
        Output("page-content", "children"),
        [Input("home-link", "n_clicks"),
         Input("fighters-link", "n_clicks"),
         Input("matches-link", "n_clicks"),
         Input('comparison-link', 'n_clicks'),
         Input('prediction-link', 'n_clicks')]
    )
    def toggle_active_tab(home_clicks, fighters_clicks, matches_clicks, comparison_clicks, predict_clicks):
        try:
            if ctx.triggered:
                trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
                if trigger_id == 'home-link':
                    return create_landing_page()
                elif trigger_id == 'fighters-link':
                    return create_fighters_tab(fighters_df=fighters_df, results_df=results_df, stats_df=stats_df)
                elif trigger_id == 'matches-link':
                    return create_matches_tab(fighters_df=fighters_df, results_df=results_df, stats_df=stats_df)
                elif trigger_id == 'comparison-link':
                    return create_comparison_tab(fighters_df=fighters_df, results_df=results_df, stats_df=stats_df)
                elif trigger_id == 'prediction-link':
                    return matches_predictions_tab(fighters_df=fighters_df, results_df=results_df, stats_df=stats_df)
            return create_landing_page()  # Default to landing page
        except Exception as e:
            print(f"Error in toggle_active_tab: {e}")
            return create_landing_page()  
    
    @app.callback(
        Output('active-tab', 'data'),
        [Input("home-link", "n_clicks"),
         Input("fighters-link", "n_clicks"),
         Input("matches-link", "n_clicks"),
         Input('comparison-link', 'n_clicks'),
         Input('prediction-link', 'n_clicks')]
    )
    def store_active_tab(home_clicks, fighters_clicks, matches_clicks, comparison_clicks, predict_clicks):
        if ctx.triggered:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if trigger_id == 'home-link':
                return 'home'
            elif trigger_id == 'fighters-link':
                return 'fighters'
            elif trigger_id == 'matches-link':
                return 'matches'
            elif trigger_id == 'comparison-link':
                return 'comparison'
            elif trigger_id == 'prediction-link':
                return 'prediction'
        return 'home'  # Default value
    
    # Register all other callbacks
    register_fighter_callbacks(app, fighters_df, results_df, stats_df)
    register_match_callbacks(app, fighters_df, results_df, stats_df)
    register_comparison_callbacks(app, fighters_df, results_df, stats_df)
    register_prediction_callbacks(app, fighters_df, results_df, stats_df)
