This set of scripts is used to monitor your wealth (or lack thereof), by scraping your bank and credit card details
from the web every day and making neat graphs.

###Usage
The usage is a little complicated because the scripts were designed for my own use.
* **dependencies**: The scripts need *Cherrypy* and *requests* to work
* **data collection**: You will pretty much have to rewrite bank.py for your needs. The current script collects data
from _bankotsar.co.il_ and _cal-online.co.il_, but the other scripts only need `bank.main` to return a list of values
that represent the different assets you own. For example, positive values for your savings account and stocks, and
negative values for loans and credit card transactions.
* **csv path**: I store the csv log on my Google Drive, but you can change the path to the file which stores the data.
Edit `web.get_path` to return this path.
* **create csv**: The scripts don't generate the csv file if it doesn't exist. You will have to create it (in the path
written in `web.get_path`) and write the first line yourself. The first line contains the value names, and must start
with `Date`, following with the names of the components that correspond to the values returned from `bank.main`. e.g.
if `bank.main` returns the values of your stocks and credit card, the csv should start with `Date,Stock,Credit`
* **run**: Run `bank_routine.py` to start collection. This script will call `bank.main` to collect the data and store
the values in the csv file, every day at 20:00. Run `web.py` to open a server at `localhost:7070` (not bound to `0.0.0.0` so only you can access the page). The server parses the csv file and displays a graph with the collected data, along with summaries and controls.