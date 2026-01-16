"""
Clean implementation of Buy & Rent vs Invest in Stocks simulation
Dedicated functions for rental property investment strategy
"""
import pandas as pd
import numpy as np


def calculate_monthly_payment(principal, annual_rate, years):
    """Calculate monthly mortgage payment"""
    if annual_rate == 0:
        return principal / (years * 12)
    
    monthly_rate = annual_rate / 12
    num_payments = years * 12
    payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
              ((1 + monthly_rate) ** num_payments - 1)
    return payment


def calculate_amortization_schedule(principal, annual_rate, years):
    """Generate mortgage amortization schedule"""
    monthly_payment = calculate_monthly_payment(principal, annual_rate, years)
    monthly_rate = annual_rate / 12
    num_payments = years * 12
    
    schedule = []
    balance = principal
    
    for month in range(1, num_payments + 1):
        interest = balance * monthly_rate
        principal_payment = monthly_payment - interest
        balance -= principal_payment
        
        schedule.append({
            'month': month,
            'payment': monthly_payment,
            'principal': principal_payment,
            'interest': interest,
            'balance': max(0, balance)
        })
    
    return pd.DataFrame(schedule)


def simulate_rental_property(params):
    """
    Simulate rental property investment strategy
    
    Strategy:
    - Day of purchase: Pay down payment + closing costs
    - Monthly: True cost = Unrecoverable costs - Rental income - Monthly tax benefit
    - Net proceeds: Property value - remaining mortgage - selling costs
    
    Tax Benefit (Monthly):
    - Monthly tax benefit = (Monthly interest + Monthly property tax) × Tax bracket
    - Already subtracted from true monthly cost
    """
    # Extract parameters
    purchase_price = params['purchase_price']
    down_payment_pct = params['down_payment_pct']
    mortgage_rate = params['mortgage_rate']
    mortgage_years = params['mortgage_years']
    closing_costs_pct = params['closing_costs_pct']
    appreciation_rate = params['appreciation_rate']
    property_tax_rate = params['property_tax_rate']
    hoa_monthly = params['hoa_monthly']
    insurance_monthly = params['insurance_monthly']
    maintenance_rate = params['maintenance_rate']
    tax_bracket = params['tax_bracket']
    monthly_rent = params['monthly_rent']
    vacancy_rate = params['vacancy_rate']
    years = params['years']
    
    
    # Calculate initial values
    down_payment = purchase_price * down_payment_pct
    closing_costs = purchase_price * closing_costs_pct
    loan_amount = purchase_price - down_payment
    initial_investment = down_payment + closing_costs
    
    # Mortgage amortization
    amortization = calculate_amortization_schedule(loan_amount, mortgage_rate, mortgage_years)
    
    # Initialize tracking variables
    months = years * 12
    monthly_data = []
    
    # Annual tracking for tax events
    annual_rental_income = 0
    annual_interest = 0
    annual_property_tax = 0
    
    for month in range(1, months + 1):
        year_num = (month - 1) // 12 + 1
        month_in_year = (month - 1) % 12 + 1
        
        # Property value appreciation
        years_elapsed = (month - 1) / 12
        property_value = purchase_price * (1 + appreciation_rate) ** years_elapsed
        
        # Mortgage payments
        if month <= len(amortization):
            mortgage_payment = amortization.iloc[month - 1]['payment']
            principal_payment = amortization.iloc[month - 1]['principal']
            interest_payment = amortization.iloc[month - 1]['interest']
            remaining_balance = amortization.iloc[month - 1]['balance']
        else:
            mortgage_payment = 0
            principal_payment = 0
            interest_payment = 0
            remaining_balance = 0
        
        # Monthly costs
        property_tax_monthly = (property_value * property_tax_rate) / 12
        maintenance_monthly = (property_value * maintenance_rate) / 12
        
        # Unrecoverable costs
        unrecoverable = interest_payment + property_tax_monthly + hoa_monthly + insurance_monthly + maintenance_monthly
        
        # Add closing costs in month 1
        if month == 1:
            unrecoverable += closing_costs
        
        # Monthly tax benefit from deductions
        # Tax benefit = Tax bracket × (Interest + Property tax)
        monthly_tax_benefit = (interest_payment + property_tax_monthly) * tax_bracket
        
        # Rental income (accounting for vacancy)
        rental_income = monthly_rent * (1 - vacancy_rate)
        
        # True cost of ownership (unrecoverable costs - rental income - tax benefit)
        true_cost = unrecoverable - rental_income - monthly_tax_benefit
        
        # Accumulate for annual tax event
        annual_rental_income += rental_income
        annual_interest += interest_payment
        annual_property_tax += property_tax_monthly
        
        # Operating income = rental income only
        monthly_operating_income = rental_income
        
        # Net proceeds = Property value - remaining mortgage
        # Closing costs are tracked in cumulative costs, not subtracted here
        net_proceeds = property_value - remaining_balance
        
        # Cumulative true cost
        cumulative_true_cost = sum([d['true_cost'] for d in monthly_data]) + true_cost if monthly_data else true_cost
        
        # Cumulative operating income
        cumulative_operating_income = sum([d['monthly_operating_income'] for d in monthly_data]) + monthly_operating_income if monthly_data else monthly_operating_income
        
        monthly_data.append({
            'month': month,
            'year': year_num,
            'property_value': property_value,
            'mortgage_payment': mortgage_payment,
            'principal_payment': principal_payment,
            'interest_payment': interest_payment,
            'remaining_balance': remaining_balance,
            'property_tax_monthly': property_tax_monthly,
            'hoa': hoa_monthly,
            'insurance': insurance_monthly,
            'maintenance': maintenance_monthly,
            'unrecoverable': unrecoverable,
            'monthly_tax_benefit': monthly_tax_benefit,
            'rental_income': rental_income,
            'true_cost': true_cost,
            'cumulative_true_cost': cumulative_true_cost,
            'monthly_operating_income': monthly_operating_income,
            'cumulative_operating_income': cumulative_operating_income,
            'net_proceeds': net_proceeds
        })
    
    df = pd.DataFrame(monthly_data)
    
    # Final calculations
    final_property_value = df.iloc[-1]['property_value']
    final_remaining_balance = df.iloc[-1]['remaining_balance']
    selling_costs = final_property_value * 0.06  # Assume 6% selling costs
    
    # Net proceeds = Property value - Selling costs - Remaining mortgage
    # Closing costs are already in cumulative costs
    final_net_proceeds = final_property_value - selling_costs - final_remaining_balance
    
    # Cumulative costs = Sum of true costs + Selling costs
    # (Closing costs are already included in month 1 unrecoverable costs)
    final_cumulative_cost = df['cumulative_true_cost'].iloc[-1] + selling_costs
    
    summary = {
        'initial_payment': initial_investment,
        'final_property_value': final_property_value,
        'selling_costs': selling_costs,
        'final_net_proceeds': final_net_proceeds,
        'total_true_cost': final_cumulative_cost,
        'total_operating_income': df['cumulative_operating_income'].iloc[-1],
        'total_rental_income': df['rental_income'].sum()
    }
    
    return {
        'monthly_df': df,
        'summary': summary
    }


