import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objs as go
from dash import Dash, html, dash_table, dcc, callback, Output, Input, dash_table, State
import dash_mantine_components as mt
# import dash_bootstrap_components as dbc

#test

app = Dash(__name__)

#****************************************************
#General Inputs:
timeline_input = dcc.Input(
    id='timeline-input',
    type='number',
    value=40,
    placeholder='Enter timeline...',
)
timeline = int(timeline_input.value)

# Input Buy:
house_value_input = dcc.Input(
    id='house_value-input',
    type='number',
    value=500000,
    placeholder='Enter house values...',
)
house_value = int(house_value_input.value)
down_payment = 20/100
principal_amount = int(house_value_input.value)*(1-down_payment)
interest_rate = 4.5/100  # 4.5%
mortgage_years = 25
#house costs
annual_home_maintenance = 3000
house_insurance = 120
strata_fee = 500
house_other = 0
property_tax = 0.25/100
#buy/sell
house_purchase_fee = 12000
house_sell_fee = 4/100

#Input Rent:
initial_portfolio = int(house_value_input.value)*down_payment
rent_monthly = 1630
rent_increase = 2.5/100
utilities_monthly = 120
rent_insurance = 30
rent_other = 0

#Input Investments:
portfolio_nominal_aftertax_return = 6.0/100
house_nominal_appreciation = 3.5/100
yearly_inflation = 2.5/100
#**********************************************************

#Total House Equity
def total_house_equity(house, portfolio):
    df_temp = pd.merge(house, portfolio, on="Month", how='right')
    df_temp = df_temp.fillna(0)

    df = pd.DataFrame()

    df["Month"] = df_temp["Month"]
    df["Portfolio Value"] = df_temp["Home Equity"] + df_temp["Portfolio Value"]

    return df

#Portfolio
#Use this longterm for backtesting different market scenerios: http://www.econ.yale.edu/~shiller/data.htm
def stock_portfolio(type, initial_sum, cashflow_df, avg_return, buy_transaction):
    portfolio = initial_sum + buy_transaction
    monthly_return = (1+avg_return)**(1/12)
    invest_return = 0

    data = []
    month = 1

    if type == 0: #rent
        for index, row in cashflow_df.iterrows():
            data.append([month, round(invest_return,2), round(portfolio, 2)])
            monthly_contribution = row['Expense Difference']
            invest_return = portfolio * (monthly_return-1)

            portfolio = portfolio + monthly_contribution + invest_return

            month += 1

        df_portfolio = pd.DataFrame(data, columns=["Month", "Investment Return", "Portfolio Value"])
    
    elif type == 1: #house
        for index, row in cashflow_df.iterrows():
            monthly_contribution = row['Expense Difference']

            if monthly_contribution > 0:
                data.append([month, round(invest_return,2), round(portfolio, 2)])
                month += 1

            else:  
                monthly_contribution = abs(row['Expense Difference'])
                invest_return = portfolio * (monthly_return-1)
                portfolio = portfolio + monthly_contribution + invest_return
                data.append([month, round(invest_return,2), round(portfolio, 2)])
                month += 1

    df_portfolio = pd.DataFrame(data, columns=["Month", "Investment Return", "Portfolio Value"])
    
    return df_portfolio

#Cashflow 
# #House vs Rent
def cashflow(house, rent):
    df = pd.merge(house[['Month', 'Monthly House Expense']], rent[['Month', 'Monthly Rent Expense']], on='Month')

    df['Expense Difference'] = df['Monthly House Expense'] - df['Monthly Rent Expense'] #if pos=to rent #if neg=to house

    return df

#House Portfolio
#Figures out the monthly increase in value
def house_equity(mortgage_years, house_value, house_appreciation, selling_fee, mortgage_df, timeline):
    monthly_house_appreciation = (1+house_appreciation)**(1/12)
    house_value = house_value * (monthly_house_appreciation)
    starting_house_value = house_value

    df_mortgage = pd.DataFrame({'Month': mortgage_df['Month'], 'Remaining_Principal': mortgage_df['Remaining_Principal']})

    data = []

    for month in range(1, (mortgage_years * 12) + 1):
        data.append([month, round(house_value, 2)])

        house_value = house_value * (monthly_house_appreciation)

    for month in range((mortgage_years * 12) + 2, (timeline * 12) + 1):
        data.append([month, round(house_value, 2)])

        house_value = house_value * (monthly_house_appreciation)

    df_house_portfolio = pd.DataFrame(data, columns=["Month", "Monthly House Value"])

    df = pd.merge(df_mortgage, df_house_portfolio, on="Month", how='right')
    df = df.fillna(0)

    df['Home Equity'] = round((df["Monthly House Value"] - df["Remaining_Principal"] - ( starting_house_value * selling_fee)), 2)

    return df


