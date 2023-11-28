import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Simple Linear Equation Graph"),
    html.Div([
        html.Label('Slope'),
        dcc.Input(id='slope-input', type='number', value=1),
        html.Label('Y-Intercept'),
        dcc.Input(id='y-intercept-input', type='number', value=0),
        html.Button('Submit', id='submit-button', n_clicks=0),
    ]),
    dcc.Graph(id='linear-graph')
])

# Define the callback to update the graph
@app.callback(
    Output('linear-graph', 'figure'),
    Input('submit-button', 'n_clicks'),
    State('slope-input', 'value'),
    State('y-intercept-input', 'value')
)
def update_graph(n_clicks, slope, y_intercept):
    if n_clicks > 0:
        x_vals = list(range(-10, 11))  # X values from -10 to 10
        y_vals = [slope * x + y_intercept for x in x_vals]  # Calculate Y values based on the linear equation

        # Create the plotly figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name='Linear Equation'))

        fig.update_layout(title='Linear Equation Graph',
                          xaxis_title='X-axis',
                          yaxis_title='Y-axis')
        
        return fig
    else:
        return dash.no_update

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
