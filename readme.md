# Scraper Airbnb

This scraper takes all requests made for a search in  the Airbnb website, and identify the URL that bring the data that will render on the result view.
This data contains aditional information that could be used for an Data Analisys.


## Install


1. Create an virtual enviroment for python 3.6+ activate it and run `pip install -r requirements.txt`
2. Require to install a proxy server to catch this requests, Install Browsemob Proxy from here https://bmp.lightbody.net/ and create and env variable called `BROWSERMOB_PATH`
with the binary path for the downloaded Proxy 
3. Download a chromedriver for Selenium and create a env path variable, check `https://googlechromelabs.github.io/chrome-for-testing/#stable` for compatibility drivers.


## Running the scraper

You can make a search on you browsert and get the URL to analyse that search replacing in the base url.

```
python baseproxy.py
```

You can repeat the search for all urls its desired and this generates csv files, to can make a preview filter can concatenate this results use the following:

```
python filter_files.py
```


## Configuration

`BROWSERMOB_PATH` - Path for Proxy server (`..\browsermob-proxy\bin\browsermob-proxy`)

`CHROMEDRIVER_PATH` - Path for CHROMEDRIVER
