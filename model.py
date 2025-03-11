#!/usr/bin/env python
# coding: utf-8

# In[152]:


import pandas as pd
import joblib

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression


# In[153]:


fighters_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fighters_w_image_2.csv')
stats_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fight_stats_with_weghtclass_date_location.csv')
results_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fight_results_with_locale_2.csv')


# In[154]:


fighters_df['Name'] = fighters_df['Name'].str.strip().str.lower()
stats_df['ROUND'] = stats_df['ROUND'].str.replace('Round ','')
results_df['DATE'] = pd.to_datetime(results_df['DATE'])




# In[159]:


def create_matchup_features(fighter1, fighter2):
    """Create symmetric matchup features that don't depend on fighter order."""
    features = {}
    numerical_features = [
        'Striking_Accuracy', 'Takedown_Accuracy', 'Sig_Str_Def', 'Takedown_Def',
        'Takedown_Avg_Per Min', 'Knockdown_Avg'
    ]
    
    for feature in numerical_features:
        if feature in fighter1 and feature in fighter2:
            # Absolute difference (symmetric)
            features[f'{feature}_abs_diff'] = abs(fighter1[feature] - fighter2[feature])
            
            # Identify better fighter for this stat
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
    
    # Experience gap (always symmetric)
    debut1 = pd.to_datetime(fighter1['Octagon_Debut'])
    debut2 = pd.to_datetime(fighter2['Octagon_Debut'])
    features['days_debut'] = abs((debut1 - debut2).days)
    
    return features


# In[160]:


def create_career_features(fighter1, fighter2):
    """Create symmetric career features that don't depend on fighter order."""
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
    
    # Experience differences (symmetric)
    f1_experience = f1_career_wins + f1_career_losses + f1_career_draws
    f2_experience = f2_career_wins + f2_career_losses + f2_career_draws
    
    features['experience_abs_diff'] = abs(f1_experience - f2_experience)
    
    if f1_experience > f2_experience:
        features['more_experienced'] = 1
    elif f1_experience < f2_experience:
        features['more_experienced'] = -1
    else:
        features['more_experienced'] = 0
    
    # Win rate comparison (symmetric)
    features['win_rate_abs_diff'] = abs(f1_career_win_rate - f2_career_win_rate)
    
    if f1_career_win_rate > f2_career_win_rate:
        features['better_win_rate'] = 1
    elif f1_career_win_rate < f2_career_win_rate:
        features['better_win_rate'] = -1
    else:
        features['better_win_rate'] = 0
    
    # Wins and losses comparison (symmetric)
    features['wins_abs_diff'] = abs(f1_career_wins - f2_career_wins)
    
    if f1_career_wins > f2_career_wins:
        features['more_wins'] = 1
    elif f1_career_wins < f2_career_wins:
        features['more_wins'] = -1
    else:
        features['more_wins'] = 0
    
    features['losses_abs_diff'] = abs(f1_career_losses - f2_career_losses)
    
    if f1_career_losses < f2_career_losses:  # Fewer losses is better
        features['fewer_losses'] = 1
    elif f1_career_losses > f2_career_losses:
        features['fewer_losses'] = -1
    else:
        features['fewer_losses'] = 0
    
    # Momentum calculation (symmetric)
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
    
    # Momentum comparison (symmetric)
    features['momentum_abs_diff'] = abs(f1_momentum - f2_momentum)
    
    if f1_momentum > f2_momentum:
        features['better_momentum'] = 1
    elif f1_momentum < f2_momentum:
        features['better_momentum'] = -1
    else:
        features['better_momentum'] = 0
    
    return features


# In[161]:


create_career_features('conor mcgregor','khabib nurmagomedov')


# In[162]:


