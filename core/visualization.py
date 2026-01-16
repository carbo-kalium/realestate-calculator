"""
Shared plotting and visualization utilities using Plotly
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd


def create_line_chart(df, x_col, y_cols, title, y_axis_title="Value ($)", x_axis_title="Month"):
    """Create a multi-line chart"""
    fig = go.Figure()
    
    if isinstance(y_cols, str):
        y_cols = [y_cols]
    
    for col in y_cols:
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[col],
            mode='lines',
            name=col.replace('_', ' ').title(),
            hovertemplate='%{y:$,.0f}<extra></extra>'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_axis_title,
        yaxis_title=y_axis_title,
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def create_cashflow_chart(df, months_col='month'):
    """Create a detailed cashflow waterfall or stacked chart"""
    fig = go.Figure()
    
    # Check which columns exist
    income_cols = [col for col in ['effective_rent', 'net_revenue', 'gross_rent'] if col in df.columns]
    expense_cols = [col for col in ['mortgage_payment', 'property_tax', 'insurance', 'maintenance', 'hoa'] if col in df.columns]
    
    # Add income traces
    for col in income_cols[:1]:  # Just take the first income column
        fig.add_trace(go.Scatter(
            x=df[months_col],
            y=df[col],
            mode='lines',
            name='Income',
            line=dict(color='green'),
            fill='tozeroy'
        ))
    
    # Add expense traces
    if expense_cols:
        total_expenses = df[expense_cols].sum(axis=1)
        fig.add_trace(go.Scatter(
            x=df[months_col],
            y=total_expenses,
            mode='lines',
            name='Total Expenses',
            line=dict(color='red'),
            fill='tozeroy'
        ))
    
    # Add net cashflow if available
    if 'post_tax_cashflow' in df.columns:
        fig.add_trace(go.Scatter(
            x=df[months_col],
            y=df['post_tax_cashflow'],
            mode='lines',
            name='Net Cashflow',
            line=dict(color='blue', width=3)
        ))
    
    fig.update_layout(
        title='Monthly Cashflow Analysis',
        xaxis_title='Month',
        yaxis_title='Amount ($)',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def create_equity_chart(df, months_col='month'):
    """Create equity buildup chart"""
    fig = go.Figure()
    
    if 'property_value' in df.columns:
        fig.add_trace(go.Scatter(
            x=df[months_col],
            y=df['property_value'],
            mode='lines',
            name='Property Value',
            line=dict(color='blue')
        ))
    
    if 'remaining_balance' in df.columns:
        fig.add_trace(go.Scatter(
            x=df[months_col],
            y=df['remaining_balance'],
            mode='lines',
            name='Mortgage Balance',
            line=dict(color='red')
        ))
    
    if 'equity' in df.columns:
        fig.add_trace(go.Scatter(
            x=df[months_col],
            y=df['equity'],
            mode='lines',
            name='Equity',
            line=dict(color='green', width=3),
            fill='tozeroy'
        ))
    
    fig.update_layout(
        title='Equity Buildup Over Time',
        xaxis_title='Month',
        yaxis_title='Amount ($)',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def create_comparison_chart(results_dict, metric='net_proceeds'):
    """Create bar chart comparing multiple strategies"""
    strategies = []
    values = []
    
    for name, result in results_dict.items():
        strategies.append(name)
        values.append(result['summary'].get(metric, 0))
    
    fig = go.Figure(data=[
        go.Bar(
            x=strategies,
            y=values,
            text=[f'${v:,.0f}' for v in values],
            textposition='auto',
            marker_color='lightblue'
        )
    ])
    
    fig.update_layout(
        title=f'Strategy Comparison: {metric.replace("_", " ").title()}',
        xaxis_title='Strategy',
        yaxis_title='Amount ($)',
        template='plotly_white',
        height=500
    )
    
    return fig


def create_cumulative_comparison(df_dict):
    """
    Create cumulative value comparison chart
    df_dict: {'Strategy Name': dataframe, ...}
    """
    fig = go.Figure()
    
    for name, df in df_dict.items():
        # Determine which column to use for cumulative value
        if 'net_worth' in df.columns:
            y_col = 'net_worth'
        elif 'equity' in df.columns:
            y_col = 'equity'
        elif 'portfolio_value' in df.columns:
            y_col = 'portfolio_value'
        elif 'property_value' in df.columns:
            y_col = 'property_value'
        else:
            continue
        
        fig.add_trace(go.Scatter(
            x=df['month'] if 'month' in df.columns else range(len(df)),
            y=df[y_col],
            mode='lines',
            name=name,
            hovertemplate='%{y:$,.0f}<extra></extra>'
        ))
    
    fig.update_layout(
        title='Net Worth Comparison (Starting from Down Payment)',
        xaxis_title='Month',
        yaxis_title='Net Worth ($)',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def create_unrecoverable_costs_comparison(home_df, stock_df, is_rental_scenario=False):
    """
    Compare cumulative unrecoverable costs: homeownership vs rent paid
    OR rental property vs stock investment
    """
    fig = go.Figure()
    
    if is_rental_scenario:
        # For rental property: cumulative true cost of ownership
        # Monthly True Cost = Unrecoverable Costs - Rental Income (After Tax) - Monthly Tax Benefits
        cumulative_true_cost = home_df['monthly_true_cost'].cumsum()
        
        fig.add_trace(go.Scatter(
            x=home_df['month'],
            y=cumulative_true_cost,
            mode='lines',
            name='Rental Property (True Cost After Income)',
            line=dict(color='#d62728', width=3),
            hovertemplate='$%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Cumulative Costs: Rental Property vs Stock Investment',
            xaxis_title='Month',
            yaxis_title='Cumulative Cost ($)',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
    else:
        # Original homeownership scenario
        fig.add_trace(go.Scatter(
            x=home_df['month'],
            y=home_df['cumulative_unrecoverable'],
            mode='lines',
            name='Homeownership (Unrecoverable Costs)',
            line=dict(color='#d62728', width=3),
            hovertemplate='$%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Cumulative Unrecoverable Costs: Homeownership vs Rent',
            xaxis_title='Month',
            yaxis_title='Cumulative Cost ($)',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
    
    fig.add_trace(go.Scatter(
        x=stock_df['month'],
        y=stock_df['cumulative_rent'],
        mode='lines',
        name='Stock Investment (No Costs)',
        line=dict(color='#ff7f0e', width=3),
        hovertemplate='$%{y:,.0f}<extra></extra>'
    ))
    
    return fig


def create_operating_income_comparison(home_df, stock_df):
    """
    Compare cumulative operating income: tax benefits vs dividends
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=home_df['month'],
        y=home_df['cumulative_operating_income'],
        mode='lines',
        name='Homeownership (Tax Benefits)',
        line=dict(color='#2ca02c', width=3),
        hovertemplate='$%{y:,.0f}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=stock_df['month'],
        y=stock_df['cumulative_operating_income'],
        mode='lines',
        name='Rent & Invest (Dividends after Tax)',
        line=dict(color='#1f77b4', width=3),
        hovertemplate='$%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Cumulative Operating Income: Tax Benefits vs Dividends',
        xaxis_title='Month',
        yaxis_title='Cumulative Operating Income ($)',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def create_net_proceeds_comparison(home_df, stock_df, subtract_costs=False):
    """
    Compare net proceeds over time
    
    Args:
        home_df: Homeownership monthly data
        stock_df: Stock investment monthly data
        subtract_costs: If True, subtract cumulative unrecoverable costs/rent from net proceeds
                       If False, show net proceeds without cost subtraction
    """
    fig = go.Figure()
    
    # Calculate net proceeds values based on subtract_costs parameter
    if subtract_costs:
        # Subtract cumulative costs from net proceeds
        home_net_proceeds = home_df['net_worth'] - home_df['cumulative_unrecoverable']
        stock_net_proceeds = stock_df['net_worth'] - stock_df['cumulative_rent']
        chart_title = 'Net Proceeds Comparison (After Subtracting Cumulative Costs)'
    else:
        # Show net proceeds without cost subtraction
        home_net_proceeds = home_df['net_worth']
        stock_net_proceeds = stock_df['net_worth']
        chart_title = 'Net Proceeds Over Time'
    
    fig.add_trace(go.Scatter(
        x=home_df['month'],
        y=home_net_proceeds,
        mode='lines',
        name='Homeownership (Net Proceeds)',
        line=dict(color='#d62728', width=3),
        hovertemplate='$%{y:,.0f}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=stock_df['month'],
        y=stock_net_proceeds,
        mode='lines',
        name='Rent & Invest (Net Proceeds)',
        line=dict(color='#ff7f0e', width=3),
        hovertemplate='$%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=chart_title,
        xaxis_title='Month',
        yaxis_title='Net Proceeds ($)',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def create_summary_table(summary_dict):
    """Create a formatted summary table from summary dictionary"""
    rows = []
    for key, value in summary_dict.items():
        formatted_key = key.replace('_', ' ').title()
        if isinstance(value, (int, float)):
            if 'rate' in key.lower() or 'roi' in key.lower() or 'return' in key.lower():
                formatted_value = f"{value:.2f}%"
            else:
                formatted_value = f"${value:,.2f}"
        else:
            formatted_value = str(value)
        rows.append({'Metric': formatted_key, 'Value': formatted_value})
    
    return pd.DataFrame(rows)


def create_annual_summary(monthly_df):
    """Create annual summary from monthly data"""
    if 'year' not in monthly_df.columns:
        monthly_df['year'] = (monthly_df['month'] - 1) // 12
    
    annual = monthly_df.groupby(monthly_df['year'].astype(int)).agg({
        col: 'sum' for col in monthly_df.columns if col not in ['month', 'year', 'property_value', 'equity', 'remaining_balance', 'portfolio_value']
    })
    
    # Add end-of-year values for certain columns
    for col in ['property_value', 'equity', 'remaining_balance', 'portfolio_value']:
        if col in monthly_df.columns:
            annual[f'{col}_end'] = monthly_df.groupby(monthly_df['year'].astype(int))[col].last()
    
    return annual.reset_index()


def format_currency(value):
    """Format value as currency"""
    if pd.isna(value):
        return "$0"
    return f"${value:,.0f}"


def format_percentage(value):
    """Format value as percentage"""
    if pd.isna(value):
        return "0.00%"
    return f"{value:.2f}%"
