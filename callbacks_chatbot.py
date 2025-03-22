from dash import Input, Output, State, callback, html, callback_context, no_update
from openai import OpenAI
import re
from config import PERPLEXITY_API_KEY, PERPLEXITY_BASE_URL

client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url=PERPLEXITY_BASE_URL)

def format_markdown_text(text):
    # Split into paragraphs
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    formatted_content = []
    
    for p in paragraphs:
        # Handle headers
        if p.startswith('####'):
            formatted_content.append(html.H4(p.lstrip('#').strip(), className="text-danger mb-3"))
            continue
        if p.startswith('###'):
            formatted_content.append(html.H3(p.lstrip('#').strip(), className="text-danger mb-3"))
            continue
        elif p.startswith('##'):
            formatted_content.append(html.H2(p.lstrip('#').strip(), className="text-danger mb-3"))
            continue
        elif p.startswith('#'):
            formatted_content.append(html.H1(p.lstrip('#').strip(), className="text-danger mb-3"))
            continue
        
        # Handle lists
        if p.startswith(('• ', '* ', '- ')):
            items = [item.strip() for item in p.split('\n') if item.strip()]
            list_items = []
            for item in items:
                # Handle bold text within list items
                item_parts = re.split(r'(\*\*.*?\*\*|__.*?__)', item.lstrip('• *- ').strip())
                formatted_parts = []
                for part in item_parts:
                    if not part:
                        continue
                    if (part.startswith('**') and part.endswith('**')) or (part.startswith('__') and part.endswith('__')):
                        formatted_parts.append(html.Strong(part[2:-2]))
                    else:
                        formatted_parts.append(part)
                list_items.append(html.Li(formatted_parts))
            formatted_content.append(html.Ul(list_items))
        
        # Handle numbered lists
        elif re.match(r'^\d+\.', p):
            items = [item.strip() for item in p.split('\n') if item.strip()]
            list_items = []
            for item in items:
                # Extract content after number and handle bold text
                content = item.split('. ', 1)[1] if '. ' in item else item
                parts = re.split(r'(\*\*.*?\*\*|__.*?__)', content)
                formatted_parts = []
                for part in parts:
                    if not part:
                        continue
                    if (part.startswith('**') and part.endswith('**')) or (part.startswith('__') and part.endswith('__')):
                        formatted_parts.append(html.Strong(part[2:-2]))
                    else:
                        formatted_parts.append(part)
                list_items.append(html.Li(formatted_parts))
            formatted_content.append(html.Ol(list_items))
        
        else:  # Regular paragraph
            # Split the text by bold markers
            parts = re.split(r'(\*\*.*?\*\*|__.*?__|\[.*?\])', p)
            # Process each part
            formatted_parts = []
            for part in parts:
                if not part:  # Skip empty parts
                    continue
                if (part.startswith('**') and part.endswith('**')) or (part.startswith('__') and part.endswith('__')):
                    # Remove the markers and create Strong component
                    clean_text = part[2:-2]
                    formatted_parts.append(html.Strong(clean_text))
                elif part.startswith('[') and part.endswith(']'):
                    # Handle citation references
                    formatted_parts.append(html.Sup(part, className="text-danger"))
                else:
                    formatted_parts.append(part)
            formatted_content.append(html.P(formatted_parts))
    
    return formatted_content

@callback(
    [Output("chat-window", "style"),
     Output("chat-message-input", "autoFocus"),
     Output("temp-messages", "data")],
    [Input("chat-button", "n_clicks"),
     Input("close-chat", "n_clicks")],
    [State("temp-messages", "data")],
    prevent_initial_call=True
)
def toggle_chat_window(open_clicks, close_clicks, existing_messages):
    if not open_clicks and not close_clicks:
        return {"display": "none"}, False, []
    
    ctx = callback_context
    if not ctx.triggered:
        return {"display": "none"}, False, []
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "chat-button":
        welcome_message = {
            "type": "bot",
            "message": """### Welcome to UFC Analytics Assistant! 👋

I'm your expert UFC analyst chatbot powered by **Group 5 AI18D02**. I can help you with:

• **Fighter Statistics** and performance analysis
• **Match History** and fight breakdowns
• **Ben xe lua

Feel free to ask me anything about UFC - I'll analyze data and provide detailed insights backed by reliable sources.

"""

        }
        return {"display": "flex"}, True, [welcome_message]
    return {"display": "none"}, False, []

