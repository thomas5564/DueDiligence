import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from urllib.parse import urlencode

def readable(i):
    """Convert large numbers to human-readable format."""
    if i >= 1e12:
        return f"{round(i / 1e12, 1)}T"
    elif i >= 1e9:
        return f"{round(i / 1e9, 1)}B"
    elif i >= 1e6:
        return f"{round(i / 1e6, 1)}M"
    elif i >= 1e3:
        return f"{round(i / 1e3, 1)}k"
    else:
        return str(i)

def create_ticker_dict(ticker, change_in_retained, cash_to_debt, debt_to_equity, prefstock, buyback):
    return {
        ticker: {
            "Change_in_Retained_Earnings": change_in_retained,
            "Cash_to_Debt_difference": cash_to_debt,
            "Debt_to_Equity_Ratio": debt_to_equity,
            "Preferred_Stock_Equity_Exists": prefstock,
            "Buyback_Detected": buyback,
        }
    }
def getBalanceSheet(t):
    ticker = yf.Ticker(t)
    balance = ticker.quarterly_balance_sheet
    return balance

def find_total_equity(b):
    common_stock_equity = b.loc["Common Stock Equity"] if "Common Stock Equity" in b.index else 0
    retained_earnings = b.loc["Retained Earnings"] if "Retained Earnings" in b.index else 0
    additional_paid_in_capital = b.loc["Additional Paid In Capital"] if "Additional Paid In Capital" in b.index else 0
    other_equity_adjustments = b.loc["Other Equity Adjustments"] if "Other Equity Adjustments" in b.index else 0
    treasury_shares = b.loc["Treasury Shares Number"] if "Treasury Shares Number" in b.index else 0
    
    # Calculate Total Equity
    total_equity = (common_stock_equity + retained_earnings +
                    additional_paid_in_capital + other_equity_adjustments)
    
    return total_equity.iloc[0]

def find_total_debt(b):
    try:
    # Initialize debt values with 0 if the index doesn't exist
        short_term_debt = b.loc["Current Liabilities"].iloc[0] if "Current Liabilities" in b.index else 0
        long_term_debt = b.loc["Total Non Current Liabilities Net Minority Interest"].iloc[0] if "Total Non Current Liabilities Net Minority Interest" in b.index else 0
        
        # Calculate Total Debt
        total_debt = short_term_debt + long_term_debt
        
        return total_debt

    except(e):
        print("error occured in finding total debt")

def visualise(data):
    plt.figure(figsize=(10, 6))  # Set the figure size for better readability
    plt.plot(data.index, data, marker='o', linestyle='-', color='b')  # Plot with blue line and circle markers
    plt.title('Retained Earnings Over Time')  # Title of the plot
    plt.xlabel('Date')  # X-axis label
    plt.ylabel('Retained Earnings ($)')  # Y-axis label
    plt.grid(True)  # Enable grid for easier readability of the plot
    plt.xticks(rotation=45)  # Rotate date labels for better visibility
    plt.tight_layout()  # Adjust layout to not cut off any label or title
    plt.show()  # Display the plot

