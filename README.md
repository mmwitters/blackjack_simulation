# Blackjack Simulation Project

All python files used to generate and run this simulation are included in this folder.
If testing the simulation, note that running all 15,000 replications can take upwards of 30 minutes on your machine. 
The following three python files are necessary to load in order to run the simulation: cards.py, blackjack.py, simulation.py.

## How to Run
Project requires at least Python 3.9 and pip for dependencies
### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Code
```bash
python simulation.py
```


## Domain Summary
* cards.py: this file includes the Card and Deck classes. It also included methods such as shuffle and draw_card.
* cards_test.py: this file has unit-tests for the cards file. This file is not necessary to run the program.
* blackjack.py: this file contains classes unique to the game of Blackjack, such as BettingBox and Hand, and also includes functions necessary for game play, such as dealer_moves and hand_result.
* blackjack_test.py: this file has unit-tests for the blackjack file. This file is not necessary to run the program.
* simulation.py: this file contains the code for all 6 strategies tested. It also has the code used to generate statistics for each strategy, write the results to a csv, and generate unique histograms. 
* results.csv: this is the csv file that was generated from my final run of the simulation, and contains all the statistics referenced in the report. 
