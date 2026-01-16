"""
Buy & Live vs Rent & Invest Calculator
Clean implementation comparing homeownership (living in property) vs renting and investing
"""
import streamlit as st
import plotly.graph_objects as go
from core.homeownership_simulation import simulate_homeownership, simulate_rent_and_invest

st.set_page_config(page_title="Buy & Live vs Rent & Invest", layout="wide")

st.title("🏠 Buy & Live vs Rent & Invest")
st.markdown("""
Compare two strategies:
- **Homeownership**: Buy property with mortgage and live in it
- **Rent & Invest**: Rent a property and invest capital in stocks
""")

# Initialize session state
if 'params_home' not in st.session_state:
    st.session_state.params_home = {}

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
st.session_state.params_home['purchase_price'] = purchase_price

down_payment_pct = st.sidebar.slider(
    "Down Payment (%)",
    min_value=5.0,
    max_value=50.0,
    value=20.0,
    step=1.0
)
st.session_state.params_home['down_payment_pct'] = down_payment_pct / 100

closing_costs_pct = st.sidebar.slider(
    "Closing Costs (%)",
    min_value=1.0,
    max_value=5.0,
    value=3.0,
    step=0.5
)
st.session_state.params_home['closing_costs_pct'] = closing_costs_pct / 100

selling_cost_pct = st.sidebar.slider(
    "Selling Costs (%)",
    min_value=1.0,
    max_value=10.0,
    value=6.0,
    step=0.5
)
st.session_state.params_home['selling_cost_pct'] = selling_cost_pct / 100

# Mortgage parameters
st.sidebar.subheader("Mortgage Details")
mortgage_rate = st.sidebar.slider(
    "Mortgage Rate (%)",
    min_value=2.0,
    max_value=10.0,
    value=6.5,
    step=0.25
)
st.session_state.params_home['mortgage_rate'] = mortgage_rate / 100

mortgage_years = st.sidebar.slider(
    "Mortgage Term (years)",
    min_value=10,
    max_value=30,
    value=30,
    step=5
)
st.session_state.params_home['mortgage_years'] = mortgage_years

# Property costs
st.sidebar.subheader("Property Costs")
property_tax_rate = st.sidebar.slider(
    "Property Tax Rate (%/year)",
    min_value=0.5,
    max_value=3.0,
    value=1.2,
    step=0.1
)
st.session_state.params_home['property_tax_rate'] = property_tax_rate / 100

hoa_monthly = st.sidebar.slider(
    "HOA ($/month)",
    min_value=0,
    max_value=1000,
    value=200,
    step=50
)
st.session_state.params_home['hoa_monthly'] = hoa_monthly

insurance_monthly = st.sidebar.slider(
    "Insurance ($/month)",
    min_value=50,
    max_value=500,
    value=150,
    step=25
)
st.session_state.params_home['insurance_monthly'] = insurance_monthly

maintenance_rate = st.sidebar.slider(
    "Maintenance Rate (%/year)",
    min_value=0.5,
    max_value=3.0,
    value=1.0,
    step=0.1
)
st.session_state.params_home['maintenance_rate'] = maintenance_rate / 100

# Rental parameters
st.sidebar.subheader("Rental Costs")
monthly_rent = st.sidebar.slider(
    "Monthly Rent ($)",
    min_value=500,
    max_value=10000,
    value=2500,
    step=100
)
st.session_state.params_home['monthly_rent'] = monthly_rent

rent_increase_rate = st.sidebar.slider(
    "Rent Increase Rate (%/year)",
    min_value=0.0,
    max_value=10.0,
    value=3.0,
    step=0.5
)
st.session_state.params_home['rent_increase_rate'] = rent_increase_rate / 100

# Market assumptions
st.sidebar.subheader("Market Assumptions")
appreciation_rate = st.sidebar.slider(
    "Property Appreciation Rate (%/year)",
    min_value=0.0,
    max_value=10.0,
    value=3.0,
    step=0.5
)
st.session_state.params_home['appreciation_rate'] = appreciation_rate / 100

stock_return_rate = st.sidebar.slider(
    "Stock Return Rate (%/year)",
    min_value=0.0,
    max_value=20.0,
    value=10.0,
    step=0.5
)
st.session_state.params_home['stock_return_rate'] = stock_return_rate / 100

dividend_yield = st.sidebar.slider(
    "Dividend Yield (%/year)",
    min_value=0.0,
    max_value=10.0,
    value=2.0,
    step=0.5
)
st.session_state.params_home['dividend_yield'] = dividend_yield / 100