def dd(ticker):
    balance = getBalanceSheet(ticker)
    
    # Ensure required data exists
    try:
        total_cash = balance.loc['Cash Cash Equivalents And Short Term Investments']
        total_debt = balance.loc['Total Debt'] if 'Total Debt' in balance.index else find_total_debt(balance)
        total_liabilities = balance.loc['Total Liabilities Net Minority Interest']
        retained_earnings = balance.loc['Retained Earnings']
    except KeyError as e:
        print(f"Error: Missing required data in {ticker}'s balance sheet: {e}")
        return None

    # Process retained earnings
    retained = retained_earnings.reset_index()
    retained.columns = ['Date', 'Retained Earnings']
    retained = retained.set_index('Date')  # Assign the result back to `retained`

    # Define helper functions
    def recentRetained(retained):
        try:
            if 'Retained Earnings' in retained.columns and len(retained) > 1:
                return retained.iloc[0]['Retained Earnings'] / retained.iloc[1]['Retained Earnings']
            else:
                return None  # Fallback if data is insufficient
        except ZeroDivisionError:
            print("Error: Division by zero occurred in change_in_retained calculation.")
            return None
        except Exception as e:
            print(f"Unexpected error in change_in_retained calculation: {e}")
            return None

    def CashDebtDiff(total_cash, total_debt):
        try:
            return (total_cash - total_debt).iloc[0]
        except Exception as e:
            print(f"Unexpected error in cashdebt calculation: {e}")
            return None

    def liabilityEquityRatio(balance):
        try:
            total_equity = find_total_equity(balance)
            if total_equity != 0:
                return total_liabilities.iloc[0] / total_equity
            else:
                return None  # Prevent division by zero
        except ZeroDivisionError:
            print("Error: Division by zero occurred in debt-to-equity calculation.")
            return None
        except Exception as e:
            print(f"Unexpected error in debt-to-equity calculation: {e}")
            return None

    def DetectPreferredStock(balance):
        try:
            # Check for Preferred Stock Equity in the index
            return 'Preferred Stock' in balance.index
        except Exception as e:
            print(f"Unexpected error in prefstock check: {e}")
            return False
            
    def DetectTreasuryShares(balance):
        try:
            # Check for Treasury Shares and ensure the column exists and has data
            if 'Treasury Shares Number' in balance.index and not balance.loc['Treasury Shares Number'].isna().all():
                return balance.loc['Treasury Shares Number'].iloc[0] > 0
            else:
                return False  # Default to False if data is missing
        except Exception as e:
            print(f"Unexpected error in buyback calculation: {e}")
            return False

    # Execute helper functions and collect results
    change_in_retained = recentRetained(retained)
    cashdebt = CashDebtDiff(total_cash, total_debt)
    debttoeq = liabilityEquityRatio(balance)
    prefstock = DetectPreferredStock(balance)
    buyback = DetectTreasuryShares(balance)

    # Return results as a dictionary for the ticker
    print(f"data for {ticker} is found. {cashdebt}")
    return create_ticker_dict(ticker, change_in_retained, cashdebt, debttoeq, prefstock, buyback)


def array_to_dataframe(data):
    # Flatten the array of dictionaries
    flattened_data = {ticker: metrics for item in data for ticker, metrics in item.items()}
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(flattened_data, orient='index')
    return df

def help(tickerlist):
    data = []
    for i in tickerlist:
        data.append(dd(i))
    return data

def get_screen(ticker_symbol):
    def categorize_market_cap(market_cap):
        if market_cap >= 200e9:
            return "mega"
        elif 10e9 <= market_cap < 200e9:
            return "large"
        elif 2e9 <= market_cap < 10e9:
            return "mid"
        elif 300e6 <= market_cap < 2e9:
            return "small"
        elif 50e6 <= market_cap < 300e6:
            return "micro"
        elif market_cap < 50e6:
            return "nano"
        else:
            return "Unknown"
    try:
        # Download the ticker information
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        # Extract the industry, sector, and market cap
        industry = info.get('industry', 'N/A')
        sector = info.get('sector', 'N/A')
        market_cap = info.get('marketCap','N/A')

        return [f"cap_{categorize_market_cap(market_cap)}",f"ind_{industry.lower().replace(" ", "")}", f'sec_{sector.lower().replace(" ", "")}']

    except Exception as e:
        return ["Error", "Error", f"Error retrieving data: {e}"]


def construct_finviz_url(filters,view_mode = 111):
    base_url = "https://finviz.com/screener.ashx"
    query_params = {
        'v': view_mode,       # View mode (e.g., 111 for descriptive view)
        'f': ','.join(filters)  # Comma-separated filters
    }
    
    # Construct the full URL
    full_url = f"{base_url}?{urlencode(query_params)}"
    return full_url


def sample(tl, ticker):
    print(tl)
    def getIndex(l, ticker):
        # Find the index of the ticker in the list
        for index, value in enumerate(l):
            if value == ticker:
                return index
        return None  # Return None if the ticker is not found
    n = getIndex(tl, ticker)

    if n is None:
        tl.append(ticker)
        n = len(tl)-1

    # Determine the slice bounds to get 10 tickers
    start = max(0, n - 4)
    end = min(len(tl), n + 5)
    result = tl[start:end]

    # Pad the list if there aren't enough elements
    while len(result) < 10:
        if start > 0:  # Add elements to the front if possible
            start -= 1
            result = [tl[start]] + result
        elif end < len(tl):  # Add elements to the back if possible
            result.append(tl[end])
            end += 1
        else:
            break  # Exit if no more elements are available to pad
    if ticker in result:
        return result
    else:
        result.append(ticker)
        return result

