from formula_lib import constants

import faicons as fa

# Load data and compute static values
from shared import app_dir
from shinywidgets import render_plotly

from shiny import reactive, render
from shiny.express import input, ui

import plotly.graph_objects as go

import numpy as np
import numpy_financial as npf

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
                ui.input_numeric("net_income_input", "Monatlicher Nettolohn", 8000, step=500)
                ui.br()
                ui.input_numeric("gross_income_input", "Monatlicher Bruttolohn", 8800, step=500)
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
                ui.br()
                ui.input_numeric("other_input", "Sonstiges", 0, step=50)

            with ui.nav_panel("Assets"):
                ui.input_numeric("bank_account_input", "Bankkonten", 0, step=500)
                ui.br()
                ui.input_numeric("investment_input", "Aktiendepot", 0, step=500)
                ui.br()
                ui.input_numeric("pillar2_input", "Säule 2", 0, step=500)
                ui.br()
                ui.input_numeric("pillar3a_input", "Säule 3a", 0, step=500)
                ui.br()
            with ui.nav_panel("Wunschimmobilie"):
                ui.input_numeric("estate_price_input", "Kaufpreis", 1000000, step="10000")
                ui.br()
                ui.input_numeric("equity_input", "Eigenmittel", 200000, step=5000)
                ui.br()
                ui.input_select("estate_type_input", "Immobilien Typ", ["Eigentumswohnung", "Einfamilienhaus", "Mehrfamilienhaus"])
                ui.br()
                ui.input_select("estate_usecase_input", "Verwendungszweck", ["Eigenbedarf", "Renditeobjekt"])
                ui.br()
                ui.input_numeric("mortgage_rate1_input", "Zinssatz 1. Hypothek [%]", 2, step=0.01)
                ui.br()
                ui.input_numeric("mortgage_rate2_input", "Zinssatz 2. Hypothek [%]", 2, step=0.01)

    with ui.nav_panel("Finanzplanung"):
        # with ui.card(full_screen=True):
        #     with ui.card_header(class_="d-flex justify-content-between align-items-center"):
        #             "Input"
        #     ui.input_slider("salary", "Salary", min=0, max=20000, value=8000, step=500)
        #     ui.input_slider("interest", "Interest Rate", min=0, max=100, value=7, post="%")
        #     ui.input_action_button("reset", "Reset filter", width="200px")
        
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
                            value = [input.net_income_input(),
                                    input.dividend_input(),
                                    input.living_cost_input(),
                                    input.groceries_input(),
                                    input.food_input(),
                                    input.transport_cost_input(),
                                    input.hobbys_input(),
                                    input.net_income_input() + input.dividend_input() - input.living_cost_input() - input.groceries_input() - input.food_input() - input.transport_cost_input() - input.hobbys_input(),
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
                        income_amounts = [input.net_income_input(), input.dividend_input()]
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
                            y=[input.net_income_input() + input.dividend_input() - input.living_cost_input() - input.groceries_input() - input.food_input() - input.transport_cost_input() - input.hobbys_input()],
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
                    initial_amount = total_assets()
                    years = np.arange(0, 60, 1)  # Time period in years
                    interest_rate = constants.IMPUTED_INTEREST_RATE
                    inflation_rate = constants.INFLATION_RATE

                    # Calculate compound interest
                    money_growth = initial_amount * (1 + interest_rate) ** years
                    money_growth = npf.fv(interest_rate, years, -(total_income()-total_expenses()), -total_assets())

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
                    
                    fig.add_trace(go.Scatter(
                            x=years, y=[1400000] * 60 , mode='lines', name='Immobilie',
                            line=dict(color='green'),
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
        with ui.layout_columns(col_widths=[6,6]):
            with ui.card():
                "Assets"
                with ui.layout_column_wrap(width=1/2):
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
            with ui.card():
                "Immobilien Informationen"
                with ui.layout_column_wrap(width=1/2):
                    with ui.value_box(showcase=ICONS.get("wallet"), theme="bg-gradient-indigo-purple", fill=False, heigth="20px"):
                        "Maximaler Immobilienpreis"
                        @render.express
                        def render_max_estate_price():
                            f"{max_estate_price() // 5000 * 5000:,} CHF"
                    with ui.value_box(showcase=ICONS.get("briefcase"), theme="bg-gradient-indigo-purple", fill=False):
                        "Eigenmietwert"
                        @render.express
                        def notional_rental_value():
                            f"{input.pillar2_input():,} CHF"
                    with ui.value_box(showcase=ICONS.get("piggy-bank"), theme="bg-gradient-indigo-purple", fill=False):
                        "Hypothekarzins"
                        @render.express
                        def total_interest_rate():
                            f"{round(total_interest_rate_mortgage()):,} CHF"



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
def gross_from_net_income():
    return input.net_income_input() * 1.1

@reactive.calc
def total_income():
    return input.net_income_input() + input.dividend_input()

@reactive.calc
def total_expenses():
    return input.living_cost_input() + input.groceries_input() + input.food_input() + input.transport_cost_input() + input.hobbys_input()

@reactive.calc
def total_assets():
    return input.bank_account_input() + input.investment_input() + input.pillar2_input() + input.pillar3a_input()

@reactive.calc
def max_estate_price():
    max_estate_price = (input.gross_income_input() * 12)/0.17667
    return min(max_estate_price, total_assets() / 0.2)

@reactive.calc
def interest_rate_first_mortgage():
    return input.estate_price_input() * 2/3 * input.mortgage_rate1_input() / 100

@reactive.calc
def interest_rate_second_mortgage():
    interest_rate =  (input.estate_price_input() * 1/3 - input.equity_input()) * input.mortgage_rate2_input() / 100
    return max(0, interest_rate)

@reactive.calc
def total_interest_rate_mortgage():
    return interest_rate_first_mortgage() + interest_rate_second_mortgage()

@reactive.calc
def notional_rental_value():
    return 0

@reactive.calc
def running_costs():
    input.estate_price_input() * constants.RUNNING_COSTS_RATE

@reactive.calc
def amortisation_second_mortgage():
    return (input.estate_price_input() * 1/3 - input.equity_input()) / constants.MORTGAGE_REIMBURSEMENT_DURATION 

@reactive.calc
def opportunity_cost():
    return input.equity_input() * constants.IMPUTED_INTEREST_RATE

@reactive.calc
def opportunity_gain():
    match input.estate_type_input():
        case "Eigentumswohnung":
            return input.estate_price_input() * constants.ROI_CONDOMINIUM
        case "Einfamilienhaus":
            return input.estate_price_input() * constants.ROI_SINGLE_HOUSE
        case "Mehrfamilienhaus":
            return input.estate_price_input() * constants.ROI_APARTMENT_HOUSE

@reactive.calc
def affordable_income():
    return 3 * (amortisation_second_mortgage() + running_costs() + (input.estate_price_input() - input.equity_input()) * constants.AFFORDABLE_INCOME_INTEREST_RATE)