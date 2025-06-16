# UFC Matches Analysis Dashboard

A comprehensive data analysis and prediction platform for UFC fights, featuring interactive visualizations, fighter comparisons, and machine learning-powered fight outcome predictions.

## Features

### Interactive Dashboard
- **Fighter Analysis**: Detailed fighter profiles with performance metrics, fighting styles, and career statistics
- **Match Analysis**: Round-by-round fight breakdowns with strike distribution and takedown analysis
- **Fighter Comparison**: Side-by-side comparison of fighters with radar charts and statistical analysis
- **Fight Prediction**: ML-powered predictions using ensemble models with confidence scores

### Machine Learning Models
- Multiple ML algorithms including Random Forest, Gradient Boosting, SVM, and ensemble methods
- Feature engineering with fighter matchup analysis, recent form weighting, and style compatibility
- Model consensus predictions with confidence intervals
- Real-time prediction capabilities

### Data Visualization
- Interactive radar charts for fighter performance metrics
- Strike distribution and fighting style analysis
- Timeline-based fight progression analysis
- Comparative statistics with dynamic filtering

## Technology Stack

- **Frontend**: Dash (Plotly) with Bootstrap components
- **Backend**: Python with Pandas for data processing
- **Machine Learning**: Scikit-learn, XGBoost, LightGBM
- **Data Visualization**: Plotly, Seaborn
- **Styling**: Custom CSS with dark theme


### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd UFC-Matches-Analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Data Sources

The project uses comprehensive UFC data including:
- **Fighter Statistics**: Career records, physical attributes, fighting styles
- **Fight Results**: Historical match outcomes with detailed results
- **Fight Statistics**: Round-by-round performance metrics
- **Event Details**: Location, date, and event information

### Key Datasets
- `fighters_w_image_2.csv`: Fighter profiles and career statistics
- `fight_stats_with_weghtclass_date_location.csv`: Detailed fight statistics
- `fight_results_with_locale_2.csv`: Fight outcomes and results

## Prediction Models

The system employs multiple machine learning models:

### Individual Models
- **Random Forest**: Ensemble decision trees for robust predictions
- **Gradient Boosting**: Sequential learning for improved accuracy
- **Support Vector Machine**: Pattern recognition for complex relationships
- **K-Nearest Neighbors**: Similarity-based predictions
- **Logistic Regression**: Linear probability modeling

### Ensemble Methods
- **Voting Classifier**: Combines multiple model predictions
- **Stacking Classifier**: Meta-learning approach for optimal combinations

### Feature Engineering
- **Matchup Features**: Fighter vs fighter statistical comparisons
- **Recent Form**: Time-weighted performance metrics
- **Style Analysis**: Fighting style compatibility assessment
- **Career Metrics**: Experience and age-related factors

## 🎯 Usage

### Fighter Analysis
1. Navigate to the "Fighters" tab
2. Select a fighter from the dropdown
3. Explore performance metrics, fighting style, and recent history

### Match Analysis
1. Go to the "Matches" tab
2. Choose a specific fight from the dropdown
3. Analyze round-by-round statistics and fight progression

### Fighter Comparison
1. Visit the "Comparison" tab
2. Select two fighters to compare
3. View side-by-side statistics and performance metrics

### Fight Prediction
1. Access the "Prediction" tab
2. Choose two fighters for the matchup
3. Click "Predict Winner" to get ML-powered predictions


### Model Configuration
Models are loaded from pre-trained files:
- `best_model_enhanced.pkl`: Primary prediction model
- `scaler_enhanced.pkl`: Feature scaling parameters
- `imputer_enhanced.pkl`: Missing value imputation

## Performance Metrics

The prediction system provides:
- **Consensus Predictions**: Aggregated results from multiple models
- **Confidence Scores**: Probability-based confidence intervals
- **Model Agreement**: Percentage of models agreeing on the outcome
- **Individual Model Results**: Detailed breakdown by algorithm
