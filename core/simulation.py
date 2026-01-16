"""
Core financial simulation engine for real estate and investment scenarios
"""
import numpy as np
import pandas as pd
from .mortgage_utils import calculate_amortization_schedule, calculate_monthly_payment
from .tax_utils import (
    calculate_income_tax, calculate_capital_gains_tax,
    calculate_mortgage_interest_deduction, calculate_property_tax_deduction,
    calculate_rental_depreciation, calculate_passive_income_tax,
    calculate_primary_residence_exclusion, calculate_dividend_tax
)


def simulate_homeownership(params):
    """
    Simulate buying and living in a primary residence
    Tracks: unrecoverable costs, operating income (tax benefits), and net worth
    Also calculates total monthly expense (unrecoverable + principal) for fair comparison
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
    selling_cost_pct = params['selling_cost_pct']
    years = params['years']
    inflation_rate = params.get('inflation_rate', 0.03)
    
    # Initial calculations
    down_payment = purchase_price * down_payment_pct
    closing_costs = purchase_price * closing_costs_pct
    loan_amount = purchase_price - down_payment
    initial_investment = down_payment + closing_costs
    
    # Amortization schedule
    amortization = calculate_amortization_schedule(loan_amount, mortgage_rate, mortgage_years)
    
    # Monthly simulation
    months = years * 12
    monthly_data = []
    cumulative_unrecoverable = 0
    cumulative_operating_income = 0
    monthly_expenses = []  # Track total monthly expenses for fair comparison
    
    for month in range(1, months + 1):
        year = (month - 1) / 12
        
        # Property value appreciation
        property_value = purchase_price * (1 + appreciation_rate) ** year
        
        # Monthly costs
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
        
        property_tax = (property_value * property_tax_rate) / 12
        maintenance = (property_value * maintenance_rate) / 12
        
        # Total monthly cost
        total_monthly_cost = mortgage_payment + property_tax + hoa_monthly + insurance_monthly + maintenance
        
        # Unrecoverable costs (everything except principal)
        # Include closing costs at month 1
        unrecoverable = interest_payment + property_tax + hoa_monthly + insurance_monthly + maintenance
        if month == 1:
            unrecoverable += closing_costs
        
        cumulative_unrecoverable += unrecoverable
        
        # Total monthly expense = unrecoverable costs + principal payment
        # This is what would be invested in stocks for fair comparison
        total_monthly_expense = unrecoverable + principal_payment
        monthly_expenses.append(total_monthly_expense)
        
        # Operating income: Tax benefit from mortgage interest and property tax deductions
        # Tax benefit = (mortgage_interest + property_tax) * (1 - tax_bracket)
        # This represents the tax savings from deductions
        monthly_tax_benefit = (interest_payment + property_tax) * (1 - tax_bracket)
        cumulative_operating_income += monthly_tax_benefit
        
        # Equity
        equity = property_value - remaining_balance
        
        # Net proceeds calculation for homeownership
        # Formula: Property Value (with appreciation) - Remaining Mortgage - Closing Costs + Cumulative Tax Benefits
        # Note: Cumulative unrecoverable costs are NOT subtracted here - user can toggle this in the chart
        # On day of purchase (month 1): net_proceeds = down_payment
        if month == 1:
            net_worth = down_payment
        else:
            net_worth = property_value - remaining_balance - closing_costs + cumulative_operating_income
        
        monthly_data.append({
            'month': month,
            'year': year,
            'property_value': property_value,
            'mortgage_payment': mortgage_payment,
            'principal_payment': principal_payment,
            'interest_payment': interest_payment,
            'property_tax': property_tax,
            'hoa': hoa_monthly,
            'insurance': insurance_monthly,
            'maintenance': maintenance,
            'total_monthly_cost': total_monthly_cost,
            'unrecoverable_cost': unrecoverable,
            'remaining_balance': remaining_balance,
            'equity': equity,
            'monthly_operating_income': monthly_operating_income,
            'cumulative_operating_income': cumulative_operating_income,
            'cumulative_unrecoverable': cumulative_unrecoverable,
            'net_worth': net_worth
        })
    
    df = pd.DataFrame(monthly_data)
    df['cumulative_principal'] = df['principal_payment'].cumsum()
    
    # Final calculations
    final_property_value = df.iloc[-1]['property_value']
    selling_costs = final_property_value * selling_cost_pct
    final_equity = df.iloc[-1]['equity']
    
    # Capital gains (primary residence - may qualify for exclusion)
    capital_gain = final_property_value - purchase_price - selling_costs
    excluded_gain = calculate_primary_residence_exclusion(capital_gain, years, is_married=False)
    taxable_gain = max(0, capital_gain - excluded_gain)
    capital_gains_tax = calculate_capital_gains_tax(taxable_gain, years)
    
    net_proceeds = final_equity - selling_costs - capital_gains_tax
    total_invested = initial_investment + df['cumulative_principal'].iloc[-1]
    roi = ((net_proceeds - total_invested) / total_invested) * 100 if total_invested > 0 else 0
    
    # Summary
    summary = {
        'initial_investment': initial_investment,
        'total_invested': total_invested,
        'final_property_value': final_property_value,
        'final_equity': final_equity,
        'selling_costs': selling_costs,
        'capital_gain': capital_gain,
        'capital_gains_tax': capital_gains_tax,
        'net_proceeds': net_proceeds,
        'total_unrecoverable': df['cumulative_unrecoverable'].iloc[-1],
        'total_principal_paid': df['cumulative_principal'].iloc[-1],
        'roi': roi,
        'annualized_return': (((net_proceeds / total_invested) ** (1 / years)) - 1) * 100 if total_invested > 0 and years > 0 else 0
    }
    
    return {
        'monthly_df': df,
        'summary': summary,
        'plots': {},
        'monthly_expenses': monthly_expenses  # For fair comparison with stock investment
    }


def simulate_stock_investment(params, homeownership_monthly_expenses=None, rental_monthly_expenses=None, rental_income_monthly=None):
    """
    Simulate renting and investing in stocks
    Tracks: cumulative rent (unrecoverable), operating income (dividends), and net worth
    
    If homeownership_monthly_expenses is provided, uses dynamic contributions:
    monthly_contribution = homeownership_total_expense - rent_paid
    
    If rental_monthly_expenses and rental_income_monthly are provided (rental property scenario):
    monthly_contribution = rental_total_expense - rental_income_after_tax
    
    This ensures fair comparison between strategies
    """
    # Extract parameters
    initial_investment = params['initial_investment']
    monthly_contribution = params['monthly_contribution']
    stock_return_rate = params['stock_return_rate']
    dividend_yield = params['dividend_yield']
    dividend_tax_rate = params.get('dividend_tax_rate', 0.15)
    monthly_rent = params['monthly_rent']
    rent_increase_rate = params['rent_increase_rate']
    years = params['years']
    
    # Use dynamic contributions if expenses are provided
    use_dynamic_contributions = homeownership_monthly_expenses is not None or (rental_monthly_expenses is not None and rental_income_monthly is not None)
    is_rental_scenario = rental_monthly_expenses is not None and rental_income_monthly is not None
    
    # Monthly simulation
    months = years * 12
    monthly_data = []
    portfolio_value = initial_investment
    cumulative_rent = 0
    cumulative_operating_income = 0
    
    for month in range(1, months + 1):
        year = (month - 1) / 12
        
        # Rent (increases annually)
        rent = monthly_rent * (1 + rent_increase_rate) ** int(year)
        cumulative_rent += rent
        
        # Calculate monthly contribution
        if use_dynamic_contributions:
            if is_rental_scenario and month <= len(rental_monthly_expenses):
                # Rental scenario: contribution already includes principal + true cost
                # (true cost already accounts for rental income and tax benefits)
                actual_contribution = rental_monthly_expenses[month - 1]
            elif not is_rental_scenario and month <= len(homeownership_monthly_expenses):
                # Buy & Live scenario: contribution = homeownership total expense - rent paid
                homeownership_expense = homeownership_monthly_expenses[month - 1]
                actual_contribution = homeownership_expense - rent
            else:
                actual_contribution = monthly_contribution
        else:
            actual_contribution = monthly_contribution
        
        # Portfolio growth
        monthly_return = stock_return_rate / 12
        portfolio_value = portfolio_value * (1 + monthly_return) + actual_contribution
        
        # Dividends - Operating income
        monthly_dividend = portfolio_value * (dividend_yield / 12)
        dividend_tax = monthly_dividend * dividend_tax_rate
        net_dividend = monthly_dividend - dividend_tax
        cumulative_operating_income += net_dividend
        
        # Net proceeds calculation for stock investment
        # Formula: Portfolio Value + Cumulative Post-Tax Dividends
        # Note: Cumulative rent is NOT subtracted here - user can toggle this in the chart
        # On day of purchase (month 1): net_proceeds = down_payment (initial_investment)
        if month == 1:
            net_worth = initial_investment
        else:
            net_worth = portfolio_value + cumulative_operating_income
        
        monthly_data.append({
            'month': month,
            'year': year,
            'rent': rent,
            'monthly_contribution': actual_contribution,  # Store actual contribution used
            'portfolio_value': portfolio_value,
            'monthly_dividend': monthly_dividend,
            'dividend_tax': dividend_tax,
            'net_dividend': net_dividend,
            'cumulative_rent': cumulative_rent,
            'cumulative_operating_income': cumulative_operating_income,
            'net_worth': net_worth
        })
    
    df = pd.DataFrame(monthly_data)
    df['cumulative_contributions'] = initial_investment + (df['monthly_contribution'].cumsum())
    
    # Summary
    final_portfolio = df.iloc[-1]['portfolio_value']
    total_contributed = df.iloc[-1]['cumulative_contributions']
    total_rent_paid = df.iloc[-1]['cumulative_rent']
    
    summary = {
        'initial_investment': initial_investment,
        'total_contributed': total_contributed,
        'final_portfolio_value': final_portfolio,
        'total_rent_paid': total_rent_paid,
        'total_operating_income': df.iloc[-1]['cumulative_operating_income'],
        'net_proceeds': final_portfolio,
        'roi': ((final_portfolio - total_contributed) / total_contributed) * 100 if total_contributed > 0 else 0,
        'annualized_return': (((final_portfolio / total_contributed) ** (1 / years)) - 1) * 100 if total_contributed > 0 and years > 0 else 0
    }
    
    return {
        'monthly_df': df,
        'summary': summary,
        'plots': {}
    }


def simulate_rental_property(params):
    """
    Simulate long-term rental investment property
    """
    purchase_price = params['purchase_price']
    down_payment_pct = params['down_payment_pct']
    mortgage_rate = params['mortgage_rate']
    mortgage_years = params['mortgage_years']
    closing_costs_pct = params['closing_costs_pct']
    monthly_rent = params['monthly_rent']
    rent_increase_rate = params['rent_increase_rate']
    occupancy_rate = params['occupancy_rate']
    management_fee_pct = params['management_fee_pct']
    property_tax_rate = params['property_tax_rate']
    insurance_monthly = params['insurance_monthly']
    maintenance_rate = params['maintenance_rate']
    appreciation_rate = params['appreciation_rate']
    tax_bracket = params['tax_bracket']
    selling_cost_pct = params['selling_cost_pct']
    years = params['years']
    
    # Initial calculations
    down_payment = purchase_price * down_payment_pct
    closing_costs = purchase_price * closing_costs_pct
    loan_amount = purchase_price - down_payment
    initial_investment = down_payment + closing_costs
    
    # Amortization and depreciation
    amortization = calculate_amortization_schedule(loan_amount, mortgage_rate, mortgage_years)
    annual_depreciation = calculate_rental_depreciation(purchase_price)
    monthly_depreciation = annual_depreciation / 12
    
    # Monthly simulation
    months = years * 12
    monthly_data = []
    
    for month in range(1, months + 1):
        year = (month - 1) / 12
        
        # Property value
        property_value = purchase_price * (1 + appreciation_rate) ** year
        
        # Rental income
        gross_rent = monthly_rent * (1 + rent_increase_rate) ** int(year)
        effective_rent = gross_rent * occupancy_rate
        management_fee = effective_rent * management_fee_pct
        
        # Operating expenses
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
        
        property_tax = (property_value * property_tax_rate) / 12
        maintenance = (property_value * maintenance_rate) / 12
        
        total_expenses = mortgage_payment + property_tax + insurance_monthly + maintenance + management_fee
        
        # Cash flow
        pre_tax_cashflow = effective_rent - total_expenses
        
        # Tax calculation
        taxable_income = effective_rent - interest_payment - property_tax - insurance_monthly - maintenance - management_fee - monthly_depreciation
        income_tax = max(0, taxable_income * tax_bracket)
        
        post_tax_cashflow = pre_tax_cashflow - income_tax
        
        equity = property_value - remaining_balance
        
        monthly_data.append({
            'month': month,
            'year': year,
            'property_value': property_value,
            'gross_rent': gross_rent,
            'effective_rent': effective_rent,
            'management_fee': management_fee,
            'mortgage_payment': mortgage_payment,
            'principal_payment': principal_payment,
            'interest_payment': interest_payment,
            'property_tax': property_tax,
            'insurance': insurance_monthly,
            'maintenance': maintenance,
            'total_expenses': total_expenses,
            'pre_tax_cashflow': pre_tax_cashflow,
            'depreciation': monthly_depreciation,
            'taxable_income': taxable_income,
            'income_tax': income_tax,
            'post_tax_cashflow': post_tax_cashflow,
            'remaining_balance': remaining_balance,
            'equity': equity
        })
    
    df = pd.DataFrame(monthly_data)
    df['cumulative_cashflow'] = df['post_tax_cashflow'].cumsum()
    df['cumulative_rental_income'] = df['effective_rent'].cumsum()
    
    # Sale calculations
    final_property_value = df.iloc[-1]['property_value']
    final_equity = df.iloc[-1]['equity']
    selling_costs = final_property_value * selling_cost_pct
    
    # Depreciation recapture and capital gains
    total_depreciation = monthly_depreciation * months
    depreciation_recapture_tax = total_depreciation * 0.25  # 25% rate
    
    capital_gain = final_property_value - purchase_price
    capital_gains_tax = calculate_capital_gains_tax(capital_gain, years, tax_rate_long=0.15)
    
    net_proceeds = final_equity - selling_costs - capital_gains_tax - depreciation_recapture_tax
    total_cash_invested = initial_investment
    total_return = net_proceeds + df['cumulative_cashflow'].iloc[-1]
    
    # Summary metrics
    summary = {
        'initial_investment': initial_investment,
        'total_rental_income': df['cumulative_rental_income'].iloc[-1],
        'total_cashflow': df['cumulative_cashflow'].iloc[-1],
        'final_property_value': final_property_value,
        'final_equity': final_equity,
        'selling_costs': selling_costs,
        'capital_gains_tax': capital_gains_tax,
        'depreciation_recapture_tax': depreciation_recapture_tax,
        'net_proceeds': net_proceeds,
        'total_return': total_return,
        'roi': (total_return / total_cash_invested) * 100 if total_cash_invested > 0 else 0,
        'cash_on_cash_return': (df['post_tax_cashflow'].sum() / initial_investment) * 100 if initial_investment > 0 else 0,
        'annualized_return': (((total_return / total_cash_invested) ** (1 / years)) - 1) * 100 if total_cash_invested > 0 and years > 0 else 0
    }
    
    return {
        'monthly_df': df,
        'summary': summary,
        'plots': {}
    }


def simulate_airbnb_property(params):
    """
    Simulate short-term rental (Airbnb) property
    """
    purchase_price = params['purchase_price']
    down_payment_pct = params['down_payment_pct']
    mortgage_rate = params['mortgage_rate']
    mortgage_years = params['mortgage_years']
    closing_costs_pct = params['closing_costs_pct']
    nightly_rate = params['nightly_rate']
    occupancy_rate = params['occupancy_rate']
    cleaning_fee_per_stay = params['cleaning_fee_per_stay']
    avg_stay_length = params.get('avg_stay_length', 3)
    platform_fee_pct = params['platform_fee_pct']
    property_tax_rate = params['property_tax_rate']
    insurance_monthly = params['insurance_monthly']
    utilities_monthly = params['utilities_monthly']
    maintenance_rate = params['maintenance_rate']
    appreciation_rate = params['appreciation_rate']
    tax_bracket = params['tax_bracket']
    selling_cost_pct = params['selling_cost_pct']
    years = params['years']
    
    # Initial calculations
    down_payment = purchase_price * down_payment_pct
    closing_costs = purchase_price * closing_costs_pct
    loan_amount = purchase_price - down_payment
    initial_investment = down_payment + closing_costs
    
    # Amortization
    amortization = calculate_amortization_schedule(loan_amount, mortgage_rate, mortgage_years)
    annual_depreciation = calculate_rental_depreciation(purchase_price)
    monthly_depreciation = annual_depreciation / 12
    
    # Monthly simulation
    months = years * 12
    monthly_data = []
    
    for month in range(1, months + 1):
        year = (month - 1) / 12
        
        # Property value
        property_value = purchase_price * (1 + appreciation_rate) ** year
        
        # Revenue calculation
        days_occupied = 30 * occupancy_rate
        bookings_per_month = days_occupied / avg_stay_length
        gross_revenue = nightly_rate * days_occupied
        cleaning_revenue = cleaning_fee_per_stay * bookings_per_month
        total_gross = gross_revenue + cleaning_revenue
        platform_fee = total_gross * platform_fee_pct
        net_revenue = total_gross - platform_fee
        
        # Expenses
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
        
        property_tax = (property_value * property_tax_rate) / 12
        maintenance = (property_value * maintenance_rate) / 12
        cleaning_costs = cleaning_fee_per_stay * bookings_per_month * 0.5  # 50% of cleaning fee
        
        total_expenses = mortgage_payment + property_tax + insurance_monthly + utilities_monthly + maintenance + cleaning_costs
        
        # Cash flow
        pre_tax_cashflow = net_revenue - total_expenses
        
        # Tax
        taxable_income = net_revenue - interest_payment - property_tax - insurance_monthly - utilities_monthly - maintenance - cleaning_costs - monthly_depreciation
        income_tax = max(0, taxable_income * tax_bracket)
        
        post_tax_cashflow = pre_tax_cashflow - income_tax
        
        equity = property_value - remaining_balance
        
        monthly_data.append({
            'month': month,
            'year': year,
            'property_value': property_value,
            'gross_revenue': total_gross,
            'platform_fee': platform_fee,
            'net_revenue': net_revenue,
            'mortgage_payment': mortgage_payment,
            'principal_payment': principal_payment,
            'interest_payment': interest_payment,
            'property_tax': property_tax,
            'insurance': insurance_monthly,
            'utilities': utilities_monthly,
            'maintenance': maintenance,
            'cleaning_costs': cleaning_costs,
            'total_expenses': total_expenses,
            'pre_tax_cashflow': pre_tax_cashflow,
            'income_tax': income_tax,
            'post_tax_cashflow': post_tax_cashflow,
            'remaining_balance': remaining_balance,
            'equity': equity
        })
    
    df = pd.DataFrame(monthly_data)
    df['cumulative_cashflow'] = df['post_tax_cashflow'].cumsum()
    df['cumulative_revenue'] = df['net_revenue'].cumsum()
    
    # Sale calculations
    final_property_value = df.iloc[-1]['property_value']
    final_equity = df.iloc[-1]['equity']
    selling_costs = final_property_value * selling_cost_pct
    
    total_depreciation = monthly_depreciation * months
    depreciation_recapture_tax = total_depreciation * 0.25
    capital_gain = final_property_value - purchase_price
    capital_gains_tax = calculate_capital_gains_tax(capital_gain, years, tax_rate_long=0.15)
    
    net_proceeds = final_equity - selling_costs - capital_gains_tax - depreciation_recapture_tax
    total_return = net_proceeds + df['cumulative_cashflow'].iloc[-1]
    
    summary = {
        'initial_investment': initial_investment,
        'total_revenue': df['cumulative_revenue'].iloc[-1],
        'total_cashflow': df['cumulative_cashflow'].iloc[-1],
        'final_property_value': final_property_value,
        'final_equity': final_equity,
        'net_proceeds': net_proceeds,
        'total_return': total_return,
        'roi': (total_return / initial_investment) * 100 if initial_investment > 0 else 0,
        'annualized_return': (((total_return / initial_investment) ** (1 / years)) - 1) * 100 if initial_investment > 0 and years > 0 else 0
    }
    
    return {
        'monthly_df': df,
        'summary': summary,
        'plots': {}
    }


def simulate_flip_project(params):
    """
    Simulate buy-renovate-sell (flip) project
    """
    purchase_price = params['purchase_price']
    down_payment_pct = params.get('down_payment_pct', 0.20)
    renovation_cost = params['renovation_cost']
    renovation_months = params['renovation_months']
    arv = params['arv']  # After Repair Value
    holding_costs_monthly = params['holding_costs_monthly']
    selling_cost_pct = params['selling_cost_pct']
    tax_bracket = params['tax_bracket']  # Short-term capital gains
    
    # Initial calculations
    down_payment = purchase_price * down_payment_pct
    total_investment = down_payment + renovation_cost
    
    # Monthly tracking
    months = renovation_months + 1  # Include sale month
    monthly_data = []
    
    for month in range(1, months + 1):
        if month <= renovation_months:
            # During renovation
            property_value = purchase_price  # No appreciation during reno
            monthly_cost = holding_costs_monthly + (renovation_cost / renovation_months)
            status = 'Renovating'
        else:
            # Sale month
            property_value = arv
            monthly_cost = holding_costs_monthly
            status = 'Sold'
        
        monthly_data.append({
            'month': month,
            'property_value': property_value,
            'monthly_cost': monthly_cost,
            'status': status
        })
    
    df = pd.DataFrame(monthly_data)
    df['cumulative_costs'] = total_investment + df['monthly_cost'].cumsum()
    
    # Sale calculations
    total_costs = df.iloc[-1]['cumulative_costs']
    selling_costs = arv * selling_cost_pct
    gross_profit = arv - purchase_price - renovation_cost - selling_costs - (holding_costs_monthly * months)
    
    # Tax (short-term capital gains = ordinary income)
    capital_gains_tax = max(0, gross_profit * tax_bracket)
    net_profit = gross_profit - capital_gains_tax
    
    roi = (net_profit / total_investment) * 100 if total_investment > 0 else 0
    
    summary = {
        'purchase_price': purchase_price,
        'renovation_cost': renovation_cost,
        'total_investment': total_investment,
        'total_costs': total_costs,
        'arv': arv,
        'selling_costs': selling_costs,
        'gross_profit': gross_profit,
        'capital_gains_tax': capital_gains_tax,
        'net_profit': net_profit,
        'roi': roi,
        'holding_period_months': months
    }
    
    return {
        'monthly_df': df,
        'summary': summary,
        'plots': {}
    }


def compare_strategies(results_dict):
    """
    Compare multiple strategy results side by side
    results_dict: {'Strategy Name': simulation_result, ...}
    """
    comparison = []
    
    for name, result in results_dict.items():
        summary = result['summary']
        comparison.append({
            'Strategy': name,
            'Initial Investment': summary.get('initial_investment', 0),
            'Total Return': summary.get('total_return', summary.get('net_proceeds', 0)),
            'ROI (%)': summary.get('roi', 0),
            'Annualized Return (%)': summary.get('annualized_return', 0)
        })
    
    return pd.DataFrame(comparison)


def simulate_rental_property(params):
    """
    Simulate buying and renting out a property with complementary stock portfolio
    
    Strategy:
    - True Cost = Unrecoverable Costs - Rental Income (After Tax)
    - Tax Benefits → Invested in stock portfolio
    - Excess Rental Income (if any) → Also invested in stock portfolio
    - Operating Income = Tax benefits + dividends from stock portfolio
    - Net Proceeds = Property Value - Mortgage - Closing + Stock Portfolio Value
    
    This creates a hybrid investment: rental property + stock portfolio from tax benefits
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
    selling_cost_pct = params['selling_cost_pct']
    monthly_rent_income = params['monthly_rent_income']
    vacancy_rate = params['vacancy_rate']
    years = params['years']
    
    # Stock portfolio parameters for tax benefit investment
    stock_return_rate = params.get('stock_return_rate', 0.10)
    dividend_yield = params.get('dividend_yield', 0.02)
    dividend_tax_rate = params.get('dividend_tax_rate', 0.15)
    
    # Calculate initial values
    down_payment = purchase_price * down_payment_pct
    closing_costs = purchase_price * closing_costs_pct
    loan_amount = purchase_price - down_payment
    initial_investment = down_payment + closing_costs
    
    # Mortgage amortization
    monthly_payment = calculate_monthly_payment(loan_amount, mortgage_rate, mortgage_years)
    amortization = calculate_amortization_schedule(loan_amount, mortgage_rate, mortgage_years)
    
    # Monthly simulation
    months = years * 12
    monthly_data = []
    cumulative_unrecoverable = 0
    cumulative_operating_income = 0
    monthly_expenses = []
    
    # Complementary stock portfolio for tax benefits and excess rental income
    stock_portfolio_value = 0
    
    for month in range(1, months + 1):
        year = (month - 1) / 12
        
        # Property value appreciation
        property_value = purchase_price * (1 + appreciation_rate) ** year
        
        # Monthly costs
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
        
        property_tax = (property_value * property_tax_rate) / 12
        maintenance = (property_value * maintenance_rate) / 12
        
        # Rental income (accounting for vacancy)
        gross_monthly_rent = monthly_rent_income * (1 - vacancy_rate)
        
        # Unrecoverable costs (everything except principal)
        # Include closing costs at month 1
        unrecoverable = interest_payment + property_tax + hoa_monthly + insurance_monthly + maintenance
        if month == 1:
            unrecoverable += closing_costs
        
        cumulative_unrecoverable += unrecoverable
        
        # Rental income is taxed at the tax bracket rate
        rental_income_after_tax = gross_monthly_rent * (1 - tax_bracket)
        
        # Tax benefit from mortgage interest and property tax deductions
        # Both interest_payment and property_tax are already monthly values
        # Monthly tax benefit = (interest + property_tax) * (1 - tax_bracket)
        monthly_tax_benefit = (interest_payment + property_tax) * (1 - tax_bracket)
        
        # Calculate true cost of ownership (monthly)
        # True Cost = Unrecoverable Costs - Rental Income (After Tax)
        # Note: Tax benefits are NOT subtracted here - they are invested in stock portfolio
        monthly_true_cost = unrecoverable - rental_income_after_tax
        
        # Determine what gets invested in the complementary stock portfolio
        # 1. Tax benefits always get invested
        # 2. If true cost is negative (rental income > costs), excess also gets invested
        if monthly_true_cost < 0:
            # Rental income covers all costs with excess
            excess_rental_income = abs(monthly_true_cost)
            stock_portfolio_contribution = monthly_tax_benefit + excess_rental_income
            monthly_true_cost = 0  # No out-of-pocket cost
        else:
            # Normal case: rental income doesn't cover all costs
            excess_rental_income = 0
            stock_portfolio_contribution = monthly_tax_benefit
        
        # Grow the complementary stock portfolio
        monthly_return = stock_return_rate / 12
        stock_portfolio_value = stock_portfolio_value * (1 + monthly_return) + stock_portfolio_contribution
        
        # Calculate dividends from stock portfolio
        monthly_dividend = stock_portfolio_value * (dividend_yield / 12)
        dividend_tax = monthly_dividend * dividend_tax_rate
        net_dividend = monthly_dividend - dividend_tax
        
        # Operating income = Tax benefits + dividends from stock portfolio
        monthly_operating_income = monthly_tax_benefit + net_dividend
        cumulative_operating_income += monthly_operating_income
        
        # Equity
        equity = property_value - remaining_balance
        
        # Net proceeds calculation for rental property
        # Formula: Property Value - Remaining Mortgage - Closing Costs + Stock Portfolio Value
        # The stock portfolio includes invested tax benefits and any excess rental income
        if month == 1:
            net_worth = down_payment
        else:
            net_worth = property_value - remaining_balance - closing_costs + stock_portfolio_value
        
        # For stock investment comparison:
        # Stock contribution = Principal Payment + True Cost
        # If true cost is 0 (excess rental income), contribution = Principal - Excess
        if excess_rental_income > 0:
            stock_contribution = principal_payment - excess_rental_income
        else:
            stock_contribution = principal_payment + monthly_true_cost
        
        monthly_expenses.append(stock_contribution)
        
        monthly_data.append({
            'month': month,
            'year': year,
            'property_value': property_value,
            'mortgage_payment': mortgage_payment,
            'principal_payment': principal_payment,
            'interest_payment': interest_payment,
            'property_tax': property_tax,
            'hoa': hoa_monthly,
            'insurance': insurance_monthly,
            'maintenance': maintenance,
            'gross_rent_income': gross_monthly_rent,
            'rental_income_after_tax': rental_income_after_tax,
            'unrecoverable_cost': unrecoverable,
            'remaining_balance': remaining_balance,
            'equity': equity,
            'monthly_tax_benefit': monthly_tax_benefit,
            'monthly_true_cost': monthly_true_cost,
            'excess_rental_income': excess_rental_income,
            'stock_portfolio_value': stock_portfolio_value,
            'stock_portfolio_contribution': stock_portfolio_contribution,
            'monthly_dividend': net_dividend,
            'monthly_operating_income': monthly_operating_income,
            'cumulative_operating_income': cumulative_operating_income,
            'cumulative_unrecoverable': cumulative_unrecoverable,
            'net_worth': net_worth
        })
    
    df = pd.DataFrame(monthly_data)
    df['cumulative_principal'] = df['principal_payment'].cumsum()
    
    # Final calculations
    final_property_value = df.iloc[-1]['property_value']
    final_stock_portfolio = df.iloc[-1]['stock_portfolio_value']
    selling_costs = final_property_value * selling_cost_pct
    final_equity = df.iloc[-1]['equity']
    
    # Capital gains (rental property - no primary residence exclusion)
    capital_gain = final_equity - initial_investment
    
    # Capital gains tax (long-term capital gains)
    capital_gains_tax = calculate_capital_gains_tax(capital_gain, years)
    
    # Net proceeds includes property equity + stock portfolio value
    net_proceeds = final_equity - selling_costs - capital_gains_tax + final_stock_portfolio
    total_invested = initial_investment + df['cumulative_principal'].iloc[-1]
    roi = ((net_proceeds - total_invested) / total_invested) * 100 if total_invested > 0 else 0
    
    # Summary
    summary = {
        'initial_investment': initial_investment,
        'total_invested': total_invested,
        'final_property_value': final_property_value,
        'final_equity': final_equity,
        'final_stock_portfolio': final_stock_portfolio,
        'selling_costs': selling_costs,
        'capital_gain': capital_gain,
        'capital_gains_tax': capital_gains_tax,
        'net_proceeds': net_proceeds,
        'total_unrecoverable': df['cumulative_unrecoverable'].iloc[-1],
        'total_principal_paid': df['cumulative_principal'].iloc[-1],
        'total_rental_income': df['gross_rent_income'].sum(),
        'total_operating_income': df['cumulative_operating_income'].iloc[-1],
        'roi': roi,
        'annualized_return': (((net_proceeds / total_invested) ** (1 / years)) - 1) * 100 if total_invested > 0 and years > 0 else 0
    }
    
    return {
        'monthly_df': df,
        'summary': summary,
        'plots': {},
        'monthly_expenses': monthly_expenses  # For fair comparison with stock investment
    }
