import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import json
from physics import Ball, BilliardTable, PhysicsEngine

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Billiard Physics Dashboard"

# Initialize physics engine with default parameters
table = BilliardTable()
physics_engine = PhysicsEngine(table)
physics_engine.setup_rack()

def run_simulation(initial_velocity, friction, cushion_elasticity, simulation_time=5.0, dt=0.01):
    """
    Run a simulation with the given parameters and return the results.
    
    Args:
        initial_velocity: Initial velocity for the cue ball [vx, vy]
        friction: Table friction coefficient
        cushion_elasticity: Cushion elasticity coefficient
        simulation_time: Duration of simulation in seconds
        dt: Time step in seconds
        
    Returns:
        dict: Simulation results with ball trajectories
    """
    # Create a new physics engine for this simulation
    table = BilliardTable(friction=friction, cushion_elasticity=cushion_elasticity)
    engine = PhysicsEngine(table)
    engine.setup_rack()
    
    # Set initial velocity for cue ball
    for ball in engine.active_balls:
        if ball.number == 0:  # Cue ball
            ball.velocity = np.array(initial_velocity)
    
    # Run simulation for the specified time
    time_points = np.arange(0, simulation_time, dt)
    
    # Store positions of each ball at each time point
    trajectories = {ball.number: {'x': [], 'y': []} for ball in engine.balls}
    pocketed = {ball.number: False for ball in engine.balls}
    
    # Run simulation
    for _ in time_points:
        # Update physics
        engine.update(dt)
        
        # Record positions
        for ball in engine.balls:
            if ball in engine.active_balls:
                trajectories[ball.number]['x'].append(ball.position[0])
                trajectories[ball.number]['y'].append(ball.position[1])
            elif not pocketed[ball.number]:
                # Ball was pocketed during this time step
                pocketed[ball.number] = True
                
    # Format final velocities
    final_velocities = {}
    for ball in engine.active_balls:
        final_velocities[ball.number] = np.linalg.norm(ball.velocity)
    
    # Package results
    results = {
        'trajectories': trajectories,
        'pocketed': pocketed,
        'final_velocities': final_velocities,
        'parameters': {
            'initial_velocity': initial_velocity,
            'friction': friction,
            'cushion_elasticity': cushion_elasticity,
            'simulation_time': simulation_time
        }
    }
    
    return results

# Layout for the dashboard
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Billiard Physics Simulation Dashboard", className="text-center my-4")
        ])
    ]),
    
    dbc.Row([
        # Simulation parameters panel
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Simulation Parameters"),
                dbc.CardBody([
                    # Cue ball velocity inputs
                    html.H5("Cue Ball Initial Velocity"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("X-Velocity (m/s)"),
                            dcc.Slider(
                                id="velocity-x-slider",
                                min=-5, max=5, step=0.1, value=2,
                                marks={i: f"{i}" for i in range(-5, 6)},
                                tooltip={"placement": "bottom", "always_visible": True}
                            ),
                        ]),
                        dbc.Col([
                            html.Label("Y-Velocity (m/s)"),
                            dcc.Slider(
                                id="velocity-y-slider",
                                min=-5, max=5, step=0.1, value=0,
                                marks={i: f"{i}" for i in range(-5, 6)},
                                tooltip={"placement": "bottom", "always_visible": True}
                            ),
                        ]),
                    ]),
                    
                    html.Hr(),
                    
                    # Table physics parameters
                    html.H5("Table Physics"),
                    html.Label("Friction Coefficient"),
                    dcc.Slider(
                        id="friction-slider",
                        min=0.01, max=0.1, step=0.01, value=0.03,
                        marks={i/100: f"{i/100}" for i in range(1, 11, 1)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    
                    html.Label("Cushion Elasticity"),
                    dcc.Slider(
                        id="elasticity-slider",
                        min=0.5, max=1.0, step=0.05, value=0.7,
                        marks={i/10: f"{i/10}" for i in range(5, 11, 1)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    
                    html.Label("Simulation Time (s)"),
                    dcc.Slider(
                        id="time-slider",
                        min=1, max=10, step=0.5, value=5,
                        marks={i: f"{i}" for i in range(1, 11, 1)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    
                    html.Hr(),
                    
                    dbc.Button("Run Simulation", id="run-button", color="primary", className="w-100 mt-3"),
                ]),
            ], className="mb-4"),
            
            # Results summary card
            dbc.Card([
                dbc.CardHeader("Simulation Results"),
                dbc.CardBody(id="results-summary")
            ])
        ], width=4),
        
        # Visualization panel
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Billiard Table Visualization"),
                dbc.CardBody([
                    dcc.Graph(
                        id="billiard-plot",
                        style={"height": "60vh"},
                        config={"displayModeBar": True}
                    )
                ])
            ]),
            
            dbc.Card([
                dbc.CardHeader("Ball Velocities Over Time"),
                dbc.CardBody([
                    dcc.Graph(
                        id="velocity-plot",
                        style={"height": "30vh"},
                    )
                ])
            ], className="mt-4")
        ], width=8)
    ]),
    
    # Hidden div to store simulation results
    html.Div(id="simulation-results", style={"display": "none"}),
    
    # Footer with instructions
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P([
                "This dashboard demonstrates the physics of billiard ball collisions. ",
                "Adjust the parameters and run the simulation to see the ball trajectories and velocities.",
                html.Br(),
                "To run the full interactive visualization, run ", html.Code("python main.py"), " in your terminal."
            ], className="text-center text-muted")
        ])
    ])
], fluid=True)

