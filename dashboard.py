# app.py
import dash
from layout_dash import create_layout
from callbacks_dash import register_callbacks
import pandas as pd

#data 
fighters_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fighters_w_image_2.csv')
stats_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fight_stats_with_weghtclass_date_location.csv')
results_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fight_results_with_locale_2.csv')

fighters_df['Name'] = fighters_df['Name'].str.strip().str.lower()

results_df['DATE'] = pd.to_datetime(results_df['DATE'])
app = dash.Dash(__name__)

#layout
app.layout = create_layout(fighters_df,results_df)  

#callbacks
register_callbacks(app, fighters_df, stats_df, results_df)

if __name__ == '__main__':
    app.run_server(debug=True)
