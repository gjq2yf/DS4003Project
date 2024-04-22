import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd

df = pd.read_csv('./DS4003Project/data/data.csv')

df = df.dropna()
g2 = df.rename(columns={
    'realrinc': 'Income',
    'occrecode': 'Occupation',
    'educcat': 'Education',
    'gender': 'Gender',
    'age': 'Age',
    'childs': 'Number of Children',
    'prestg10': 'Occupational Prestige'
})
g2 = g2.dropna(subset=['Income', 'Education'])

def income_bucket(income):
    if income < 8156:
        return "Lower Income"
    elif income < 22326:
        return "Lower Middle Income"
    elif income < 27171:
        return "Upper Middle Income"
    else:
        return "Upper Income"

g2['income_buckets'] = g2['Income'].apply(income_bucket)


THEMES = {
    "light": "https://cdn.jsdelivr.net/npm/dash-bootstrap-components@1.0.2/dist/dash-bootstrap-components-minty.min.css",
    "dark": "https://cdn.jsdelivr.net/npm/dash-bootstrap-components@1.0.2/dist/dash-bootstrap-components-vapor.min.css"
}

app = dash.Dash(__name__)
server = app.server

app.layout = dbc.Container([
    dbc.NavbarSimple(
        children=[
            dbc.Button("Toggle Theme", id="theme-toggle", n_clicks=0, color="secondary", className="ml-auto")
        ],
        brand="Income and Socioeconomic Factors Analysis",
        brand_href="#",
        color="primary",
        dark=True
    ),
    dcc.Store(id='theme-store', data={'theme': 'light'}),
    dcc.Store(id='stylesheet', data={'theme': dbc.themes.MINTY}),
    html.Link(rel='stylesheet', href=THEMES['light'], id='theme-link'),
    html.Div(id="content", className="light-theme", children=[
        dbc.Tabs([
            dbc.Tab(label='Children, Age, and Income', children=[
                html.Div([
                    dbc.Row([
                        html.Div([
                            html.H4("Children, Age, and Income", className="mb-2 text-primary"),
                            html.P(
                                "Adjust the filters below to view different data perspectives based on education, occupation, and gender over the years (1974 to 2018). Occupational prestige refers to an occupational prestige score (a number between 0 and 100) that measures the relative social standing of an occupation in a society.",
                                className="text-secondary"),
                            html.Label('Select Year:', className='mb-1'),
                            dcc.Slider(
                                id='year-slider',
                                min=1974,
                                max=2018,
                                step=2,
                                value=2018,
                                marks={str(year): str(year) for year in range(1974, 2019, 2)}
                            )
                        ], style={'margin-top': '20px', 'margin-bottom': '10px'}),
                    ]),
                    dbc.Row([
                        html.Div([
                            html.Label('Select Gender:', className='mb-1'),
                            dcc.Checklist(
                                id='gender-choice',
                                options=[{'label': i, 'value': i} for i in ['Male', 'Female']],
                                value=['Male', 'Female'],  # default
                                inline=True
                            )
                        ], style={'margin-bottom': '10px'})
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Label('Select X-Axis Variable:', className='mb-1'),
                            dcc.Dropdown(
                                id='x-axis-choice',
                                options=[
                                    {'label': 'Age', 'value': 'Age'},
                                    {'label': 'Number of Children', 'value': 'Number of Children'}
                                ],
                                value='Age',  # default
                                clearable=False
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label('Select Y-Axis Variable:', className='mb-1'),
                            dcc.Dropdown(
                                id='y-axis-choice',
                                options=[
                                    {'label': 'Income', 'value': 'Income'},
                                    {'label': 'Occupational Prestige', 'value': 'Occupational Prestige'}
                                ],
                                value='Income',
                                clearable=False
                            )
                        ], width=6)
                    ]),
                    dbc.Row([
                        dcc.Graph(id='scatter-plot', style={'height': '450px', 'margin-top': '30px'})
                    ]),
                ])
            ]),
            dbc.Tab(label='Education, Occupation, Income, and Gender', children=[
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            html.H4("Education, Occupation, Income, and Gender", className="mb-2 text-primary"),
                            html.P("Adjust the filters below as well as the graph's legend to view different data perspectives based on education, occupation, and gender. The income buckets separate people into four different categories: Lower Income (less than $8,155), Lower Middle Income (between $8,156 and $22,325), Upper Middle Income (between $22,326 and $27,170), and Upper Income (greater than $27,171).", className="text-secondary"),
                            html.Label('Select Gender:', className='mb-2'),
                            dcc.Dropdown(
                                id='gender-select',
                                options=[
                                    {'label': 'All Genders', 'value': 'Everyone'},
                                    {'label': 'Women Only', 'value': 'Female'},
                                    {'label': 'Men Only', 'value': 'Male'}
                                ],
                                value='Everyone'
                            ),
                            html.Label('Select X-Axis Variable:', className='mb-2'),
                            dcc.Dropdown(
                                id='x-axis-select',
                                options=[
                                    {'label': 'Education Level', 'value': 'Education'},
                                    {'label': 'Occupation', 'value': 'Occupation'}
                                ],
                                value='Education'
                            ),
                            html.Label('Select Occupations:', className='mb-3'),
                            dcc.Checklist(
                                id='occupation-select',
                                options=[{'label': i, 'value': i} for i in g2['Occupation'].unique()],
                                value=g2['Occupation'].unique().tolist(),
                                inline=False
                            )
                        ], style={'margin-top': '20px'}, width=4),
                        dbc.Col([
                            dcc.Graph(id='stacked-bar-plot')
                        ], style={'margin-top': '50px'}, width=8)
                    ])
                ])
            ])
        ])
    ])
], fluid=True, style={'padding': '0'})