#House Cost - Monthly
def house(timeline, mortgage_df, annual_home_maintenance, utilities, insurance, strata, other, inflation, prop_tax, house_appreciation, house):
    monthly_home_maintenance = annual_home_maintenance/12
    monthly_inflation = (1+inflation)**(1/12)
    monthly_property_tax = (house * prop_tax) / 12

    data = []
    count = 0

    for month in range(1, (timeline * 12) + 1):
        data.append([month, round(monthly_home_maintenance, 2), round(utilities, 2), round(insurance, 2), round(strata, 2), round(other, 2), round(monthly_property_tax, 2)])

        count += 1
        if count % 12 == 0:
            annual_home_maintenance = annual_home_maintenance * (1+inflation) #updates once a year
            insurance = insurance * (1+inflation) #updates once a year
            strata = strata * (1+inflation) #updates once a year)
            monthly_property_tax = (prop_tax * (house * (1+house_appreciation)))/12
            count = 0
        
        utilities = utilities * (monthly_inflation) #updates every month
        monthly_home_maintenance = annual_home_maintenance/12 #updates every month

    df_mortgage = pd.DataFrame({'Month': mortgage_df['Month'], 'Principal_Payment': mortgage_df['Principal_Payment'], 'Interest_Payment': mortgage_df['Interest_Payment']})
    df_house = pd.DataFrame(data, columns=["Month", "Monthly Maintenance", "Monthly Utilities", "Monthly Insurance", "Monthly Strata", "Monthly Other", 'Propert Tax'])

    df = pd.merge(df_mortgage, df_house, on="Month", how='right')
    df = df.fillna(0)

    df["Monthly House Expense"] = df["Monthly Maintenance"] + df['Monthly Utilities'] + df['Monthly Insurance'] + df['Monthly Strata'] + df['Monthly Other'] + df['Propert Tax'] + df['Principal_Payment'] + df['Interest_Payment']

    return df

#Rent Cost - Monthly
#IT WORKS!!!!!!!!#
def rent(rent, rent_increase, utilities, insurance, timeline, inflation, other):
    monthly_rent_expense = rent + insurance + utilities + other
    monthly_inflation = (1+inflation)**(1/12)

    data = []
    count = 0

    for month in range(1, (timeline * 12) + 1):
        data.append([month, round(rent, 2), round(utilities, 2), round(insurance, 2), round(other, 2), round(monthly_rent_expense, 2)])

        count += 1
        if count % 12 == 0:
            rent = rent * (1+rent_increase) #updates once a year
            insurance = insurance * (1+inflation)#updates once a year
            count = 0
        
        utilities = utilities * (monthly_inflation)#updates every month
        
        monthly_rent_expense = rent + insurance + utilities + other

    df = pd.DataFrame(data, columns=["Month", "Monthly Rent", "Monthly Utilities", "Monthly Insurance", "Monthly Other", "Monthly Rent Expense"])

    return df

#Mortgage calculator
#IT WORKS!!!!!!!!#
def mortgage_amortization(principal, annual_interest_rate, years):
    semi_annual_rate = annual_interest_rate / 2
    compounded_annual_rate = ((1+semi_annual_rate)**2)-1
    monthly_interest_rate = (1+compounded_annual_rate)**(1/12)-1
    total_payments = years * 12
    monthly_payment = principal * monthly_interest_rate / (1 - (1 + monthly_interest_rate) ** -total_payments)
    
    data = []
    remaining_principal = principal
    
    for month in range(1, total_payments + 1):
        
        interest_payment = remaining_principal * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        remaining_principal -= principal_payment

        data.append([month, round(remaining_principal, 2), round(principal_payment, 2), round(interest_payment, 2)])
        
    df = pd.DataFrame(data, columns=["Month", "Remaining_Principal", "Principal_Payment", "Interest_Payment"])

    return df

#Create dataframes
amortization_table = mortgage_amortization(principal_amount, interest_rate, mortgage_years)
rent_cost = rent(rent_monthly, rent_increase, utilities_monthly, rent_insurance, timeline, yearly_inflation, rent_other)
house_cost = house(timeline, amortization_table, annual_home_maintenance, utilities_monthly, house_insurance, strata_fee, house_other, yearly_inflation, property_tax, house_nominal_appreciation, house_value)
house_equity_df = house_equity(timeline, house_value, house_nominal_appreciation, house_sell_fee, amortization_table, timeline)
cash = cashflow(house_cost, rent_cost)
rent_portfolio = stock_portfolio(0, (house_value * down_payment), cash, portfolio_nominal_aftertax_return, house_purchase_fee)
house_portfolio = stock_portfolio(1, 0, cash, portfolio_nominal_aftertax_return, 0)
final_house_equity = total_house_equity(house_equity_df, house_portfolio)
#portfolio = portfolio(amortization_table, rent_scenerio)
dfs = [rent_portfolio, final_house_equity]

