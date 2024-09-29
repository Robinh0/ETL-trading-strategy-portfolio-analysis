import os
import pandas as pd

def camel_to_snake_case(input):
    return input.lower().replace(" ", "_")


def get_csv_files():
    current_directory = os.getcwd()
    all_files = os.listdir(current_directory)
    csv_files = [file for file in all_files if file.endswith('.csv')]
    return csv_files


def create_and_merge_dataframes(selected_columns):
    def create_open_and_close_dates(df):
        rows_to_drop = []
        for i in range(1, len(df)):
            if df.loc[i, 'type'] == 'Exit Long':
                df.loc[i, 'starting_date'] = df.loc[i+1, 'date/time']
                df.loc[i, 'ending_date'] = df.loc[i, 'date/time']
            else:
                rows_to_drop.append(i)
        df = df.drop(rows_to_drop)
        df = df.dropna(subset=['ending_date'])
        df = df.reset_index(drop=True)
        return df
    
    dataframes = []
    for file in csv_files:
        df = pd.read_csv(f"{file}")
        df.columns = [camel_to_snake_case(column) for column in df.columns]
        df['symbol'] = file.split('.')[0]
        df['cum_bankroll'] = None
        df = create_open_and_close_dates(df)
        df['profit_%'] = (df['profit_%'] / 100).astype(float)
        new_df = df[selected_columns]
        dataframes.append(new_df)
    df = pd.concat(dataframes, ignore_index=True).sort_values(by='starting_date').reset_index(drop=True)
    return df

def create_first_row_starting_bankroll(df, columns):
    data = {column: None for column in columns}  # Create a dictionary for all columns
    data['cum_bankroll'] = INITIAL_BANKROLL  # Set cum_bankroll to 30000
    df_first_row = pd.DataFrame([data])  # Create DataFrame with one row
    df = pd.concat([df_first_row, df], ignore_index=True)
    return df


def calculate_cum_bankroll(df, pct_capital_per_trade):
    for i in range(1, len(df)):
        previous_bankroll = df.loc[i-1, 'cum_bankroll']
        profit_percent = df.loc[i, 'profit_%']
        trade_skipped = df.loc[i, 'trade_skipped']
        if (trade_skipped == "insufficient_buying_power"):
        # if (trade_skipped == False):
            cum_bankroll = previous_bankroll
        elif (trade_skipped == "counter_skip_trade"):
            cum_bankroll = previous_bankroll
        else:
            cum_bankroll = (previous_bankroll + (previous_bankroll * (profit_percent) * pct_capital_per_trade))
        df.loc[i, 'cum_bankroll'] = cum_bankroll
    df['cum_bankroll'] = df['cum_bankroll'].astype(int) 
    return df

def calculate_max_n_open_trades(df):
    # df['trade_skipped'] = None
    for i in range(0, len(df)):
        # current_bankroll = df.loc[i, 'cum_bankroll']
        n_open_trades = len(df[(df['starting_date'] <= df.loc[i, 'starting_date']) & (df["ending_date"] >= df.loc[i, 'ending_date']) & (df['trade_skipped'] == False)])
        if n_open_trades * PCT_OF_CAPITAL_PER_TRADE > MARGIN_FACTOR:
            # n_open_trades = min((n_open_trades * PCT_OF_CAPITAL_PER_TRADE), MARGIN_FACTOR)
            n_open_trades = int((MARGIN_FACTOR) / (PCT_OF_CAPITAL_PER_TRADE))
            df.loc[i, 'trade_skipped'] = 'insufficient_buying_power'
            df.loc[i, 'profit_%'] = df.loc[i, 'profit_%'] / 1
        df.loc[i, 'max_n_open_trades'] = n_open_trades
    return df


def create_max_drawdown_column(df):
    for i in range(0, len(df)):
        highest_bankroll = df['cum_bankroll'][:i+1].max()
        current_bankroll = df.loc[i, 'cum_bankroll']
        drawdown = ((highest_bankroll - current_bankroll) / highest_bankroll) * -1
        df.loc[i, 'highest_high'] = highest_bankroll  # Store the highest high up to row i
        df.loc[i, 'max_drawdown'] = round(drawdown,2)
    return df


def calculate_counter(df):
    df['counter'] = 0
    df['counter_reset'] = None
    for i in range(1, len(df)):
        if df.loc[i-1, 'counter_reset'] == True:
            previous_counter = 0
        else:
            previous_counter = df.loc[i-1, 'counter']
        profit = df.loc[i, 'profit_%']
        counter = previous_counter +1
        if profit > 0:
            df.loc[i, 'counter_reset'] = True
        df.loc[i, 'counter'] = counter
        if counter > MAX_COUNTER_VALUE:
            df.loc[i, 'trade_skipped'] = 'counter_skip_trade'
    return df


# CONSTANTS
INITIAL_BANKROLL = 100
MARGIN_FACTOR = 4
PCT_OF_CAPITAL_PER_TRADE = 1
MAX_COUNTER_VALUE = 50
SELECTED_COLUMNS_START = ['symbol', 'type', 'starting_date', 'ending_date', 'profit_%', 'cum_bankroll']

csv_files = get_csv_files()

df = create_and_merge_dataframes(SELECTED_COLUMNS_START)

df['trade_skipped'] = False
df.loc[0, 'trade_skipped'] = None
df.loc[1, 'trade_skipped'] = False
df['counter'] = 0
df['counter_reset'] = None

df = create_first_row_starting_bankroll(df=df, columns=SELECTED_COLUMNS_START)
df = calculate_counter(df)
df = calculate_max_n_open_trades(df)

df = calculate_cum_bankroll(df, pct_capital_per_trade=PCT_OF_CAPITAL_PER_TRADE)
# df = create_max_drawdown_column(df)


# PRINT STATEMENT
print("\nFinal print statement:")
print(df[:50])

print(df)