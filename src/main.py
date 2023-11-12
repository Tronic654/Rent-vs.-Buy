import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_mantine_components as mt

app = Dash(__name__)
#General Inputs:
timeline = 40

# Input Buy:
house_value = 500000
down_payment = 0.2
principal_amount = house_value*(1-down_payment)
interest_rate = 4.5/100  # 4.5%
mortgage_years = 25
#house costs
annual_home_maintenance = 7500
house_insurance = 120
strata_fee = 600
house_other = 0
#buy/sell
house_purchase_fee = 12000
house_sell_fee = 0.04

#Input Rent:
initial_portfolio = house_value*down_payment
rent_monthly = 1630
rent_increase = 2.5/100
utilities_monthly = 120
rent_insurance = 30
rent_other = 0

#Input Investments:
portfolio_nominal_aftertax_return = 6.0/100
house_nominal_appreciation = 3.5/100
yearly_inflation = 2.5/100

#Portfolio
#Use this longterm for backtesting different market scenerios: http://www.econ.yale.edu/~shiller/data.htm
def portfolio():
    #monthly contribution = 
    return

#House Portfolio
#Figures out the monthly increase in value
def house_portfolio(timeline, house_value, house_appreciation, selling_fee, mortgage_df):
    monthly_house_appreciation = (1+house_appreciation)**(1/12)
    house_value = house_value * (monthly_house_appreciation)

    df_mortgage = pd.DataFrame({'Month': mortgage_df['Month'], 'Remaining_Principal': mortgage_df['Remaining_Principal']})

    data = []

    for month in range(1, (timeline * 12) + 1):
        data.append([month, round(house_value, 2)])

        house_value = house_value * (monthly_house_appreciation)

    df_house_portfolio = pd.DataFrame(data, columns=["Month", "Monthly House Value"])

    df = pd.merge(df_mortgage, df_house_portfolio, on="Month")

    df['Home Equity'] = df["Monthly House Value"] - df["Remaining_Principal"] - (df["Monthly House Value"] * selling_fee)

    return df


#House Cost - Monthly
def house(timeline, mortgage_df, annual_home_maintenance, utilities, insurance, strata, other, inflation):
    #housing expense
    monthly_home_maintenance = annual_home_maintenance/12
    monthly_inflation = (1+inflation)**(1/12)
    monthly_house_expense = monthly_home_maintenance + utilities + insurance + strata + other

    data = []
    count = 0

    for month in range(1, (timeline * 12) + 1):
        data.append([month, round(monthly_home_maintenance, 2), round(utilities, 2), round(insurance, 2), round(strata, 2), round(other, 2), round(monthly_house_expense, 2)])

        count += 1
        if count % 12 == 0:
            annual_home_maintenance = annual_home_maintenance * (1+inflation) #updates once a year
            insurance = insurance * (1+inflation) #updates once a year
            strata = strata * (1+inflation) #updates once a year)
            count = 0
        
        utilities = utilities * (monthly_inflation) #updates every month
        monthly_home_maintenance = annual_home_maintenance/12 #updates every month

        monthly_house_expense = monthly_home_maintenance + utilities + insurance + strata + other

    df_house = pd.DataFrame(data, columns=["Month", "Monthly Maintenance", "Monthly Utilities", "Monthly Insurance", "Monthly Strata", "Monthly Other", "Monthly House Expense"])

    return df_house

#Rent Cost - Monthly
#IT WORKS!!!!!!!!#
def rent(rent, rent_increase, utilities, insurance, timeline, inflation, other):
    monthly_rent_expense = rent + insurance + utilities
    monthly_inflation = (1+inflation)**(1/12)

    data = []
    count = 0

    for month in range(1, (timeline * 12) + 1):
        data.append([month, round(rent, 2), round(utilities, 2), round(insurance, 2), round(monthly_rent_expense, 2), round(other, 2)])

        count += 1
        if count % 12 == 0:
            rent = rent * (1+rent_increase) #updates once a year
            insurance = insurance * (1+inflation)#updates once a year
            count = 0
        
        utilities = utilities * (monthly_inflation)#updates every month
        
        monthly_rent_expense = rent + insurance + utilities

    df = pd.DataFrame(data, columns=["Month", "Monthly Rent", "Monthly Utilities", "Monthly Insurance", "Monthly Rent Expense", "Monthly Other"])

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
house_cost = house(timeline, amortization_table, annual_home_maintenance, utilities_monthly, house_insurance, strata_fee, house_other, yearly_inflation)
house_equity = house_portfolio(timeline, house_value, house_nominal_appreciation, house_sell_fee, amortization_table)
#portfolio = portfolio(amortization_table, rent_scenerio)

#Create table from dataframe
app.layout = dash_table.DataTable(amortization_table.to_dict('records'))

app.layout = mt.Grid(
    children=[
        mt.Col(
            span=6,
            children=[
                html.H2("Table 1"), dash_table.DataTable(amortization_table.to_dict('records'))
            ]
        ),
        mt.Col(
            span=6,
            children=[
                html.H2("Table 2"), dash_table.DataTable(house_equity.to_dict('records'))
            ]
        )
    ]
)

if __name__ == '__main__':
    app.run(debug=True)