tax_bracket = st.sidebar.slider(
    "Tax Bracket (%)",
    min_value=10.0,
    max_value=40.0,
    value=25.0,
    step=1.0
)
st.session_state.params_home['tax_bracket'] = tax_bracket / 100

years = st.sidebar.slider(
    "Time Horizon (years)",
    min_value=5,
    max_value=30,
    value=30,
    step=1
)
st.session_state.params_home['years'] = years

# Run simulations
home_result = simulate_homeownership(st.session_state.params_home)
home_df = home_result['monthly_df']
home_summary = home_result['summary']

# Extract homeownership true monthly costs for stock simulation
homeownership_true_costs = home_df['true_monthly_cost'].tolist()

# Stock investment parameters
stock_params = {
    'initial_investment': home_summary['initial_payment'],
    'monthly_rent': st.session_state.params_home['monthly_rent'],
    'rent_increase_rate': st.session_state.params_home['rent_increase_rate'],
    'stock_return_rate': st.session_state.params_home['stock_return_rate'],
    'dividend_yield': st.session_state.params_home['dividend_yield'],
    'tax_bracket': st.session_state.params_home['tax_bracket'],
    'years': st.session_state.params_home['years']
}

stock_result = simulate_rent_and_invest(stock_params, homeownership_true_costs)
stock_df = stock_result['monthly_df']
stock_summary = stock_result['summary']

# Display results
st.header("📈 Comparison Results")

# Summary metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Initial Payment",
        f"${home_summary['initial_payment']:,.0f}"
    )

with col2:
    home_final = home_summary['final_net_proceeds']
    stock_final = stock_summary['final_net_proceeds']
    st.metric(
        "Homeownership Net Proceeds",
        f"${home_final:,.0f}"
    )

with col3:
    st.metric(
        "Rent & Invest Net Proceeds",
        f"${stock_final:,.0f}",
        delta=f"${stock_final - home_final:,.0f}"
    )

# Determine winner
if home_final > stock_final:
    winner = "Homeownership"
    difference = home_final - stock_final
else:
    winner = "Rent & Invest"
    difference = stock_final - home_final

st.success(f"🏆 **Winner: {winner}** by ${difference:,.0f} in net proceeds")

st.divider()

# Charts
tab1, tab2, tab3 = st.tabs(["📊 Net Proceeds", "💰 Cumulative Costs", "💵 Operating Income"])

