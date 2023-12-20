This set of scripts is used to monitor your wealth (or lack thereof), by scraping your bank and credit card details
from the web every day and making neat graphs.

Usage
-----
* **dependencies**: run `pip install -r requirements.txt` to install required dependencies.
* **configuration**: The file `config.ini` contains the configuration for the scripts.
  * Edit the bank and credit sections: set the bank and credit card sites you are using, and set the username and
  password for each. See assets.md for a list of supported banks and credit cards.
  * Edit `data_file_path` to select the path for the csv file with the collected data.
 For example, I store the csv log on my Google Drive.
* **run data collection**: Use "cron" to run "bank_csv.py" every day at a specified hour, e.g.
`0 21 * * * cd /home/kodi/BankMonitor && /usr/bin/python bank_csv.py`
* **run server**: Run `web.py` to open a server at the address and port specified in `config.ini`.
The default is at `localhost:7070` (not bound to `0.0.0.0` so only you can access the page).
The server parses the csv file and displays a graph with the collected data, along with summaries and controls.