def get_revenue(tickers):
    revenues = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        try:
            # Fetch the income statement
            income_statement = stock.financials
            
            # Get the revenue (total revenue) for the latest period
            latest_revenue = income_statement.loc['Total Revenue'].iloc[0]
            revenues[ticker] = latest_revenue
        except Exception as e:
            # Append None if there's an issue
            revenues.append({ticker: None})
    return revenues

def get_operating_margins(tickers):
    operating_margins = {}
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract operating margin
            margin = info.get('operatingMargins')
            if margin is not None:
                operating_margins[ticker] = margin * 100  # Convert to percentage
            else:
                operating_margins[ticker] = None  # Handle missing data
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            operating_margins[ticker] = None

    return operating_margins


def calculate_price_to_sales(tickers):
    ps_ratios = {}
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Fetch market capitalization and revenue
            market_cap = info.get('marketCap')  # Market capitalization
            total_revenue = info.get('totalRevenue')  # Total revenue
            
            # Calculate Price-to-Sales ratio
            if market_cap is not None and total_revenue is not None and total_revenue > 0:
                ps_ratios[ticker] = market_cap / total_revenue
            else:
                ps_ratios[ticker] = None  # Handle missing or invalid data
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            ps_ratios[ticker] = None
    
    return ps_ratios

def calculate_revenue_growth(tickers):
    growth_data = {}
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            # Fetch financials (Income Statement)
            financials = stock.financials
            
            # Extract revenue (Total Revenue is often labeled as 'Total Revenue')
            revenue = financials.loc['Total Revenue']
            
            # Convert revenue to a DataFrame for easier handling
            revenue = revenue.sort_index(ascending=True)  # Sort by date
            
            # Ensure there are at least 4 years of data for 3-year growth
            if len(revenue) < 4:
                growth_data[ticker] = {
                    '1_year_growth': None,
                    '3_year_growth': None
                }
                continue
            
            # Calculate 1-year and 3-year revenue growth
            one_year_growth = ((revenue[-1] - revenue[-2]) / revenue[-2]) * 100
            three_year_growth = ((revenue[-1] - revenue[-4]) / revenue[-4]) * 100
            
            # Store the data
            growth_data[ticker] = {
                '1_year_growth': one_year_growth,
                '3_year_growth': three_year_growth
            }
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            growth_data[ticker] = {
                '1_year_growth': None,
                '3_year_growth': None
            }
    return growth_data

def tabulate(tickers):
    ps=calculate_price_to_sales(tickers)
    om = get_operating_margins(tickers)
    growth = calculate_revenue_growth(tickers)
    r= get_revenue(tickers)

    data=[]
    for ticker, metric_value in om.items():
        mc = yf.Ticker(ticker).info.get('marketCap')  # Market capitalization
        data.append({
            'Ticker': ticker,
            'operating_margins': metric_value,
            'ps':ps[ticker],
            'revenue':r[ticker],
            '1YearGrowth': growth[ticker]['1_year_growth'],
            '3YearGrowth': growth[ticker]['3_year_growth'],
            'mc' : readable(mc)
        })
    return data



def rank(data):
    rankedData = data.copy()
    keys_to_rank = [key for key in rankedData[0].keys() if key != 'Ticker']
    
    # Rank each metric
    for key in keys_to_rank:
        # Sort the data by the current key
        sorted_data = sorted(rankedData, key=lambda x: x[key], reverse=True)
        
        # Assign rankings
        for rank, item in enumerate(sorted_data, 1):
            item[f"{key}_rank"] = rank
    
    # Pair value with its rank for each metric
    for item in rankedData:
        for key in keys_to_rank:
            item[key] = (item[key], item[f"{key}_rank"])
    
    # Remove the extra rank fields to clean up
    for item in rankedData:
        for key in keys_to_rank:
            del item[f"{key}_rank"]
    return rankedData
    