@app.callback(
    Output('scatter-plot', 'figure'),
    [
        Input('x-axis-choice', 'value'),
        Input('y-axis-choice', 'value'),
        Input('gender-choice', 'value'),
        Input('year-slider', 'value'),
        State('theme-store', 'data')
    ]
)
def update_scatter_plot(x_choice, y_choice, genders, year, theme_data):
    filtered_data = g2[(g2['year'] == year) & (g2['Gender'].isin(genders))]
    fig = px.scatter(
        filtered_data,
        x=x_choice,
        y=y_choice,
        color='Gender',
        labels={'Number of Children': 'Number of Children', 'Age': 'Age', 'Income': 'Income', 'Occupational Prestige': 'Occupational Prestige'}
    )

    if theme_data['theme'] == 'light':
        background_color = 'rgba(120, 194, 173, 0.35)'
        font_color = "#f3969a"
    else:
        background_color = 'rgba(234, 57, 184, 0.35)'
        font_color = '#6f42c1'

    fig.update_layout(
        plot_bgcolor=background_color,
        font=dict(color=font_color),
        title_text=f"Relationship Between {x_choice} and {y_choice} From 1974 to {year}",
        title_x=0.5
    )
    return fig

@app.callback(
    Output('stacked-bar-plot', 'figure'),
    [
        Input('gender-select', 'value'),
        Input('x-axis-select', 'value'),
        Input('occupation-select', 'value'),
        State('theme-store', 'data')
    ]
)
def update_bar_plot(gender, x_axis_select, occupations, theme_data):
    filtered_data = g2.copy()
    education_order = ["Less Than High School", "High School", "Junior College", "Bachelor", "Graduate"]
    if gender != 'Everyone':
        filtered_data = filtered_data[filtered_data['Gender'] == gender]
    if x_axis_select == 'Occupation':
        filtered_data = filtered_data[filtered_data['Occupation'].isin(occupations)]
    elif x_axis_select == 'Education':
        filtered_data['Education'] = pd.Categorical(filtered_data['Education'], categories=education_order,
                                                    ordered=True)

    category_orders = {
        'income_buckets': ['Lower Income', 'Lower Middle Income', 'Upper Middle Income', 'Upper Income']
    }

    if x_axis_select == 'Education':
        category_orders['Education'] = education_order

    fig = px.histogram(
        filtered_data,
        x=x_axis_select,
        color='income_buckets',
        category_orders=category_orders,
    )

    background_color = 'rgba(120, 194, 173, 0.35)' if theme_data['theme'] == 'light' else 'rgba(234, 57, 184, 0.35)'
    font_color = "#f3969a" if theme_data['theme'] == 'light' else '#6f42c1'

    fig.update_layout(
        plot_bgcolor=background_color,
        font=dict(color=font_color),
        legend_title_text='Income Buckets',
        legend=dict(
            orientation="h",
            xanchor="center",
            x=0.5,
            yanchor="bottom",
            y=1.02
        ),
        height=650,
        title=dict(text=f'Histogram of {x_axis_select} by Income Level', x=0.5, y=1)
    )

    return fig

@app.callback(
    Output('theme-link', 'href'),
    [Input('theme-toggle', 'n_clicks')],
    [dash.dependencies.State('theme-store', 'data')]
)
def toggle_theme(n_clicks, data):
    if n_clicks % 2 == 0:
        data['theme'] = dbc.themes.MINTY
    else:
        data['theme'] = dbc.themes.VAPOR
    return data['theme']

if __name__ == '__main__':
    app.run_server(debug=True)
