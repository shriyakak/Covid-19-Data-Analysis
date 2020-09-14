import sys
import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html

from scipy import optimize
from scipy import integrate
from utils import SIR_model
from dash.dependencies import Input, Output,State

df_analyse=pd.read_csv('../data/processed/COVID_final_set.csv',sep=';')
df_population = pd.read_csv('../data/population.csv', sep=';')

fig = go.Figure()
app = dash.Dash()
app.layout = html.Div([



    html.H1('SIR Model (Susceptible, Infectious, and Recovered)', style={'text-align': 'center',
                                                                        'padding': 10,
                                                                        'background-color': '#f0f0f5',}),
    
    dcc.Markdown(''' The below graphs shows the future trend of the spread of COVID-19(dotted line) using the SIR model.''', style={'text-align': 'center',
                                                                        'padding': 10,
                                                                        'background-color': '#f0f0f5',}),
    
     dcc.Markdown('''__Select Country for visualization__ '''),


    dcc.Dropdown(
        id = 'country_drop_down',
        options=[ {'label': each,'value':each} for each in df_analyse['country'].unique()],
        value= 'India', # which are pre-selected
        multi=False),

    dcc.Graph(figure = fig, id = 'SIR_graph')
    ])

@app.callback(
    Output('SIR_graph', 'figure'),
    [Input('country_drop_down', 'value')])

def update_SIR_figure(country_drop_down):

    traces = []

    df_plot = df_analyse[df_analyse['country'] == country_drop_down]
    df_plot = df_plot[['state', 'country', 'confirmed', 'date']].groupby(['country', 'date']).agg(np.sum).reset_index()
    df_plot.sort_values('date', ascending = True).head()
    df_plot = df_plot.confirmed[55:]

    population = df_population[df_population['COUNTRY'] == country_drop_down]['Value'].values[0]

    t, fitted = SIR_model(df_plot, population)

    traces.append(dict (x = t,
                        y = fitted,
                        mode = 'markers+lines',
                        opacity = 0.9,
                        name = 'SIR-Model',
                        line = dict(color = 'dark-blue'))
                  )

    traces.append(dict (x = t,
                        y = df_plot,
                        mode = 'lines',
                        opacity = 0.9,
                        name = 'Original Data',
                        line = dict(color = 'red'))
                  )

    return {
            'data': traces,
            'layout': dict (
                width=1280,
                height=720,
                title = 'SIR model fitting for '+country_drop_down,

                xaxis= {'title':'Days',
                       'tickangle':-45,
                        'nticks':20,
                        'tickfont':dict(size=14,color="#7f7f7f"),
                      },

                yaxis={'title': "Number of Infected people"}
        )
    }


if __name__ == '__main__':
    app.run_server(debug = True, use_reloader = False, port=8052)

