import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load dataset
file_path = r'C:\Users\SUPRIYA GOUDA\Desktop\Retail_ECommerce_Dataset.csv'
df = pd.read_csv(file_path)

# Ensure the TransactionDate column is in datetime format
df['TransactionDate'] = pd.to_datetime(df['TransactionDate'], errors='coerce')  # Handle invalid dates
df = df.dropna(subset=['TransactionDate'])  # Drop rows with invalid dates
df['Month'] = df['TransactionDate'].dt.to_period('M').astype(str)  # Extract month

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1('Sales Dashboard', style={'textAlign': 'center', 'color': '#4CAF50', 'fontFamily': 'Arial, sans-serif'}),

    html.Div([
        html.Div([
            html.H3('Select Date Range:', style={'color': '#1E88E5', 'fontFamily': 'Arial, sans-serif'}),
            dcc.DatePickerRange(
                id='date-range',
                start_date=df['TransactionDate'].min(),
                end_date=df['TransactionDate'].max(),
                display_format='YYYY-MM-DD',
                style={'width': '100%'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px', 'backgroundColor': '#E3F2FD', 'borderRadius': '10px'}),

        html.Div([
            html.H3('Select State:', style={'color': '#1E88E5', 'fontFamily': 'Arial, sans-serif'}),
            dcc.Dropdown(
                id='state-dropdown',
                options=[{'label': i, 'value': i} for i in df['State'].unique()],
                value=df['State'].unique()[0] if len(df['State'].unique()) > 0 else None,
                style={'width': '100%'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px', 'backgroundColor': '#E3F2FD', 'borderRadius': '10px'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),

    html.Div([
        html.Div([
            dcc.Graph(id='sales-trend', style={'height': '400px'})
        ], style={'flex': '1', 'padding': '10px', 'backgroundColor': '#F1F8E9', 'borderRadius': '10px'}),

        html.Div([
            dcc.Graph(id='category-pie', style={'height': '400px'})
        ], style={'flex': '1', 'padding': '10px', 'backgroundColor': '#F1F8E9', 'borderRadius': '10px'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),

    html.Div([
        html.Div([
            dcc.Graph(id='state-bar', style={'height': '400px'})
        ], style={'flex': '1', 'padding': '10px', 'backgroundColor': '#FFF3E0', 'borderRadius': '10px'}),

        html.Div([
            dcc.Graph(id='delivery-status', style={'height': '400px'})
        ], style={'flex': '1', 'padding': '10px', 'backgroundColor': '#FFF3E0', 'borderRadius': '10px'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),

    html.Div([
        html.Div([
            dcc.Graph(id='top-products', style={'height': '400px'})
        ], style={'flex': '1', 'padding': '10px', 'backgroundColor': '#FFEBEE', 'borderRadius': '10px'}),

        html.Div([
            dcc.Graph(id='customer-ratings', style={'height': '400px'})
        ], style={'flex': '1', 'padding': '10px', 'backgroundColor': '#FFEBEE', 'borderRadius': '10px'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),

], style={'padding': '20px', 'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#F9F9F9'} )

# Callbacks
@app.callback(
    [Output('sales-trend', 'figure'),
     Output('category-pie', 'figure'),
     Output('state-bar', 'figure'),
     Output('delivery-status', 'figure'),
     Output('top-products', 'figure'),
     Output('customer-ratings', 'figure')],
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('state-dropdown', 'value')]
)
def update_graphs(start_date, end_date, selected_state):
    # Ensure inputs are valid
    if not start_date or not end_date or not selected_state:
        return {}, {}, {}, {}, {}, {}

    # Filter data based on inputs
    filtered_df = df[(df['TransactionDate'] >= pd.to_datetime(start_date)) &
                     (df['TransactionDate'] <= pd.to_datetime(end_date)) &
                     (df['State'] == selected_state)]

    # Sales trend
    sales_trend = px.line(
        filtered_df,
        x='TransactionDate',
        y='TotalAmount',
        title='Daily Sales Trend',
        color_discrete_sequence=['#1E88E5']
    )

    # Category distribution
    category_pie = px.pie(
        filtered_df,
        names='SubCategory',
        values='TotalAmount',
        title='Sales by SubCategory',
        color_discrete_sequence=px.colors.sequential.RdBu
    )

    # State comparison
    state_summary = df.groupby('State', as_index=False)['TotalAmount'].sum()
    state_bar = px.bar(
        state_summary,
        x='State',
        y='TotalAmount',
        title='Total Sales by State',
        color='TotalAmount',
        color_continuous_scale=px.colors.sequential.Viridis
    )

    # Delivery status
    delivery_status = px.bar(
        filtered_df.groupby('DeliveryStatus', as_index=False)['TotalAmount'].sum(),
        x='DeliveryStatus',
        y='TotalAmount',
        title='Delivery Status Overview',
        color='TotalAmount',
        color_continuous_scale=px.colors.sequential.Plasma
    )

    # Top products
    top_products = px.bar(
        filtered_df.groupby('ProductName', as_index=False)['TotalAmount'].sum().nlargest(10, 'TotalAmount'),
        x='ProductName',
        y='TotalAmount',
        title='Top 10 Products by Sales',
        color='TotalAmount',
        color_continuous_scale=px.colors.sequential.Tealgrn
    )

    # Customer ratings
    if 'CustomerRating' in filtered_df.columns and not filtered_df['CustomerRating'].isna().all():
        customer_ratings = px.histogram(
            filtered_df,
            x='CustomerRating',
            nbins=10,
            title='Customer Ratings Distribution',
            color_discrete_sequence=['#FF7043']
        )
    else:
        customer_ratings = {}

    return sales_trend, category_pie, state_bar, delivery_status, top_products, customer_ratings

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8060)
