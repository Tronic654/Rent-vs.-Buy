import dash
from dash import dcc, html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# Define the layout for different "pages"
page_1_layout = html.Div([
    html.H1('Page 1 Content'),
    html.P('This is the content of Page 1.'),
])

page_2_layout = html.Div([
    html.H1('Page 2 Content'),
    html.P('This is the content of Page 2.'),
])

# Define the main layout that includes the navigation and the pages
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('Page 1', href='/page-1'),
        html.Span(' | '),
        dcc.Link('Page 2', href='/page-2'),
    ]),
    html.Div(id='page-content')
])

# Define callback to change the content based on the URL
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    else:
        return '404 Page Not Found'

if __name__ == '__main__':
    app.run_server(debug=True)
