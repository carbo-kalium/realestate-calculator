# Real Estate Investment Simulator - Buy & Rent vs Invest in Stocks

## Overview

Clean, focused implementation comparing two investment strategies:
1. **Rental Property Investment** - Buy property, rent it out, invest tax surplus
2. **Stock Investment** - Invest equivalent capital in stocks

## Implementation Details

### Rental Property Strategy

**Day of Purchase:**
- Pay down payment + closing costs
- Down payment → builds equity
- Closing costs → unrecoverable

**Monthly:**
- True Cost = Unrecoverable costs - Rental income × (1 - vacancy rate)
- Unrecoverable costs = Interest + Property tax + Insurance + HOA + Maintenance
- Rental income accounts for vacancy (e.g., 8.3% = 1 month/year vacant)

**Annual Tax Event:**
- Tax on rental income: Rental income × tax bracket
- Tax benefit from deductions: (Property tax + Interest) × (1 - tax bracket)
- Tax on dividends from stock portfolio: Dividends × tax bracket
- Surplus cash = Tax benefit - Tax on rental income - Tax on dividends
- Surplus invested in stock portfolio

**Net Proceeds:**
- Property value (with appreciation) - Closing costs at sale - Remaining mortgage + Stock portfolio value

**Operating Income:**
- Rental income + Dividends from stock portfolio

**Cumulative Costs:**
- Sum of monthly true costs

### Stock Investment Strategy

**Day of Purchase:**
- Invest same amount (down payment + closing costs) in stock portfolio

**Monthly:**
- Contribution = Rental property's (true cost + principal payment)
- This ensures equal cash outflow between strategies
- Dividends reinvested monthly

**Annual Tax Event:**
- Tax on cumulative dividends for the year
- Tax = Total dividends × tax bracket

**Net Proceeds:**
- Total stock portfolio value

**Operating Income:**
- Dividend income

**Cumulative Costs:**
- Cumulative dividend taxes paid

## File Structure

```
realestate/
├── app.py                          # Landing page
├── pages/
│   └── 1_Buy_and_Rent.py          # Main calculator page
├── core/
│   ├── __init__.py
│   └── rental_simulation.py       # Clean simulation functions
└── README.md                       # This file
```

## Key Features

- **Clean Separation**: Dedicated simulation functions for rental property strategy
- **Fair Comparison**: Equal cash outflow between both strategies
- **Tax Accuracy**: Annual tax events properly modeled
- **Stock Portfolio**: Tax surplus invested with same return/dividend rates
- **Interactive UI**: Sliders for all parameters with auto-update
- **Visual Analytics**: Charts for net proceeds, costs, and operating income

## Running the Application

```bash
cd /home/chinmay/projects/tradeselect/realestate
source /home/chinmay/projects/tradeselect/trader-ai/trader/bin/activate
streamlit run app.py --server.headless true --server.port 8501
```

Then visit: http://localhost:8501

## Parameters

### Property Details
- Purchase Price
- Down Payment (%)
- Closing Costs (%)

### Mortgage Details
- Mortgage Rate (%)
- Mortgage Term (years)

### Property Costs
- Property Tax Rate (%/year)
- HOA ($/month)
- Insurance ($/month)
- Maintenance Rate (%/year)

### Rental Income
- Monthly Rent ($)
- Vacancy Rate (%)

### Market Assumptions
- Property Appreciation Rate (%/year)
- Stock Return Rate (%/year)
- Dividend Yield (%/year)
- Tax Bracket (%)
- Time Horizon (years)

## Calculation Logic

### True Cost of Ownership
```
Monthly True Cost = Unrecoverable Costs - Rental Income × (1 - Vacancy Rate)

Where:
- Unrecoverable Costs = Interest + Property Tax + Insurance + HOA + Maintenance
- Rental Income = Monthly Rent × (1 - Vacancy Rate)
```

### Annual Tax Event
```
Tax on Rental Income = Annual Rental Income × Tax Bracket
Tax Benefit = (Annual Property Tax + Annual Interest) × (1 - Tax Bracket)
Tax on Dividends = Annual Dividends × Tax Bracket

Surplus = Tax Benefit - Tax on Rental Income - Tax on Dividends

If Surplus > 0:
    Invest Surplus in Stock Portfolio
```

### Stock Contribution
```
Monthly Contribution = True Cost + Principal Payment

This ensures both strategies have the same monthly cash outflow
```

### Net Proceeds
```
Rental Property:
Net Proceeds = Property Value - Closing Costs at Sale - Remaining Mortgage + Stock Portfolio Value

Stock Investment:
Net Proceeds = Stock Portfolio Value
```

## Charts

1. **Net Proceeds Over Time**
   - Shows total wealth accumulation for both strategies
   - Rental property includes property value + stock portfolio
   - Stock investment shows total portfolio value

2. **Cumulative Costs Over Time**
   - Rental property: Sum of monthly true costs
   - Stock investment: Cumulative dividend taxes

3. **Cumulative Operating Income Over Time**
   - Rental property: Rental income + stock dividends
   - Stock investment: Dividend income

## Design Principles

1. **Clean Implementation**: No shared functions between different strategies
2. **Accurate Tax Modeling**: Annual tax events properly handled
3. **Fair Comparison**: Equal cash outflow ensures apples-to-apples comparison
4. **Realistic Behavior**: Tax surplus invested, not consumed
5. **User-Friendly**: Auto-updating sliders, clear visualizations

## Version

**Version 2.0.0** - Clean implementation (October 28, 2025)

## Notes

- All old documentation and previous implementations have been removed
- This is a fresh start with clean, dedicated simulation logic
- Focus solely on "Buy & Rent vs Invest in Stocks" strategy
- No code sharing between different investment strategies
- Tax events happen annually, not monthly
- Surplus cash from tax benefits invested in stock portfolio
- Fair comparison maintained through equal monthly cash outflow