# Callback to run simulation when button is clicked
@app.callback(
    Output("simulation-results", "children"),
    [Input("run-button", "n_clicks")],
    [State("velocity-x-slider", "value"),
     State("velocity-y-slider", "value"),
     State("friction-slider", "value"),
     State("elasticity-slider", "value"),
     State("time-slider", "value")]
)
def run_simulation_callback(n_clicks, vx, vy, friction, elasticity, sim_time):
    if n_clicks is None:
        # Default simulation results
        results = run_simulation([2, 0], 0.03, 0.7, 5.0)
    else:
        # Run simulation with user-provided parameters
        results = run_simulation([vx, vy], friction, elasticity, sim_time)
    
    # Return results as JSON
    return json.dumps(results)

# Callback to update the billiard table plot
@app.callback(
    Output("billiard-plot", "figure"),
    [Input("simulation-results", "children")]
)
def update_billiard_plot(results_json):
    if not results_json:
        return go.Figure()
    
    results = json.loads(results_json)
    
    # Create figure with the table dimensions
    fig = go.Figure()
    
    # Set up the plot as a billiard table
    table_length = 2.7  # meters
    table_width = 1.35  # meters
    
    # Draw the table
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=table_length, y1=table_width,
        fillcolor="green",
        line=dict(color="darkgreen", width=2)
    )
    
    # Add pockets (simplified positions)
    pocket_radius = 0.06
    pockets = [
        (0.04, 0.04),  # Top left
        (table_length - 0.04, 0.04),  # Top right
        (0.04, table_width - 0.04),  # Bottom left
        (table_length - 0.04, table_width - 0.04),  # Bottom right
        (table_length / 2, 0),  # Middle top
        (table_length / 2, table_width)  # Middle bottom
    ]
    
    for x, y in pockets:
        fig.add_shape(
            type="circle",
            x0=x - pocket_radius, y0=y - pocket_radius,
            x1=x + pocket_radius, y1=y + pocket_radius,
            fillcolor="black",
            line=dict(color="black")
        )
    
    # Plot ball trajectories
    ball_colors = {
        0: 'white',  # Cue ball
        8: 'black',  # 8-ball
    }
    
    # Generate colors for other balls
    for i in range(1, 16):
        if i != 8:  # Skip the 8-ball which is already black
            if i < 8:
                # Solid colors
                hue = (i - 1) / 7
                ball_colors[i] = f"hsl({int(hue * 360)}, 100%, 50%)"
            else:
                # Striped balls - use the same color as solids but with lower opacity
                hue = (i - 9) / 7
                ball_colors[i] = f"hsl({int(hue * 360)}, 100%, 50%)"
    
    # Plot trajectories for each ball
    for ball_num, trajectory in results['trajectories'].items():
        ball_num = int(ball_num)
        x_vals = trajectory['x']
        y_vals = trajectory['y']
        
        # Skip if no trajectory data
        if not x_vals:
            continue
        
        color = ball_colors.get(ball_num, 'gray')
        
        # Add line for ball trajectory
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode='lines',
            line=dict(color=color, width=1, dash='dot'),
            name=f"Ball {ball_num} path",
            showlegend=False
        ))
        
        # Add marker for final position
        if not results['pocketed'].get(str(ball_num), False):
            fig.add_trace(go.Scatter(
                x=[x_vals[-1]],
                y=[y_vals[-1]],
                mode='markers',
                marker=dict(
                    color=color,
                    size=12,
                    line=dict(color='black', width=1)
                ),
                name=f"Ball {ball_num}",
                text=str(ball_num),
                hoverinfo='text'
            ))
    
    # Format the layout
    fig.update_layout(
        title="Billiard Ball Trajectories",
        xaxis=dict(
            title="X Position (m)",
            range=[-0.1, table_length + 0.1],
            constrain="domain"
        ),
        yaxis=dict(
            title="Y Position (m)",
            range=[-0.1, table_width + 0.1],
            scaleanchor="x",
            scaleratio=1
        ),
        margin=dict(l=50, r=50, t=50, b=50),
        plot_bgcolor="green",
        paper_bgcolor="white",
        hovermode="closest"
    )
    
    return fig

