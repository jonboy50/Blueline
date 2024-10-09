import pandas as pd
import yfinance as yf

# Function to calculate Bollinger Bands %B
def calc_bbp(data, length=20, mult=2, smooth_length=3):
    basis = data['Close'].rolling(window=length).mean()
    dev = mult * data['Close'].rolling(window=length).std()
    upper_band = basis + dev
    lower_band = basis - dev
    bbp = (data['Close'] - lower_band) / (upper_band - lower_band) * 100
    smoothed_bbp = bbp.ewm(span=smooth_length).mean()  # EMA smoothing
    return smoothed_bbp

# Function to download data for a specific timeframe and calculate BB%
def get_bbp_for_timeframe(pair, interval, periods=100):
    data = yf.download(pair, period="3mo", interval=interval)
    if data.empty:
        return None
    return calc_bbp(data)

# Function to check if BB% is overbought or oversold in two timeframes
def find_overbought_oversold_pairs(base_currency, compare_currencies):
    overbought_oversold_pairs = []

    # Define timeframes (e.g., 4-hour, daily, weekly)
    timeframes = {"4h": "1h", "daily": "1d", "weekly": "1wk"}

    for base in compare_currencies:
        for compare in compare_currencies:
            if base != compare:
                pair = base + compare + "=X"

                # Download and calculate BB% for each timeframe
                bbp_4h = get_bbp_for_timeframe(pair, timeframes['4h'])
                bbp_daily = get_bbp_for_timeframe(pair, timeframes['daily'])
                bbp_weekly = get_bbp_for_timeframe(pair, timeframes['weekly'])

                if bbp_4h is not None and bbp_daily is not None and bbp_weekly is not None:
                    # Check if any two timeframes are in overbought/oversold regions
                    is_overbought_4h = bbp_4h.iloc[-1] > 80
                    is_oversold_4h = bbp_4h.iloc[-1] < 20
                    is_overbought_daily = bbp_daily.iloc[-1] > 80
                    is_oversold_daily = bbp_daily.iloc[-1] < 20
                    is_overbought_weekly = bbp_weekly.iloc[-1] > 80
                    is_oversold_weekly = bbp_weekly.iloc[-1] < 20

                    if (is_overbought_4h and is_overbought_daily) or (is_oversold_4h and is_oversold_daily):
                        overbought_oversold_pairs.append((pair, "4h & Daily"))
                    elif (is_overbought_daily and is_overbought_weekly) or (is_oversold_daily and is_oversold_weekly):
                        overbought_oversold_pairs.append((pair, "Daily & Weekly"))
                    elif (is_overbought_4h and is_overbought_weekly) or (is_oversold_4h and is_oversold_weekly):
                        overbought_oversold_pairs.append((pair, "4h & Weekly"))

    return overbought_oversold_pairs

if __name__ == "__main__":
    compare_currencies = ['USD', 'GBP', 'AUD', 'CAD', 'CHF', 'EUR', 'NZD', 'JPY']
    overbought_oversold = find_overbought_oversold_pairs('USD', compare_currencies)

    if overbought_oversold:
        for pair, timeframes in overbought_oversold:
            print(f"Pair {pair} is in overbought/oversold condition on {timeframes}.")
    else:
        print("No pairs found in overbought/oversold conditions.")
