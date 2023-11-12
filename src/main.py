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
down_payment = 20/100
principal_amount = house_value*(1-down_payment)
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
def stock_portfolio(initial_sum, ):
    #cakculates based on a starting amount and then a monthly contribution
    #This will work for both the rent secenerio and the buy scenerio
    #Once the mortgage and rent swap can you start adding it to the mortgage equity difference? 
    #when (house expense) > (rent expense) -> rent portfolio receives difference as contributions
    #when (house expense) < (rent expense) -> house portfolio receives difference as contributions. This is added the the eqioty of the house
    #monthly contribution = 




    return

#Cashflow of the house vs rent
def cashflow(house, rent):
    df = pd.merge(house[['Month', 'Monthly House Expense']], rent[['Month', 'Monthly Rent Expense']], on='Month')

    df['Expense Difference'] = df['Monthly House Expense'] - df['Monthly Rent Expense'] #if pos=to rent #if neg=to house

    return df

#House Portfolio
#Figures out the monthly increase in value
def house_equity(timeline, house_value, house_appreciation, selling_fee, mortgage_df):
    monthly_house_appreciation = (1+house_appreciation)**(1/12)
    house_value = house_value * (monthly_house_appreciation)

    df_mortgage = pd.DataFrame({'Month': mortgage_df['Month'], 'Remaining_Principal': mortgage_df['Remaining_Principal']})

    data = []

    for month in range(1, (timeline * 12) + 1):
        data.append([month, round(house_value, 2)])

        house_value = house_value * (monthly_house_appreciation)

    df_house_portfolio = pd.DataFrame(data, columns=["Month", "Monthly House Value"])

    df = pd.merge(df_mortgage, df_house_portfolio, on="Month")

    df['Home Equity'] = round((df["Monthly House Value"] - df["Remaining_Principal"] - (df["Monthly House Value"] * selling_fee)), 2)

    return df


#House Cost - Monthly
#When merging the mortage df to the house df it cuts the rows to the shpter df size
def house(timeline, mortgage_df, annual_home_maintenance, utilities, insurance, strata, other, inflation, prop_tax, house_appreciation, house):
    #housing expense
    monthly_home_maintenance = annual_home_maintenance/12
    monthly_inflation = (1+inflation)**(1/12)
    #monthly_house_expense = monthly_home_maintenance + utilities + insurance + strata + other
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

        #monthly_house_expense = monthly_home_maintenance + utilities + insurance + strata + other

    df_mortgage = pd.DataFrame({'Month': mortgage_df['Month'], 'Principal_Payment': mortgage_df['Principal_Payment'], 'Interest_Payment': mortgage_df['Interest_Payment']})
    df_house = pd.DataFrame(data, columns=["Month", "Monthly Maintenance", "Monthly Utilities", "Monthly Insurance", "Monthly Strata", "Monthly Other", 'Propert Tax'])

    df = pd.merge(df_mortgage, df_house, on="Month", how='right')
    df = df.fillna(0)

    df["Monthly House Expense"] = df["Monthly Maintenance"] + df['Monthly Utilities'] + df['Monthly Insurance'] + df['Monthly Strata'] + df['Monthly Other'] + df['Principal_Payment'] + df['Interest_Payment']

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
house_equity_df = house_equity(timeline, house_value, house_nominal_appreciation, house_sell_fee, amortization_table)
cash = cashflow(house_cost, rent_cost)
#portfolio = portfolio(amortization_table, rent_scenerio)

#Create table from dataframe
app.layout = dash_table.DataTable(amortization_table.to_dict('records'))

app.layout = mt.Grid(
    children=[
        mt.Col(
            span=6,
            children=[
                html.H2("Table 1"), dash_table.DataTable(cash.to_dict('records'))
            ]
        ),
        mt.Col(
            span=6,
            children=[
                html.H2("Table 2"), dash_table.DataTable(house_cost.to_dict('records'))
            ]
        )
    ]
)

if __name__ == '__main__':
    app.run(debug=True)