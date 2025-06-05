import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import numpy as np
from scipy.stats import lognorm
from plotly.colors import sample_colorscale
import plotly.graph_objects as go

col_names = [
    "sim_condition",
    "starting_glucose",
    "netIoB",
    "pa_duration",
    "activity",
    "preset",
    "target_min",
    "target_max",
    "vp_index",
    "noise_condition",
    "del_g",
    "LBGI",
    "HBGI",
    "BGRI",
    "%TBR (<54 mg/dl)",
    "%TBR (<54-<70 mg/dl)",
    "%TBR (<70 mg/dl)",
    "%TIR (70-180 mg/dl)",
    "%TAR (>180 mg/dl)",
    "%TAR (>180-<=250 mg/dl)",
    "%TAR (>=250 mg/dl)",
    "basal",
    "bolus",
    "Magni Risk",
]  # column names of the dataframes

metrics_list = [
    "%TIR (70-180 mg/dl)",
    "%TBR (<54 mg/dl)",
    "%TBR (<70 mg/dl)",
    "%TAR (>180 mg/dl)",
    "LBGI",
    "HBGI",
    "BGRI",
    "Magni Risk",
]

t1dexi_presets = {
    "walking": 0.2,
    "biking": 0.2,
    "jogging": 0.2,
    "strength training": 0.4,
}

# parameters of log-normal t1dexi starting glucose distribution
mu = 4.93
sigma = 0.34

target_mins = list(np.arange(100, 180, 20))
target_mins.append(150)
target_mins.sort()
target_labels = [f"{v}-{v+20}" for v in target_mins]
sample_points = [
    0.25,
    0.4,
    0.6,
    0.8,
    1.0,
]  # sample points for the target-based color map
colors = sample_colorscale("Blues", sample_points)
color_map = dict(zip(target_labels, colors))

