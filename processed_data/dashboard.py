# app.py
import dash
from layout_dash import create_layout
from callbacks_dash import register_callbacks

# Initialize the Dash app
app = dash.Dash(__name__)
app.layout = create_layout()

# Register callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
