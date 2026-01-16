"""
Buy & Rent vs Invest in Stocks Calculator
Clean implementation with dedicated simulation logic
"""
import streamlit as st
import plotly.graph_objects as go
from core.rental_simulation import simulate_rental_property, simulate_stock_investment

st.set_page_config(page_title="Buy & Rent vs Invest in Stocks", layout="wide")

st.title("🏘️ Buy & Rent vs Invest in Stocks")
st.markdown("""
Compare two investment strategies:
- **Rental Property**: Buy property, rent it out, invest tax surplus in stocks
- **Stock Investment**: Invest same capital in stocks with equivalent monthly contributions
""")

# Initialize session state
if 'params' not in st.session_state:
    st.session_state.params = {}

# Sidebar inputs
st.sidebar.header("📊 Investment Parameters")

# Property parameters
st.sidebar.subheader("Property Details")
purchase_price = st.sidebar.slider(
    "Purchase Price ($)",
    min_value=100000,
    max_value=2000000,
    value=500000,
    step=10000
)
st.session_state.params['purchase_price'] = purchase_price

down_payment_pct = st.sidebar.slider(
    "Down Payment (%)",
    min_value=5.0,
    max_value=50.0,
    value=20.0,
    step=1.0
)
st.session_state.params['down_payment_pct'] = down_payment_pct / 100

closing_costs_pct = st.sidebar.slider(
    "Closing Costs (%)",
    min_value=1.0,
    max_value=5.0,
    value=3.0,
    step=0.5
)
st.session_state.params['closing_costs_pct'] = closing_costs_pct / 100

# Mortgage parameters
st.sidebar.subheader("Mortgage Details")
mortgage_rate = st.sidebar.slider(
    "Mortgage Rate (%)",
    min_value=2.0,
    max_value=10.0,
    value=6.5,
    step=0.25
)
st.session_state.params['mortgage_rate'] = mortgage_rate / 100

mortgage_years = st.sidebar.slider(
    "Mortgage Term (years)",
    min_value=10,
    max_value=30,
    value=30,
    step=5
)
st.session_state.params['mortgage_years'] = mortgage_years

# Property costs
st.sidebar.subheader("Property Costs")
property_tax_rate = st.sidebar.slider(
    "Property Tax Rate (%/year)",
    min_value=0.5,
    max_value=3.0,
    value=1.2,
    step=0.1
)
st.session_state.params['property_tax_rate'] = property_tax_rate / 100

hoa_monthly = st.sidebar.slider(
    "HOA ($/month)",
    min_value=0,
    max_value=1000,
    value=200,
    step=50
)
st.session_state.params['hoa_monthly'] = hoa_monthly

insurance_monthly = st.sidebar.slider(
    "Insurance ($/month)",
    min_value=50,
    max_value=500,
    value=150,
    step=25
)
st.session_state.params['insurance_monthly'] = insurance_monthly

maintenance_rate = st.sidebar.slider(
    "Maintenance Rate (%/year)",
    min_value=0.5,
    max_value=3.0,
    value=1.0,
    step=0.1
)
st.session_state.params['maintenance_rate'] = maintenance_rate / 100

# Rental income
st.sidebar.subheader("Rental Income")
monthly_rent = st.sidebar.slider(
    "Monthly Rent ($)",
    min_value=500,
    max_value=10000,
    value=3500,
    step=100
)
st.session_state.params['monthly_rent'] = monthly_rent

vacancy_rate = st.sidebar.slider(
    "Vacancy Rate (%)",
    min_value=0.0,
    max_value=20.0,
    value=8.3,
    step=0.5
)
st.session_state.params['vacancy_rate'] = vacancy_rate / 100

# Market assumptions
st.sidebar.subheader("Market Assumptions")
appreciation_rate = st.sidebar.slider(
    "Property Appreciation Rate (%/year)",
    min_value=0.0,
    max_value=10.0,
    value=3.0,
    step=0.5
)
st.session_state.params['appreciation_rate'] = appreciation_rate / 100

stock_return_rate = st.sidebar.slider(
    "Stock Return Rate (%/year)",
    min_value=0.0,
    max_value=20.0,
    value=10.0,
    step=0.5
)
st.session_state.params['stock_return_rate'] = stock_return_rate / 100

dividend_yield = st.sidebar.slider(
    "Dividend Yield (%/year)",
    min_value=0.0,
    max_value=10.0,
    value=2.0,
    step=0.5
)
st.session_state.params['dividend_yield'] = dividend_yield / 100

tax_bracket = st.sidebar.slider(
    "Tax Bracket (%)",
    min_value=10.0,
    max_value=40.0,
    value=25.0,
    step=1.0
)
st.session_state.params['tax_bracket'] = tax_bracket / 100

