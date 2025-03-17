from dash import dcc, html, Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import pandas as pd

def register_match_callbacks(app, fighters_df, results_df, stats_df):
    """Register callbacks for the matches tab"""
    @app.callback(
        Output("match-details-content", "children"),
        Input("match-dropdown", "value")
    )
    def update_match_details(match_name):
        if not match_name:
            return html.Div("Please select an event")
        match_data = results_df[results_df['BOUT'] == match_name].iloc[0]
        
        fighter_1 = match_data['FIGHTER_1']
        fighter_2 = match_data['FIGHTER_2']

        # Determine winner
        if match_data['fighter_1_result'] == 1:
            winner = fighter_1
            loser = fighter_2
        else:
            winner = fighter_2
            loser = fighter_1
            
        method_mapping = {0: "ko/tko/could not continue", 1: "submission", 2: "decision", 3:"dq", 4:"overturned"}
        method = method_mapping.get(match_data['method_label'], "Unknown")

        return html.Div([
            html.H4(match_data['EVENT'], className="text-center mb-3"),
            html.P(f"Date: {match_data['DATE']}", className="text-center text-muted mb-4"),
            
            html.Div(className="d-flex justify-content-between align-items-center mb-4", children=[
                html.Div(className="text-center", children=[
                    html.H5(fighter_1, className="mt-2"),
                    html.P(match_data['weight_class'], 
                        className="text-muted")
                ]),
                
                html.Div(className="text-center", children=[
                    html.H3("VS", className="text-danger")
                ]),
                
                html.Div(className="text-center", children=[
                    html.H5(fighter_2, className="mt-2"),
                    html.P(match_data['weight_class'], 
                        className="text-muted")
                ]),
            ]),
            
            html.Div(className="text-center mb-3", children=[
                html.H5("RESULT"),
                html.H4([
                    html.Span(f"Winner: {winner}", className="text-success"),
                ]),
                html.P(f"via {method} - Round {match_data['ROUND']} ({match_data['total_time_seconds']}s)")
            ])
        ])

    @app.callback(
        Output("match-stats-chart", "figure"),
        Input("match-dropdown", "value")
    )
    def update_match_stats(match_name):
        if not match_name:
            return {}

        bout_stats = stats_df[stats_df['BOUT'] == match_name]
        if bout_stats.empty:
            return {} 

        fig = go.Figure()
        
        color_palette = ["#1f77b4","#d62728"]
        
        for i, fighter in enumerate(bout_stats['FIGHTER'].unique()):
            fighter_stats = bout_stats[bout_stats['FIGHTER'] == fighter]
            
            fig.add_trace(go.Scatter(
                x=fighter_stats['ROUND'],
                y=fighter_stats['SIG.STR. %'],
                name=f"{fighter} Sig Strike Accuracy",
                mode='lines+markers',
                line=dict(width=3, color=color_palette[i % len(color_palette)]),
                marker=dict(size=8, symbol="circle"),
                yaxis='y2'
            ))

            fig.add_trace(go.Bar(
                x=fighter_stats['ROUND'],
                y=fighter_stats['sig_str_land'],
                name=f"{fighter} Sig Strikes Landed",
                marker=dict(color=color_palette[i % len(color_palette)], opacity=0.6),  
            ))

        fig.update_layout(
            title=dict(
                text=f"<b>Round Performance: {match_name}</b>",
                y=0.009,
                x=0.5,
                font=dict(size=20, color="white"),
            ),
            xaxis=dict(
                title="<b>Round</b>",
                tickmode="linear",
                tick0=1,
                dtick=1,
                title_font=dict(size=16, color="white"),
                tickfont=dict(size=14, color="white"),
                showgrid=True,
                gridcolor="rgba(255, 255, 255, 0.1)",
                zerolinecolor="rgba(255, 255, 255, 0.2)"
            ),
            yaxis=dict(
                title="<b>Significant Strikes Landed</b>",
                title_font=dict(size=16, color="white"),
                tickfont=dict(size=14, color="white"),
                showgrid=True,
                gridcolor="rgba(255, 255, 255, 0.1)",
                zerolinecolor="rgba(255, 255, 255, 0.2)"
            ),
            yaxis2=dict(
                title="<b>Significant Strike Accuracy (%)</b>",
                title_font=dict(size=16, color="white"),
                tickfont=dict(size=14, color="white"),
                overlaying='y',
                side='right',
                range=[0, 1],
                showgrid=False,
                tickformat=".0%",
                gridcolor="rgba(255, 255, 255, 0.1)",
                zerolinecolor="rgba(255, 255, 255, 0.2)"
            ),
            barmode='group',
            paper_bgcolor="rgba(0, 0, 0, 0)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            legend=dict(
                x=0.5,
                y=1.1,
                orientation="h",
                bgcolor="rgba(0, 0, 0, 0)",
                bordercolor="rgba(255, 255, 255, 0.2)",
                borderwidth=1,
                font=dict(size=14, color="white"),
                xanchor="center",
                yanchor="bottom"
            )
        )
        return fig

    @app.callback(
        Output('strike-distribution', 'figure'),
        Input('match-dropdown', 'value')
    )
    def update_strike_distribution(match_name):
        if not match_name:
            return {}
            
        bout_stats = stats_df[stats_df['BOUT'] == match_name]
        fighters = bout_stats['FIGHTER'].unique()
        
        fig = make_subplots(
            rows=2, 
            cols=2,
            specs=[[{'type': 'pie'}, {'type': 'pie'}],
                [{'type': 'pie'}, {'type': 'pie'}]],
            subplot_titles=[
                f"{fighters[0]} - Attempted", f"{fighters[0]} - Landed",
                f"{fighters[1]} - Attempted", f"{fighters[1]} - Landed"
            ]
        )
        
        colors = ["#636EFA", "#EF553B", "#00CC96"]
        
        for i, fighter in enumerate(fighters):
            fighter_stats = bout_stats[bout_stats['FIGHTER'] == fighter]
            
            head_strikes = fighter_stats['total_head_attempt'].sum()
            body_strikes = fighter_stats['total_body_attempt'].sum()
            leg_strikes = fighter_stats['total_leg_attempt'].sum()
            
            head_strikes_land = fighter_stats['total_head_land'].sum()
            body_strikes_land = fighter_stats['total_body_land'].sum()
            leg_strikes_land = fighter_stats['total_leg_land'].sum()
            
            fig.add_trace(
                go.Pie(
                    labels=['Head', 'Body', 'Leg'],
                    values=[head_strikes, body_strikes, leg_strikes],
                    name=f"{fighter} Attempts",
                    marker=dict(colors=colors),
                    textinfo='percent',
                    hoverinfo='label+value+percent',
                    hole=0.3,
                ),
                row=i+1, col=1
            )
            
            fig.add_trace(
                go.Pie(
                    labels=['Head', 'Body', 'Leg'],
                    values=[head_strikes_land, body_strikes_land, leg_strikes_land],
                    name=f"{fighter} Landed",
                    marker=dict(colors=colors),
                    textinfo='percent',
                    hoverinfo='label+value+percent',
                    hole=0.3,
                ),
                row=i+1, col=2
            )
        
        fig.update_layout(
            title=dict(
                text=f"Strike Distribution: {match_name}",
                font=dict(size=20, color="white")
            ),
            height=600,
            paper_bgcolor="rgba(0, 0, 0, 0)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            font=dict(color="white"),
            showlegend=False,
            margin=dict(t=60, l=40, r=40, b=40)
        )
        
        return fig
    
    @app.callback(
        Output('takedown-analysis', 'figure'),
        Input('match-dropdown', 'value')
    )
    def update_strike_distribution(match_name):
        if not match_name:
            return {}
        attempt_color = "#1f77b4"
        landed_color = "#d62728"
        bout_stats = stats_df[stats_df['BOUT'] == match_name]
        fighters = bout_stats['FIGHTER'].unique()
        fig = go.Figure()
        for fighter in fighters:
            fighter_stats = bout_stats[bout_stats['FIGHTER'] == fighter]
            takedown_attempts = fighter_stats['touchdown_attempt'].sum()
            takedown_land = fighter_stats['takedown_land'].sum()

            fig.add_trace(go.Bar(
                x=['Attempt', 'Landed'],
                y=[takedown_attempts, takedown_land],
                name=fighter,
            ))
        fig.update_layout(
            title=dict(
                text=f"Takedown Success: {match_name}",
                font=dict(size=20, color="white")
            ),
            xaxis_title="Takedowns",
            yaxis_title="Count",
            barmode='group',
            paper_bgcolor="rgba(0, 0, 0, 0)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            font=dict(color="white"),
            legend=dict(
                font=dict(size=14, color="white"),
                bgcolor="rgba(0, 0, 0, 0)",
                bordercolor="rgba(255, 255, 255, 0.2)",
                borderwidth=1
            ),
            xaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.1)",
                zerolinecolor="rgba(255, 255, 255, 0.2)"
            ),
            yaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.1)",
                zerolinecolor="rgba(255, 255, 255, 0.2)"
            ),
            margin=dict(t=60, l=40, r=40, b=40)
        )
        return fig
    
    @app.callback(
        [Output("timeline-slider", "max"),
         Output("timeline-slider", "value"),
         Output("timeline-slider", "marks")],
        Input("match-dropdown", "value")
    )
    def update_timeline_slider_props(match_name):
        if not match_name or match_name not in stats_df['BOUT'].unique():
            max_round = 3
        else:
            bout_stats = stats_df[stats_df['BOUT'] == match_name]
            max_round = int(bout_stats['ROUND'].max()) if not bout_stats.empty else 3
        
        marks = {i: {'label': f'R{i}', 'style': {'color': 'white'}} for i in range(1, max_round + 1)}
        
        return max_round, max_round, marks
    
    @app.callback(
        Output("fight-timeline", "figure"),
        [Input("match-dropdown", "value"),
         Input("timeline-slider", "value")],
    )
    def update_fight_timeline(match_name, selected_round):
        if not match_name:
            return {}
            
        bout_stats = stats_df[stats_df['BOUT'] == match_name].copy()
        if bout_stats.empty:
            return {}
            
        fighters = bout_stats['FIGHTER'].unique()
        if len(fighters) != 2:
            return {}
        
        bout_stats['ROUND'] = pd.to_numeric(bout_stats['ROUND'], errors='coerce')
        bout_stats = bout_stats.dropna(subset=['ROUND'])
        bout_stats['ROUND'] = bout_stats['ROUND'].astype(int)
        
        if selected_round is not None:
            selected_round = int(selected_round)
        else:
            selected_round = bout_stats['ROUND'].max()
        
        filtered_stats = bout_stats[bout_stats['ROUND'] <= selected_round]
        
        fig = go.Figure()
        
        for fighter_idx, fighter in enumerate(fighters):
            fighter_stats = filtered_stats[filtered_stats['FIGHTER'] == fighter]
            
            if fighter_stats.empty:
                continue

            round_stats = fighter_stats.groupby('ROUND').agg({
                'sig_str_land': 'sum',
                'sig_str_attempt': 'sum',
                'total_str_land': 'sum',
                'takedown_land': 'sum',
                'touchdown_attempt': 'sum' 
            }).reset_index()
            
            round_stats['cum_sig_strikes'] = round_stats['sig_str_land'].cumsum()
            round_stats['cum_takedowns'] = round_stats['takedown_land'].cumsum()
            
            fig.add_trace(go.Scatter(
                x=round_stats['ROUND'],
                y=round_stats['cum_sig_strikes'],
                mode='lines+markers',
                name=f"{fighter} - Sig. Strikes",
                line=dict(width=3, color='red' if fighter_idx == 0 else 'blue'),
                marker=dict(size=8)
            ))
            
            fig.add_trace(go.Scatter(
                x=round_stats['ROUND'],
                y=round_stats['cum_takedowns'] * 5,
                mode='lines+markers',
                name=f"{fighter} - Takedowns (×5)",
                line=dict(width=2, dash='dot', color='darkred' if fighter_idx == 0 else 'darkblue'),
                marker=dict(symbol='diamond', size=8)
            ))
        
        fig.update_layout(
            title=dict(
                text=f"Fight Progression: {match_name}",
                font=dict(size=20, color="white")
            ),
            xaxis=dict(
                title="Round",
                tickmode='array',
                tickvals=list(range(1, int(bout_stats['ROUND'].max()) + 1)),
                ticktext=[f"R{r}" for r in range(1, int(bout_stats['ROUND'].max()) + 1)],
                gridcolor="rgba(255, 255, 255, 0.1)",
                zerolinecolor="rgba(255, 255, 255, 0.2)"
            ),
            yaxis=dict(
                title="Cumulative Stats",
                gridcolor="rgba(255, 255, 255, 0.1)",
                zerolinecolor="rgba(255, 255, 255, 0.2)"
            ),
            paper_bgcolor="rgba(0, 0, 0, 0)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            font=dict(color="white"),
            legend=dict(
                font=dict(color="white"),
                bgcolor="rgba(0, 0, 0, 0)",
                bordercolor="rgba(255, 255, 255, 0.2)",
                borderwidth=1
            ),
            margin=dict(t=60, l=40, r=40, b=40)
        )
        
        return fig
    
    @app.callback(
        Output("fight-round-distribution", "figure"),
        [Input("match-dropdown", "value"),
         Input("timeline-slider", "value")],
    )
    def update_round_strike_distribution(match_name, selected_round):
        if not match_name:
            return {}
            
        bout_stats = stats_df[stats_df['BOUT'] == match_name].copy()
        if bout_stats.empty:
            return {}
                
        fighters = bout_stats['FIGHTER'].unique()
        if len(fighters) != 2:
            return {}
        
        bout_stats['ROUND'] = pd.to_numeric(bout_stats['ROUND'], errors='coerce')
        bout_stats = bout_stats.dropna(subset=['ROUND'])
        bout_stats['ROUND'] = bout_stats['ROUND'].astype(int)
        
        if selected_round is not None:
            selected_round = int(selected_round)
        else:
            selected_round = bout_stats['ROUND'].max()
        
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "pie"}, {"type": "pie"}]],
            subplot_titles=(f"{fighters[0]} - Round {selected_round}", f"{fighters[1]} - Round {selected_round}")
        )
        
        for fighter_idx, fighter in enumerate(fighters):
            selected_round_stats = bout_stats[(bout_stats['FIGHTER'] == fighter) & (bout_stats['ROUND'] == selected_round)]
            
            if not selected_round_stats.empty:
                head_strikes = selected_round_stats['total_head_land'].sum()
                body_strikes = selected_round_stats['total_body_land'].sum()
                leg_strikes = selected_round_stats['total_leg_land'].sum()
                
                colors = ["#636EFA", "#EF553B", "#00CC96"]
                
                fig.add_trace(
                    go.Pie(
                        labels=['Head', 'Body', 'Leg'],
                        values=[head_strikes, body_strikes, leg_strikes],
                        textinfo='percent',
                        hoverinfo='label+value+percent',
                        marker=dict(colors=colors),
                        hole=0.3,
                    ),
                    row=1, col=fighter_idx+1
                )
        
        fig.update_layout(
            title=dict(
                text=f"Strike Distribution in Round {selected_round}",
                font=dict(size=20, color="white")
            ),
            height=350,
            paper_bgcolor="rgba(0, 0, 0, 0)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            font=dict(color="white"),
            showlegend=True,
            legend=dict(
                font=dict(color="white"),
                bgcolor="rgba(0, 0, 0, 0)",
                bordercolor="rgba(255, 255, 255, 0.2)",
                borderwidth=1
            ),
            margin=dict(t=60, l=40, r=40, b=40)
        )
        
        return fig