def create_style_matchup_features(fighter1, fighter2):
    """Create symmetric style features that don't depend on fighter order."""
    features = {}
    
    # Calculate strike bias
    fighter1_strike_bias = fighter1['Sig_Strikes_Per Min'] / (fighter1['Takedown_Avg_Per Min'] + 0.1)
    fighter2_strike_bias = fighter2['Sig_Strikes_Per Min'] / (fighter2['Takedown_Avg_Per Min'] + 0.1)
    
    # Style clash is already symmetric (uses absolute difference)
    features['style_clash'] = abs(fighter1_strike_bias - fighter2_strike_bias)
    
    # Ground game comparison
    f1_ground_offense = fighter1['Sub_Avg_Per_Min']
    f2_ground_defense = fighter2['Takedown_Def']
    f1_ground_advantage = f1_ground_offense - f2_ground_defense
    
    f2_ground_offense = fighter2['Sub_Avg_Per_Min']
    f1_ground_defense = fighter1['Takedown_Def']
    f2_ground_advantage = f2_ground_offense - f1_ground_defense
    
    # Symmetric ground advantage
    features['ground_advantage_abs_diff'] = abs(f1_ground_advantage - f2_ground_advantage)
    
    if f1_ground_advantage > f2_ground_advantage:
        features['better_ground_game'] = 1
    elif f1_ground_advantage < f2_ground_advantage:
        features['better_ground_game'] = -1
    else:
        features['better_ground_game'] = 0
    
    # Head striking comparison (symmetric)
    f1_head_pct = fighter1['Sig_Strikes_Head_Percent']
    f2_head_pct = fighter2['Sig_Strikes_Head_Percent']
    
    features['head_striking_abs_diff'] = abs(f1_head_pct - f2_head_pct)
    
    if f1_head_pct > f2_head_pct:
        features['more_head_strikes'] = 1
    elif f1_head_pct < f2_head_pct:
        features['more_head_strikes'] = -1
    else:
        features['more_head_strikes'] = 0
    
    # Distance control comparison (symmetric)
    f1_distance_pct = fighter1['Sig_Strikes_While_Standing_Percent']
    f2_distance_pct = fighter2['Sig_Strikes_While_Standing_Percent']
    
    features['distance_control_abs_diff'] = abs(f1_distance_pct - f2_distance_pct)
    
    if f1_distance_pct > f2_distance_pct:
        features['better_distance_control'] = 1
    elif f1_distance_pct < f2_distance_pct:
        features['better_distance_control'] = -1
    else:
        features['better_distance_control'] = 0
    
    return features


# In[163]:


def create_fight_features(fight, fighters_df):
    """Create features for a single fight using symmetric feature extraction."""
    fighter1_name = fight['FIGHTER_1']
    fighter2_name = fight['FIGHTER_2']
    
    f1_data = fighters_df[fighters_df['Name'] == fighter1_name]
    f2_data = fighters_df[fighters_df['Name'] == fighter2_name]
    
    if f1_data.empty or f2_data.empty:
        return None, None
    
    fighter1 = f1_data.iloc[0]
    fighter2 = f2_data.iloc[0]
    
    if fight['fighter_1_result'] == 1:
        outcome = 1
    elif fight['fighter_1_result'] == 4:
        outcome = 4
    else:
        outcome = 0
    
    try:
        # Create symmetric features
        features = {}
        
        # Apply our new symmetric feature extraction functions
        features.update(create_matchup_features(fighter1, fighter2))
        features.update(create_career_features(fighter1_name, fighter2_name))
        features.update(create_style_matchup_features(fighter1, fighter2))
        
        # Add one more feature that indicates which fighter is first in the data
        # This helps the model learn if there's any potential ordering bias in the dataset
        features['fighter1_position'] = 1  # fighter1 is in position 1
        
        return features, outcome
    except Exception as e:
        print(f"Error processing fight between {fighter1_name} and {fighter2_name}: {str(e)}")
        return None, None


# In[164]:


