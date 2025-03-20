

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier, 
    GradientBoostingClassifier, 
    AdaBoostClassifier,
    ExtraTreesClassifier, 
    VotingClassifier, 
    StackingClassifier
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from xgboost import XGBClassifier
import lightgbm as lgb

# Create model directory structure if it doesn't exist
for dir_path in ['models/individual', 'models/ensembles', 'models/preprocessing']:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


fighters_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fighters_w_image_2.csv')
stats_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fight_stats_with_weghtclass_date_location.csv')
results_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fight_results_with_locale_2.csv')
fighters_df['Name'] = fighters_df['Name'].str.strip().str.lower()
stats_df['ROUND'] = stats_df['ROUND'].str.replace('Round ','')
results_df['DATE'] = pd.to_datetime(results_df['DATE'])


if 'fighter_1_result' in results_df.columns:
    results_df['fighter_1_result'] = results_df['fighter_1_result'].replace(4, 2)

if 'fighter_2_result' in results_df.columns:
    results_df['fighter_2_result'] = results_df['fighter_2_result'].replace(4, 2)


results_df['fighter_2_result'].unique()




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


def create_round_momentum_features(fighter1_name, fighter2_name, stats_df, results_df, current_date=None):
    """Create features that capture a fighter's round-by-round performance trends."""
    
    if current_date is None:
        current_date = pd.to_datetime('today')
    
    def get_fighter_round_momentum(fighter_name, historical_date):
        # Get all fights before the prediction date
        historical_fights = results_df[results_df['DATE'] < historical_date]
        fighter_stats = stats_df[
            (stats_df['FIGHTER'] == fighter_name) & 
            (stats_df['DATE'].astype(str).isin(historical_fights['DATE'].astype(str)))
        ]
        
        if fighter_stats.empty:
            return {
                'avg_momentum_score': 0,
                'early_round_effectiveness': 0,
                'late_round_effectiveness': 0,
                'consistency_score': 0
            }
        
        # Group by event and calculate round-by-round changes
        momentum_scores = []
        early_round_scores = []
        late_round_scores = []
        consistency_scores = []
        
        for event in fighter_stats['EVENT'].unique():
            fight_stats = fighter_stats[fighter_stats['EVENT'] == event].sort_values('ROUND')
            
            if len(fight_stats) > 1:
                # Calculate round-by-round striking effectiveness changes
                effectiveness = fight_stats['SIG.STR. %'].astype(float)
                round_changes = effectiveness.diff().dropna()
                
                # Momentum score: positive indicates improvement across rounds
                momentum_scores.append(round_changes.mean())
                
                # Early vs Late effectiveness
                early_round_scores.append(effectiveness.iloc[0])
                late_round_scores.append(effectiveness.iloc[-1])
                
                # Consistency: lower std dev means more consistent performance
                consistency_scores.append(effectiveness.std())
        
        if momentum_scores:
            # Weight recent fights more heavily
            weights = np.exp(-0.1 * np.arange(len(momentum_scores)))
            weights = weights / weights.sum()
            
            return {
                'avg_momentum_score': np.average(momentum_scores, weights=weights),
                'early_round_effectiveness': np.average(early_round_scores, weights=weights),
                'late_round_effectiveness': np.average(late_round_scores, weights=weights),
                'consistency_score': np.average(consistency_scores, weights=weights)
            }
        else:
            return {
                'avg_momentum_score': 0,
                'early_round_effectiveness': 0,
                'late_round_effectiveness': 0,
                'consistency_score': 0
            }
    
    # Get momentum stats for both fighters
    f1_momentum = get_fighter_round_momentum(fighter1_name, current_date)
    f2_momentum = get_fighter_round_momentum(fighter2_name, current_date)
    
    # Create comparative features
    features = {}
    
    # Compare momentum trends
    momentum_diff = f1_momentum['avg_momentum_score'] - f2_momentum['avg_momentum_score']
    features['round_momentum_advantage'] = np.sign(momentum_diff)
    features['round_momentum_magnitude'] = abs(momentum_diff)
    
    # Compare round effectiveness
    early_diff = f1_momentum['early_round_effectiveness'] - f2_momentum['early_round_effectiveness']
    late_diff = f1_momentum['late_round_effectiveness'] - f2_momentum['late_round_effectiveness']
    
    features['early_round_advantage'] = np.sign(early_diff)
    features['late_round_advantage'] = np.sign(late_diff)
    
    # Compare consistency
    consistency_diff = f1_momentum['consistency_score'] - f2_momentum['consistency_score']
    features['consistency_advantage'] = np.sign(-consistency_diff)  # Lower std dev is better
    
    # Calculate round progression patterns
    f1_progression = f1_momentum['late_round_effectiveness'] - f1_momentum['early_round_effectiveness']
    f2_progression = f2_momentum['late_round_effectiveness'] - f2_momentum['early_round_effectiveness']
    
    features['round_progression_diff'] = f1_progression - f2_progression
    
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
    
    # Get historical fight performance before current date
    historical_stats = stats_df[stats_df['DATE'].astype(str).isin(results_df[results_df['DATE'] < current_date]['DATE'].astype(str))]
    
    features.update(create_round_momentum_features(fighter1_name, fighter2_name, historical_stats, results_df, current_date))
    features.update(create_round_progression_features(fighter1_name, fighter2_name, historical_stats))
    
    # features['fighter1_position'] = 1
    
    return features



