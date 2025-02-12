import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from pathlib import Path
import os

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], suppress_callback_exceptions=True)
server = app.server

# Load data
current_dir = Path(__file__).parent
data = pd.read_csv(current_dir / 'data.csv')

# Landing page layout
landing_layout = html.Div([
    html.Header([
        html.Div([
            html.H1("CarbonWatch", className="header-title animate-slide"),
            html.P("Tracking Global Emissions", className="header-subtitle animate-fade")
        ], className="header-content")
    ], className="header"),
    
    html.Section([
        html.Div([
            html.H2("Our Climate Challenge", className="animate-pop"),
            html.P("Every ton of CO₂ impacts our future", className="animate-fade"),
            dcc.Link(
                html.Button("Explore Dashboard", className="cta-button animate-pulse"),
                href="/dashboard"
            )
        ], className="hero-content")
    ], className="hero"),
    
    html.Section([
        html.Div([
            html.Div([
                html.I(className="fas fa-industry"),
                html.H3("Energy Production"),
                html.P("Accounts for 35% of global emissions")
            ], className="fact-card"),
            html.Div([
                html.I(className="fas fa-car"),
                html.H3("Transportation"),
                html.P("Responsible for 20% of CO₂ output")
            ], className="fact-card"),
            html.Div([
                html.I(className="fas fa-tree"),
                html.H3("Deforestation"),
                html.P("Causes 10% of annual emissions")
            ], className="fact-card")
        ], className="facts-grid")
    ], className="facts"),
    
    html.Footer([
        html.P("© 2024 CarbonWatch. Data from IPCC reports.")
    ], className="footer")
])

# Dashboard layout
dashboard_layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Carbon Emissions Dashboard", className="text-center mb-4"), width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='country-selector',
                options=[{'label': 'All Countries', 'value': 'All'}] + 
                        [{'label': c, 'value': c} for c in data['Country Name'].unique()],
                value='All',
                className='mb-3'
            )
        ], md=6),
        dbc.Col([
            dcc.Dropdown(
                id='year-selector',
                options=[{'label': y, 'value': y} for y in data['Year'].unique()],
                value=2022,
                className='mb-3'
            )
        ], md=6)
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='bar-chart'), md=6),
        dbc.Col(dcc.Graph(id='pie-chart'), md=6)
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='line-chart'), md=12)
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Link("Back to Home", href="/", className="btn btn-outline-light mt-4"))
    ])
], fluid=True)

# App layout and routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callbacks
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/dashboard':
        return dashboard_layout
    return landing_layout

@app.callback(
    [Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure'),
     Output('line-chart', 'figure')],
    [Input('country-selector', 'value'),
     Input('year-selector', 'value')]
)
def update_graphs(selected_country, selected_year):
    # Bar Chart
    if selected_country == 'All':
        bar_data = data[data['Year'] == selected_year]
        x_axis = 'Country Name'
        title_suffix = f'({selected_year})'
    else:
        bar_data = data[data['Country Name'] == selected_country]
        x_axis = 'Year'
        title_suffix = f'for {selected_country}'
    
    bar_fig = px.bar(
        bar_data,
        x=x_axis,
        y='CO2 Emissions (million tons)',
        title=f'Emissions Distribution {title_suffix}',
        color=x_axis,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # Pie Chart
    pie_fig = px.pie(
        data[data['Year'] == selected_year],
        names='Country Name', 
        values='CO2 Emissions (million tons)',
        title=f'Global Emissions Distribution ({selected_year})',
        hole=0.4
    )
    
    # Line Chart
    line_fig = px.line(
        data, 
        x='Year', 
        y='CO2 Emissions (million tons)', 
        color='Country Name',
        title='Emission Trends Over Time',
        markers=True
    )
    
    # Update layout
    for fig in [bar_fig, pie_fig, line_fig]:
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            margin=dict(t=40, b=20),
            height=400
        )
    
    return bar_fig, pie_fig, line_fig

# Add this line to allow Vercel to run the app
if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))) 