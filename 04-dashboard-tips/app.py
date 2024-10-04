import faicons as fa

# Load data and compute static values
from shared import app_dir
from shinywidgets import render_plotly

from shiny import reactive, render
from shiny.express import input, ui

# Add page title and sidebar
ui.page_opts(title="Financial Dashboard", fillable=True)

with ui.sidebar(open="desktop"):
    ui.input_slider("salary", "Salary", min=0, max=20000, value=8000)
    ui.input_slider(
        "interest",
        "Interest Rate",
        min=0,
        max=100,
        value=7,
        post="%",
    )
    ui.input_action_button("reset", "Reset filter")

# Add main content
ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "wallet": fa.icon_svg("wallet"),
    "currency-dollar": fa.icon_svg("dollar-sign"),
    "ellipsis": fa.icon_svg("ellipsis"),
}

with ui.layout_columns(fill=False):
    with ui.value_box(showcase=ICONS["user"]):
        "Client"

        @render.express
        def total_tippers():
            "Claude Hähni"

    with ui.value_box(showcase=ICONS["currency-dollar"]):
        "Monthly Income"

        @render.express
        def income():
            f"{input.salary()}$"

    with ui.value_box(showcase=ICONS["wallet"]):
        "Monthly Spending"

        @render.express
        def expense():
            "5000$"


with ui.layout_columns(col_widths=[6, 6, 12]):
    with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Income/Expense Distribution"
            
        @render_plotly
        def sankey_render():
            import plotly.graph_objects as go
            fig = go.Figure(data=[go.Sankey(
                node = dict(
                pad = 15,
                thickness = 20,
                line = dict(color = "black", width = 0.5),
                label = ["Gehalt", "Budget", "Miete", "Transport", "Haushalt", "Ersparnis"],
                color = "blue"
                ),
                link = dict(
                source = [0, 1, 1, 1, 1], # indices correspond to labels, eg A1, A2, A1, B1, ...
                target = [1, 2, 3, 4, 5],
                value = [input.salary(), 2500, 1000, 1500, input.salary()- 5000]
            ))])

            fig.update_layout(
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
                )
            )

            return fig

    with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Future Value"
        
        with ui.popover(title="Toggles"):
            ICONS["ellipsis"]
            ui.input_checkbox("inflation_toggle", "Show Inflation", True)

        @render_plotly
        def fv_render():
            import plotly.graph_objects as go
            import numpy as np

            # Parameters
            initial_amount = 20000  # Initial investment
            years = np.arange(0, 30, 1)  # Time period in years
            interest_rate = input.interest() /100  # Interest rate from user input
            inflation_rate = 0.02  # Inflation rate (2%)

            # Calculate compound interest
            money_growth = initial_amount * (1 + interest_rate) ** years

            # Calculate the inflation-only line
            inflation_value = initial_amount * (1 + inflation_rate) ** years

            # Create the plot
            fig = go.Figure()

            # Add the growth line with a filled area
            fig.add_trace(go.Scatter(
                x=years, y=money_growth, mode='lines', name='Money Growth',
                fill='tozeroy', fillcolor='rgba(0, 0, 255, 0.2)',  # Blue fill with transparency
                line=dict(color='blue'),
                showlegend=True  # Ensure legend is shown
            ))

            # Add the inflation line with a filled area
            if input.inflation_toggle():
                fig.add_trace(go.Scatter(
                    x=years, y=inflation_value, mode='lines', name='Inflation',
                    fill='tozeroy', fillcolor='rgba(255, 0, 0, 0.2)',  # Red fill with transparency
                    line=dict(color='red'),
                    showlegend=True  # Ensure legend is shown
                ))

            # Add titles and labels
            fig.update_layout(
                title="Exponential Growth of Money vs Inflation Over Time",
                xaxis_title="Years",
                yaxis_title="Money Value",
                legend_title="Growth vs Inflation",
                legend=dict(
                    yanchor="top",
                    y=-0.2,  # Place the legend below the graph
                    xanchor="center",
                    x=0.5,  # Center the legend horizontally
                    orientation="h"  # Horizontal legend layout
                )
            )
            return fig

ui.include_css(app_dir / "styles.css")

# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------

@reactive.effect
@reactive.event(input.reset)
def _():
    ui.update_slider("salary", value=8000)
    ui.update_slider("interest", value=7)
