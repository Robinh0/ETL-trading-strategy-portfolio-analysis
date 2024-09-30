import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def camel_to_snake_case(input):
    return input.lower().replace(" ", "_")


def get_csv_files(strategy_folder_name):
    current_directory = os.getcwd()
    subdirectory = os.path.join(
        current_directory, 'tradingview_backtests', strategy_folder_name)
    all_files = os.listdir(subdirectory)
    csv_files = [file for file in all_files if file.endswith('.csv')]
    return csv_files


def create_and_merge_dataframes(selected_columns):
    def create_open_and_close_dates(df):
        rows_to_drop = []
        for i in range(1, len(df)):
            if df.loc[i, 'type'] == 'Exit Long':
                df.loc[i, 'starting_date'] = df.loc[i+-1, 'date/time']
                df.loc[i, 'ending_date'] = df.loc[i, 'date/time']
            else:
                rows_to_drop.append(i)
        df = df.drop(rows_to_drop)
        df = df.dropna(subset=['ending_date'])
        df = df.reset_index(drop=True)
        return df

    dataframes = []
    for file in csv_files:
        df = pd.read_csv(
            f"tradingview_backtests/{STRATEGY_FOLDER_NAME}/{file}")
        df.columns = [camel_to_snake_case(column) for column in df.columns]
        df['symbol'] = file.split('.')[0]
        df['cum_bankroll'] = None
        df = create_open_and_close_dates(df)
        df['profit_%'] = (df['profit_%'] / 100).astype(float)
        new_df = df[selected_columns]
        dataframes.append(new_df)
    df = pd.concat(dataframes, ignore_index=True).sort_values(
        by='starting_date').reset_index(drop=True)

    df['trade_skipped'] = False
    df['counter'] = 0
    df['counter_reset'] = None
    df['max_trades'] = MAX_TRADES

    df = create_first_row_starting_bankroll(
        df=df, columns=selected_columns)
    return df


def create_first_row_starting_bankroll(df, columns):
    # Create a dictionary for all columns
    data = {column: None for column in columns}
    data['cum_bankroll'] = STARTING_BANKROLL  # Set cum_bankroll to 30000
    df_first_row = pd.DataFrame([data])  # Create DataFrame with one row
    df = pd.concat([df_first_row, df], ignore_index=True)
    df.loc[0, 'trade_skipped'] = None
    return df


def calculate_cum_bankroll(df, pct_capital_per_trade):
    for i in range(1, len(df)):
        previous_bankroll = df.loc[i-1, 'cum_bankroll']
        profit_percent = df.loc[i, 'profit_%']
        trade_skipped = df.loc[i, 'trade_skipped']
        if (trade_skipped == "insufficient_buying_power") or (trade_skipped == "counter_skip_trade"):
            cum_bankroll = previous_bankroll
        else:
            cum_bankroll = (previous_bankroll + (previous_bankroll *
                            (profit_percent) * pct_capital_per_trade))
        df.loc[i, 'cum_bankroll'] = cum_bankroll
    df['cum_bankroll'] = round(df['cum_bankroll'].astype(float), 0)
    return df


def calculate_n_open_trades(df):
    for i in range(0, len(df)):
        n_open_trades = len(df[(df['starting_date'] <= df.loc[i, 'starting_date']) & (
            df["ending_date"] >= df.loc[i, 'ending_date']) & (df['trade_skipped'] == False)])
        if n_open_trades > MAX_TRADES:
            n_open_trades = MAX_TRADES
            df.loc[i, 'trade_skipped'] = 'insufficient_buying_power'
        df.loc[i, 'n_open_trades'] = n_open_trades
    return df


def create_max_drawdown_column(df):
    for i in range(0, len(df)):
        highest_bankroll = df['cum_bankroll'][:i+1].max()
        current_bankroll = df.loc[i, 'cum_bankroll']
        drawdown = ((highest_bankroll - current_bankroll) /
                    highest_bankroll) * -1
        # Store the highest high up to row i
        df.loc[i, 'highest_high'] = highest_bankroll
        df.loc[i, 'max_drawdown'] = round(drawdown, 2)
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
        counter = previous_counter + 1
        if profit > 0:
            df.loc[i, 'counter_reset'] = True
        df.loc[i, 'counter'] = counter
        if counter > MAX_COUNTER_VALUE:
            df.loc[i, 'trade_skipped'] = 'counter_skip_trade'
    return df


