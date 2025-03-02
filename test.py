import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Initialize the Dash app
app = dash.Dash(__name__)

# Sample data for fighters (placeholder)
fighter_stats = {
    "Fighter 1": {"Wins": 15, "Losses": 2, "KO": 10},
    "Fighter 2": {"Wins": 12, "Losses": 3, "KO": 8},
    "Fighter 3": {"Wins": 9, "Losses": 1, "KO": 5}
}

# Layout of the dashboard
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif'}, children=[
    # Header Section
    html.Div([
        html.Img(src='https://via.placeholder.com/50', style={'float': 'left', 'marginRight': '10px'}),
        html.H1("AUSSIE BUCKETS", style={'color': '#000', 'margin': '0', 'display': 'inline'}),
        html.P("SAY NO TO MARKUPS", style={'color': '#f1c40f', 'margin': '0', 'display': 'inline'}),
        html.Ul([
            html.Li(html.A("Products", href="#"), style={'display': 'inline', 'marginRight': '20px'}),
            html.Li(html.A("Industries", href="#"), style={'display': 'inline', 'marginRight': '20px'}),
            html.Li(html.A("Testimonials", href="#"), style={'display': 'inline', 'marginRight': '20px'}),
            html.Li(html.A("Finance", href="#"), style={'display': 'inline', 'marginRight': '20px'}),
            html.Li(html.A("Why AB?", href="#"), style={'display': 'inline', 'marginRight': '20px'}),
            html.Li(html.A("Contact", href="#"), style={'display': 'inline', 'marginRight': '20px'}),
            html.Li(html.Button("Quick Quote", style={'backgroundColor': '#f1c40f', 'border': 'none', 'padding': '5px 10px', 'cursor': 'pointer'}))
        ], style={'listStyleType': 'none', 'margin': '0', 'padding': '10px', 'overflow': 'hidden', 'backgroundColor': '#fff'})
    ], style={'borderBottom': '2px solid #f1c40f', 'padding': '10px'}),

    # Main Section
    html.Div([
        html.Img(src='https://via.placeholder.com/1200x400', style={'width': '100%', 'height': 'auto'}),
        html.H2("THE LARGEST SUPPLIER OF EXCAVATOR ATTACHMENTS IN AUSTRALIA", 
                style={'color': '#f1c40f', 'textAlign': 'center', 'margin': '20px 0'}),
        html.P("As the leading supplier of attachments in Australia, we use modern technology and superior materials to exceed your expectations.", 
               style={'textAlign': 'center', 'maxWidth': '600px', 'margin': '0 auto'}),
        html.Div([
            html.Button("Quick Quote", style={'backgroundColor': '#f1c40f', 'border': 'none', 'padding': '10px 20px', 'marginRight': '10px'}),
            html.Button("Full Range", style={'backgroundColor': '#333', 'color': '#fff', 'border': 'none', 'padding': '10px 20px'})
        ], style={'textAlign': 'center', 'margin': '20px 0'})
    ], style={'backgroundColor': '#f5f5f5', 'padding': '20px'}),

    # Brands Section
    html.Div([
        html.Img(src='https://via.placeholder.com/100', alt="Caterpillar", style={'margin': '10px'}),
        html.Img(src='https://via.placeholder.com/100', alt="Yanmar", style={'margin': '10px'}),
        html.Img(src='https://via.placeholder.com/100', alt="Komatsu", style={'margin': '10px'}),
        html.Img(src='https://via.placeholder.com/100', alt="Case", style={'margin': '10px'}),
        html.Img(src='https://via.placeholder.com/100', alt="JCB", style={'margin': '10px'}),
        html.Img(src='https://via.placeholder.com/100', alt="John Deere", style={'margin': '10px'})
    ], style={'textAlign': 'center', 'margin': '20px 0'}),

    # Product Categories
    html.Div([
        html.H3("Browse Our Expansive Range Of Excavator Buckets, Grabs And Attachments", 
                style={'color': '#e74c3c', 'textAlign': 'center'}),
        html.P("Aussie Buckets was born out of a necessity to provide hard-working Australians with quality products at a fair and honest price. We offer a comprehensive range of high-quality, 100% purpose-built products, making our heavy equipment the ultimate choice for all Australian operators.", 
               style={'textAlign': 'center', 'maxWidth': '600px', 'margin': '0 auto 20px'}),
        html.Div([
            html.Div([
                html.Img(src='https://via.placeholder.com/200', style={'width': '100%'}),
                html.P("Excavator Buckets")
            ], style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center', 'margin': '10px'}),
            html.Div([
                html.Img(src='https://via.placeholder.com/200', style={'width': '100%'}),
                html.P("Excavator Grabs")
            ], style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center', 'margin': '10px'}),
            html.Div([
                html.Img(src='https://via.placeholder.com/200', style={'width': '100%'}),
                html.P("Excavator Attachments")
            ], style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center', 'margin': '10px'})
        ])
    ], style={'padding': '20px'}),

    # Fighter Statistics Section (instead of news)
    html.Div([
        html.H3("Fighter Statistics", style={'textAlign': 'center', 'color': '#2c3e50'}),
        html.Div([
            html.Div([
                html.H4(fighter, style={'textAlign': 'center'}),
                html.P(f"Wins: {stats['Wins']}", style={'textAlign': 'center'}),
                html.P(f"Losses: {stats['Losses']}", style={'textAlign': 'center'}),
                html.P(f"KO: {stats['KO']}", style={'textAlign': 'center'})
            ], style={'display': 'inline-block', 'width': '30%', 'margin': '10px', 'border': '1px solid #ddd', 'padding': '10px'})
            for fighter, stats in fighter_stats.items()
        ])
    ], style={'padding': '20px', 'backgroundColor': '#ecf0f1'})
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)