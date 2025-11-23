import pandas as pd

# sum of closed prices over the last 20 periods divided by 20
short_window = 20

# sum of closed prices over the last 50 periods divided by 50 
long_window = 50

def main() -> None:
    df = pd.read_csv("data/NVDA_3M.csv")
    print(df.head())


if __name__ == "__main__":
    main()