@callback(
    [Output("temp-messages", "data", allow_duplicate=True),
     Output("chat-message-input", "value")],
    [Input("send-message", "n_clicks"),
     Input("chat-message-input", "n_submit")],
    [State("chat-message-input", "value"),
     State("temp-messages", "data")],
    prevent_initial_call=True
)
def update_temp_messages(n_clicks, n_submit, message, existing_messages):
    if not message:
        return existing_messages or [], ""
    
    existing_messages = existing_messages or []
    
    new_messages = [
        *existing_messages,
        {"type": "user", "message": message},
        {"type": "typing"}
    ]
    
    return new_messages, ""

@callback(
    [Output("chat-messages", "children"),
     Output("chat-messages", "style")],
    [Input("temp-messages", "data")],
    prevent_initial_call=True
)
def render_messages(messages):
    if not messages:
        return [], {"overflowY": "auto"}
    
    rendered_messages = []
    for msg in messages:
        if msg["type"] == "user":
            rendered_messages.append(
                html.Div(msg["message"], className="chat-message user-message")
            )
        elif msg["type"] == "bot":
            formatted_content = format_markdown_text(msg["message"])
            rendered_messages.append(
                html.Div(formatted_content, className="chat-message bot-message")
            )
        elif msg["type"] == "typing":
            rendered_messages.append(
                html.Div([
                    html.Div(className="typing-circle"),
                    html.Div(className="typing-circle"),
                    html.Div(className="typing-circle")
                ], className="typing-indicator")
            )
    # Return messages and scroll settings
    return rendered_messages, {
        "overflowY": "auto",
        "scrollBehavior": "smooth",
        "scrollTop": "100000vh",
        "maxHeight": "calc(100% - 120px)"  
    }

@callback(
    Output("temp-messages", "data", allow_duplicate=True),
    [Input("temp-messages", "data")],
    prevent_initial_call=True
)
def process_bot_response(messages):
    if not messages or messages[-1]["type"] != "typing":
        return no_update
    
    try:
        # Send request to Perplexity AI
        response = client.chat.completions.create(
            model="sonar",
            messages=[
                {"role": "system", "content": """You are an expert UFC analyst chatbot made by Group 5 AI18D02. Answer like someone from the betting site lol.

Always structure your responses with these formatting rules:

1. Start each main topic with a ### header
2. Place a blank line after each header
3. Use **bold text** for fighter names, statistics
4. Use bullet points (•) for listing attributes or characteristics
5. Use numbered lists (1., 2., etc.) for sequential events or rankings
6. When citing sources, use [1], [2], etc. and include sources at the end
7. Separate sections with blank lines for better readability
8. Keep responses focused and well-organized
9. Dont put random things in code block format
10. Always focus your responses on UFC fighters, matches, and statistics, dont go off-topic.

Example structure:
### Fighter Profile
**John Doe** is a UFC veteran with...

### Fighting Style
• **Striking**: Known for powerful...
• **Ground Game**: Black belt in...

### Recent Performance
1. Won against **Mike Smith** [1]
2. Lost to **Tom Jones** [2]

"""},
                {"role": "user", "content": messages[-2]["message"]}  # Get the last user message
            ],
        )
        bot_response = response.choices[0].message.content
        
        # Replace typing indicator with bot response
        messages = [
            msg for msg in messages[:-1]  # Remove typing indicator
            if msg["type"] != "typing"    # Remove any stray typing indicators
        ]
        messages.append({"type": "bot", "message": bot_response})
        
        return messages
        
    except Exception as e:
        # Replace typing indicator with error message
        messages = [
            msg for msg in messages[:-1]  # Remove typing indicator
            if msg["type"] != "typing"    # Remove any stray typing indicators
        ]
        messages.append({"type": "bot", "message": f"Sorry, I encountered an error: {str(e)}"})
        return messages
