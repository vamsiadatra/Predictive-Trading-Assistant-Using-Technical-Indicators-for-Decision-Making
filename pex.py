import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Download EUR/INR data
start_date = "2023-01-01"
end_date = "2023-12-07"
eurinr_data = yf.download("EURINR=X", start=start_date, end=end_date)

# Function to calculate technical indicators
def technical_indicators(data, window=20):
    # Calculate typical price
    typical_price = (data["High"]+data["Low"]+data["Close"])/3

    # Calculate moving average
    ma = data["Close"].rolling(window=window).mean()
    ma = ma.bfill()

    # Calculate standard deviation
    std = data["Close"].rolling(window=window).std()
    std = std.bfill()

    # Calculate Bollinger Bands
    upper_band = ma + 2 * std
    lower_band = ma - 2 * std

    #typical_price = (data + data + data)/3

    # Calculate mean deviation
    x = (typical_price.rolling(window = window).mean()).bfill()
    mean_deviation = (abs(typical_price - x).rolling(window = window).mean()).bfill()

    # Calculate CCI
    cci = (typical_price - x) / (0.015 * mean_deviation)

    # Combine data into a DataFrame
    metrics = pd.DataFrame(
        {
            "High": data["High"],
            "Low":data["Low"],
            "Close": data["Close"],
            "TypicalPrice":typical_price,
            "MA": ma,
            "Std": std,
            "Upper_Band": upper_band,
            "Lower_Band": lower_band,
            "CCI": cci,
        }
    )
    return metrics


# Calculating technical indicators using the entire dataset
all_data_metrics = technical_indicators(eurinr_data)
#print(all_data_metrics.head(10))
# Function for decision making
def decisionMaking():
    # seperating data for analysis
    one_day_metrics = all_data_metrics.tail(1)
    one_week_metrics = all_data_metrics.tail(6)

    # defining some additional values for decision making
    current_portfolio_value = 10000
    additional_indicator_threshold = 1000
    additional_indicator_value = 1500

    # setting bullish and bearish thresholds
    bullish_threshold = 0
    bearish_threshold = 0

    # counting bullish and bearish counts
    bullish_count = len(all_data_metrics[all_data_metrics['CCI'] > bullish_threshold])
    bearish_count = len(all_data_metrics[all_data_metrics['CCI'] < bearish_threshold])

    # Determine trend prediction effectiveness based on historical signals
    total_count = bullish_count + bearish_count
    if total_count == 0:
        print("Insufficient historical data for trend prediction.")
    else:
        bullish_percentage = (bullish_count / total_count) * 100
        bearish_percentage = (bearish_count / total_count) * 100

        # Assessing the effectiveness of indicators
        if bullish_percentage > bearish_percentage:
            print(f"\nBullish trend expected based on historical signals: {bullish_percentage:.2f}% bullish signals")
        elif bearish_percentage > bullish_percentage:
            print(f"Bearish trend expected based on historical signals: {bearish_percentage:.2f}% bearish signals")
        else:
            print("No clear trend based on historical signals.")

        additional_indicator_value = 1  # some additional indicator value for decision-making
        additional_indicator_threshold = 0  # threshold for the additional indicator

        # thresholds for decision-making based on indicators
        ma_upcoming_day = one_day_metrics['MA'].iloc[-1]
        cci_upcoming_day = one_day_metrics['CCI'].iloc[-1]
        week_cci_mean = one_week_metrics['CCI'].mean()

        # Risk management considerations
        risk_tolerance = 0.05  # risk tolerance level (5% in this case)

        # decision criteria incorporating multiple indicators, sentiment analysis, and risk management
        buy_condition = (
            ma_upcoming_day >= all_data_metrics['MA'].iloc[-1] and
            cci_upcoming_day > 0 and
            week_cci_mean > 0 and
            additional_indicator_value > additional_indicator_threshold and
            bullish_percentage > 50  # Buy if bullish sentiment is high (adjust threshold)
        )

        sell_condition = (
            ma_upcoming_day < all_data_metrics['MA'].iloc[-1] and
            cci_upcoming_day < 0 and
            week_cci_mean < 0 and
            additional_indicator_value < additional_indicator_threshold and
            bearish_percentage > 45  # Sell if bearish sentiment is high (adjust threshold)
        )

        # Apply risk management - determine position size based on risk tolerance
        if buy_condition:
            position_size = risk_tolerance * current_portfolio_value  # Adjust position size based on risk tolerance
            decision = "BUY"
        elif sell_condition:
            position_size = risk_tolerance * current_portfolio_value  # Adjust position size based on risk tolerance
            decision = "SELL"
        else:
            position_size = 0  # No position if conditions are not met
            decision = "NEUTRAL"

        # Display decision, sentiment analysis, and position size
        print(f"\n MA for upcoming day: {ma_upcoming_day}\n CCI for upcoming day: {cci_upcoming_day}\n Week CCI mean: {week_cci_mean}\n")

        print("Decision for the upcoming day and week:", decision)
        print(f"Bullish Percentage: {bullish_percentage:.2f}%")
        print(f"Bearish Percentage: {bearish_percentage:.2f}%")
        print("Position size:", position_size)

###########################################################PLOTTINGG###########################################################################
# Function for plotting: 
def plots():
    dates_as_strings = [str(date) for date in all_data_metrics.index.date]
    #1. EUR/INR data raw
    plt.figure(figsize=(8, 6))  # Define the size of the figure
    plt.plot(eurinr_data["Close"].index, eurinr_data["Close"].values)
    plt.title('Figure 1 - EUR/INR Closing Prices')
    plt.xlabel('Date')
    plt.ylabel('Closing Price')
    plt.grid(True)
    plt.show()  # Display the first figure

    #2. histogram of EUR/INR data
    plt.figure(figsize=(8, 6))  # Define the size of the figure
    plt.hist(eurinr_data["Close"].values, bins=20, color='orange')
    plt.title('Figure 2 - Histogram of EUR/INR Closing Prices')
    plt.xlabel('Closing Price')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.show()  # Display the second figure

    #3. MA and BB
    plt.figure(figsize=(10, 6))
    plt.plot(dates_as_strings, all_data_metrics["Upper_Band"], marker='o', label="MA Upper Band")
    plt.plot(dates_as_strings, all_data_metrics["MA"], marker='o', label='Historical MA')
    plt.plot(dates_as_strings, all_data_metrics["Lower_Band"], marker='o', label="MA Lower Band")
    plt.plot(dates_as_strings, all_data_metrics["Close"])
    plt.xlabel('Dates')
    plt.ylabel('MA Values')
    plt.title('Moving Averages (MA)')
    plt.legend()
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

    #4. CCI Values
    plt.figure(figsize=(10, 6))
    plt.plot(dates_as_strings, all_data_metrics["CCI"], marker='o', label="Historical CCI")
    plt.xlabel('Dates')
    plt.ylabel('CCI Values')
    plt.title('CCI')
    plt.legend()
    plt.xticks(rotation=90)
    plt.show()


# decision Making
decisionMaking()

# ploltting
plots() 