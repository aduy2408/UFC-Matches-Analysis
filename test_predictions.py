import joblib
import pandas as pd
import numpy as np
from model2 import create_enhanced_fight_features

def load_all_models():
    """Load all saved models and preprocessors."""
    models = {
        'logistic_regression': joblib.load('logistic_regression_model.joblib'),
        'random_forest': joblib.load('random_forest_model.joblib'),
        'gradient_boosting': joblib.load('gradient_boosting_model.joblib'),
        'svm': joblib.load('svm_model.joblib'),
        'knn': joblib.load('knn_model.joblib'),
        'xgboost': joblib.load('xgboost_model.joblib'),
        'adaboostclassifier': joblib.load('adaboostclassifier_model.joblib'),
        'lightgbm': joblib.load('lightgbm_model.joblib'),
        'stacked_ensemble': joblib.load('stacked_ensemble_model.joblib')
    }
    
    scaler = joblib.load('scaler_enhanced.pkl')
    imputer = joblib.load('imputer_enhanced.pkl')
    
    return models, scaler, imputer

def predict_fight(fighter1_name, fighter2_name, models, scaler, imputer, fighters_df, results_df, stats_df, current_date=None):
    """Get predictions from all models for a single fight."""
    
    # Generate features
    features = create_enhanced_fight_features(
        fighter1_name,
        fighter2_name,
        fighters_df,
        results_df,
        stats_df,
        current_date
    )
    
    if features is None:
        return None
    
    # Prepare feature vector
    X = np.array([list(features.values())])
    X = imputer.transform(X)
    X_scaled = scaler.transform(X)
    
    # Get predictions from all models
    predictions = {}
    for name, model in models.items():
        proba = model.predict_proba(X_scaled)[0]
        
        predictions[name] = {
            'winner': fighter1_name if np.argmax(proba) == 1 else fighter2_name,
            'confidence': max(proba),
            'probabilities': {
                fighter1_name: proba[1],
                fighter2_name: proba[0],
                'Draw': proba[2] if len(proba) > 2 else 0
            }
        }
    
    return predictions

def get_consensus_prediction(predictions):
    """Get consensus prediction from all models."""
    if not predictions:
        return None
    
    # Count votes for each fighter
    votes = {}
    confidences = {}
    
    for model_name, pred in predictions.items():
        winner = pred['winner']
        confidence = pred['confidence']
        
        if winner not in votes:
            votes[winner] = 0
            confidences[winner] = []
        
        votes[winner] += 1
        confidences[winner].append(confidence)
    
    # Get fighter with most votes
    winner = max(votes.items(), key=lambda x: x[1])[0]
    
    # Calculate average confidence for winner
    avg_confidence = np.mean(confidences[winner])
    
    # Calculate agreement percentage
    total_votes = sum(votes.values())
    agreement = votes[winner] / total_votes
    
    return {
        'winner': winner,
        'confidence': avg_confidence,
        'agreement': agreement,
        'vote_distribution': {k: v/total_votes for k, v in votes.items()}
    }

if __name__ == "__main__":
    # Load data
    fighters_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fighters_w_image_2.csv')
    results_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fight_results_with_locale_2.csv')
    stats_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fight_stats_with_weghtclass_date_location.csv')
    
    # Process data
    fighters_df['Name'] = fighters_df['Name'].str.strip().str.lower()
    stats_df['ROUND'] = stats_df['ROUND'].str.replace('Round ','')
    results_df['DATE'] = pd.to_datetime(results_df['DATE'])
    
    # Load models
    print("Loading models...")
    models, scaler, imputer = load_all_models()
    
    # Example predictions
    upcoming_fights = [
        ("jon jones", "stipe miocic"),
        ("israel adesanya", "dricus du plessis"),
        ("alexander volkanovski", "ilia topuria"),
        ("dustin poirier", "conor mcgregor"),
        ("khamzat chimaev", "kamaru usman")
    ]
    
    print("\nGenerating predictions for upcoming fights...")
    for fighter1, fighter2 in upcoming_fights:
        print(f"\n{fighter1.title()} vs {fighter2.title()}")
        
        # Get predictions from all models
        predictions = predict_fight(
            fighter1, fighter2,
            models, scaler, imputer,
            fighters_df, results_df, stats_df
        )
        
        if predictions:
            # Show individual model predictions
            print("\nIndividual Model Predictions:")
            for model_name, pred in predictions.items():
                print(f"\n{model_name.replace('_', ' ').title()}:")
                print(f"Winner: {pred['winner']} ({pred['confidence']:.2%} confidence)")
                print("Probabilities:")
                for fighter, prob in pred['probabilities'].items():
                    print(f"  {fighter}: {prob:.2%}")
            
            # Show consensus prediction
            consensus = get_consensus_prediction(predictions)
            print("\nConsensus Prediction:")
            print(f"Winner: {consensus['winner']} ({consensus['confidence']:.2%} confidence)")
            print(f"Model Agreement: {consensus['agreement']:.2%}")
            print("Vote Distribution:")
            for fighter, votes in consensus['vote_distribution'].items():
                print(f"  {fighter}: {votes:.2%}")
        else:
            print("Could not generate predictions - missing fighter data")
