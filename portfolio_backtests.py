import os
import pandas as pd

def get_csv_files():
    current_directory = os.getcwd()
    all_files = os.listdir(current_directory)
    csv_files = [file for file in all_files if file.endswith('.csv')]
    return csv_files

def merge_dataframes():
    dataframes = []
    for file in csv_files:
        df = pd.read_csv(f"{file}")
        df['Symbol'] = file.split('.')[0]
        df = df[df['Type'] == 'Exit Long']
        df['Profit %'] = (df['Profit %'] / 100).astype(float)
        new_df = df[['Symbol', 'Type', 'Date/Time', 'Profit %']]
        dataframes.append(new_df)
    return dataframes

initial_bankroll = 30000
csv_files = get_csv_files()
print(csv_files)

dataframes = merge_dataframes()

portfolio_df = pd.concat(dataframes, ignore_index=True).sort_values(by='Date/Time').reset_index(drop=True)
portfolio_df.loc[0, 'Cum Bankroll'] = initial_bankroll + (initial_bankroll * portfolio_df.loc[0, 'Profit %'])

for i in range(1, len(portfolio_df)):
    previous_bankroll = portfolio_df.loc[i - 1, 'Cum Bankroll']
    profit_percent = portfolio_df.loc[i, 'Profit %']
    portfolio_df.loc[i, 'Cum Bankroll'] = previous_bankroll + (previous_bankroll * (profit_percent))

portfolio_df['Cum Bankroll'] = portfolio_df['Cum Bankroll'].astype(int) 

def create_max_drawdown_column(portfolio_df):
    def calculate_row_0(portfolio_df):
        cum_bankroll_row_0 = portfolio_df.loc[0, 'Cum Bankroll']
        if cum_bankroll_row_0 <= initial_bankroll:
            difference = (cum_bankroll_row_0 - initial_bankroll)
            if difference < 0:
                portfolio_df.loc[0, 'Max Drawdown'] = (difference/initial_bankroll)
                pass
            print(difference)
        else:
            portfolio_df.loc[0, 'Max Drawdown'] = 0
        portfolio_df.loc[0, 'Highest High'] = max(cum_bankroll_row_0, initial_bankroll)
        return portfolio_df
    
    def calculate_remaining_rows(portfolio_df):
        for i in range(0, len(portfolio_df)):
            highest_bankroll = portfolio_df['Cum Bankroll'][:i+1].max()
            current_bankroll = portfolio_df.loc[i, 'Cum Bankroll']
            drawdown = ((highest_bankroll - current_bankroll) / highest_bankroll) * -1
            portfolio_df.loc[i, 'Highest High'] = highest_bankroll  # Store the highest high up to row i
            portfolio_df.loc[i, 'Max Drawdown'] = round(drawdown,2)
        return portfolio_df
    
    portfolio_df = calculate_row_0(portfolio_df)
    portfolio_df = calculate_remaining_rows(portfolio_df)
    return portfolio_df

portfolio_df = create_max_drawdown_column(portfolio_df)

print(portfolio_df)