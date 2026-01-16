"""
Tax calculation utilities for different income types and deductions
"""


def calculate_income_tax(income, tax_rate):
    """Simple income tax calculation"""
    return income * tax_rate


def calculate_capital_gains_tax(gain, holding_period_years, tax_rate_short=0.25, tax_rate_long=0.15):
    """
    Calculate capital gains tax
    holding_period_years < 1: short-term (ordinary income rate)
    holding_period_years >= 1: long-term (preferential rate)
    """
    if gain <= 0:
        return 0
    
    if holding_period_years < 1:
        return gain * tax_rate_short
    else:
        return gain * tax_rate_long


def calculate_primary_residence_exclusion(gain, holding_period_years, is_married=False):
    """
    Primary residence capital gains exclusion
    Must own and live in home 2 of last 5 years
    Exclusion: $250k single, $500k married
    """
    if holding_period_years < 2:
        return 0
    
    exclusion = 500000 if is_married else 250000
    excluded_gain = min(gain, exclusion)
    return excluded_gain


def calculate_mortgage_interest_deduction(interest_paid, tax_rate, standard_deduction=13850):
    """
    Calculate tax benefit from mortgage interest deduction
    Only beneficial if itemized deductions > standard deduction
    """
    if interest_paid > standard_deduction:
        return interest_paid * tax_rate
    else:
        # Standard deduction is better
        return 0


def calculate_property_tax_deduction(property_tax, tax_rate, salt_cap=10000):
    """
    Calculate tax benefit from property tax deduction
    Subject to SALT (State and Local Tax) cap
    """
    deductible_amount = min(property_tax, salt_cap)
    return deductible_amount * tax_rate


def calculate_rental_depreciation(property_value, land_value_ratio=0.2, years=27.5):
    """
    Calculate annual depreciation for rental property
    Only structure depreciates, not land (typically 20% of value)
    Residential rental: 27.5 year straight-line
    """
    depreciable_basis = property_value * (1 - land_value_ratio)
    annual_depreciation = depreciable_basis / years
    return annual_depreciation


def calculate_passive_income_tax(rental_income, expenses, depreciation, tax_rate):
    """
    Calculate tax on passive rental income
    Income - Expenses - Depreciation = Taxable Income
    """
    taxable_income = rental_income - expenses - depreciation
    if taxable_income > 0:
        return taxable_income * tax_rate
    else:
        # Loss can offset other passive income (with limitations)
        return 0


def calculate_dividend_tax(dividend_income, qualified_rate=0.15, ordinary_rate=0.25):
    """
    Calculate tax on dividend income
    Assume all dividends are qualified (lower rate)
    """
    return dividend_income * qualified_rate
