# Trading-bot-portfolio-analysis-with-pandas

This is an ETL pipeline that I created to analyse the backtests of two individual stock trading strategies, when applied to a portfolio of stocks. The goal was 1) to compare the outcome the strategies in pct gain (from 2000 to 2024) and drawdown percentage and 2) to find the optimal position size settings whilst maintaining an acceptable drawdown.

The tool also allowed me to find the optimal setting for the "max_counter_losing_trade_sequence" variable, which is around 20.

**Input**
A list of .csv exports from Tradingview, for both trading strategies.

**Output**
A .csv file with the columns: starting_bankroll, ending_bankroll (hidden for privacy reasons), max_drawdown, pct_capital_per_trade, max_counter, margin_factor	max_open_trades.

![image](https://github.com/user-attachments/assets/a59815a2-aedb-4e0f-97f5-0af6ab3c1858)