def simulate_stock_investment(params, rental_monthly_expenses):
    """
    Simulate stock-only investment strategy
    
    Strategy:
    - Day of purchase: Invest down payment + closing costs
    - Monthly: Contribute true cost + principal payment from rental strategy
    - Monthly: Dividends reinvested
    - Annually: Pay tax on cumulative dividends
    - Net proceeds: Stock portfolio value
    """
    # Extract parameters
    initial_investment = params['initial_investment']
    stock_return_rate = params['stock_return_rate']
    dividend_yield = params['dividend_yield']
    tax_bracket = params['tax_bracket']
    years = params['years']
    
    # Initialize
    months = years * 12
    monthly_data = []
    
    portfolio_value = initial_investment
    cumulative_dividends = 0
    cumulative_dividend_tax = 0
    annual_dividends = 0
    
    for month in range(1, months + 1):
        year_num = (month - 1) // 12 + 1
        month_in_year = (month - 1) % 12 + 1
        
        # Monthly contribution from rental strategy
        monthly_contribution = rental_monthly_expenses[month - 1]
        
        # Portfolio growth
        monthly_return = stock_return_rate / 12
        portfolio_value = portfolio_value * (1 + monthly_return) + monthly_contribution
        
        # Monthly dividends (reinvested)
        monthly_dividend = portfolio_value * (dividend_yield / 12)
        annual_dividends += monthly_dividend
        cumulative_dividends += monthly_dividend
        
        # Operating income = dividends
        monthly_operating_income = monthly_dividend
        
        # Annual tax event
        if month_in_year == 12:
            # Tax on dividends
            dividend_tax = annual_dividends * tax_bracket
            cumulative_dividend_tax += dividend_tax
            
            # Reset annual tracker
            annual_dividends = 0
        else:
            dividend_tax = 0
        
        # Net proceeds = portfolio value
        net_proceeds = portfolio_value
        
        # Cumulative cost = dividend taxes paid
        cumulative_cost = cumulative_dividend_tax
        
        # Cumulative operating income
        cumulative_operating_income = sum([d['monthly_operating_income'] for d in monthly_data]) + monthly_operating_income if monthly_data else monthly_operating_income
        
        monthly_data.append({
            'month': month,
            'year': year_num,
            'portfolio_value': portfolio_value,
            'monthly_contribution': monthly_contribution,
            'monthly_dividend': monthly_dividend,
            'monthly_operating_income': monthly_operating_income,
            'cumulative_operating_income': cumulative_operating_income,
            'dividend_tax': dividend_tax,
            'cumulative_cost': cumulative_cost,
            'net_proceeds': net_proceeds
        })
    
    df = pd.DataFrame(monthly_data)
    
    summary = {
        'initial_payment': initial_investment,
        'final_portfolio_value': df.iloc[-1]['portfolio_value'],
        'total_contributions': df['monthly_contribution'].sum(),
        'total_dividends': cumulative_dividends,
        'total_dividend_tax': cumulative_dividend_tax,
        'final_net_proceeds': df.iloc[-1]['net_proceeds']
    }
    
    return {
        'monthly_df': df,
        'summary': summary
    }