# Callback to update the results summary
@app.callback(
    Output("results-summary", "children"),
    [Input("simulation-results", "children")]
)
def update_results_summary(results_json):
    if not results_json:
        return "Run a simulation to see results."
    
    results = json.loads(results_json)
    
    # Get parameters
    params = results['parameters']
    vx, vy = params['initial_velocity']
    speed = np.sqrt(vx**2 + vy**2)
    
    # Count pocketed balls
    pocketed_count = sum(1 for is_pocketed in results['pocketed'].values() if is_pocketed)
    
    # Cue ball status
    cue_ball_pocketed = results['pocketed'].get('0', False)
    cue_ball_status = "Pocketed" if cue_ball_pocketed else "On table"
    
    # Eight ball status
    eight_ball_pocketed = results['pocketed'].get('8', False)
    eight_ball_status = "Pocketed" if eight_ball_pocketed else "On table"
    
    # Format stats
    stats = html.Div([
        html.H5("Shot Statistics"),
        html.P([
            html.Strong("Initial Speed: "), f"{speed:.2f} m/s",
            html.Br(),
            html.Strong("Angle: "), f"{np.arctan2(vy, vx) * 180 / np.pi:.1f}°",
        ]),
        
        html.H5("Ball Statistics"),
        html.P([
            html.Strong("Balls Pocketed: "), f"{pocketed_count} / 16",
            html.Br(),
            html.Strong("Cue Ball: "), cue_ball_status,
            html.Br(),
            html.Strong("Eight Ball: "), eight_ball_status,
        ]),
        
        html.H5("Physics Parameters"),
        html.P([
            html.Strong("Friction: "), f"{params['friction']:.2f}",
            html.Br(),
            html.Strong("Cushion Elasticity: "), f"{params['cushion_elasticity']:.2f}",
            html.Br(),
            html.Strong("Simulation Time: "), f"{params['simulation_time']:.1f} seconds",
        ]),
    ])
    
    return stats

# Callback to update the velocity plot
@app.callback(
    Output("velocity-plot", "figure"),
    [Input("simulation-results", "children")]
)
def update_velocity_plot(results_json):
    if not results_json:
        return go.Figure()
    
    results = json.loads(results_json)
    
    # Create velocity figure
    fig = go.Figure()
    
    # We would need velocity over time data for a proper plot
    # For now, just show the final velocities of active balls
    final_vels = results['final_velocities']
    ball_numbers = list(final_vels.keys())
    velocities = list(final_vels.values())
    
    # If we have velocity data
    if velocities:
        # Sort by ball number
        ball_numbers = [int(n) for n in ball_numbers]
        ball_numbers, velocities = zip(*sorted(zip(ball_numbers, velocities)))
        
        # Plot the data
        fig.add_trace(go.Bar(
            x=[f"Ball {n}" for n in ball_numbers],
            y=velocities,
            marker_color=['white' if n == 0 else 'black' if n == 8 else 'red' 
                          for n in ball_numbers],
            text=[f"{v:.2f} m/s" for v in velocities],
            textposition="auto"
        ))
        
        # Format layout
        fig.update_layout(
            title="Final Ball Velocities",
            xaxis_title="Ball",
            yaxis_title="Velocity (m/s)",
            yaxis=dict(range=[0, max(velocities) * 1.1 if velocities else 1]),
            margin=dict(l=50, r=50, t=50, b=50),
        )
    else:
        # Empty plot with message
        fig.update_layout(
            title="No velocity data available",
            xaxis_title="Ball",
            yaxis_title="Velocity (m/s)",
        )
    
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
