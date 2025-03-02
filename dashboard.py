# app.py
from layout_dash import  create_layout_2
from callbacks_dash import register_callbacks_2
import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

#data 
fighters_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fighters_w_image_2.csv')
stats_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fight_stats_with_weghtclass_date_location.csv')
results_df = pd.read_csv('/home/duyle/Documents/VSC/Project_DAP391/processed_data/fight_results_with_locale_2.csv')

fighters_df['Name'] = fighters_df['Name'].str.strip().str.lower()

results_df['DATE'] = pd.to_datetime(results_df['DATE'])
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], use_pages=False)

#layout
app.layout = create_layout_2(fighters_df,results_df)  

#callbacks
register_callbacks_2(app, fighters_df, results_df,stats_df)

if __name__ == '__main__':
    app.run_server(debug=True)