def prepare_enhanced_training_data(results_df, fighters_df, stats_df):
    X_features = []
    y_outcomes = []
    valid_indices = []  # Track which original indices are kept
    skipped_fights = []
    
    for idx, fight in results_df.iterrows():
        fighter1_name = fight['FIGHTER_1']
        fighter2_name = fight['FIGHTER_2']
        
        # Check if both fighters exist
        fighter1_exists = not fighters_df[fighters_df['Name'] == fighter1_name].empty
        fighter2_exists = not fighters_df[fighters_df['Name'] == fighter2_name].empty
        
        if not fighter1_exists or not fighter2_exists:
            if not fighter1_exists:
                print(f"Fighter {fighter1_name} not found in dataset")
            if not fighter2_exists:
                print(f"Fighter {fighter2_name} not found in dataset")
            skipped_fights.append((fighter1_name, fighter2_name))
            continue
            
        # Use the fight date for time-sensitive features
        fight_date = fight['DATE']
        
        # Extract features
        try:
            features = create_enhanced_fight_features(
                fighter1_name, 
                fighter2_name, 
                fighters_df, 
                results_df[results_df['DATE'] < fight_date], 
                stats_df,
                fight_date
            )
            
            if features is not None:
                if fight['fighter_1_result'] == 1:
                    outcome = 1  
                elif fight['fighter_1_result'] == 2:
                    outcome = 2  
                else:
                    outcome = 0 
                
                X_features.append(list(features.values()))
                y_outcomes.append(outcome)
                valid_indices.append(idx) 
            else:
                skipped_fights.append((fighter1_name, fighter2_name))
        except Exception as e:
            print(f"Error processing {fighter1_name} vs {fighter2_name}: {str(e)}")
            skipped_fights.append((fighter1_name, fighter2_name))
    
    if skipped_fights:
        print(f"Skipped {len(skipped_fights)} fights due to missing data or errors")
        if len(skipped_fights) < 10:  
            print("Examples:", skipped_fights[:5])
    
    if len(X_features) == 0:
        raise ValueError("No valid fight data was found to prepare for training")
    
 
    
    X = np.array(X_features)
    y = np.array(y_outcomes)
    
    imputer = SimpleImputer(strategy='mean')
    X = imputer.fit_transform(X)
    
    return X, y,  imputer, valid_indices



