import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import datetime as dt


app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Dashboard energia"

server = app.server
app.config.suppress_callback_exceptions = True


# Load data from csv
def load_data():
    # Leer CSV
    df = pd.read_csv("datos_energia.csv")

    # Convertir columna de tiempo a datetime
    df["time"] = pd.to_datetime(df["time"])

    # Usar la fecha como índice
    df = df.set_index("time").sort_index()

    return df


# Cargar datos
data = load_data()


# Graficar serie
def plot_series(data, initial_date, proy):
    data_plot = data.loc[initial_date:]
    data_plot = data_plot[:-(120 - proy)]

    fig = go.Figure([
        go.Scatter(
            name='Demanda energética',
            x=data_plot.index,
            y=data_plot['AT_load_actual_entsoe_transparency'],
            mode='lines',
            line=dict(color="#188463"),
        ),
        go.Scatter(
            name='Proyección',
            x=data_plot.index,
            y=data_plot['forecast'],
            mode='lines',
            line=dict(color="#bbffeb"),
        ),
        go.Scatter(
            name='Upper Bound',
            x=data_plot.index,
            y=data_plot['Upper bound'],
            mode='lines',
            line=dict(width=0),
            showlegend=False
        ),
        go.Scatter(
            name='Lower Bound',
            x=data_plot.index,
            y=data_plot['Lower bound'],
            mode='lines',
            fill='tonexty',
            fillcolor="rgba(242, 255, 251, 0.3)",
            line=dict(width=0),
            showlegend=False
        )
    ])

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis_title='Demanda total [MW]',
        hovermode="x",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#2cfec1"
    )

    fig.update_xaxes(showgrid=True, gridwidth=0.25, gridcolor='#7C7C7C')
    fig.update_yaxes(showgrid=True, gridwidth=0.25, gridcolor='#7C7C7C')

    return fig


def description_card():
    return html.Div(
        id="description-card",
        children=[
            html.H3("Pronóstico de producción energética"),
            html.Div(
                id="intro",
                children=(
                    "Esta herramienta contiene información sobre la demanda energética "
                    "total en Austria cada hora según ENTSO-E. "
                    "Además, permite realizar pronósticos hasta 5 días en el futuro."
                ),
            ),
        ],
    )


def generate_control_card():
    return html.Div(
        id="control-card",
        children=[

            html.P("Seleccionar fecha y hora inicial:"),

            html.Div(
                children=[
                    html.Div(
                        children=[
                            dcc.DatePickerSingle(
                                id='datepicker-inicial',
                                min_date_allowed=min(data.index.date),
                                max_date_allowed=max(data.index.date),
                                initial_visible_month=min(data.index.date),
                                date=max(data.index.date) - dt.timedelta(days=7)
                            )
                        ],
                        style=dict(width='30%')
                    ),

                    html.P(" ", style=dict(width='5%')),

                    html.Div(
                        children=[
                            dcc.Dropdown(
                                id="dropdown-hora-inicial-hora",
                                options=[{"label": i, "value": i} for i in range(24)],
                                value=(max(data.index) - dt.timedelta(days=7)).hour,
                            )
                        ],
                        style=dict(width='20%')
                    ),
                ],
                style=dict(display='flex')
            ),

            html.Br(),

            html.Div(
                children=[
                    html.P("Ingrese horas a proyectar:"),
                    dcc.Slider(
                        id="slider-proyeccion",
                        min=0,
                        max=119,
                        step=1,
                        value=0,
                        marks=None,
                        tooltip={"placement": "bottom", "always_visible": True},
                    )
                ]
            )
        ]
    )


app.layout = html.Div(
    children=[

        html.Div(
            className="four columns",
            children=[
                description_card(),
                generate_control_card(),
            ],
        ),

        html.Div(
            className="eight columns",
            children=[
                html.B("Demanda energética total en Austria [MW]"),
                html.Hr(),
                dcc.Graph(id="plot_series")
            ],
        ),
    ],
)


@app.callback(
    Output("plot_series", "figure"),
    [
        Input("datepicker-inicial", "date"),
        Input("dropdown-hora-inicial-hora", "value"),
        Input("slider-proyeccion", "value")
    ]
)
def update_output_div(date, hour, proy):

    if date is not None and hour is not None and proy is not None:
        initial_date = pd.to_datetime(f"{date} {hour}:00")
        return plot_series(data, initial_date, int(proy))


# Run the server
if __name__ == "__main__":
    app.run(debug=True)