#Create table from dataframe
# app.layout = dash_table.DataTable(amortization_table.to_dict('records'))

# app.layout = mt.Grid(
#     children=[
#         mt.Col(
#             span=4,
#             children=[
#                 html.H2("Table 1"), dash_table.DataTable(house_equity_df.to_dict('records'))
#             ]
#         ),
#         mt.Col(
#             span=4,
#             children=[
#                 html.H2("Table 2"), dash_table.DataTable(house_portfolio.to_dict('records'))
#             ]
#         ),
#         mt.Col(
#             span=4,
#             children=[
#                 html.H2("Table 3"), dash_table.DataTable(final_house_equity.to_dict('records'))
#             ]
#         )
#     ]
# )

# Create a callback to update the graph based on timeline input
@app.callback(
    Output('line-graph', 'figure'),
    Output('Table-1', 'test'),
    Input('submit-button-state', 'n_clicks'),
    State('timeline-input', 'value'),
    State('house_value-input', 'value')
)
def update_graph(n_clicks, timeline, house_value):
    # Recalculate the dataframes based on the new timeline value
    # initial_portfolio = int(house_value_input.value)*down_payment
    # principal_amount = int(house_value_input.value)*(1-down_payment)

    amortization_table = mortgage_amortization(principal_amount, interest_rate, mortgage_years)
    rent_cost = rent(rent_monthly, rent_increase, utilities_monthly, rent_insurance, timeline, yearly_inflation, rent_other)
    house_cost = house(timeline, amortization_table, annual_home_maintenance, utilities_monthly, house_insurance, strata_fee, house_other, yearly_inflation, property_tax, house_nominal_appreciation, house_value)
    house_equity_df = house_equity(timeline, house_value, house_nominal_appreciation, house_sell_fee, amortization_table, timeline)
    cash = cashflow(house_cost, rent_cost)
    rent_portfolio = stock_portfolio(0, (house_value * down_payment), cash, portfolio_nominal_aftertax_return, house_purchase_fee)
    house_portfolio = stock_portfolio(1, 0, cash, portfolio_nominal_aftertax_return, 0)
    final_house_equity = total_house_equity(house_equity_df, house_portfolio)
    dfs = [rent_portfolio, final_house_equity]

    test = cash.to_dict('records')
    # Update the graph with the new dataframes
    figure = {
        'data': [
            go.Scatter(
                x=df['Month'],
                y=df['Portfolio Value'],
                mode='lines+markers',
                name='Rent' if i == 0 else 'Buy'
            ) for i, df in enumerate(dfs)
        ],
        'layout': go.Layout(
            title='Rent vs. Buy',
            xaxis={'title': 'Months'},
            yaxis={'title': 'Dollars(CAD)'},
            showlegend=True
        )
    }

    return figure, test

app.layout = html.Div([
    html.Div([
        html.Label('Timeline'),
        timeline_input,
    ]),
    html.Div([
        html.Label('House Value'),
        house_value_input,
    ]),
    html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
    dcc.Graph(
        id='line-graph',
        figure={  # Placeholder figure
            'data': [],
            'layout': {
                'title': 'Rent vs. Buy',
                'xaxis': {'title': 'Months'},
                'yaxis': {'title': 'Dollars(CAD)'},
                'showlegend': True
            }
        }
    ),
    # dbc.Row([
    #     dbc.Col(
    #         [
    #             html.H2("Table 1"), 
    #             dash_table.DataTable(data=house_equity_df.to_dict('records'))
    #         ],
    #         width=4
    #     ),
    #     dbc.Col(
    #         [
    #             html.H2("Table 2"), 
    #             dash_table.DataTable(data=house_portfolio.to_dict('records'))
    #         ],
    #         width=4
    #     ),
    #     dbc.Col(
    #         [
    #             html.H2("Table 3"), 
    #             dash_table.DataTable(data=final_house_equity.to_dict('records'))
    #         ],
    #         width=4
    #     ),
    # ])
    mt.Grid(children=[
        mt.Col(
            span=3,
            children=[
                html.H2("Mortgage"), dash_table.DataTable(id='Table-1', data=amortization_table.to_dict('records'))
            ]
        ),
        mt.Col(
            span=3,
            children=[
                html.H2("House Equity"), dash_table.DataTable(id='Table-2',data=house_equity_df.to_dict('records'))
            ]
        ),
        mt.Col(
            span=3,
            children=[
                html.H2("House Portfolio"), dash_table.DataTable(id='Table-3',data=house_portfolio.to_dict('records'))
            ]
        ),
        mt.Col(
            span=3,
            children=[
                html.H2("Total House Equity"), dash_table.DataTable(id='Table-4',data=final_house_equity.to_dict('records'))
            ]
        )
    ])
])


if __name__ == '__main__':
    app.run(debug=True)