def create_time_based_cv_splits(results_df, valid_indices, n_splits=5):
    
    valid_results = results_df.loc[valid_indices].copy()
    #sort
    valid_results = valid_results.sort_values(by='DATE')
    
    unique_dates = valid_results['DATE'].unique()
    
    # Create date splits
    date_splits = np.array_split(unique_dates, n_splits)
    
    # Create train/test indices for each split
    splits = []
    for i in range(1, len(date_splits)):
        train_dates = np.concatenate(date_splits[:i])
        
        # Current split dates are testing
        test_dates = date_splits[i]
        
        # Get row indices in valid_results 
        train_idx = valid_results[valid_results['DATE'].isin(train_dates)].index.tolist()
        test_idx = valid_results[valid_results['DATE'].isin(test_dates)].index.tolist()
        
        # Map indices to positions in  X, y arrays
        train_positions = [valid_indices.index(idx) for idx in train_idx]
        test_positions = [valid_indices.index(idx) for idx in test_idx]
        
        splits.append((train_positions, test_positions))
    
    return splits



def train_enhanced_model(X, y, cv_splits=None):
    
    if cv_splits is None:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        cv_method = 5  
    else:
        X_train, y_train = X, y
        X_test, y_test = X, y  
        cv_method = cv_splits
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Base models
    models = {
        'Logistic Regression': LogisticRegression(max_iter=2000, solver='liblinear', random_state=69),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=56),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=77, random_state=32),
        'SVM': SVC(probability=True, kernel='rbf', C=1, random_state=42),
        'KNN': KNeighborsClassifier(n_neighbors=11),
        'XGBoost': XGBClassifier(random_state=46),
        'AdaBoost': AdaBoostClassifier(n_estimators=89, random_state=78),
        'LightGBM': lgb.LGBMClassifier(random_state=56),
        'Extra Trees': ExtraTreesClassifier(n_estimators=100, random_state=42),
    }
    
    # Train and evaluate base models
    results = {}
    trained_models = {}
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        model.fit(X_train_scaled, y_train)
        trained_models[name] = model
        
        cv_scores = cross_val_score(model, X, y, cv=cv_method)
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()
        
        print(f"{name} CV performance: {cv_mean:.3f} ± {cv_std:.3f}")
        
        results[name] = {
            'model': model,
            'cv_mean': cv_mean,
            'cv_std': cv_std
        }
        
        # Save individual model
        joblib.dump(model, f"models/individual/{name.lower().replace(' ', '_')}.pkl")
    
    # Create and train ensemble models
    print("\nTraining ensemble models...")
    
    # Voting Classifier (Hard)
    voting_hard = VotingClassifier(
        estimators=[(name, model) for name, model in trained_models.items()],
        voting='hard'
    )
    voting_hard.fit(X_train_scaled, y_train)
    
    # Voting Classifier (Soft)
    voting_soft = VotingClassifier(
        estimators=[(name, model) for name, model in trained_models.items()],
        voting='soft'
    )
    voting_soft.fit(X_train_scaled, y_train)
    
    # Stacking with LogisticRegression meta-learner
    stacking_lr = StackingClassifier(
        estimators=[(name, model) for name, model in trained_models.items()],
        final_estimator=LogisticRegression(max_iter=2000),
        cv=5
    )
    stacking_lr.fit(X_train_scaled, y_train)
    
    # Stacking with RandomForest meta-learner
    stacking_rf = StackingClassifier(
        estimators=[(name, model) for name, model in trained_models.items()],
        final_estimator=RandomForestClassifier(n_estimators=100),
        cv=5
    )
    stacking_rf.fit(X_train_scaled, y_train)
    
    # Evaluate and save ensemble models
    ensemble_models = {
        'Voting (Hard)': voting_hard,
        'Voting (Soft)': voting_soft,
        'Stacking (LR)': stacking_lr,
        'Stacking (RF)': stacking_rf
    }
    
    for name, model in ensemble_models.items():
        cv_scores = cross_val_score(model, X, y, cv=cv_method)
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()
        
        print(f"{name} CV performance: {cv_mean:.3f} ± {cv_std:.3f}")
        
        results[name] = {
            'model': model,
            'cv_mean': cv_mean,
            'cv_std': cv_std
        }
        
        # Save ensemble model
        joblib.dump(model, f"models/ensembles/{name.lower().replace(' ', '_').replace('(', '').replace(')', '')}.pkl")
    
    # Save preprocessing objects
    joblib.dump(scaler, "models/preprocessing/scaler.pkl")
    
    best_model_name = max(results, key=lambda x: results[x]['cv_mean'])
    best_model = results[best_model_name]['model']
    
    print(f"\nBest model: {best_model_name} with CV score {results[best_model_name]['cv_mean']:.3f}")
    
    return best_model, scaler, results





