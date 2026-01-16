"""
Mortgage and loan calculation utilities
"""
import numpy as np
import pandas as pd


def calculate_monthly_payment(principal, annual_rate, years):
    """Calculate monthly mortgage payment using standard amortization formula"""
    if annual_rate == 0:
        return principal / (years * 12)
    
    monthly_rate = annual_rate / 12
    num_payments = years * 12
    payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / \
              ((1 + monthly_rate)**num_payments - 1)
    return payment


def calculate_amortization_schedule(principal, annual_rate, years):
    """
    Generate complete amortization schedule
    Returns DataFrame with columns: month, payment, principal, interest, balance
    """
    monthly_payment = calculate_monthly_payment(principal, annual_rate, years)
    monthly_rate = annual_rate / 12
    num_payments = int(years * 12)
    
    schedule = []
    balance = principal
    
    for month in range(1, num_payments + 1):
        interest_payment = balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        balance -= principal_payment
        
        schedule.append({
            'month': month,
            'payment': monthly_payment,
            'principal': principal_payment,
            'interest': interest_payment,
            'balance': max(0, balance)
        })
    
    return pd.DataFrame(schedule)


def calculate_remaining_balance(principal, annual_rate, years, months_paid):
    """Calculate remaining mortgage balance after certain months"""
    if months_paid >= years * 12:
        return 0
    
    schedule = calculate_amortization_schedule(principal, annual_rate, years)
    if months_paid == 0:
        return principal
    return schedule.iloc[months_paid - 1]['balance']


def calculate_total_interest(principal, annual_rate, years):
    """Calculate total interest paid over loan term"""
    schedule = calculate_amortization_schedule(principal, annual_rate, years)
    return schedule['interest'].sum()