def prepare_training_data(results_df, fighters_df):
    X_features = []
    y_outcomes = []
    feature_names = None
    skipped_fights=[]
    for _, fight in results_df.iterrows():
        features, outcome = create_fight_features(fight, fighters_df)
        
        if features is not None and outcome is not None:
            X_features.append(list(features.values()))
            y_outcomes.append(outcome)
            # Save feature names once
            if feature_names is None:
                feature_names = list(features.keys())
        else:
            skipped_fights.append((fight['FIGHTER_1'], fight['FIGHTER_2']))
    
    if skipped_fights:
        print(f"Skipped {len(skipped_fights)} fights due to missing fighter data")
    
    if len(X_features) == 0:
        raise ValueError("No valid fight data was found to prepare for training")
    
    # Convert to numpy arrays
    X = np.array(X_features)
    print(len(X))
    y = np.array(y_outcomes)
    
    # # Handle missing values
    # nan_count = np.isnan(X).sum()
    # if nan_count > 0:
    #     print(f"Found {nan_count} NaN values in feature data")
    #     imputer = SimpleImputer(strategy='mean')
    #     X = imputer.fit_transform(X)
    
    return X, y, feature_names


# In[173]:


def train_multiple_models(X, y):
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    X_train = StandardScaler().fit_transform(X_train)
    X_test = StandardScaler().fit_transform(X_test)
    print(f"Training models with {X_train.shape[0]} samples, {X_train.shape[1]} features")
    
    models = {
        'Logistic Regression': LogisticRegression(max_iter=2000,solver='liblinear', random_state=42),
        'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=11),
        'SVM': SVC(probability=True,kernel='rbf',C=1, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
    }
    
    best_model = None
    best_accuracy = 0

    results = {}
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        test_accuracy = accuracy_score(y_test, y_pred)
        
        cv_scores = cross_val_score(model, X, y, cv=5)
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()
        
        print(f"{name} Test accuracy: {test_accuracy:.3f}")
        print(f"{name} CV performance: {cv_mean:.3f} ± {cv_std:.3f}")
        
        results[name] = {
            'model': model,
            'test_accuracy': test_accuracy,
            'cv_mean': cv_mean,
            'cv_std': cv_std,
            # 'classification_report': classification_report(y_test, y_pred)
        }
        
        if cv_mean > best_accuracy:
            best_accuracy = cv_mean
            best_model = model
    
    print("\n===== Model Comparison =====")
    for name, result in results.items():
        print(f"{name}: Test Acc={result['test_accuracy']:.3f}, CV={result['cv_mean']:.3f}±{result['cv_std']:.3f}")
    
    print(f"\nBest model: {max(results.items(), key=lambda x: x[1]['cv_mean'])[0]}")
    
    return results, best_model


# In[174]:


def run_complete_pipeline(fighters_df, results_df, stats_df):
    X, y, feature_names = prepare_training_data(results_df, fighters_df)
    
    model_results, best_model = train_multiple_models(X, y)
    
    return model_results, best_model, feature_names


# In[175]:


results, best_model,features = run_complete_pipeline(fighters_df, results_df, stats_df)


# In[176]:


joblib.dump(best_model, f"best_model.pkl") 


# In[178]:


best_model


# In[171]:


def predict_fight(fighter1_name, fighter2_name, fighters_df, results_df, loaded_model):
    try:
        fighter1 = fighters_df[fighters_df['Name'] == fighter1_name]
        fighter2 = fighters_df[fighters_df['Name'] == fighter2_name]
        
        if fighter1.empty or fighter2.empty:
            print(f"Fighter data missing: {fighter1_name if fighter1.empty else ''} {fighter2_name if fighter2.empty else ''}")
            return fighter1_name, 0.5
            
        fighter1 = fighter1.iloc[0]
        fighter2 = fighter2.iloc[0]
        
        features = {}
        
        matchup_features = create_matchup_features(fighter1, fighter2)
        # print(f"Matchup features: {len(matchup_features)}")
        # print(f"Names: {list(matchup_features.keys())}")
        
        career_features = create_career_features(fighter1_name, fighter2_name)
        # print(f"Career features: {len(career_features)}")
        # print(f"Names: {list(career_features.keys())}")
        
        style_features = create_style_matchup_features(fighter1, fighter2)
        # print(f"Style features: {len(style_features)}")
        # print(f"Names: {list(style_features.keys())}")
        
        features.update(matchup_features)
        features.update(career_features)
        features.update(style_features)
        features['fighter1_position'] = 1
        # print(f"Total unique features: {len(features)}")
        # print(f"Final feature names: {list(features.keys())}")
        X = []        
        
        feature_values = list(features.values())
        feature_names = list(features.keys())
        X = np.array([feature_values])   
        # print(X)     
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
        return 'None', 0

predict_fight('conor mcgregor', 'israel adesanya', fighters_df, results_df, best_model)


# In[172]:


def test_prediction_model(fighters_df, results_df, loaded_model):
    """
    Test the prediction model with various fighter matchups and analyze results
    """
    print("\n===== UFC FIGHT PREDICTION MODEL TESTING =====\n")
    
    # 1. Test with known rivalries (historical matchups)
    print("\n----- TESTING KNOWN RIVALRIES -----")
    known_matchups = [
        ('conor mcgregor', 'nate diaz'),         # These two fought twice, split 1-1
        ('khabib nurmagomedov', 'conor mcgregor'), # Khabib won
        ('jon jones', 'daniel cormier'),          # Jones won twice
        ('israel adesanya', 'robert whittaker'),   # Adesanya won
        ('kamaru usman', 'colby covington'),      # Usman won twice
        ('alexander volkanovski', 'max holloway') # Volkanovski won multiple times
    ]
    
    print("\nHistorical Matchups:")
    for f1, f2 in known_matchups:
        try:
            winner, confidence = predict_fight(f1, f2, fighters_df, results_df, loaded_model)
            print(f"{f1} vs {f2}: Winner: {winner}, Confidence: {confidence:.2f}")
        except Exception as e:
            print(f"{f1} vs {f2}: Error - {str(e)}")
    
    # 2. Test with reversed order of same fighters
    print("\n----- TESTING ORDER SENSITIVITY -----")
    print("\nSame matchups with fighter order reversed:")
    for f1, f2 in known_matchups:
        try:
            winner1, conf1 = predict_fight(f1, f2, fighters_df, results_df, loaded_model)
            winner2, conf2 = predict_fight(f2, f1, fighters_df, results_df, loaded_model)
            
            if winner1 == f1 and winner2 == f2:
                print(f"{f1} vs {f2}: Model predicts whoever is first! This indicates a bias.")
            elif winner1 == winner2:
                print(f"{f1} vs {f2}: Model consistently predicts {winner1} regardless of order. Good!")
            else:
                print(f"{f1} vs {f2}: Inconsistent results when order is reversed!")
                
        except Exception as e:
            print(f"{f1} vs {f2}: Error - {str(e)}")
    
    # 3. Test with extreme mismatches (different weight classes)
    print("\n----- TESTING EXTREME MISMATCHES -----")
    mismatches = [
        ('jon jones', 'demetrious johnson'),      # Heavyweight vs Flyweight
        ('francis ngannou', 'petr yan'),          # Heavyweight vs Bantamweight
        ('kamaru usman', 'alexander volkanovski'), # Welterweight vs Featherweight
        ('weili zhang', 'cyril gane')            # Women's Strawweight vs Heavyweight
    ]
    
    print("\nExtreme Weight Mismatches:")
    for f1, f2 in mismatches:
        try:
            winner, confidence = predict_fight(f1, f2, fighters_df, results_df, loaded_model)
            print(f"{f1} vs {f2}: Winner: {winner}, Confidence: {confidence:.2f}")
            
            # Check if bigger fighter usually wins extreme mismatches
            f1_info = fighters_df[fighters_df['Name'] == f1].iloc[0]
            f2_info = fighters_df[fighters_df['Name'] == f2].iloc[0]
            if 'Weight_Class' in f1_info and 'Weight_Class' in f2_info:
                print(f"  {f1} Weight: {f1_info['Weight_Class']}, {f2} Weight: {f2_info['Weight_Class']}")
        except Exception as e:
            print(f"{f1} vs {f2}: Error - {str(e)}")
    
    # 4. Test with very similar fighters
    print("\n----- TESTING SIMILAR FIGHTERS -----")
    similar_fighters = [
        ('dustin poirier', 'justin gaethje'),     # Similar style brawlers
        ('israel adesanya', 'anderson silva'),     # Similar style strikers
        ('khabib nurmagomedov', 'islam makhachev'), # Similar style grapplers
        ('amanda nunes', 'valentina shevchenko')  # Similar level champs
    ]
    
    print("\nSimilar Fighters:")
    for f1, f2 in similar_fighters:
        try:
            winner, confidence = predict_fight(f1, f2, fighters_df, results_df, loaded_model)
            print(f"{f1} vs {f2}: Winner: {winner}, Confidence: {confidence:.2f}")
            
            # Check if confidence is lower for similar fighters (should be)
            if confidence < 0.6:
                print("  Low confidence as expected for similar fighters.")
            else:
                print("  Unusually high confidence for similar fighters.")
        except Exception as e:
            print(f"{f1} vs {f2}: Error - {str(e)}")
    
    # 5. Check for bias in predictions
    print("\n----- CHECKING FOR PREDICTION BIAS -----")
    
    # Generate random matchups
    import random
    random_pairs = []
    fighters = fighters_df['Name'].sample(40).tolist()
    
    for _ in range(20):
        f1 = random.choice(fighters)
        f2 = random.choice(fighters)
        if f1 != f2 and (f1, f2) not in random_pairs and (f2, f1) not in random_pairs:
            random_pairs.append((f1, f2))
    
    # Track statistics
    fighter1_wins = 0
    fighter2_wins = 0
    high_confidence_count = 0
    low_confidence_count = 0
    total_confidence = 0
    
    print("\nRandom Matchups:")
    for f1, f2 in random_pairs:
        try:
            winner, confidence = predict_fight(f1, f2, fighters_df, results_df, loaded_model)
            print(f"{f1} vs {f2}: Winner: {winner}, Confidence: {confidence:.2f}")
            
            if winner == f1:
                fighter1_wins += 1
            else:
                fighter2_wins += 1
                
            if confidence > 0.7:
                high_confidence_count += 1
            if confidence < 0.55:
                low_confidence_count += 1
                
            total_confidence += confidence
            
        except Exception as e:
            print(f"{f1} vs {f2}: Error - {str(e)}")
    
    # Print bias statistics
    print("\nBias Analysis:")
    print(f"Fighter 1 win rate: {fighter1_wins / len(random_pairs):.2f}")
    print(f"Fighter 2 win rate: {fighter2_wins / len(random_pairs):.2f}")
    print(f"Average confidence: {total_confidence / len(random_pairs):.2f}")
    print(f"High confidence predictions (>70%): {high_confidence_count} ({high_confidence_count/len(random_pairs):.2f})")
    print(f"Low confidence predictions (<55%): {low_confidence_count} ({low_confidence_count/len(random_pairs):.2f})")
    
    if fighter1_wins / len(random_pairs) > 0.7:
        print("WARNING: Model shows strong bias toward predicting Fighter 1 as the winner!")
        print("This suggests a problem with feature engineering or model training.")
    
    print("\n===== TEST COMPLETE =====")

# Run the tests
test_prediction_model(fighters_df, results_df, best_model)


# In[102]:



