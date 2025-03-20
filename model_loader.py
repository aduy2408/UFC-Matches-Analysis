import os
import joblib

def load_all_models():
    """Load all saved models from the models directory."""
    models = {}
    
    # Load individual models
    individual_path = 'models/individual'
    for model_file in os.listdir(individual_path):
        if model_file.endswith('.pkl'):
            model_name = model_file.replace('.pkl', '')
            model = joblib.load(os.path.join(individual_path, model_file))
            models[model_name] = {
                'model': model,
                'type': 'individual',
                'has_proba': hasattr(model, 'predict_proba') and callable(getattr(model, 'predict_proba'))
            }
    
    # Load ensemble models
    ensemble_path = 'models/ensembles'
    for model_file in os.listdir(ensemble_path):
        if model_file.endswith('.pkl'):
            model_name = model_file.replace('.pkl', '')
            model = joblib.load(os.path.join(ensemble_path, model_file))
            models[model_name] = {
                'model': model,
                'type': 'ensemble',
                'has_proba': hasattr(model, 'predict_proba') and callable(getattr(model, 'predict_proba'))
            }
    
    scaler = joblib.load('models/preprocessing/scaler.pkl')
    
    return models, scaler