# visualization app code
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.H4(
                                [
                                    "Activity Metrics Visualization Tool ",
                                    html.Span(
                                        "ⓘ",
                                        id="heading-info",
                                        style={
                                            "cursor": "pointer",
                                            "fontSize": "1.4rem",
                                            "color": "#bbb",
                                            "marginLeft": "0.5rem",
                                            "fontWeight": "bold",
                                            "verticalAlign": "middle",
                                        },
                                    ),
                                ],
                                className="custom-heading",
                            ),
                            dbc.Popover(
                                dbc.PopoverBody(
                                    [
                                        html.P(
                                            "This tool is used for visualizing the impact of preset- and target-based insulin interventions during simulated physical activity (PA) in individuals with type 1 diabetes."
                                        ),
                                        html.P(
                                            "Developed by UC Santa Barbara in collaboration with University of Pavia, Stanford Health, and Tidepool."
                                        ),
                                    ]
                                ),
                                target="heading-info",
                                trigger="hover",
                                placement="right",
                            ),
                        ]
                    ),
                    width=14,
                )
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.H6(
                        "Adjust the dropdowns to select sessions for evaluation",
                        style={
                            "color": "white",
                            "fontSize": "1.25rem",
                            "marginBottom": "1rem",
                        },
                    )
                )
            ],
            className="ms-5",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Activity", className="label-white"),
                        dcc.Dropdown(
                            id="activity-dropdown",
                            options=[
                                {"label": "Walking", "value": "walking"},
                                {"label": "Biking", "value": "biking"},
                                {"label": "Jogging", "value": "jogging"},
                                {
                                    "label": "Strength Training",
                                    "value": "strength training",
                                },
                            ],
                            value="walking",
                            clearable=False,
                        ),
                    ],
                    width=2,
                ),
                dbc.Col(
                    [
                        dbc.Label("Activity Duration (min)", className="label-white"),
                        dcc.Dropdown(
                            id="duration-dropdown",
                            options=[
                                {"label": "30", "value": 30},
                                {"label": "60", "value": 60},
                                {"label": "All", "value": "all"},
                            ],
                            value="all",
                            clearable=False,
                        ),
                    ],
                    width=2,
                ),
                dbc.Col(
                    [
                        dbc.Label("Noise", className="label-white"),
                        dcc.Dropdown(
                            id="noise-dropdown",
                            options=[
                                {"label": "All", "value": "all"},
                                {"label": "No Noise", "value": "nonoise"},
                                {
                                    "label": "Uniformly Sampled Noise (Max 25%)",
                                    "value": "samplednoise",
                                },
                                {"label": "25% Noise", "value": "fullnoise"},
                            ],
                            value="all",
                            clearable=False,
                        ),
                    ],
                    width=2,
                ),
                dbc.Col(
                    [
                        dbc.Label("Max netIoB", className="label-white"),
                        dcc.Dropdown(
                            id="max-netiob-dropdown",
                            options=[
                                {"label": str(i), "value": i} for i in [0, 1, 2, 3]
                            ],
                            value=3,
                            clearable=False,
                        ),
                    ],
                    width=2,
                ),
            ],
            className="ms-5 mt-2",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Min Starting Glucose", className="label-white"),
                        dcc.Dropdown(
                            id="min-glucose-dropdown",
                            options=[
                                {"label": str(i), "value": i}
                                for i in list(np.arange(70, 260, 20))
                            ],
                            value=70,
                            clearable=False,
                        ),
                    ],
                    width=2,
                ),
                dbc.Col(
                    [
                        dbc.Label("Max Starting Glucose", className="label-white"),
                        dcc.Dropdown(
                            id="max-glucose-dropdown",
                            options=[
                                {"label": str(i), "value": i}
                                for i in list(np.arange(70, 260, 20))
                            ],
                            value=250,
                            clearable=False,
                        ),
                    ],
                    width=2,
                ),
                dbc.Col(
                    [
                        dbc.Label("Evaluation Start Time", className="label-white"),
                        dcc.Dropdown(
                            id="eval-start-dropdown",
                            options=[
                                {"label": "1Hr Before Activity", "value": "1hr_before"},
                                {
                                    "label": "Activity Start Time",
                                    "value": "activity_start",
                                },
                                {"label": "Activity End Time", "value": "activity_end"},
                            ],
                            value="activity_start",
                            clearable=False,
                        ),
                    ],
                    width=2,
                ),
                dbc.Col(
                    [
                        dbc.Label("Evaluation End Time", className="label-white"),
                        dcc.Dropdown(
                            id="eval-end-dropdown",
                            options=[
                                {
                                    "label": "Activity Start Time",
                                    "value": "activity_start",
                                },
                                {"label": "Activity End Time", "value": "activity_end"},
                                {"label": "1Hr After Activity", "value": "1hr_after"},
                                {"label": "2Hr After Activity", "value": "2hr_after"},
                                {"label": "3Hr After Activity", "value": "3hr_after"},
                            ],
                            value="3hr_after",
                            clearable=False,
                        ),
                    ],
                    width=2,
                ),
            ],
            className="ms-5 mt-2",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label("Metric Y-Axis", size="sm", className="label-white"),
                        dcc.Dropdown(
                            id="y-metric-dropdown",
                            options=[
                                {"label": metric, "value": metric}
                                for metric in metrics_list
                            ],
                            value="%TBR (<70 mg/dl)",
                            clearable=False,
                        ),
                    ],
                    width=2,
                ),
                dbc.Col(
                    [
                        dbc.Label("Metric X-Axis", size="sm", className="label-white"),
                        dcc.Dropdown(
                            id="x-metric-dropdown",
                            options=[
                                {"label": metric, "value": metric}
                                for metric in metrics_list
                            ],
                            value="%TIR (70-180 mg/dl)",
                            clearable=False,
                        ),
                    ],
                    width=2,
                ),
                dbc.Col(
                    [
                        dbc.Label("Averaging", className="label-white"),
                        dcc.Dropdown(
                            id="averaging-dropdown",
                            options=[
                                {"label": "Weighted", "value": "Weighted"},
                                {"label": "Unweighted", "value": "Unweighted"},
                            ],
                            value="Weighted",
                            clearable=False,
                        ),
                    ],
                    width=2,
                ),
            ],
            className="ms-5 mt-2",
        ),
        dbc.Col(
            dcc.Graph(id="scatter-plot", style={"height": "500px"}),
            width=10,
            className="ms-5 mt-5",
        ),
    ],
    fluid=True,
)


