from dash import Dash, html

app = Dash(__name__) #This line is known as the Dash constructor and is responsible for initializing your app.

#The app layout represents the app components that will be displayed in the web browser, 
#normally contained within a html.Div. In this example, a single component was added: another html.Div.
app.layout = html.Div([
    html.Div(children='Hello World')
])

#These lines are for running your app, and they are almost always the same for any Dash app you create.
if __name__ == '__main__':
    app.run(debug=True)