import faicons as fa

# Load data and compute static values
from shared import app_dir
from shinywidgets import render_plotly

from shiny import reactive, render
from shiny.express import input, ui

import plotly.graph_objects as go

ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "wallet": fa.icon_svg("wallet"),
    "briefcase": fa.icon_svg("briefcase"),
    "piggy-bank": fa.icon_svg("piggy-bank"),
    "stocks": fa.icon_svg("arrow-trend-up"),
    "currency-dollar": fa.icon_svg("dollar-sign"),
    "ellipsis": fa.icon_svg("ellipsis"),
    "income": fa.icon_svg("hand-holding-dollar"),
    "spending": fa.icon_svg("credit-card"),
}

# Add page title and sidebar
ui.page_opts(title="Financial Dashboard", fillable=True)

with ui.navset_pill_list(id="pill", widths=(2,10)):
    with ui.nav_panel("Einstellungen"):
        with ui.navset_card_tab(id="tab"):  
            with ui.nav_panel("Einkommen"):
                ui.input_numeric("salary_input", "Einkommen", 8000, step=500)
                ui.br()
                ui.input_numeric("dividend_input", "Gewinn", 0, step=50)

            with ui.nav_panel("Ausgaben"):
                ui.input_numeric("living_cost_input", "Wohnen", 0)
                ui.br()
                ui.input_numeric("groceries_input", "Haushalt", 0)
                ui.br()
                ui.input_numeric("food_input", "Essen", 0, step=50)
                ui.br()
                ui.input_numeric("transport_cost_input", "Transport", 0, step=50)
                ui.br()
                ui.input_numeric("hobbys_input", "Hobbys", 0, step=50)

            with ui.nav_panel("Assets"):
                ui.input_numeric("bank_account_input", "Bankkonten", 0, step=1000)
                ui.br()
                ui.input_numeric("investment_input", "Aktiendepot", 0, step=1000)
                ui.br()
                ui.input_numeric("pillar2_input", "Säule 2", 0, step=1000)
                ui.br()
                ui.input_numeric("pillar3a_input", "Säule 3a", 0, step=1000)
                ui.br()

    with ui.nav_panel("Finanzplanung"):
        # with ui.card(full_screen=True):
            # with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            #         "Input"
            # ui.input_slider("salary", "Salary", min=0, max=20000, value=8000, step=500)
            # ui.input_slider("interest", "Interest Rate", min=0, max=100, value=7, post="%")
            # ui.input_action_button("reset", "Reset filter", width="200px")
        
        with ui.layout_columns(col_widths=(4, 4, 4)):
            with ui.value_box(showcase=ICONS.get("income"), theme="bg-gradient-red-orange", fill=False, heigth="20px"):
                "Monatliche Einkünfte"
                @render.express
                def render_income():
                    f"{total_income():,} CHF"
            with ui.value_box(showcase=ICONS.get("spending"), theme="bg-gradient-red-orange", fill=False):
                "Monatliche Ausgaben"
                @render.express
                def render_expenses():
                    f"{total_expenses():,} CHF"
            with ui.value_box(showcase=ICONS.get("piggy-bank"), theme="bg-gradient-green-teal", fill=False):
                "Ersparnisse"
                @render.express
                def render_savings():
                    f"{total_income()-total_expenses():,} CHF"
        with ui.layout_columns(col_widths=[6, 6]):
            with ui.navset_card_underline(title="Einkünfte und Ausgaben"):
                with ui.nav_panel("sankey"):
                    @render_plotly
                    def sankey_render():
                        node_colors = ["#1f77b4", "#4682b4", "#5f9ea0", "#6495ed", "#00bfff", "#87cefa", "#add8e6", "#b0e0e6", "green"]  # Various blue shades and green
                        fig = go.Figure(data=[go.Sankey(
                            node = dict(
                            pad = 15,
                            thickness = 20,
                            line = dict(color = "black", width = 0.5),
                            label = ["Einkommen", "Gewinn", "Budget", "Wohnen", "Haushalt", "Essen", "Transport", "Hobbys", "Ersparnisse"],
                            color = node_colors
                            ),
                            link = dict(
                            source = [0, 1, 2, 2, 2, 2, 2, 2], # indices correspond to labels
                            target = [2, 2, 3, 4, 5, 6, 7, 8],
                            value = [input.salary_input(),
                                    input.dividend_input(),
                                    input.living_cost_input(),
                                    input.groceries_input(),
                                    input.food_input(),
                                    input.transport_cost_input(),
                                    input.hobbys_input(),
                                    input.salary_input() + input.dividend_input() - input.living_cost_input() - input.groceries_input() - input.food_input() - input.transport_cost_input() - input.hobbys_input(),
                                    ]
                        ))])

                        fig.update_layout(
                            legend=dict(
                                orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
                            )
                        )
                        
                        fig._config = fig._config | {'displayModeBar': False}
                        return fig
                        
                with ui.nav_panel("bars"):
                    @render_plotly
                    def bars_render():
                        # Sample data for income and spendings
                        income_categories = ["Einkommen", "Gewinn"]
                        income_amounts = [input.salary_input(), input.dividend_input()]
                        spending_categories = ["Wohnen", "Haushalt", "Essen", "Transport", "Hobbys"]
                        spending_amounts= [-input.living_cost_input(), -input.groceries_input(), -input.food_input(), -input.transport_cost_input(), -input.hobbys_input()]

                        # Create a bar chart
                        fig = go.Figure()

                        # Add income bars (blue)
                        fig.add_trace(go.Bar(
                            x= income_categories,
                            y= income_amounts,
                            name='Einkünfte',
                            marker_color='blue'
                        ))

                        # Add spendings bars (red)
                        fig.add_trace(go.Bar(
                            x=spending_categories,
                            y=spending_amounts,
                            name='Ausgaben',
                            marker_color='red'
                        ))

                        # Add savings bar (green)
                        fig.add_trace(go.Bar(
                            x=["Ersparnisse"],
                            y=[input.salary_input() + input.dividend_input() - input.living_cost_input() - input.groceries_input() - input.food_input() - input.transport_cost_input() - input.hobbys_input()],
                            name='Ersparnisse',
                            marker_color='green'
                        ))

                        # Update layout
                        fig.update_layout(
                            title='Incomes and Spendings by Category',
                            barmode='group',
                            yaxis_title='Amount ($)',
                            xaxis_title='Category',
                            yaxis=dict(showgrid=True),
                            showlegend=True
                        )
                        fig._config = fig._config | {'displayModeBar': False}
                        return fig

            with ui.card(full_screen=True):
                with ui.card_header(class_="d-flex justify-content-between align-items-center"):
                    "Future Value"
                
                with ui.popover(title="Toggles"):
                    ICONS["ellipsis"]
                    ui.input_switch("inflation_toggle", "Show Inflation", True)

                @render_plotly
                def fv_render():
                    import plotly.graph_objects as go
                    import numpy as np

                    # Parameters
                    initial_amount = 20000  # Initial investment
                    years = np.arange(0, 60, 1)  # Time period in years
                    interest_rate = 0.07  # Interest rate from user input
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
                    fig._config = fig._config | {'displayModeBar': False}
                    fig.update_layout(modebar_remove=['zoom', 'pan', 'toImage'])
                    return fig
    with ui.nav_panel("Immobilien"):
        with ui.layout_columns(col_widths=(3, 3, 3, 3)):
            with ui.value_box(showcase=ICONS.get("wallet"), theme="bg-gradient-indigo-purple", fill=False, heigth="20px"):
                "Privatgelder"
                @render.express
                def render_private_assets():
                    f"{input.bank_account_input():,} CHF"
            with ui.value_box(showcase=ICONS.get("briefcase"), theme="bg-gradient-indigo-purple", fill=False):
                "Säule 2"
                @render.express
                def render_pillar2():
                    f"{input.pillar2_input():,} CHF"
            with ui.value_box(showcase=ICONS.get("piggy-bank"), theme="bg-gradient-indigo-purple", fill=False):
                "Säule 3a"
                @render.express
                def render_pillar3():
                    f"{input.pillar3a_input():,} CHF"
            with ui.value_box(showcase=ICONS.get("stocks"), theme="bg-gradient-indigo-purple", fill=False):
                "Aktiendepots"
                @render.express
                def render_investments():
                    f"{input.investment_input():,} CHF"
    with ui.nav_panel("Portfolio"):
        "Panel A content"

# with ui.sidebar(open="desktop"):
#     ui.input_slider("salary", "Salary", min=0, max=20000, value=8000, step=500)
#     ui.input_slider(
#         "interest",
#         "Interest Rate",
#         min=0,
#         max=100,
#         value=7,
#         post="%",
#     )
#     ui.input_action_button("reset", "Reset filter")


ui.include_css(app_dir / "styles.css")

# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------

@reactive.calc
def total_income():
    return input.salary_input() + input.dividend_input()

@reactive.calc
def total_expenses():
    return input.living_cost_input() + input.groceries_input() + input.food_input() + input.transport_cost_input() + input.hobbys_input()
