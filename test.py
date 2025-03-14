import dash
from dash import html, dcc, Input, Output, clientside_callback
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout
app.layout = html.Div([
    # Navigation bar
    html.Div([
        html.Div([
            html.Img(src='assets/logo.png', style={'height': '28px', 'marginRight': '10px'}),
            html.Span("Dash BC", style={'fontWeight': '600', 'fontSize': '18px'})
        ], style={'display': 'flex', 'alignItems': 'center'}),
        
        html.Div([
            html.A("Features", href="#", style={'textDecoration': 'none', 'color': '#333', 'fontWeight': '500', 'marginRight': '30px'}),
            html.A("Models", href="#", style={'textDecoration': 'none', 'color': '#333', 'fontWeight': '500', 'marginRight': '30px'}),
            html.A("Pricing", href="#", style={'textDecoration': 'none', 'color': '#333', 'fontWeight': '500'}),
        ], style={'display': 'flex'}),
        
        html.Div([
            html.Button("Log in", style={
                'background': 'none',
                'border': 'none',
                'cursor': 'pointer',
                'padding': '8px 16px',
                'fontWeight': '500',
                'marginRight': '15px'
            }),
            html.Button("Get Started", style={
                'backgroundColor': '#111',
                'color': 'white',
                'border': 'none',
                'borderRadius': '6px',
                'padding': '8px 16px',
                'fontWeight': '500',
                'cursor': 'pointer'
            }),
        ], style={'display': 'flex'}),
    ], style={
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center',
        'padding': '20px 0',
        'borderBottom': '1px solid #f0f0f0'
    }),
    
    # Hero section
    html.Div([
        html.Div([
            # Main title
            html.H1([
                html.Span("Dash", style={'color': '#333'}),
                html.Span(" BC", style={'color': '#6440A4'})
            ], style={
                'fontSize': '72px',
                'fontWeight': '700',
                'marginBottom': '20px'
            }),
            
            # Subtitle with typing effect (static version first)
            html.H2(id='typing-text', style={
                'fontSize': '36px',
                'fontWeight': '600',
                'marginBottom': '30px',
                'minHeight': '50px'
            }),

            # Static paragraph
            html.P("Experience data visualization with lightning-fast responses. Access top visualization models from one unified interface.", style={
                'fontSize': '18px',
                'color': '#666',
                'marginBottom': '40px',
                'lineHeight': '1.6'
            }),
            
            # Buttons
            html.Div([
                html.Button("Try for Free →", style={
                    'backgroundColor': '#111',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '6px',
                    'padding': '12px 24px',
                    'fontWeight': '500',
                    'cursor': 'pointer',
                    'marginRight': '20px'
                }),
                html.Button("See the Demo", style={
                    'background': 'none',
                    'border': '1px solid #ddd',
                    'borderRadius': '6px',
                    'padding': '12px 24px',
                    'fontWeight': '500',
                    'cursor': 'pointer'
                }),
            ], style={'display': 'flex', 'justifyContent': 'center'}),
        ], style={
            'maxWidth': '800px',
            'textAlign': 'center'
        })
    ], style={
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center',
        'minHeight': '70vh',
        'padding': '40px 0'
    }),
    
    # Add the necessary JavaScript to the page
    html.Script(id='typing-script')
], style={
    'fontFamily': "'Inter', sans-serif",
    'width': '100%',
    'maxWidth': '1200px',
    'margin': '0 auto',
    'padding': '0 20px'
})

# Create app.clientside_callback to inject JavaScript code
app.clientside_callback(
    """
    function(n_intervals) {
        const text = "Lightning-fast data visualization for everyone.";
        const typingElement = document.getElementById('typing-text');
        
        // Set default content in case JavaScript fails
        if (!typingElement.innerText) {
            typingElement.innerText = text;
        }
        
        // Define typing function
        let i = 0;
        function typeWriter() {
            typingElement.innerHTML = "";
            if (i < text.length) {
                typingElement.innerHTML += text.substring(0, i+1);
                i++;
                setTimeout(typeWriter, 50);
            }
        }
        
        // Only run once when page loads
        if (typingElement && n_intervals === 0) {
            typingElement.innerHTML = ""; // Clear initial text
            setTimeout(typeWriter, 500);
        }
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('typing-script', 'children'),
    Input('typing-text', 'id')
)

# Set the initial text for non-JS browsers or before JS loads
app.clientside_callback(
    """
    function(n_intervals) {
        return "Lightning-fast data visualization for everyone.";
    }
    """,
    Output('typing-text', 'children'),
    Input('typing-text', 'id')
)

# Add custom head tags for fonts
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Dash BC - Data Visualization Platform</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)