# Market-Making-Game-Practice
This is just a simple practice game that I made that should help simulate market-making to practice your spreads and estimates
## Settings Guide:

- **Fermi/EV**: 
   - If you use Fermi, it will generate a random Fermi question from a word bank. You can modify on this on your own if there are other other combinations you would like, under the fermi() function.
   -EV will give you a dice or cards option to practice the range and distribution of the product/sum of dice/cards, respectively.
   
- **Choose a Number of Trades**:
   - If you use random, you will get a random number of trades that you execute, by default set from 5-10, but you can of course change this (line 235)
   - Net position will allow unlimited trades as so long as your net position doesn't become too many short or long.  
- **To play**:
   - After determining your settings, press Start Game. It should give you a line of the instructions, as well as your number of trades/net position, a dropdown with the computer value (if you want it for some reason), as well as the containers for the trade process.
   - Once the trades are done, calculate your position/your max loss, which, depending on your trades, can occur in the bottom or top of the range of values. Click Reset Game to start over.

