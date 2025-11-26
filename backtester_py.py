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
    
def simulate_trading_strategy(closes, short_window, long_window, capital, allocation_pct, fee_pct, slippage_bps, stop_loss_pct):

    cash = capital
    equity_curve = [capital] * len(closes)
    trades = [None] * len(closes)
    shares = 0.0
    entry_price = None

    slip = slippage_bps / 10000

    short_sma = calculate_sma_series(closes, short_window)
    long_sma = calculate_sma_series(closes, long_window)

    for i in range(long_window, len(closes)):

        if short_sma[i] is None or long_sma[i] is None:
            equity_curve[i] = cash + shares * closes[i]
            continue
        
        

        diff = short_sma[i] - long_sma[i]
        prev_diff = short_sma[i-1] - long_sma[i-1]

        buy_signal  = (prev_diff <= 0 and diff > 0)
        sell_signal = (prev_diff >= 0 and diff < 0)

        # stop loss sell
        if shares > 0 and entry_price is not None:
            if closes[i] < entry_price*(1-stop_loss_pct):
                sell_signal = True

        # buy condition
        if cash > 0 and buy_signal:

            invest = allocation_pct * cash
            buy_price = closes[i] * (1+slip)

            new_shares = invest / buy_price
            cash -= invest
            cash -= invest * fee_pct  # fee on buy

            shares += new_shares

            entry_price = buy_price
       
            trades[i] = {"i": i, "side": "BUY", "price": buy_price, "qty": new_shares}
            

        # sell condition
        elif shares > 0 and sell_signal:

            sell_price = closes[i] * (1 - slip)
            new_cash = shares * sell_price
            cash += new_cash
            cash -= new_cash * fee_pct  # fee on sell
            
            trades[i] = {"i": i, "side": "SELL", "price": sell_price, "qty": shares}

            shares = 0.0
            entry_price = None


        # add portfolio value
        equity_curve[i] = cash + shares * closes[i]
    
    
    return equity_curve, trades

def calculate_return(equity_curve):
    start = equity_curve[0]
    end = equity_curve[-1]
    return (end-start)/start

def calculate_win_rate(trades):
    wins = 0
    closed = 0
    open_buy_price = None

    for i in trades:
        if i["side"] == "BUY":
            if open_buy_price is None:
                open_buy_price = i["price"]

        elif i["side"] == "SELL":
            if open_buy_price is not None:
                closed += 1
                if i["price"] > open_buy_price:
                    wins += 1
                open_buy_price = None  

    return wins / closed if closed > 0 else 0.0

def calculate_avg_trade_return(trades):
    trade_returns = []
    closed = 0
    open_buy_price = None

    for i in trades:
        if i["side"] == "BUY":
            if open_buy_price is None:
                open_buy_price = i["price"]

        elif i["side"] == "SELL":
            if open_buy_price is not None:
                closed += 1
                trade_returns.append((i["price"] - open_buy_price)/open_buy_price)
                open_buy_price = None  

    
    return sum(trade_returns)/ closed if closed > 0 else 0.0


def calculate_mdd(equity_curve):

    max_price = equity_curve[0]
    mdd = 0.0

    for i in equity_curve:
        if i is None:
            continue
        if i > max_price:
            max_price = i
        dd = (i - max_price)/max_price
        if dd < mdd:
            mdd = dd

    return mdd

def calculate_profit_factor(trades):

    trade_returns = []
    closed = 0
    open_buy_price = None

    for i in trades:
        if i["side"] == "BUY":
            if open_buy_price is None:
                open_buy_price = i["price"]

        elif i["side"] == "SELL":
            if open_buy_price is not None:
                closed += 1
                trade_returns.append(i["price"] - open_buy_price)
                open_buy_price = None  

    profits = 0.0
    losses = 0.0
    
    for i in trade_returns:
        if i > 0:
            profits += i
        elif i < 0:
            losses += i

    if losses < 0:
        return profits / abs(losses)
    else:
        if profits > 0:
            return float("inf")
        else:
            return 0.0


def main() -> None:
    
    short_window = 20
    long_window = 50

    df = pd.read_csv("data/NVDA_1YR.csv")
    closes = df["Close"].to_list()

    equity, trades = simulate_trading_strategy(closes, short_window, long_window, 10000, 0.50, 0.001, 5, 0.08)

    print(f"Final equity: {equity[-1]:.2f}")
    print("Trades taken:", [t for t in trades if t is not None])


if __name__ == "__main__":
    main()