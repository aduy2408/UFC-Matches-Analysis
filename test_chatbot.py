from dash import Dash, html, dcc, Input, Output, State, callback
from openai import OpenAI
import time

# Initialize the Perplexity client
client = OpenAI(api_key="YOUR_API_KEY_HERE", base_url="https://api.perplexity.ai")

# Initialize the Dash app
app = Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1("Sonar Chatbot Dashboard", style={'textAlign': 'center', 'color': '#ffffff'}),
    html.Div([
        dcc.Input(
            id="user-input",
            type="text",
            placeholder="Ask a question...",
            style={'width': '70%', 'padding': '10px', 'marginRight': '10px'}
        ),
        html.Button("Submit", id="submit-button", n_clicks=0, style={'padding': '10px 20px'})
    ], style={'display': 'flex', 'justifyContent': 'center', 'margin': '20px 0'}),
    html.Div(id="response-output", style={
        'padding': '20px', 
        'border': '1px solid #ccc', 
        'borderRadius': '5px', 
        'backgroundColor': '#2b2b2b', 
        'color': '#ffffff', 
        'maxWidth': '800px', 
        'margin': '0 auto',
        'whiteSpace': 'pre-wrap'  # Preserve line breaks and spacing
    })
], style={'backgroundColor': '#1a1a1a', 'minHeight': '100vh', 'padding': '20px'})

# Callback to handle user input and API response with "..." loading effect
@callback(
    Output("response-output", "children"),
    Input("submit-button", "n_clicks"),
    State("user-input", "value"),
    prevent_initial_call=True
)
def update_response(n_clicks, user_input):
    if not user_input:
        return "Please enter a question."

    # Step 1: Immediately show "..." to indicate loading
    yield "..."  # This won't work directly in Dash; we simulate it below with a multi-stage callback

    # Define the conversation for the Sonar API
    messages = [
        {"role": "system", "content": "You are a helpful chatbot powered by Perplexity Sonar."},
        {"role": "user", "content": user_input}
    ]

    try:
        # Send request to Sonar API
        response = client.chat.completions.create(
            model="sonar",  # Use "sonar" for the base version if preferred
            messages=messages
        )
        bot_response = response.choices[0].message.content

        # Step 2: Return the final response formatted as Markdown
        return dcc.Markdown(f"**Response:**\n{bot_response}")
    except Exception as e:
        return f"Error: {str(e)}"

# Enhanced version with "..." effect using a multi-step callback
@callback(
    Output("response-output", "children"),
    Input("submit-button", "n_clicks"),
    State("user-input", "value"),
    prevent_initial_call=True
)
def update_response_with_loading(n_clicks, user_input):
    if not user_input:
        return "Please enter a question."

    # Step 1: Show "..." immediately
    # Dash doesn't support yielding directly, so we use a simple delay to simulate loading
    from dash import no_update
    import threading

    # Initial response with "..."
    output = html.Div("...")

    def fetch_response():
        messages = [
            {"role": "system", "content": "You are a helpful chatbot powered by Perplexity Sonar."},
            {"role": "user", "content": user_input}
        ]
        try:
            response = client.chat.completions.create(model="sonar-pro", messages=messages)
            bot_response = response.choices[0].message.content
            app.server.clients[n_clicks] = dcc.Markdown(f"**Response:**\n{bot_response}")
        except Exception as e:
            app.server.clients[n_clicks] = f"Error: {str(e)}"

    # Start API call in a separate thread to allow "..." to display first
    thread = threading.Thread(target=fetch_response)
    thread.start()

    # Return "..." initially, then rely on a secondary callback or client-side logic to update
    return output

# Secondary callback to check for the final response (simplified polling approach)
app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            setTimeout(function() {
                // This is a simplified check; in practice, use a proper server-side state or WebSocket
                fetch('/get_response?n_clicks=' + n_clicks)
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('response-output').innerHTML = data.response;
                    });
            }, 1000);  // Poll after 1 second
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("response-output", "children"),
    Input("submit-button", "n_clicks")
)

# Flask route to serve the final response
@app.server.route('/get_response')
def get_response():
    from flask import request, jsonify
    n_clicks = int(request.args.get('n_clicks', 0))
    response = app.server.clients.get(n_clicks, "Waiting for response...")
    if isinstance(response, str) and "Waiting" in response:
        return jsonify({"response": "..."})
    return jsonify({"response": response.to_json() if hasattr(response, 'to_json') else str(response)})

# Run the app
if __name__ == "__main__":
    app.run(debug=True)