@app.callback(
    Output("scatter-plot", "figure"),
    Input("activity-dropdown", "value"),
    Input("duration-dropdown", "value"),
    Input("noise-dropdown", "value"),
    Input("x-metric-dropdown", "value"),
    Input("y-metric-dropdown", "value"),
    Input("max-netiob-dropdown", "value"),
    Input("averaging-dropdown", "value"),
    Input("min-glucose-dropdown", "value"),
    Input("max-glucose-dropdown", "value"),
    Input("eval-start-dropdown", "value"),
    Input("eval-end-dropdown", "value"),
)
def update_plot(
    selected_activity,
    pa_duration,
    noise,
    x_metric,
    y_metric,
    max_netiob,
    averaging,
    min_glucose,
    max_glucose,
    eval_start,
    eval_end,
):
    if noise == "all":
        all_dfs = []
        for noise_level in ["nonoise", "samplednoise", "fullnoise"]:
            df = pd.read_csv(
                f"./data/03_13_{noise_level}_{eval_start}_{eval_end}.csv",
                names=col_names,
                header=None,
            )
            df["noise"] = noise_level
            all_dfs.append(df)
        df = pd.concat(all_dfs, ignore_index=True)
    else:
        df = pd.read_csv(
            f"./data/03_13_{noise}_{eval_start}_{eval_end}.csv",
            names=col_names,
            header=None,
        )
    df["activity"] = df["activity"].replace(
        "rength training", "strength training"
    )  # fix typo in results df
    df["weight"] = lognorm.pdf(
        np.array(df["starting_glucose"]), s=sigma, scale=np.exp(mu)
    )  # weight of each simulation based on starting glucose
    df["label"] = df.apply(
        lambda x: f"Target: {x['target_min']}-{x['target_max']}\nPreset: {int(x['preset']*100)}%",
        axis=1,
    )  # label to display in the plot

    # filter df based on set parameters in the visualization.
    df_filtered = df[
        (df["activity"] == selected_activity)
        & (df["netIoB"] <= max_netiob)
        & ((df["pa_duration"] == pa_duration) if pa_duration != "all" else True)
        & (df["starting_glucose"] >= min_glucose)
        & (df["starting_glucose"] <= max_glucose)
        & (df["target_min"] < 180)
    ]

    df_filtered = df_filtered[
        metrics_list + ["label", "weight", "target_min", "preset"]
    ]

    if averaging == "Unweighted":
        df_avg = (
            df_filtered.groupby(["label", "target_min", "preset"], as_index=False)
            .mean()
            .reset_index()
        )
    else:
        df_avg = (
            df_filtered.groupby(["label", "target_min", "preset"], as_index=False)
            .apply(
                lambda g: pd.Series(
                    np.average(
                        g.drop(columns=["label", "weight", "target_min", "preset"]),
                        weights=g["weight"],
                        axis=0,
                    ),
                    index=g.drop(
                        columns=["label", "weight", "target_min", "preset"]
                    ).columns,
                )
            )
            .reset_index()
        )

    df_avg["target"] = df_avg.apply(
        lambda x: f"{x['target_min']}-{x['target_min']+20}", axis=1
    )
    df_avg["size"] = (
        df_avg["preset"] * 100
    )  # for setting the size of the scatter points based on the preset

    df_avg = df_avg.round(2)

    fig = px.scatter(
        df_avg,
        x=x_metric,
        y=y_metric,
        color="target",
        color_discrete_map=color_map,
        size="size",
        size_max=18,
        opacity=0.75,
        title=f"{y_metric} vs {x_metric} for {selected_activity}",
        hover_data={"label": True, "size": False, "target": False},
    )

    # highlight the baseline : default target and 100% preset
    baseline_df = df_avg[(df_avg["target"] == "100-120") & (df_avg["preset"] == 1.0)]
    fig.add_trace(
        go.Scatter(
            x=baseline_df[x_metric],
            y=baseline_df[y_metric],
            name="No Action<br><sub>Default target 100-120, Preset 100%</sub>",
            mode="markers",
            marker=dict(symbol="diamond", color="#A1BB97", size=14, line=dict(width=0)),
            customdata=baseline_df[["label"]],
            hovertemplate=(
                f"{x_metric}: {baseline_df[x_metric].iloc[0]:.2f}<br>"
                f"{y_metric}: {baseline_df[y_metric].iloc[0]:.2f}<br>"
                "%{customdata[0]}<extra></extra>"
            ),
            showlegend=True,
        )
    )

    # highlight the raised target with 100% preset point
    raised_target_df = df_avg[
        (df_avg["target"] == "150-170") & (df_avg["preset"] == 1.0)
    ]
    fig.add_trace(
        go.Scatter(
            x=raised_target_df[x_metric],
            y=raised_target_df[y_metric],
            name="Raised Target<br><sub>Target 150-170, Preset 100%</sub>",
            mode="markers",
            marker=dict(symbol="diamond", color="#E5CFA4", size=14, line=dict(width=0)),
            customdata=raised_target_df[["label"]],
            hovertemplate=(
                f"{x_metric}: {raised_target_df[x_metric].iloc[0]:.2f}<br>"
                f"{y_metric}: {raised_target_df[y_metric].iloc[0]:.2f}<br>"
                "%{customdata[0]}<extra></extra>"
            ),
            showlegend=True,
        )
    )

    # highlight the preset only data point
    preset_only_df = df_avg[
        (df_avg["preset"] == t1dexi_presets[selected_activity])
        & (df_avg["target"] == "100-120")
    ]
    fig.add_trace(
        go.Scatter(
            x=preset_only_df[x_metric],
            y=preset_only_df[y_metric],
            name=f"Preset Only<br><sub>Default target 100-120, T1DEXI Preset {int(t1dexi_presets[selected_activity]*100)}%</sub>",
            mode="markers",
            marker=dict(symbol="star", color="#D4938B", size=18, line=dict(width=0)),
            customdata=preset_only_df[["label"]],
            hovertemplate=(
                f"{x_metric}: {preset_only_df[x_metric].iloc[0]:.2f}<br>"
                f"{y_metric}: {preset_only_df[y_metric].iloc[0]:.2f}<br>"
                "%{customdata[0]}<extra></extra>"
            ),
            showlegend=True,
        )
    )

    # highlight the raised target + T1DEXI preset point
    preset_and_raised_target_df = df_avg[
        (df_avg["target"] == "150-170")
        & (df_avg["preset"] == t1dexi_presets[selected_activity])
    ]
    fig.add_trace(
        go.Scatter(
            x=preset_and_raised_target_df[x_metric],
            y=preset_and_raised_target_df[y_metric],
            name=f"Preset + Raised Target<br><sub>Target 150-170, Preset {int(t1dexi_presets[selected_activity]*100)}%</sub>",
            mode="markers",
            marker=dict(symbol="star", color="pink", size=18, line=dict(width=0)),
            customdata=preset_and_raised_target_df[["label"]],
            hovertemplate=(
                f"{x_metric}: {preset_and_raised_target_df[x_metric].iloc[0]:.2f}<br>"
                f"{y_metric}: {preset_and_raised_target_df[y_metric].iloc[0]:.2f}<br>"
                "%{customdata[0]}<extra></extra>"
            ),
            showlegend=True,
        )
    )

    # update plot aesthetics
    fig.update_layout(
        paper_bgcolor="#0F203A",
        font=dict(family="Basis Grotesque Pro", color="white"),
        title_font=dict(size=20, color="white"),
        legend=dict(
            title=dict(
                text="Key [Target]",  # Your custom legend title
                font=dict(family="Basis Grotesque Pro", size=16, color="white"),
            ),
            bordercolor="white",
            borderwidth=1,
            font=dict(family="Basis Grotesque Pro", color="white", size=16),
            x=1.05,
            y=0.5,
            xanchor="left",
            yanchor="middle",
            # itemclick="toggleothers",
        ),
        margin=dict(l=50, r=300, t=50, b=50),
        legend_tracegroupgap=4,  # Optional: only works if using legend groups
    )

    return fig


if __name__ == "__main__":
    app.run(debug=True)