years = st.sidebar.slider(
    "Time Horizon (years)",
    min_value=5,
    max_value=30,
    value=30,
    step=1
)
st.session_state.params['years'] = years

# Run simulations
rental_result = simulate_rental_property(st.session_state.params)
rental_df = rental_result['monthly_df']
rental_summary = rental_result['summary']

# Extract rental monthly expenses for stock simulation
rental_monthly_expenses = (rental_df['true_cost'] + rental_df['principal_payment']).tolist()

# Stock investment parameters
stock_params = {
    'initial_investment': rental_summary['initial_payment'],
    'stock_return_rate': st.session_state.params['stock_return_rate'],
    'dividend_yield': st.session_state.params['dividend_yield'],
    'tax_bracket': st.session_state.params['tax_bracket'],
    'years': st.session_state.params['years']
}

stock_result = simulate_stock_investment(stock_params, rental_monthly_expenses)
stock_df = stock_result['monthly_df']
stock_summary = stock_result['summary']

# Display results
st.header("📈 Comparison Results")

# Summary metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Initial Payment",
        f"${rental_summary['initial_payment']:,.0f}"
    )

with col2:
    st.metric(
        "Final Property Value",
        f"${rental_summary['final_property_value']:,.0f}"
    )

with col3:
    st.metric(
        "Net Proceeds",
        f"${rental_summary['final_net_proceeds']:,.0f}"
    )

st.divider()

# Charts
tab1, tab2, tab3 = st.tabs(["📊 Net Proceeds", "💰 Cumulative Costs", "💵 Operating Income"])