with tab1:
    st.subheader("Net Proceeds Over Time")
    st.markdown("""
    - **Homeownership**: Property value - mortgage - selling costs
    - **Rent & Invest**: Total stock portfolio value
    """)
    
    # Convert months to years for x-axis
    home_df_yearly = home_df[home_df['month'] % 12 == 0].copy()
    home_df_yearly['year_label'] = home_df_yearly['month'] / 12
    
    stock_df_yearly = stock_df[stock_df['month'] % 12 == 0].copy()
    stock_df_yearly['year_label'] = stock_df_yearly['month'] / 12
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=home_df_yearly['year_label'],
        y=home_df_yearly['net_proceeds'],
        mode='lines+markers',
        name='Homeownership',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=4)
    ))
    
    fig.add_trace(go.Scatter(
        x=stock_df_yearly['year_label'],
        y=stock_df_yearly['net_proceeds'],
        mode='lines+markers',
        name='Rent & Invest',
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
    - **Homeownership**: True costs after tax benefit offset (interest, taxes, insurance, HOA, maintenance, closing costs - tax benefits)
    - **Rent & Invest**: Rent paid + dividend taxes
    """)
    
    # Convert months to years for x-axis
    home_df_yearly = home_df[home_df['month'] % 12 == 0].copy()
    home_df_yearly['year_label'] = home_df_yearly['month'] / 12
    
    stock_df_yearly = stock_df[stock_df['month'] % 12 == 0].copy()
    stock_df_yearly['year_label'] = stock_df_yearly['month'] / 12
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=home_df_yearly['year_label'],
        y=home_df_yearly['cumulative_true_cost'],
        mode='lines+markers',
        name='Homeownership (True Cost)',
        line=dict(color='#d62728', width=3),
        marker=dict(size=4)
    ))
    
    fig.add_trace(go.Scatter(
        x=stock_df_yearly['year_label'],
        y=stock_df_yearly['cumulative_cost'],
        mode='lines+markers',
        name='Rent & Invest',
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
    - **Homeownership**: Tax benefits from mortgage interest and property tax deductions
    - **Rent & Invest**: Dividend income (before tax)
    """)
    
    # Convert months to years for x-axis
    home_df_yearly = home_df[home_df['month'] % 12 == 0].copy()
    home_df_yearly['year_label'] = home_df_yearly['month'] / 12
    
    stock_df_yearly = stock_df[stock_df['month'] % 12 == 0].copy()
    stock_df_yearly['year_label'] = stock_df_yearly['month'] / 12
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=home_df_yearly['year_label'],
        y=home_df_yearly['cumulative_tax_benefits'],
        mode='lines+markers',
        name='Homeownership (Tax Benefits)',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=4)
    ))
    
    fig.add_trace(go.Scatter(
        x=stock_df_yearly['year_label'],
        y=stock_df_yearly['cumulative_operating_income'],
        mode='lines+markers',
        name='Rent & Invest (Dividends)',
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
    st.subheader("Homeownership Summary")
    st.write(f"**Initial Payment:** ${home_summary['initial_payment']:,.0f}")
    st.write(f"**Final Property Value:** ${home_summary['final_property_value']:,.0f}")
    st.write(f"**Final Equity:** ${home_summary['final_equity']:,.0f}")
    st.write(f"**Selling Costs:** ${home_summary['selling_costs']:,.0f}")
    st.write(f"**Final Net Proceeds:** ${home_summary['final_net_proceeds']:,.0f}")
    st.write(f"**Total Unrecoverable Costs:** ${home_summary['total_unrecoverable_costs']:,.0f}")
    st.write(f"**Total Tax Benefits:** ${home_summary['total_tax_benefits']:,.0f}")
    st.write(f"**Total True Cost:** ${home_summary['total_true_cost']:,.0f}")
    st.write(f"**Total Principal Paid:** ${home_summary['total_principal_paid']:,.0f}")

with col2:
    st.subheader("Rent & Invest Summary")
    st.write(f"**Initial Payment:** ${stock_summary['initial_payment']:,.0f}")
    st.write(f"**Total Stock Contributions:** ${stock_summary['total_contributions']:,.0f}")
    st.write(f"**Final Portfolio Value:** ${stock_summary['final_portfolio_value']:,.0f}")
    st.write(f"**Total Rent Paid:** ${stock_summary['total_rent_paid']:,.0f}")
    st.write(f"**Total Dividends:** ${stock_summary['total_dividends']:,.0f}")
    st.write(f"**Total Dividend Tax:** ${stock_summary['total_dividend_tax']:,.0f}")
    st.write(f"**Total Cost (rent + taxes):** ${stock_summary['total_cost']:,.0f}")
    st.write(f"**Final Net Proceeds:** ${stock_summary['final_net_proceeds']:,.0f}")

st.divider()

# Educational Content
st.header("📚 How The Calculations Work")

st.markdown("""
This section explains the financial calculations used in this comparison to help you understand how we arrive at the final numbers.
""")

with st.expander("🏠 Homeownership Strategy - Detailed Explanation", expanded=False):
    st.markdown("""
    ### Initial Payment
    When you buy a home to live in, you pay:
    - **Down Payment**: A percentage of the purchase price (e.g., 20% of $500k = $100k)
    - **Closing Costs**: Typically 2-3% of purchase price for buyer-side costs
    
    **Total Initial Payment** = Down Payment + Closing Costs
    
    ---
    
    ### Monthly Costs
    
    **Total Monthly Costs Before Tax Benefits**:
    - Mortgage payment (principal + interest)
    - Property taxes
    - Insurance
    - HOA fees
    - Maintenance (typically 1% of property value per year)
    
    **Monthly Tax Benefit**:
    When you own your primary residence, you can deduct mortgage interest and property taxes from your taxable income:
    ```
    Monthly Tax Benefit = (Monthly Interest + Monthly Property Tax) × Tax Bracket
    ```
    
    This is the tax refund you receive at year-end from these deductions.
    
    **True Monthly Cost**:
    ```
    True Cost = Total Costs - Monthly Tax Benefit
    ```
    
    This represents your actual out-of-pocket cost after accounting for tax savings.
    
    **Example**:
    - Monthly costs: $4,000
    - Deductible costs (interest + property tax): $3,200
    - Tax benefit: $800 (25% tax bracket times $3,200)
    - **True monthly cost: $4,000 - $800 = $3,200**
    
    ---
    
    ### Building Equity
    
    Each month, part of your mortgage payment goes toward principal:
    - **Principal Payment**: Builds equity (your ownership stake)
    - **Interest Payment**: Cost of borrowing (tax deductible)
    
    Over time, principal payments increase and interest decreases (amortization).
    
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
    
    This is the total cash you've spent during homeownership:
    ```
    Cumulative Cost = Closing Costs (at purchase) + Sum of True Monthly Costs + Selling Costs (at sale)
    ```
    
    **Components**:
    - **Closing Costs**: One-time costs paid at purchase (2-3% of property price)
    - **Sum of True Monthly Costs**: All monthly costs minus tax benefits over the entire period
    - **Selling Costs**: One-time costs paid when selling (typically 6% of sale price)
    
    This shows the total cash outflow during your homeownership period.
    
    ---
    
    ### Operating Income
    
    For homeowners, operating income is the tax benefits received:
    ```
    Operating Income = Tax Benefits from Deductions
    ```
    
    This represents the tax savings you receive each year from mortgage interest and property tax deductions.
    """)

with st.expander("🏢 Rent & Invest Strategy - Detailed Explanation", expanded=False):
    st.markdown("""
    ### Initial Payment
    You start with the same capital as the homeownership strategy:
    - **Initial Payment** = Down Payment + Closing Costs (same as homeownership)
    
    This capital is invested in stocks instead of used for a home purchase.
    
    ---
    
    ### Monthly Rent
    
    You pay rent to live somewhere:
    - **Monthly Rent**: Typically increases annually (e.g., 3% per year)
    - **Rent is a pure cost**: You don't build equity when renting
    
    ---
    
    ### Monthly Stock Contributions
    
    To maintain equal total monthly cash outflow with homeownership:
    ```
    Monthly Contribution = Homeownership True Cost - Monthly Rent
    ```
    
    **Why this formula?**
    - The homeowner pays their true cost (after tax benefits)
    - The renter pays rent PLUS invests the difference
    - Total monthly outflow is equal for both
    
    **Example**:
    - Homeownership true cost: $3,200
    - Monthly rent: $2,500
    - **Stock contribution: $3,200 - $2,500 = $700**
    - **Total outflow for renter: $2,500 (rent) + $700 (savings) = $3,200**
    
    **Note**: If rent exceeds homeownership costs, the contribution can be negative (withdrawing from savings).
    
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
    
    For the rent & invest strategy:
    ```
    Cumulative Cost = Cumulative Rent Paid + Cumulative Dividend Taxes
    ```
    
    This shows how much cash you've spent over time on rent and taxes.
    
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
    Both strategies start with the same initial payment:
    - Homeownership: Down Payment + Closing Costs
    - Rent & Invest: Same amount invested in stocks
    
    ✅ **Fair start**
    
    ---
    
    ### Equal Monthly Cash Outflow
    Both strategies require the same total monthly cash outflow:
    - Homeownership: True Cost (after tax benefits)
    - Rent & Invest: Rent + Stock Contribution
    
    The stock contribution adjusts to ensure:
    ```
    Homeownership True Cost = Rent + Stock Contribution
    ```
    
    ✅ **Equal monthly commitment**
    
    ---
    
    ### Proper Tax Accounting
    Both strategies account for taxes:
    - Homeownership: Tax benefits from mortgage interest and property tax deductions
    - Rent & Invest: Tax on dividends
    
    ✅ **Realistic tax treatment**
    
    ---
    
    ### Net Proceeds Include All Wealth
    Final net proceeds account for all assets and costs:
    - Homeownership: Property value - mortgage - selling costs - closing costs
    - Rent & Invest: Portfolio value
    
    ✅ **Complete wealth calculation**
    
    ---
    
    ### Key Assumptions
    
    - Property appreciation is constant (you can adjust the rate)
    - Stock returns are constant (you can adjust the rate)
    - Tax bracket remains constant
    - Rent increases annually at the rent increase rate
    - Maintenance costs scale with property value
    - Mortgage interest and property taxes are fully deductible
    
    These assumptions allow for clear comparison. In reality, returns vary and tax rules can be complex, but this gives you a baseline for decision-making.
    """)

st.info("💡 **Tip**: Adjust the parameters in the sidebar to see how different assumptions affect the comparison. Try different scenarios where rent is higher or lower than homeownership costs to understand the trade-offs.")
