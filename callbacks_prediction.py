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
loaded_model = joblib.load('/home/duyle/Documents/VSC/Project_DAP391/best_model.pkl')


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
            
        # Validate input
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
            
        winner, confidence = predict_fight(fighter1_name, fighter2_name, fighters_df, results_df, loaded_model)
        
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



    @app.callback(
    [Output("model-type-info", "children"),
     Output("model-accuracy-info", "children")],
    [Input("predict-button", "n_clicks")]
)
    def update_model_info(n_clicks):
        if not model_package:
            return "Not available", "Not available"
        
        model_type = model_package.get('model_type', 'Unknown')
        
        if 'performance' in model_package and model_type in model_package['performance']:
            accuracy = f"{model_package['performance'][model_type]['accuracy']:.1%}"
        else:
            accuracy = "Not available"
        

        
        return model_type, accuracy
    
def predict_fight(fighter1_name, fighter2_name, fighters_df, results_df, model_package):
    try:
        # Get fighter data
        fighter1 = fighters_df[fighters_df['Name'] == fighter1_name]
        fighter2 = fighters_df[fighters_df['Name'] == fighter2_name]
        
        if fighter1.empty or fighter2.empty:
            print(f"Fighter data missing: {fighter1_name if fighter1.empty else ''} {fighter2_name if fighter2.empty else ''}")
            return fighter1_name, 0.5
            
        fighter1 = fighter1.iloc[0]
        fighter2 = fighter2.iloc[0]
        
        # Create features
        features = {}
        
        # Create matchup features
        matchup_features = create_matchup_features(fighter1, fighter2)
        print(f"Matchup features: {len(matchup_features)}")
        print(f"Names: {list(matchup_features.keys())}")
        
        # Create career features
        career_features = create_career_features(fighter1_name, fighter2_name)
        print(f"Career features: {len(career_features)}")
        print(f"Names: {list(career_features.keys())}")
        
        # Create style features
        style_features = create_style_matchup_features(fighter1, fighter2)
        print(f"Style features: {len(style_features)}")
        print(f"Names: {list(style_features.keys())}")
        
        # Combine all feature dictionaries
        features.update(matchup_features)
        features.update(career_features)
        features.update(style_features)
        
        # Check how many features we have
        print(f"Total unique features: {len(features)}")
        print(f"Final feature names: {list(features.keys())}")
        X = []        
        # Prepare data for model
        feature_values = list(features.values())
        feature_names = list(features.keys())
        print(X)
        X = np.array([feature_values])   
        print(X)     
        X = np.array(X)
        

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        

        prediction = loaded_model.predict(X_scaled)
        print(prediction)
        probabilities = loaded_model.predict_proba(X_scaled)[0]
        
        if prediction == 1:
            winner = fighter1_name
            confidence = probabilities[1]
        elif prediction == 4:
            winner='None'
            confidence=1
        else:
            winner = fighter2_name
            confidence = probabilities[0]
        
        
        return winner, confidence
        
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        return fighter1_name, 0.5

def create_matchup_features(fighter1, fighter2):
    features = {}
    numerical_features = [
        'Striking_Accuracy', 'Takedown_Accuracy', 'Sig_Str_Def', 'Takedown_Def','Takedown_Avg_Per Min',
        'Knockdown_Avg'
    ]
    
    for feature in numerical_features:
        if feature in fighter1 and feature in fighter2:
            features[f'{feature}_diff'] = fighter1[feature] - fighter2[feature]
    
    f1_total = fighter1['Wins'] + fighter1['Losses']
    f2_total = fighter2['Wins'] + fighter2['Losses']
    
    f1_win_rate = 0 if f1_total == 0 else fighter1['Wins'] / f1_total
    f2_win_rate = 0 if f2_total == 0 else fighter2['Wins'] / f2_total
    features['win_rate_diff'] = f1_win_rate - f2_win_rate
    
    try:
        debut1 = pd.to_datetime(fighter1['Octagon_Debut'])
        debut2 = pd.to_datetime(fighter2['Octagon_Debut'])
        features['days_debut'] = abs((debut1 - debut2).days)
    except:
        features['days_debut'] = 0  
    
    return features

def create_career_features(fighter1, fighter2):
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
    
    f1_experience = f1_career_wins + f1_career_losses + f1_career_draws
    f2_experience = f2_career_wins + f2_career_losses + f2_career_draws
    
    features['win_rate_diff'] = f1_career_win_rate - f2_career_win_rate
    features['experience_diff'] = f1_experience - f2_experience
    features['wins_diff'] = f1_career_wins - f2_career_wins
    features['losses_diff'] = f1_career_losses - f2_career_losses
    
    # Get fight history for both fighters
    f1_history = results_df[(results_df['FIGHTER_1'] == fighter1) | (results_df['FIGHTER_2'] == fighter1)]
    f2_history = results_df[(results_df['FIGHTER_1'] == fighter2) | (results_df['FIGHTER_2'] == fighter2)]
    
    f1_momentum = 0
    f2_momentum = 0
    
    # Process fighter 1 recent history
    if len(f1_history) >= 2:
        f1_history = f1_history.sort_values(by='DATE', ascending=False)
        recent_f1_fights = f1_history.head(2)
        
        f1_recent_wins = 0
        for _, fight in recent_f1_fights.iterrows():
            if (fight['FIGHTER_1'] == fighter1 and fight['fighter_1_result'] == 1) or \
               (fight['FIGHTER_2'] == fighter1 and fight['fighter_1_result'] == 0):
                f1_recent_wins += 1
        
        f1_recent_win_rate = f1_recent_wins / 2
        f1_momentum = f1_recent_win_rate - f1_career_win_rate
    
    # Process fighter 2 recent history
    if len(f2_history) >= 2:
        f2_history = f2_history.sort_values(by='DATE', ascending=False)
        recent_f2_fights = f2_history.head(2)
        
        f2_recent_wins = 0
        for _, fight in recent_f2_fights.iterrows():
            if (fight['FIGHTER_1'] == fighter2 and fight['fighter_1_result'] == 1) or \
               (fight['FIGHTER_2'] == fighter2 and fight['fighter_1_result'] == 0):
                f2_recent_wins += 1
        
        f2_recent_win_rate = f2_recent_wins / 2
        f2_momentum = f2_recent_win_rate - f2_career_win_rate
    
    features['momentum_diff'] = f1_momentum - f2_momentum
    
    return features

def create_style_matchup_features(fighter1, fighter2):
    features = {}
    
    fighter1_strike_bias = fighter1['Sig_Strikes_Per Min'] / (fighter1['Takedown_Avg_Per Min'] + 0.1)
    fighter2_strike_bias = fighter2['Sig_Strikes_Per Min'] / (fighter2['Takedown_Avg_Per Min'] + 0.1)
    
    features['style_clash'] = abs(fighter1_strike_bias - fighter2_strike_bias)
    
    features['ground_advantage'] = (fighter1['Sub_Avg_Per_Min'] - fighter2['Takedown_Def']) - \
                                 (fighter2['Sub_Avg_Per_Min'] - fighter1['Takedown_Def'])
    
    f1_head_pct = fighter1['Sig_Strikes_Head_Percent']
    f2_head_pct = fighter2['Sig_Strikes_Head_Percent']
    features['head_striking_diff'] = f1_head_pct - f2_head_pct
    
    f1_distance_pct = fighter1['Sig_Strikes_While_Standing_Percent']
    f2_distance_pct = fighter2['Sig_Strikes_While_Standing_Percent']
    features['distance_control_diff'] = f1_distance_pct - f2_distance_pct
    
    return features
