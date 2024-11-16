# Trading-bot-portfolio-analysis-with-pandas

This is an ETL pipeline that I created to analyse the backtests of two individual stock trading strategies, when applied to a portfolio of stocks. The goal was 1) to compare the outcome the strategies in pct gain (from 2000 to 2024) and drawdown percentage and 2) to find the optimal position size settings whilst maintaining an acceptable drawdown.

The tool also allowed me to find the optimal setting for the "max_counter_losing_trade_sequence" variable, which is around 20. After 20 sequent losses, the position sizing will be adjusted to 1 share, untill the first trade with profit re-occurs.


**Input**  
A list of .csv exports from Tradingview, for both trading strategies.


**Output**  
A .csv file with the columns: starting_bankroll, ending_bankroll (hidden below), max_drawdown, pct_capital_per_trade, max_counter, margin_factor	max_open_trades.


**Results**  
Below we see a comparison of the results with a position size of 0.25 (25%) of the total bankroll. From the images, we can see that the fib_dynamic strategy has slightly lower profits, but much less drawdown, being 17% as compared to 26% with the quant_program strategy. The fib_dynamic strategy with a position size of 0.5 would have (1682199511.0/6018042.0 = 290) times more profit than the 0.25 position size quant_program strategy, whilst having only 4% more drawdown (see tables below).

Therefore, it is my hypothesis that the fib_dynamic strategy with a position size of 0.5 (50%) total bankroll will outperform the quant_program strategy with a 0.25 (25%) of total bankroll, with the potential of having a slightly higher drawdown percentage.

**fib_dynamic_strategy with 0.25 (25%) position size**
![bankroll_pctCap_0 25_maxCounter_20](https://github.com/user-attachments/assets/bc8b866c-20d8-492c-99a9-dde17930e8f4)

**quant_program_strategy with 0.25 (25%) position size**
![bankroll_pctCap_0 25_maxCounter_20](https://github.com/user-attachments/assets/cc746b4d-83e0-406c-b98e-d2f031b3ea1a)

**fib_dynamic_strategy table with 0.5 (50%) of total bankroll row highlighted**
![image](https://github.com/user-attachments/assets/f4e98f61-5e3c-4457-a95d-7df7ba609a90)

**quant_program table with 0.25 (25%) of total bankroll row highlighted**
![image](https://github.com/user-attachments/assets/0f1ca197-6370-42a2-8878-3b28da520438)

