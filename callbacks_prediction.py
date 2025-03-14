from dash import dcc, html, Input, Output,State
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
import joblib
import os
import numpy as np
model_package = joblib.load('/home/duyle/Documents/VSC/Project_DAP391/ufc_model.joblib')
MODEL_LOADED = True
loaded_model = joblib.load('/home/duyle/Documents/VSC/Project_DAP391/best_model_enhanced.pkl')
scaler = joblib.load('/home/duyle/Documents/VSC/Project_DAP391/scaler_enhanced.pkl')
imputer = joblib.load('/home/duyle/Documents/VSC/Project_DAP391/imputer_enhanced.pkl')

fighters_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fighters_w_image_2.csv')
stats_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fight_stats_with_weghtclass_date_location.csv') 
results_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fight_results_with_locale_2.csv')
fighters_df['Name'] = fighters_df['Name'].str.strip().str.lower()
stats_df['ROUND'] = stats_df['ROUND'].str.replace('Round ','')
results_df['DATE'] = pd.to_datetime(results_df['DATE'])


def register_prediction_callbacks(app, fighters_df, results_df, stats_df):
    @app.callback(
        Output("fighter-1-overview-predict", "children"),
        Input("predict-fighter1-dropdown", "value")
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
        Output("fighter-2-overview-predict", "children"),
        Input("predict-fighter2-dropdown", "value")
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

    @app.callback(
        Output("prediction-output", "children"),
        [Input("predict-button", "n_clicks")],
        [State("predict-fighter1-dropdown", "value"),
        State("predict-fighter2-dropdown", "value")]
    )
    def update_prediction(n_clicks, fighter1_name, fighter2_name):
        # If button hasn't been clicked yet, show initial state
        if not n_clicks:
            return html.Div(
                html.P("Click the PREDICT WINNER button to see the fight prediction", 
                    className="text-center text-muted"),
                className="text-center p-4"
            )
            
        if not fighter1_name or not fighter2_name:
            return html.Div(
                html.P("Please select two fighters to compare", 
                    className="text-center text-danger"),
                className="text-center p-4"
            )
            
        if fighter1_name == fighter2_name:
            return html.Div(
                html.P("Please select different fighters", 
                    className="text-center text-danger"),
                className="text-center p-4"
            )
            
        winner, confidence = predict_fight_enhanced(fighter1_name=fighter1_name, fighter2_name=fighter2_name, fighters_df=fighters_df, results_df=results_df, model = loaded_model, scaler=scaler, imputer=imputer, stats_df=stats_df)
        
        if confidence > 0.67:
            confidence_color = "success"
            confidence_text = "High Confidence"
        elif confidence > 0.55:
            confidence_color = "warning"
            confidence_text = "Medium Confidence"
        else:
            confidence_color = "danger"
            confidence_text = "Low Confidence"
        

        return html.Div([
            html.H4("Prediction Result", className="text-center mb-3"),
            
            dbc.Row([
                dbc.Card(
                    dbc.CardBody([
                        html.H4("PREDICTED WINNER", className="text-center text-muted mb-3"),
                        html.H2(winner, className="text-center text-success"),
                    ]),
                ),
            ]),
            dbc.Row([
                dbc.Card(
                    dbc.CardBody([
                        html.H4("MODEL CONFIDENCE", className="text-center text-muted mb-3"),
                        html.Div([
                            html.H2(f"{confidence:.1%}", className=f"text-{confidence_color}"),
                            html.P(confidence_text, className=f"text-{confidence_color}")
                        ], className="text-center")
                    ]),
                ),
            ]),
            
        ])

def create_matchup_features(fighter1, fighter2):
    """Create symmetric matchup features that don't depend on fighter order."""
    features = {}
    numerical_features = [
        'Striking_Accuracy', 'Takedown_Accuracy', 'Sig_Str_Def', 'Takedown_Def',
        'Takedown_Avg_Per Min', 'Knockdown_Avg'
    ]
    
    for feature in numerical_features:
        if feature in fighter1 and feature in fighter2:
            features[f'{feature}_abs_diff'] = abs(fighter1[feature] - fighter2[feature])
            
            if fighter1[feature] > fighter2[feature]:
                features[f'{feature}_better'] = 1
            elif fighter1[feature] < fighter2[feature]:
                features[f'{feature}_better'] = -1
            else:
                features[f'{feature}_better'] = 0
    
    # Calculate win rates
    f1_total = fighter1['Wins'] + fighter1['Losses']
    f2_total = fighter2['Wins'] + fighter2['Losses']
    
    f1_win_rate = 0 if f1_total == 0 else fighter1['Wins'] / f1_total
    f2_win_rate = 0 if f2_total == 0 else fighter2['Wins'] / f2_total
    
    # Symmetric win rate features
    features['win_rate_abs_diff'] = abs(f1_win_rate - f2_win_rate)
    
    if f1_win_rate > f2_win_rate:
        features['win_rate_better'] = 1
    elif f1_win_rate < f2_win_rate:
        features['win_rate_better'] = -1
    else:
        features['win_rate_better'] = 0
    
    # Experience gap 
    debut1 = pd.to_datetime(fighter1['Octagon_Debut'])
    debut2 = pd.to_datetime(fighter2['Octagon_Debut'])
    features['days_debut'] = abs((debut1 - debut2).days)
    
    return features

def create_recency_weighted_features(fighter_name, results_df, decay_factor=0.9):
    """Create features that weight recent fights more heavily."""
    
    fighter_history = results_df[(results_df['FIGHTER_1'] == fighter_name) | 
                                (results_df['FIGHTER_2'] == fighter_name)]
    
    if fighter_history.empty:
        return {
            'recent_win_rate': 0,
            'decay_weighted_win_rate': 0,
            'form_momentum': 0
        }
    
    # Sort by date 
    fighter_history = fighter_history.sort_values(by='DATE', ascending=False)
    
    # Get wins/losses and calculate weighted stats
    wins = []
    for idx, fight in fighter_history.iterrows():
        if (fight['FIGHTER_1'] == fighter_name and fight['fighter_1_result'] == 1) or \
           (fight['FIGHTER_2'] == fighter_name and fight['fighter_2_result'] == 1):
            wins.append(1)
        else:
            wins.append(0)
    
    # weighted win rate
    weights = [decay_factor**i for i in range(len(wins))]
    weighted_wins = sum(w*win for w, win in zip(weights, wins))
    weighted_total = sum(weights)
    decay_weighted_win_rate = weighted_wins / weighted_total if weighted_total > 0 else 0
    
    # Recent win rate 
    recent_win_rate = sum(wins[:3]) / min(3, len(wins))
    
    # difference between recent and overall win rates
    all_time_win_rate = sum(wins) / len(wins)
    form_momentum = recent_win_rate - all_time_win_rate
    
    return {
        'recent_win_rate': recent_win_rate,
        'decay_weighted_win_rate': decay_weighted_win_rate,
        'form_momentum': form_momentum
    }

def create_career_features(fighter1, fighter2, fighters_df, results_df):
    features = {}
    
    fighter1_info = fighters_df[fighters_df['Name'] == fighter1]
    fighter2_info = fighters_df[fighters_df['Name'] == fighter2]
    
    if fighter1_info.empty or fighter2_info.empty:
        if fighter1_info.empty:
            print(f"Fighter {fighter1} not found")
        if fighter2_info.empty:
            print(f"Fighter {fighter2} not found")
        return features
    
    f1_career_wins = fighter1_info['Wins'].iloc[0]
    f1_career_losses = fighter1_info['Losses'].iloc[0]
    f1_career_draws = fighter1_info['Draws'].iloc[0]
    
    f2_career_wins = fighter2_info['Wins'].iloc[0]
    f2_career_losses = fighter2_info['Losses'].iloc[0]
    f2_career_draws = fighter2_info['Draws'].iloc[0]
    
    f1_total_career_fights = f1_career_wins + f1_career_losses
    f1_career_win_rate = f1_career_wins / f1_total_career_fights if f1_total_career_fights > 0 else 0
    
    f2_total_career_fights = f2_career_wins + f2_career_losses
    f2_career_win_rate = f2_career_wins / f2_total_career_fights if f2_total_career_fights > 0 else 0
    
    # Experience differences 
    f1_experience = f1_career_wins + f1_career_losses + f1_career_draws
    f2_experience = f2_career_wins + f2_career_losses + f2_career_draws
    
    features['experience_abs_diff'] = abs(f1_experience - f2_experience)
    
    if f1_experience > f2_experience:
        features['more_experienced'] = 1
    elif f1_experience < f2_experience:
        features['more_experienced'] = -1
    else:
        features['more_experienced'] = 0
    
    #weighted features
    f1_recency = create_recency_weighted_features(fighter1, results_df)
    f2_recency = create_recency_weighted_features(fighter2, results_df)
    
    # Compare recency-weighted win rates 
    features['recent_win_rate_diff'] = abs(f1_recency['recent_win_rate'] - f2_recency['recent_win_rate'])
    
    if f1_recency['recent_win_rate'] > f2_recency['recent_win_rate']:
        features['better_recent_form'] = 1
    elif f1_recency['recent_win_rate'] < f2_recency['recent_win_rate']:
        features['better_recent_form'] = -1
    else:
        features['better_recent_form'] = 0
    
    # Momentum comparison 
    features['momentum_abs_diff'] = abs(f1_recency['form_momentum'] - f2_recency['form_momentum'])
    
    if f1_recency['form_momentum'] > f2_recency['form_momentum']:
        features['better_momentum'] = 1
    elif f1_recency['form_momentum'] < f2_recency['form_momentum']:
        features['better_momentum'] = -1
    else:
        features['better_momentum'] = 0
    
    return features

def create_style_matchup_features(fighter1, fighter2):
    features = {}
    
    # Calculate strike bias
    fighter1_strike_bias = fighter1['Sig_Strikes_Per Min'] / (fighter1['Takedown_Avg_Per Min'] + 0.1)
    fighter2_strike_bias = fighter2['Sig_Strikes_Per Min'] / (fighter2['Takedown_Avg_Per Min'] + 0.1)
    
    # Style clash is already symmetric 
    features['style_clash'] = abs(fighter1_strike_bias - fighter2_strike_bias)
    

    # Striking effectiveness against defense
    f1_strike_effectiveness = fighter1['Striking_Accuracy'] * (1 - fighter2['Sig_Str_Def'])
    f2_strike_effectiveness = fighter2['Striking_Accuracy'] * (1 - fighter1['Sig_Str_Def'])
    
    features['striking_effectiveness_diff'] = abs(f1_strike_effectiveness - f2_strike_effectiveness)
    
    if f1_strike_effectiveness > f2_strike_effectiveness:
        features['better_striker'] = 1
    elif f1_strike_effectiveness < f2_strike_effectiveness:
        features['better_striker'] = -1
    else:
        features['better_striker'] = 0
    
    # Grappling effectiveness
    f1_takedown_effectiveness = fighter1['Takedown_Accuracy'] * (1 - fighter2['Takedown_Def'])
    f2_takedown_effectiveness = fighter2['Takedown_Accuracy'] * (1 - fighter1['Takedown_Def'])
    
    features['takedown_effectiveness_diff'] = abs(f1_takedown_effectiveness - f2_takedown_effectiveness)
    
    if f1_takedown_effectiveness > f2_takedown_effectiveness:
        features['better_grappler'] = 1
    elif f1_takedown_effectiveness < f2_takedown_effectiveness:
        features['better_grappler'] = -1
    else:
        features['better_grappler'] = 0
    
    return features

def create_age_career_interaction(fighter1_name, fighter2_name, fighters_df):    
    def get_age(fighter_name):
        fighter_data = fighters_df[fighters_df['Name'] == fighter_name]
        
        if fighter_data.empty or 'Age' not in fighter_data.columns:
            debut = fighter_data['Octagon_Debut'].iloc[0]
            years_since_debut = (pd.to_datetime('today') - pd.to_datetime(debut)).days / 365.25
            return 24 + years_since_debut  
        
        return fighter_data['Age'].iloc[0]
    
    def calculate_career_metrics(fighter_name):
        fighter_data = fighters_df[fighters_df['Name'] == fighter_name]
        
        if fighter_data.empty:
            return {
                'age': 30,
                'pro_fights': 10,
                'ufc_fights': 5,
                'fighter_age': 'prime',
                'age_per_fight': 3
            }
        
        # Get age (estimate from debut if not explicitly available)

        debut = fighter_data['Octagon_Debut'].iloc[0]
        years_since_debut = (pd.to_datetime('today') - pd.to_datetime(debut)).days / 365.25
        age = 2 + years_since_debut
        
        # Get fight counts
        wins = fighter_data['Wins'].iloc[0] if 'Wins' in fighter_data.columns else 0
        losses = fighter_data['Losses'].iloc[0] if 'Losses' in fighter_data.columns else 0
        draws = fighter_data['Draws'].iloc[0] if 'Draws' in fighter_data.columns else 0
        
        pro_fights = wins + losses + draws
        
        # Estimate UFC fights
        years_in_ufc = (pd.to_datetime('today') - pd.to_datetime(debut)).days / 365.25
        ufc_fights = min(pro_fights, round(years_in_ufc * 2.5))  
        
        # Determine fight age category
        if age < 27:
            fighter_age = 'prospect'
        elif age < 34:
            fighter_age = 'prime'
        else:
            fighter_age = 'veteran'
        
        # Calculate age normalized by number of fights 
        age_per_fight = age / pro_fights if pro_fights > 0 else age
        
        return {
            'age': age,
            'pro_fights': pro_fights,
            'ufc_fights': ufc_fights,
            'fighter_age': fighter_age,
            'age_per_fight': age_per_fight
        }
    
    # Get metrics for both fighters
    f1_metrics = calculate_career_metrics(fighter1_name)
    f2_metrics = calculate_career_metrics(fighter2_name)
    
    # Calculate comparative features
    features = {}
    
    # Age difference
    age_diff = f1_metrics['age'] - f2_metrics['age']
    features['age_diff'] = age_diff
    
    # Experience difference
    exp_diff = f1_metrics['pro_fights'] - f2_metrics['pro_fights']
    features['experience_diff'] = exp_diff
    
    # UFC experience difference
    ufc_exp_diff = f1_metrics['ufc_fights'] - f2_metrics['ufc_fights']
    features['ufc_experience_diff'] = ufc_exp_diff
    
    # Age normalized by fight experience
    apf_diff = f1_metrics['age_per_fight'] - f2_metrics['age_per_fight']
    features['age_per_fight_diff'] = apf_diff
    
    # Career stage advantage (from age perspective)
    career_stage_map = {'prospect': 1, 'prime': 2, 'veteran': 0}
    f1_stage = career_stage_map[f1_metrics['fighter_age']]
    f2_stage = career_stage_map[f2_metrics['fighter_age']]
    
    if f1_stage > f2_stage:
        features['career_stage_advantage'] = 1
    elif f1_stage < f2_stage:
        features['career_stage_advantage'] = -1
    else:
        features['career_stage_advantage'] = 0
    
    return features

def create_layoff_features(fighter1_name, fighter2_name, current_date, results_df):
    
    def get_fighter_layoff(fighter_name, current_date):
        fighter_bouts = results_df[(results_df['FIGHTER_1'] == fighter_name) | 
                                  (results_df['FIGHTER_2'] == fighter_name)]
        
        if fighter_bouts.empty:
            return {
                'days_since_last_fight': 365,  # Default to 1 year
                'layoff_impact': 0,
                'interval_deviation': 0
            }
        
        if not isinstance(current_date, pd.Timestamp):
            current_date = pd.to_datetime(current_date)
        
        # Sort by date
        fighter_bouts = fighter_bouts.sort_values(by='DATE', ascending=False)
        
        # Calculate days since last fight
        last_fight_date = fighter_bouts.iloc[0]['DATE']
        days_since_last_fight = (current_date - last_fight_date).days
        
        # Calculate average interval between fights
        if len(fighter_bouts) > 1:
            intervals = []
            for i in range(len(fighter_bouts) - 1):
                interval = (fighter_bouts.iloc[i]['DATE'] - fighter_bouts.iloc[i+1]['DATE']).days
                intervals.append(interval)
            
            typical_interval = np.median(intervals) if intervals else 120 
            interval_deviation = days_since_last_fight / typical_interval if typical_interval > 0 else 1
        else:
            interval_deviation = 1
        
        # If layoff is extremely long
        is_unusual_layoff = 1 if interval_deviation > 2 else 0
        
        # Estimate layoff impact 
        if interval_deviation < 0.5: 
            layoff_impact = -0.5
        elif interval_deviation > 2:  
            layoff_impact = -0.3
        else:  
            layoff_impact = 0.2
        
        return {
            'days_since_last_fight': days_since_last_fight,
            'layoff_impact': layoff_impact,
            'interval_deviation': interval_deviation,
            'is_unusual_layoff': is_unusual_layoff
        }
    
    # Get layoff metrics for both fighters
    f1_layoff = get_fighter_layoff(fighter1_name, current_date)
    f2_layoff = get_fighter_layoff(fighter2_name, current_date)
    
    # Create comparative features
    features = {}
    
    # Calculate layoff difference
    layoff_diff = f1_layoff['days_since_last_fight'] - f2_layoff['days_since_last_fight']
    features['layoff_diff'] = layoff_diff
    
    # Determine which fighter might have ring rust advantage
    if abs(layoff_diff) > 60: 
        if layoff_diff > 0: 
            features['ring_rust_advantage'] = -1  # Disadvantage for fighter 1
        else:  
            features['ring_rust_advantage'] = 1  # Advantage for fighter 1
    else:
        features['ring_rust_advantage'] = 0  
    # Compare layoff impacts 
    impact_diff = f1_layoff['layoff_impact'] - f2_layoff['layoff_impact']
    
    if impact_diff > 0.2:
        features['layoff_timing_advantage'] = 1 
    elif impact_diff < -0.2:
        features['layoff_timing_advantage'] = -1 
    else:
        features['layoff_timing_advantage'] = 0 
    
    return features

def create_round_progression_features(fighter1_name, fighter2_name, stats_df):
    
    def get_fighter_round_stats(fighter_name):
        fighter_rounds = stats_df[(stats_df['FIGHTER'] == fighter_name)]
        
        if fighter_rounds.empty:
            return {
                'round_decay': 0,
                'third_round_surge': 0
            }
        
        # Group stats by round
        round_grouped = fighter_rounds.groupby('ROUND')
        
        # Calculate average stats per round
        round_avg_stats = {}
        
        for round_num, group in round_grouped:
            # Calculate average strike stats for the round
            round_avg_stats[round_num] = {
                'sig_str_landed': group['sig_str_land'].mean(),
                'sig_str_attempted': group['sig_str_attempt'].mean(),
                'accuracy': group['SIG.STR. %'].mean() if 'SIG.STR. %' in group.columns else 0,
                'control_time': group['CTRL'].mean() if 'CTRL' in group.columns else 0
            }
        
        # Calculate round progression features
        # Round-to-round striking output decay/improvement
        if 1 in round_avg_stats and 3 in round_avg_stats:
            round1_output = round_avg_stats[1]['sig_str_landed']
            round3_output = round_avg_stats[3]['sig_str_landed']
            
            round_decay = (round3_output - round1_output) / round1_output if round1_output > 0 else 0
        else:
            round_decay = 0
        
        # Third round surge (comparing to round 2)
        if 2 in round_avg_stats and 3 in round_avg_stats:
            round2_output = round_avg_stats[2]['sig_str_landed']
            round3_output = round_avg_stats[3]['sig_str_landed']
            
            third_round_surge = (round3_output - round2_output) / round2_output if round2_output > 0 else 0
        else:
            third_round_surge = 0
        
        return {
            'round_decay': round_decay,
            'third_round_surge': third_round_surge
        }
    
    # Get round progression stats 
    f1_round_progression = get_fighter_round_stats(fighter1_name)
    f2_round_progression = get_fighter_round_stats(fighter2_name)
    
    # Create comparative features
    features = {}
    
    # Compare round decay rates
    decay_diff = f1_round_progression['round_decay'] - f2_round_progression['round_decay']
    
    if decay_diff > 0.1:  
        features['cardio_advantage'] = 1
    elif decay_diff < -0.1:  
        features['cardio_advantage'] = -1
    else:
        features['cardio_advantage'] = 0
    
    # Compare third round surge 
    surge_diff = f1_round_progression['third_round_surge'] - f2_round_progression['third_round_surge']
    
    if surge_diff > 0.1: 
        features['late_round_advantage'] = 1
    elif surge_diff < -0.1:  
        features['late_round_advantage'] = -1
    else:
        features['late_round_advantage'] = 0
    
    return features

def create_enhanced_fight_features(fighter1_name, fighter2_name, fighters_df, results_df, stats_df, current_date=None):
    
    if current_date is None:
        current_date = pd.to_datetime('today')
    
    # Get fighter data
    f1_data = fighters_df[fighters_df['Name'] == fighter1_name]
    f2_data = fighters_df[fighters_df['Name'] == fighter2_name]
    
    if f1_data.empty or f2_data.empty:
        print(f"Fighter data missing: {fighter1_name if f1_data.empty else ''} {fighter2_name if f2_data.empty else ''}")
        return None
    
    fighter1 = f1_data.iloc[0]
    fighter2 = f2_data.iloc[0]
    
    features = {}
    
    features.update(create_matchup_features(fighter1, fighter2))
    features.update(create_career_features(fighter1_name, fighter2_name, fighters_df, results_df))
    features.update(create_style_matchup_features(fighter1, fighter2))
    
    features.update(create_age_career_interaction(fighter1_name, fighter2_name, fighters_df))
    
    features.update(create_layoff_features(fighter1_name, fighter2_name, current_date, results_df))
    
    features.update(create_round_progression_features(fighter1_name, fighter2_name, stats_df))
    
    # features['fighter1_position'] = 1
    
    return features

def predict_fight_enhanced(fighter1_name, fighter2_name, model, scaler, imputer, fighters_df, results_df, stats_df, current_date=None):
    
    # Check if fighters exist in the dataset
    fighter1_exists = not fighters_df[fighters_df['Name'] == fighter1_name].empty
    fighter2_exists = not fighters_df[fighters_df['Name'] == fighter2_name].empty
    
    if not fighter1_exists or not fighter2_exists:
        missing_fighters = []
        if not fighter1_exists:
            missing_fighters.append(fighter1_name)
        if not fighter2_exists:
            missing_fighters.append(fighter2_name)
            
        print(f"Missing fighter data for: {', '.join(missing_fighters)}")
        
        # Fallback prediction based on record if available
        if fighter1_exists and not fighter2_exists:
            return fighter1_name, 0.6, {"reason": "opponent data missing"}
        elif fighter2_exists and not fighter1_exists:
            return fighter2_name, 0.6, {"reason": "opponent data missing"}
        else:
            return "Unknown", 0.5, {"reason": "both fighters missing"}
    
    if current_date is None:
        current_date = pd.to_datetime('today')
    
    try:
        features = create_enhanced_fight_features(
            fighter1_name, 
            fighter2_name,
            fighters_df,
            results_df,
            stats_df,
            current_date
        )
        
        if features is None:
            return 'Unknown', 0.5, {"reason": "feature extraction failed"}
        
        feature_values = list(features.values())
        X = np.array([feature_values])
        
        if np.isnan(X).any():
            X = imputer.transform(X)
        
        X_scaled = scaler.transform(X)
        
        prediction = model.predict(X_scaled)
        probabilities = model.predict_proba(X_scaled)[0]
        
        if prediction == 1:
            winner = fighter1_name
            confidence = probabilities[1]
        elif prediction == 2:
            winner = 'Draw'
            confidence = probabilities[2] if len(probabilities) > 2 else 0.5
        else:
            winner = fighter2_name
            confidence = probabilities[0]
        
        # key_features = {}
        # if hasattr(model, 'feature_importances_'):
        #     # For tree-based models
        #     importances = model.feature_importances_
        #     feature_names = list(features.keys())
            
        #     # Get top 5 most important features for this prediction
        #     top_indices = np.argsort(importances)[-5:]
        #     for idx in top_indices:
        #         if idx < len(feature_names):
        #             key_features[feature_names[idx]] = features[feature_names[idx]]
        
        return winner, confidence
        
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        return 'Error', 0.5, {"error": str(e)}