with tab1:
    st.subheader("Net Proceeds Over Time")
    st.markdown("""
    - **Rental Property**: Property value - mortgage - closing costs
    - **Stock Investment**: Total portfolio value
    """)
    
    # Convert months to years for x-axis
    rental_df_yearly = rental_df[rental_df['month'] % 12 == 0].copy()
    rental_df_yearly['year_label'] = rental_df_yearly['month'] / 12
    
    stock_df_yearly = stock_df[stock_df['month'] % 12 == 0].copy()
    stock_df_yearly['year_label'] = stock_df_yearly['month'] / 12
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=rental_df_yearly['year_label'],
        y=rental_df_yearly['net_proceeds'],
        mode='lines+markers',
        name='Rental Property',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=4)
    ))
    
    fig.add_trace(go.Scatter(
        x=stock_df_yearly['year_label'],
        y=stock_df_yearly['net_proceeds'],
        mode='lines+markers',
        name='Stock Investment',
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        xaxis_title='Years',
        yaxis_title='Net Proceeds ($)',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        xaxis=dict(tickformat='d')
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Cumulative Costs Over Time")
    st.markdown("""
    - **Rental Property**: Sum of monthly true costs (unrecoverable costs - rental income)
    - **Stock Investment**: Cumulative dividend taxes paid annually
    """)
    
    # Convert months to years for x-axis
    rental_df_yearly = rental_df[rental_df['month'] % 12 == 0].copy()
    rental_df_yearly['year_label'] = rental_df_yearly['month'] / 12
    
    stock_df_yearly = stock_df[stock_df['month'] % 12 == 0].copy()
    stock_df_yearly['year_label'] = stock_df_yearly['month'] / 12
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=rental_df_yearly['year_label'],
        y=rental_df_yearly['cumulative_true_cost'],
        mode='lines+markers',
        name='Rental Property',
        line=dict(color='#d62728', width=3),
        marker=dict(size=4)
    ))
    
    fig.add_trace(go.Scatter(
        x=stock_df_yearly['year_label'],
        y=stock_df_yearly['cumulative_cost'],
        mode='lines+markers',
        name='Stock Investment',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        xaxis_title='Years',
        yaxis_title='Cumulative Cost ($)',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        xaxis=dict(tickformat='d')
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Cumulative Operating Income Over Time")
    st.markdown("""
    - **Rental Property**: Rental income + dividends from stock portfolio
    - **Stock Investment**: Dividend income
    """)
    
    # Convert months to years for x-axis
    rental_df_yearly = rental_df[rental_df['month'] % 12 == 0].copy()
    rental_df_yearly['year_label'] = rental_df_yearly['month'] / 12
    
    stock_df_yearly = stock_df[stock_df['month'] % 12 == 0].copy()
    stock_df_yearly['year_label'] = stock_df_yearly['month'] / 12
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=rental_df_yearly['year_label'],
        y=rental_df_yearly['cumulative_operating_income'],
        mode='lines+markers',
        name='Rental Property',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=4)
    ))
    
    fig.add_trace(go.Scatter(
        x=stock_df_yearly['year_label'],
        y=stock_df_yearly['cumulative_operating_income'],
        mode='lines+markers',
        name='Stock Investment',
        line=dict(color='#9467bd', width=3),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        xaxis_title='Years',
        yaxis_title='Cumulative Operating Income ($)',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        xaxis=dict(tickformat='d')
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Detailed breakdown
st.header("📋 Detailed Breakdown")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Rental Property Summary")
    st.write(f"**Initial Payment:** ${rental_summary['initial_payment']:,.0f}")
    st.write(f"**Final Property Value:** ${rental_summary['final_property_value']:,.0f}")
    st.write(f"**Selling Costs:** ${rental_summary['selling_costs']:,.0f}")
    st.write(f"**Final Net Proceeds:** ${rental_summary['final_net_proceeds']:,.0f}")
    st.write(f"**Total True Cost:** ${rental_summary['total_true_cost']:,.0f}")
    st.write(f"**Total Operating Income:** ${rental_summary['total_operating_income']:,.0f}")
    st.write(f"**Total Rental Income:** ${rental_summary['total_rental_income']:,.0f}")

with col2:
    st.subheader("Stock Investment Summary")
    st.write(f"**Initial Payment:** ${stock_summary['initial_payment']:,.0f}")
    st.write(f"**Total Contributions:** ${stock_summary['total_contributions']:,.0f}")
    st.write(f"**Final Portfolio Value:** ${stock_summary['final_portfolio_value']:,.0f}")
    st.write(f"**Total Dividends:** ${stock_summary['total_dividends']:,.0f}")
    st.write(f"**Total Dividend Tax:** ${stock_summary['total_dividend_tax']:,.0f}")
    st.write(f"**Final Net Proceeds:** ${stock_summary['final_net_proceeds']:,.0f}")

st.divider()

# Educational Content
st.header("📚 How The Calculations Work")

st.markdown("""
This section explains the financial calculations used in this comparison to help you understand how we arrive at the final numbers.
""")

with st.expander("🏠 Rental Property Strategy - Detailed Explanation", expanded=False):
    st.markdown("""
    ### Initial Payment
    When you buy a rental property, you pay:
    - **Down Payment**: A percentage of the purchase price (e.g., 20% of $500k = $100k)
    - **Closing Costs**: Typically 2-3% of purchase price for buyer-side costs
    
    **Total Initial Payment** = Down Payment + Closing Costs
    
    ---
    
    ### Monthly Cash Flow
    
    **Unrecoverable Costs** (money you can't get back):
    - Mortgage interest payment
    - Property taxes
    - Insurance
    - HOA fees
    - Maintenance (typically 1% of property value per year)
    
    **Rental Income**:
    - Monthly rent collected from tenants
    - Adjusted for vacancy rate (e.g., 8.3% vacancy = 1 month vacant per year)
    - Formula: `Rent × (1 - Vacancy Rate)`
    
    **True Monthly Cost**:
    ```
    True Cost = Unrecoverable Costs - Rental Income - Monthly Tax Benefit
    ```
    
    Where:
    - **Monthly Tax Benefit** = (Monthly Interest + Monthly Property Tax) × Tax Bracket
    
    This represents your actual out-of-pocket cost after accounting for rental income and tax savings from deductions.
    
    ---
    
    ### Monthly Tax Benefit
    
    Each month, you receive a tax benefit from deductible expenses:
    ```
    Monthly Tax Benefit = (Monthly Interest + Monthly Property Tax) × Tax Bracket
    ```
    
    This benefit is already subtracted from your true monthly cost above.
    
    ---
    
    ### Annual Tax Settlement
    
    At the end of each year, the IRS settles taxes based on actual annual figures:
    
    1. **Tax on Rental Income**:
       ```
       Tax Owed = Annual Rental Income × Tax Bracket
       ```
       You owe taxes on the rental income you received.
    
    2. **Tax Benefit from Deductions**:
       ```
       Tax Benefit = (Annual Interest + Annual Property Tax) × Tax Bracket
       ```
       You can deduct mortgage interest and property taxes, which reduces your taxable income and results in a tax refund.
    
    **Note**: The monthly tax benefit is already subtracted from your true monthly cost, so this annual settlement is for informational purposes to understand your actual tax liability.
    
    ---
    
    ### Net Proceeds (Final Wealth)
    
    At the end of your investment period:
    ```
    Net Proceeds = Property Value - Remaining Mortgage - Selling Costs
    ```
    
    **Components**:
    - **Property Value**: Original price grown by appreciation rate (e.g., 3% per year)
    - **Remaining Mortgage**: What you still owe on the loan
    - **Selling Costs**: Typically 6% (agent commission + closing costs at sale)
    
    **Note**: Closing costs paid at purchase are already included in cumulative costs, so they're not subtracted again here.
    
    ---
    
    ### Cumulative Costs
    
    This is the total cash you've spent during the rental investment:
    ```
    Cumulative Cost = Closing Costs (at purchase) + Sum of Monthly True Costs + Selling Costs (at sale)
    ```
    
    **Components**:
    - **Closing Costs**: One-time costs paid at purchase (2-3% of property price)
    - **Sum of Monthly True Costs**: Monthly unrecoverable costs minus rental income
    - **Selling Costs**: One-time costs paid when selling (typically 6% of sale price)
    
    This shows the total cash outflow during your investment period.
    
    ---
    
    ### Operating Income
    
    This is the income generated by your rental property:
    ```
    Operating Income = Rental Income
    ```
    
    This shows the passive income stream your investments generate.
    """)

with st.expander("📈 Stock Investment Strategy - Detailed Explanation", expanded=False):
    st.markdown("""
    ### Initial Payment
    You start with the same capital as the rental property strategy:
    - **Initial Payment** = Down Payment + Closing Costs (same as rental property)
    
    This ensures a fair comparison between strategies.
    
    ---
    
    ### Monthly Contributions
    
    To maintain equal monthly cash outflow:
    ```
    Monthly Contribution = Rental Property's (True Cost + Principal Payment)
    ```
    
    **Why include principal payment?**
    - In the rental strategy, principal payments build equity (wealth)
    - In the stock strategy, contributions build portfolio value (wealth)
    - This ensures both strategies have the same total monthly cash outflow
    
    **Example**:
    - Rental true cost: $1,500
    - Principal payment: $500
    - **Stock contribution: $2,000**
    
    Both strategies spend $2,000 per month.
    
    ---
    
    ### Portfolio Growth
    
    Your stock portfolio grows through:
    
    1. **Monthly Returns**:
       ```
       Monthly Return Rate = Annual Return Rate / 12
       Portfolio Value = Portfolio Value × (1 + Monthly Return)
       ```
    
    2. **Monthly Contributions**:
       ```
       Portfolio Value = Portfolio Value + Monthly Contribution
       ```
    
    3. **Dividend Reinvestment**:
       ```
       Monthly Dividend = Portfolio Value × (Dividend Yield / 12)
       ```
       Dividends are automatically reinvested into the portfolio.
    
    ---
    
    ### Annual Tax Event
    
    At the end of each year:
    ```
    Dividend Tax = Annual Dividends × Tax Bracket
    ```
    
    You owe taxes on the dividends your portfolio generated during the year.
    
    ---
    
    ### Net Proceeds (Final Wealth)
    
    At the end of your investment period:
    ```
    Net Proceeds = Stock Portfolio Value
    ```
    
    This is your total wealth - the complete value of your stock portfolio.
    
    ---
    
    ### Cumulative Costs
    
    For the stock strategy, costs are the taxes paid:
    ```
    Cumulative Cost = Sum of Annual Dividend Taxes
    ```
    
    This is the only "cost" in the stock strategy (other than contributions which build wealth).
    
    ---
    
    ### Operating Income
    
    Income generated by dividends:
    ```
    Operating Income = Dividends (before tax)
    ```
    
    This shows the passive income your stock portfolio generates.
    """)

with st.expander("⚖️ Fair Comparison - How We Ensure Parity", expanded=False):
    st.markdown("""
    ### Equal Starting Capital
    Both strategies start with the same initial investment:
    - Rental Property: Down Payment + Closing Costs
    - Stock Investment: Same amount
    
    ✅ **Fair start**
    
    ---
    
    ### Equal Monthly Cash Outflow
    Both strategies require the same monthly cash outflow:
    - Rental Property: True Cost (costs - rental income)
    - Stock Investment: Contribution = Rental's (True Cost + Principal Payment)
    
    ✅ **Equal monthly commitment**
    
    ---
    
    ### Proper Tax Accounting
    Both strategies account for taxes:
    - Rental Property: Tax on rental income, tax benefits from deductions, tax on dividends
    - Stock Investment: Tax on dividends
    
    ✅ **Realistic tax treatment**
    
    ---
    
    ### Net Proceeds Include All Wealth
    Final net proceeds account for all assets and costs:
    - Rental Property: Property value + stock portfolio - mortgage - selling costs - closing costs
    - Stock Investment: Portfolio value
    
    ✅ **Complete wealth calculation**
    
    ---
    
    ### Key Assumptions
    
    - Property appreciation is constant (you can adjust the rate)
    - Stock returns are constant (you can adjust the rate)
    - Tax bracket remains constant
    - Rent increases annually at the rent increase rate
    - Vacancy rate is applied to rental income
    - Maintenance costs scale with property value
    
    These assumptions allow for clear comparison. In reality, returns vary, but this gives you a baseline for decision-making.
    """)

st.info("💡 **Tip**: Adjust the parameters in the sidebar to see how different assumptions affect the comparison. Try different appreciation rates, stock returns, and time horizons to understand the sensitivities.")

