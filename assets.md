## Banks
The following banks can be defined in config.ini under `[bank]`
* BankOtsar
* BankLeumi
* BankDiscount
  * requires  *pycrypto* dependency
  * 'username' should be in format '\<user id\>,\<user code\>'
* BankBeinleumi
  * See Selenium section below for dependencies

## Credit Cards
The following credit card types can be defined in config.ini under `[card]`
* CardCal
  * See Selenium section below for dependencies
* CardLeumi
  * Only if the card is issued by Bank Leumi
* CardIsracard
  * 'username' should be in format '\<user id\>,\<user name\>'


## Selenium
Some assets require selenium to work properly.
The following is partial explanation on how to set it up.

* Install the "selenium" Python package (e.g. with pip or easy_install)
* Install FireFox (on Ubuntu, use `sudo apt-get install firefox-mozilla-build`)
* Install "geckodriver"
  * Download from https://github.com/mozilla/geckodriver/releases
  * On Ubuntu, untar and move to /usr/local/bin)
* To run selenium in a virtual display on Linux systems, install "xvfb" (e.g. with apt-get), and make sure xvfb will run on startup by configuring an init script and running update-rc.
