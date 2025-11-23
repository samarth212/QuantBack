import pandas as pd


def calculate_sma_series(closes, window):
    sma = [None] * len(closes)
    running_sum = 0.0

    for i, price in enumerate(closes):
        running_sum += price
        if i >= window:
            running_sum -= closes[i - window]
        if i >= window - 1:
            sma[i] = running_sum / window

    return sma
    
def simulate_trading_strategy(closes, short_window, long_window, capital, open_price):

    if capital < open_price:
        raise ValueError("Capital is too low to buy one share of this stock.")
    
    cash = capital
    equity_curve = [capital] * len(closes)
    trades = [None] * len(closes)
    shares = 0.0

    short_sma = calculate_sma_series(closes, short_window)
    long_sma = calculate_sma_series(closes, long_window)

    for i in range(long_window, len(closes)):

        if short_sma[i] is None or long_sma[i] is None:
            continue

        diff = short_sma[i] - long_sma[i]
        prev_diff = short_sma[i-1] - long_sma[i-1]

        # buy condition
        if shares == 0 and diff > 0 and prev_diff <= 0:
            shares = cash/closes[i]
            cash = 0
            trades[i] = {"side": "BUY", "price": closes[i]}
        # sell condition
        elif shares > 0 and diff < 0 and prev_diff >= 0:
            cash = shares * closes[i]
            shares = 0
            trades[i] = {"side": "SELL", "price": closes[i]}

        # add portfolio value
        equity_curve[i] = cash + shares * closes[i]
    
    
    return equity_curve, trades

    


def main() -> None:
    
    short_window = 20
    long_window = 50

    df = pd.read_csv("data/NVDA_1YR.csv")
    closes = df["Close"].to_list()
    open_price = df["Open"][0]

    equity, trades = simulate_trading_strategy(closes, short_window, long_window, 190, open_price)

    print(f"Final equity: {equity[-1]:.2f}")
    print("Trades taken:", [t for t in trades if t is not None])


if __name__ == "__main__":
    main()