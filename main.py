import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# load the dataset
df = pd.read_csv('data.csv')

# get rid of missing values
df = df.dropna()

# rename columns
g2 = df.rename(columns={
    'realrinc': 'income',
    'occrecode': 'occupation',
    'educcat': 'education'
})

# get rid of missing values
g2 = g2.dropna(subset=['income', 'education'])

# create income buckets
def income_bucket(income):
    if income < 8156:
        return "Lower income"
    elif income < 22326:
        return "Lower Middle income"
    elif income < 27171:
        return "Upper middle income"
    else:
        return "Upper income"

g2['income_buckets'] = g2['income'].apply(income_bucket)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

app.layout = dbc.Container([
    dbc.NavbarSimple('Relationship Between Gender, Education, Children, and Income', brand='Dash App'),
    dbc.Tabs([
        dbc.Tab(label='Introduction', children=[
            html.H3('Introduction to Our Data'),
            html.P('Your introduction content here...')
        ]),
        dbc.Tab(label='Q1: Children, Age, Income', children=[
            html.Div([
                dcc.Dropdown(
                    id='x-axis-choice',
                    options=[
                        {'label': 'Age', 'value': 'age'},
                        {'label': 'Number of Children', 'value': 'childs'}
                    ],
                    value='age',  # default
                    clearable=False
                ),
                dcc.Dropdown(
                    id='y-axis-choice',
                    options=[
                        {'label': 'Income', 'value': 'income'},
                        {'label': 'Occupational Prestige', 'value': 'prestige'}
                    ],
                    value='income',  # default
                    clearable=False
                ),
                dcc.Checklist(
                    id='gender-choice',
                    options=[{'label': i, 'value': i} for i in ['Male', 'Female']],
                    value=['Female'],  # default
                    inline=True
                ),
                dcc.Slider(
                    id='year-slider',
                    min=1974,
                    max=2018,
                    step=2,
                    value=1974,
                    marks={str(year): str(year) for year in range(1974, 2019, 2)},
                ),
                dcc.Graph(id='scatter-plot')
            ])
        ]),
        dbc.Tab(label='Q2: Education, Occupation, Income, Gender', children=[
            html.Div([
                dcc.Dropdown(
                    id='gender-select',
                    options=[
                        {'label': 'Everyone', 'value': 'everyone'},
                        {'label': 'Women Only', 'value': 'female'},
                        {'label': 'Men Only', 'value': 'male'}
                    ],
                    value='everyone',  # default
                    clearable=False
                ),
                dcc.Dropdown(
                    id='x-axis-select',
                    options=[
                        {'label': 'Education Level', 'value': 'education'},
                        {'label': 'Occupation', 'value': 'occupation'}
                    ],
                    value='education',  # default
                    clearable=False
                ),
                dcc.Checklist(
                    id='occupation-select',
                    options=[{'label': occupation, 'value': occupation} for occupation in g2['occupation'].unique() if pd.notnull(occupation)],
                    value=[occupation for occupation in g2['occupation'].unique() if pd.notnull(occupation)],  # default
                    inline=True
                ),
                dcc.Graph(id='bar-plot')
            ])
        ]),
        dbc.Tab(label='Q3: Gender, Industry, Income', children=[
            html.H3('Question 3 content and graphs...')
            # add third visualization here
        ])
    ])
])

# callback for updating the scatter plot
@app.callback(
    Output('scatter-plot', 'figure'),
    [
        Input('x-axis-choice', 'value'),
        Input('y-axis-choice', 'value'),
        Input('gender-choice', 'value'),
        Input('year-slider', 'value')
    ]
)

def update_scatter_plot(x_choice, y_choice, genders, year):
    filtered_data = g2[(g2['year'] == year) & (g2['gender'].isin(genders))]
    fig = px.scatter(filtered_data, x=x_choice, y=y_choice, color='gender',
                     labels={'childs': 'Number of Children', 'age': 'Age', 'income': 'Income', 'prestige': 'Occupational Prestige'},
                     title=f"Relationship of {x_choice} and {y_choice} in {year}")
    return fig

# callback for updating bar plot
@app.callback(
    Output('bar-plot', 'figure'),
    [
        Input('gender-select', 'value'),
        Input('x-axis-select', 'value'),
        Input('occupation-select', 'value')
    ]
)

def update_bar_plot(gender, x_axis, selected_occupations):
    filtered_data = g2[g2['occupation'].isin(selected_occupations)]
    if gender != 'everyone':
        filtered_data = filtered_data[filtered_data['gender'] == gender.capitalize()]
    fig = px.bar(filtered_data, x=x_axis, y='income', color='occupation',
                 title="Income by Education Level and Occupation")

    # increase opacity
    fig.update_traces(opacity=0.9)

    # make background less opaque
    '''
    fig.update_layout(
        plot_bgcolor='rgba(255, 255, 255, 0.9)',  # Light background for the plot area
        paper_bgcolor='rgba(255, 255, 255, 0.9)',  # Light background for the entire figure
        barmode='group',
        xaxis_tickangle=-45
    )
    '''

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)