def predict_fight_enhanced(fighter1_name, fighter2_name, models_dict, scaler, imputer, fighters_df, results_df, stats_df, current_date=None):
    
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
        
        # Get predictions from all models
        predictions = {}
        feature_names = list(features.keys())
        
        for model_name, model_info in models_dict.items():
            model = model_info['model']
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
            
            key_features = {}
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                top_indices = np.argsort(importances)[-5:]
                for idx in top_indices:
                    if idx < len(feature_names):
                        key_features[feature_names[idx]] = features[feature_names[idx]]
            
            predictions[model_name] = {
                'winner': winner,
                'confidence': confidence,
                'key_features': key_features
            }
        
        # Calculate aggregate statistics
        winner_counts = {}
        total_confidence = {}
        
        for pred in predictions.values():
            winner = pred['winner']
            confidence = pred['confidence']
            
            winner_counts[winner] = winner_counts.get(winner, 0) + 1
            total_confidence[winner] = total_confidence.get(winner, 0) + confidence
        
        # Calculate consensus winner and average confidence
        consensus_winner = max(winner_counts.items(), key=lambda x: x[1])[0]
        consensus_confidence = total_confidence[consensus_winner] / winner_counts[consensus_winner]
        
        # Calculate model agreement percentage
        agreement_pct = (winner_counts[consensus_winner] / len(predictions)) * 100
        
        return {
            'individual_predictions': predictions,
            'consensus': {
                'winner': consensus_winner,
                'confidence': consensus_confidence,
                'agreement_percentage': agreement_pct
            }
        }
        
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        return 'Error', 0.5, {"error": str(e)}





def run_complete_enhanced_pipeline(fighters_df, results_df, stats_df):
    
    print("Preparing training data with enhanced features...")
    X, y, imputer, valid_indices = prepare_enhanced_training_data(results_df, fighters_df, stats_df)

    print(f"Generated {X.shape[1]} features for {X.shape[0]} fights")
    print(f"Original dataset had {len(results_df)} fights, {len(valid_indices)} were valid for training")
    
    print("\nCreating time-based cross-validation splits...")
    cv_splits = create_time_based_cv_splits(results_df, valid_indices)
    
    print("\nTraining models with time-based cross-validation...")
    best_model, scaler, all_results = train_enhanced_model(X, y, cv_splits)
    print("All unique classes in dataset:", np.unique(y))
    for i, (train_idx, test_idx) in enumerate(cv_splits):
        print(f"Fold {i} - Train classes: {np.unique(y[train_idx])}, Test classes: {np.unique(y[test_idx])}")
        
    print("\nSaving models and preprocessors...")
    joblib.dump(best_model, "best_model_enhanced.pkl")
    joblib.dump(scaler, "scaler_enhanced.pkl")
    joblib.dump(imputer, "imputer_enhanced.pkl")
    # joblib.dump(feature_names, "feature_names_enhanced.pkl")
    
    print("\nPipeline complete! Models and preprocessors saved.")
    
    return best_model, scaler, imputer, valid_indices





