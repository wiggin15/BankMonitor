This set of scripts is used to monitor your wealth (or lack thereof), by scraping your bank and credit card details
from the web every day and making neat graphs.

###Usage
* **dependencies**: The scripts need *Flask* and *requests* to work
* **configuration**: There is a `config.ini` file with the entire configuration. You need to set your user name and
password for the bank and credit card sites, as well as the type (BankOtsar or BankLeumi for bank, CardCal or CardLeumi
for credit card).
* **csv path**: I store the csv log on my Google Drive, but you can change the path to the file which stores the data.
Edit `data_file_path` in the `config.ini` file.
* **run**: Run `bank_routine.py` to start collection. This script will call `bank.main` to collect the data and store
the values in the csv file, every day at 20:00. Run `web.py` to open a server at `localhost:7070` (not bound to
`0.0.0.0` so only you can access the page). The server parses the csv file and displays a graph with the collected data,
along with summaries and controls.