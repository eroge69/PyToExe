
import dash
from dash import dcc, html, Input, Output, State, ctx
import pandas as pd
import plotly.express as px
import base64
import io

app = dash.Dash(__name__)
app.title = "Universal Animated Dashboard"

# Layout
app.layout = html.Div([
    html.H2("📊 Universal Animated Dashboard", style={"textAlign": "center"}),

    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select an Excel File (.xlsx)')
        ]),
        style={
            'width': '100%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed',
            'borderRadius': '5px', 'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),

    html.Div(id='dropdown-container', style={'display': 'none'}),

    html.Div([
        dcc.Graph(id='animated-chart')
    ])
])

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if filename.endswith('.xlsx'):
        return pd.read_excel(io.BytesIO(decoded))
    else:
        return None

@app.callback(
    Output('dropdown-container', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_dropdowns(contents, filename):
    if contents is None:
        return dash.no_update
    df = parse_contents(contents, filename)
    if df is None or df.empty:
        return html.Div("Failed to load the file.")

    columns = [{'label': col, 'value': col} for col in df.columns]

    return html.Div([
        html.Div([
            html.Label("X-axis:"), dcc.Dropdown(id='x-axis', options=columns)
        ], style={"width": "24%", "display": "inline-block", "padding": "10px"}),

        html.Div([
            html.Label("Y-axis:"), dcc.Dropdown(id='y-axis', options=columns)
        ], style={"width": "24%", "display": "inline-block", "padding": "10px"}),

        html.Div([
            html.Label("Animation Frame (optional):"),
            dcc.Dropdown(id='anim-axis', options=columns)
        ], style={"width": "24%", "display": "inline-block", "padding": "10px"}),

        html.Div([
            html.Label("Filter Column (optional):"),
            dcc.Dropdown(id='filter-col', options=columns)
        ], style={"width": "24%", "display": "inline-block", "padding": "10px"}),

        html.Div([
            html.Label("Filter Value (optional):"),
            dcc.Dropdown(id='filter-val')
        ], style={"width": "24%", "display": "inline-block", "padding": "10px"}),

        dcc.Store(id='stored-data', data=df.to_dict('records')),

    ], style={'display': 'block'})

@app.callback(
    Output('filter-val', 'options'),
    Input('filter-col', 'value'),
    State('stored-data', 'data')
)
def update_filter_values(col, data):
    if col and data:
        df = pd.DataFrame(data)
        return [{'label': i, 'value': i} for i in sorted(df[col].dropna().unique())]
    return []

@app.callback(
    Output('animated-chart', 'figure'),
    Input('x-axis', 'value'),
    Input('y-axis', 'value'),
    Input('anim-axis', 'value'),
    Input('filter-col', 'value'),
    Input('filter-val', 'value'),
    State('stored-data', 'data')
)
def update_graph(x, y, anim, f_col, f_val, data):
    if not all([x, y, data]):
        return {}
    df = pd.DataFrame(data)
    if f_col and f_val:
        df = df[df[f_col] == f_val]

    try:
        fig = px.bar(df, x=x, y=y, animation_frame=anim) if anim else px.bar(df, x=x, y=y)
        fig.update_layout(transition_duration=500)
        return fig
    except Exception as e:
        return px.scatter(title=f"Error in rendering: {str(e)}")

if __name__ == '__main__':
    app.run_server(debug=True)