def predict_upcoming_card(event_name, matchups, fighters_df, results_df, stats_df, models_dict, scaler, imputer):
    """Make predictions for all fights on an upcoming card with robust error handling."""
    
    print(f"Predictions for {event_name}:")
    print("-" * 50)
    
    results = []
    
    for fighter1, fighter2 in matchups:
        print(f"Predicting: {fighter1} vs {fighter2}")
        
        fighter1_exists = not fighters_df[fighters_df['Name'] == fighter1].empty
        fighter2_exists = not fighters_df[fighters_df['Name'] == fighter2].empty
        
        if not fighter1_exists:
            print(f"Warning: {fighter1} not found in dataset")
        if not fighter2_exists:
            print(f"Warning: {fighter2} not found in dataset")
        
        try:
            predictions = predict_fight_enhanced(
                fighter1, fighter2, models_dict, scaler, imputer, fighters_df, results_df, stats_df
            )
            
            print(f"\n{fighter1} vs {fighter2}:")
            print("\nIndividual Model Predictions:")
            print("-" * 40)
            
            for model_name, pred in predictions['individual_predictions'].items():
                print(f"{model_name}:")
                print(f"  Winner: {pred['winner']}")
                print(f"  Confidence: {pred['confidence']:.1%}")
                if pred['key_features']:
                    print("  Key factors:")
                    for feature, value in pred['key_features'].items():
                        print(f"    - {feature}: {value}")
                print("-" * 40)
            
            print("\nConsensus Prediction:")
            print(f"Winner: {predictions['consensus']['winner']}")
            print(f"Confidence: {predictions['consensus']['confidence']:.1%}")
            print(f"Model Agreement: {predictions['consensus']['agreement_percentage']:.1f}%")
            
            results.append({
                "fighter1": fighter1,
                "fighter2": fighter2,
                "predictions": predictions
            })
            
        except Exception as e:
            print(f"Failed to predict {fighter1} vs {fighter2}: {str(e)}")
            results.append({
                "fighter1": fighter1,
                "fighter2": fighter2,
                "predicted_winner": "Error",
                "confidence": 0.0,
                "error": str(e)
            })
        
        print("-" * 50)
        
    return results





try:

    # best_model, scaler, imputer, valid_indices = run_complete_enhanced_pipeline(
    #     fighters_df, results_df, stats_df
    # )
    


    # Define matchups you want to predict
    upcoming_fights = [
        ("conor mcgregor", "michael chandler"),
        ("israel adesanya", "dricus du plessis"),
        ("jon jones", "tom aspinall"),
        # Add a matchup that might have missing fighters to test robustness
        ("non existent fighter", "another missing fighter")
    ]

    results = predict_upcoming_card(
        "UFC 300", upcoming_fights, fighters_df, results_df, stats_df,
        all_results, scaler, imputer
    )
    
    print("\nPrediction Summary:")
    print("=" * 80)
    for result in results:
        if "predictions" in result:
            print(f"\n{result['fighter1']} vs {result['fighter2']}:")
            print("\nModel Predictions:")
            print("-" * 40)
            
            consensus = result['predictions']['consensus']
            print(f"Consensus Winner: {consensus['winner']}")
            print(f"Confidence: {consensus['confidence']:.1%}")
            print(f"Model Agreement: {consensus['agreement_percentage']:.1f}%")
            
            print("\nIndividual Model Predictions:")
            for model_name, pred in result['predictions']['individual_predictions'].items():
                print(f"\n{model_name}:")
                print(f"Winner: {pred['winner']} ({pred['confidence']:.1%})")
                
                if pred['key_features']:
                    print("Key factors:")
                    for feature, value in pred['key_features'].items():
                        print(f"  - {feature}: {value}")
        else:
            print(f"\n{result['fighter1']} vs {result['fighter2']}: Failed - {result.get('error', 'Unknown error')}")
        print("=" * 80)

except Exception as e:
    print(f"An error occurred in the main pipeline: {str(e)}")
    import traceback
    traceback.print_exc()
