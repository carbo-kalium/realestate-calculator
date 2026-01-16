"""
Clean implementation of Buy & Live vs Rent & Invest simulation
Dedicated functions for homeownership (living in property) strategy
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


def simulate_homeownership(params):
    """
    Simulate homeownership strategy (Buy & Live)
    
    Strategy:
    - Buy property with mortgage and live in it
    - Pay monthly costs: mortgage, taxes, insurance, HOA, maintenance
    - Receive monthly tax benefits from deductions
    - True monthly cost = Total costs - Tax benefits
    - Build equity through principal payments and appreciation
    
    Key Calculations:
    - Monthly tax benefit = (Interest + Property tax) × (1 - Tax bracket)
    - True monthly cost = Mortgage + Taxes + Insurance + HOA + Maintenance - Tax benefit
    - Net proceeds = Property value - Remaining mortgage - Selling costs
    """
    # Extract parameters
    purchase_price = params['purchase_price']
    down_payment_pct = params['down_payment_pct']
    mortgage_rate = params['mortgage_rate']
    mortgage_years = params['mortgage_years']
    closing_costs_pct = params['closing_costs_pct']
    selling_cost_pct = params['selling_cost_pct']
    appreciation_rate = params['appreciation_rate']
    property_tax_rate = params['property_tax_rate']
    hoa_monthly = params['hoa_monthly']
    insurance_monthly = params['insurance_monthly']
    maintenance_rate = params['maintenance_rate']
    tax_bracket = params['tax_bracket']
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
    
    for month in range(1, months + 1):
        year_num = (month - 1) // 12 + 1
        
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
        
        # Monthly tax benefit from deductions
        # Tax benefit = Tax bracket × (Interest + Property tax)
        # This is the tax refund received at year-end
        monthly_tax_benefit = (interest_payment + property_tax_monthly) * tax_bracket
        
        # Total monthly costs before tax benefit
        total_costs_before_tax = mortgage_payment + property_tax_monthly + insurance_monthly + hoa_monthly + maintenance_monthly
        
        # True monthly cost after tax benefit offset
        true_monthly_cost = total_costs_before_tax - monthly_tax_benefit
        
        # Unrecoverable costs (everything except principal)
        unrecoverable = interest_payment + property_tax_monthly + insurance_monthly + hoa_monthly + maintenance_monthly
        if month == 1:
            unrecoverable += closing_costs
        
        # Cumulative values
        cumulative_unrecoverable = sum([d['unrecoverable'] for d in monthly_data]) + unrecoverable if monthly_data else unrecoverable
        cumulative_tax_benefits = sum([d['monthly_tax_benefit'] for d in monthly_data]) + monthly_tax_benefit if monthly_data else monthly_tax_benefit
        cumulative_true_cost = sum([d['true_monthly_cost'] for d in monthly_data]) + true_monthly_cost if monthly_data else true_monthly_cost
        
        # Equity
        equity = property_value - remaining_balance
        
        # Net proceeds = Property value - Remaining mortgage - Selling costs
        # Closing costs are already accounted for in cumulative costs
        selling_costs = property_value * selling_cost_pct
        net_proceeds = property_value - remaining_balance - selling_costs
        
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
            'total_costs_before_tax': total_costs_before_tax,
            'monthly_tax_benefit': monthly_tax_benefit,
            'true_monthly_cost': true_monthly_cost,
            'unrecoverable': unrecoverable,
            'cumulative_unrecoverable': cumulative_unrecoverable,
            'cumulative_tax_benefits': cumulative_tax_benefits,
            'cumulative_true_cost': cumulative_true_cost,
            'equity': equity,
            'net_proceeds': net_proceeds
        })
    
    df = pd.DataFrame(monthly_data)
    
    # Final calculations
    final_property_value = df.iloc[-1]['property_value']
    final_remaining_balance = df.iloc[-1]['remaining_balance']
    final_selling_costs = final_property_value * selling_cost_pct
    final_net_proceeds = final_property_value - final_remaining_balance - final_selling_costs
    
    # Cumulative costs = Sum of true monthly costs + Selling costs
    # (Closing costs are already included in month 1 unrecoverable costs)
    final_cumulative_cost = df['cumulative_true_cost'].iloc[-1] + final_selling_costs
    
    summary = {
        'initial_payment': initial_investment,
        'final_property_value': final_property_value,
        'final_equity': final_property_value - final_remaining_balance,
        'selling_costs': final_selling_costs,
        'final_net_proceeds': final_net_proceeds,
        'total_unrecoverable_costs': df['cumulative_unrecoverable'].iloc[-1],
        'total_tax_benefits': df['cumulative_tax_benefits'].iloc[-1],
        'total_true_cost': final_cumulative_cost,
        'total_principal_paid': df['principal_payment'].sum()
    }
    
    return {
        'monthly_df': df,
        'summary': summary
    }


def simulate_rent_and_invest(params, homeownership_true_monthly_costs):
    """
    Simulate rent & invest in stocks strategy
    
    Strategy:
    - Rent a property and invest capital in stocks
    - Monthly stock contribution = Homeownership true cost - Rent
    - This ensures equal total monthly outflow
    - Dividends reinvested monthly
    - Annual tax on dividends
    
    Key Calculations:
    - Monthly contribution = Homeownership true monthly cost - Monthly rent
    - Net proceeds = Stock portfolio value
    - Cumulative costs = Rent paid + Dividend taxes
    """
    # Extract parameters
    initial_investment = params['initial_investment']
    monthly_rent = params['monthly_rent']
    rent_increase_rate = params['rent_increase_rate']
    stock_return_rate = params['stock_return_rate']
    dividend_yield = params['dividend_yield']
    tax_bracket = params['tax_bracket']
    years = params['years']
    
    # Initialize
    months = years * 12
    monthly_data = []
    
    portfolio_value = initial_investment
    cumulative_rent = 0
    cumulative_dividends = 0
    cumulative_dividend_tax = 0
    annual_dividends = 0
    
    for month in range(1, months + 1):
        year_num = (month - 1) // 12 + 1
        month_in_year = (month - 1) % 12 + 1
        
        # Rent (increases annually)
        years_elapsed = (month - 1) / 12
        current_rent = monthly_rent * (1 + rent_increase_rate) ** int(years_elapsed)
        cumulative_rent += current_rent
        
        # Monthly stock contribution = Homeownership true cost - Rent
        homeownership_cost = homeownership_true_monthly_costs[month - 1]
        monthly_contribution = homeownership_cost - current_rent
        
        # Portfolio growth
        monthly_return = stock_return_rate / 12
        portfolio_value = portfolio_value * (1 + monthly_return) + monthly_contribution
        
        # Monthly dividends (reinvested)
        monthly_dividend = portfolio_value * (dividend_yield / 12)
        annual_dividends += monthly_dividend
        cumulative_dividends += monthly_dividend
        
        # Operating income = dividends (before tax)
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
        
        # Cumulative cost = rent + dividend taxes
        cumulative_cost = cumulative_rent + cumulative_dividend_tax
        
        # Cumulative operating income
        cumulative_operating_income = sum([d['monthly_operating_income'] for d in monthly_data]) + monthly_operating_income if monthly_data else monthly_operating_income
        
        monthly_data.append({
            'month': month,
            'year': year_num,
            'portfolio_value': portfolio_value,
            'monthly_rent': current_rent,
            'cumulative_rent': cumulative_rent,
            'monthly_contribution': monthly_contribution,
            'monthly_dividend': monthly_dividend,
            'monthly_operating_income': monthly_operating_income,
            'cumulative_operating_income': cumulative_operating_income,
            'dividend_tax': dividend_tax,
            'cumulative_dividend_tax': cumulative_dividend_tax,
            'cumulative_cost': cumulative_cost,
            'net_proceeds': net_proceeds
        })
    
    df = pd.DataFrame(monthly_data)
    
    summary = {
        'initial_payment': initial_investment,
        'final_portfolio_value': df.iloc[-1]['portfolio_value'],
        'total_contributions': df['monthly_contribution'].sum(),
        'total_rent_paid': df['cumulative_rent'].iloc[-1],
        'total_dividends': cumulative_dividends,
        'total_dividend_tax': cumulative_dividend_tax,
        'total_cost': df['cumulative_cost'].iloc[-1],
        'final_net_proceeds': df.iloc[-1]['net_proceeds']
    }
    
    return {
        'monthly_df': df,
        'summary': summary
    }