def create_subplots(df):
    """
    Creates plots with the logarithmic cum_bankroll on the left y axis, and the max_drawdown on the right y axis.
    """
    # Create a new figure and axis for the cum_bankroll
    fig, ax1 = plt.subplots()

    # Plot cum_bankroll with a logarithmic scale on the primary y-axis
    ax1.plot(df['ending_date'], df['cum_bankroll'], marker='o',
             color='b', linestyle='-', label='Cumulative Bankroll')
    ax1.set_xlabel('Ending Date')
    ax1.set_ylabel('Cumulative Bankroll (Log Scale)', color='b')
    ax1.set_yscale('log')
    ax1.tick_params(axis='y', labelcolor='b')

    # Create a twin y-axis for max_drawdown on the same plot
    ax2 = ax1.twinx()  # This creates a new y-axis that shares the same x-axis
    ax2.plot(df['ending_date'], df['max_drawdown'], marker='x',
             color='r', linestyle='--', label='Max Drawdown')
    ax2.set_ylabel('Max Drawdown', color='r')
    ax2.tick_params(axis='y', labelcolor='r')

    # Add grid and titles
    plt.title('Cumulative Bankroll and Max Drawdown Over Time')
    ax1.grid(True)
    plt.savefig(
        f'bankroll_pctCap_{PCT_OF_CAPITAL_PER_TRADE}_maxCounter_{MAX_COUNTER_VALUE}.png', format='png', dpi=300)


def create_cum_bankroll_plot(df):
    plt.plot(df['ending_date'], df['cum_bankroll'], marker='o',
             color='b', linestyle='-', label='Cumulative Bankroll')
    plt.title('Cumulative Bankroll Over Time')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Bankroll')
    plt.yscale('log')
    plt.grid(True)
    plt.legend()
    plt.savefig(
        f'cum_bankroll_pctCap_{PCT_OF_CAPITAL_PER_TRADE}_maxCounter_{MAX_COUNTER_VALUE}.png', format='png', dpi=300)


def remove_first_placeholder_row(df):
    return df[1:]


# CONSTANTS
STARTING_BANKROLL = 1000
MARGIN_FACTOR = 4
MAX_COUNTER_VALUE = 20
SELECTED_COLUMNS_START = [
    'symbol', 'type', 'starting_date', 'ending_date', 'profit_%', 'cum_bankroll']

# STRATEGY_FOLDER_NAME = 'fib_dynamic'
STRATEGY_FOLDER_NAME = 'quant_program'

csv_files = get_csv_files(STRATEGY_FOLDER_NAME)
result_dataframes = []

for i in np.arange(0.25, 4.25, 0.25):
    PCT_OF_CAPITAL_PER_TRADE = i
    MAX_TRADES = int(MARGIN_FACTOR / PCT_OF_CAPITAL_PER_TRADE)

    df = create_and_merge_dataframes(SELECTED_COLUMNS_START)
    df = calculate_counter(df)
    df = calculate_n_open_trades(df)
    df = calculate_cum_bankroll(
        df, pct_capital_per_trade=PCT_OF_CAPITAL_PER_TRADE)
    df = create_max_drawdown_column(df)
    df = remove_first_placeholder_row(df)

    # Prints
    print("\nFirst 50 rows:")
    print(df[:50])
    print("\nHead and tail of df:")
    print(df)

    # Exports
    df.to_csv(
        f'results/df_pctCap_{PCT_OF_CAPITAL_PER_TRADE}_maxCounter_{MAX_COUNTER_VALUE}.csv')
    # create_subplots(df)

    # Create result_df with a single row
    result_df = pd.DataFrame([{
        'starting_bankroll': STARTING_BANKROLL,
        'ending_bankroll': df.iloc[-1]['cum_bankroll'],
        'max_drawdown': min(df['max_drawdown']),
        'pct_capital_per_trade': PCT_OF_CAPITAL_PER_TRADE,
        'max_counter': MAX_COUNTER_VALUE,
        'margin_factor': MARGIN_FACTOR,
        'max_open_trades': MAX_TRADES,
    }])
    result_dataframes.append(result_df)
    # print(result_df)

results = pd.concat(result_dataframes, ignore_index=True)
results.to_csv('results/results.csv')
