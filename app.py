import sys
import requests
import json
import time
import atexit
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

# Setting up logging to print to stdout
FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
log = logging.getLogger("bitcoin-logger")
log.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(FORMATTER)
log.addHandler(console_handler)

# Initializing Flask App
app = Flask(__name__)

# Save Bitcoin rate list into file
def saveRate(rateList):
    with open('rates', 'w+') as myfile:
        json.dump(rateList, myfile)

# Read Bitcoing rate list from file
def readRate():
    rates = []
    try:
        with open('rates', 'r') as myfile:
            rates = json.load(myfile)
            return rates
    except:
        return []
    
# Read Bitcoing 10 minutes avarage from file
def readAvg():
    try:
        with open('avgRates', 'r') as myfile:
            return json.load(myfile)
    except:
        return 0

# Get last Bitcoing rate, print it, add it to rate list and save the list into file
def getCurrentRate():
    URL = "https://api.coindesk.com/v1/bpi/currentprice.json"
    rates = []
    try:
        # API request to get last Bitcoing rate
        r = requests.get(url = URL)
        data = json.loads(r.text)

        # read saved rate list from file
        rates = readRate()

        # append last Bitcoin rate and save the list into file
        rates.append(data["bpi"]["USD"]["rate_float"])
        saveRate(rates)

        # print last Bitcoing rate to log (stdout)
        log.info("Bitcoin Last Rate: " + str(data["bpi"]["USD"]["rate_float"]))
    except:
        log.error("Error getting last bitcoin rate")

# Calculate and print average Bitcoin rate using saved rate list
def saveAvgRate():
    rates = []
    # Read saved rate list from file
    rates = readRate()

    # Calculate and print to log average Bitcoin rate
    avg = round(sum(rates) / len(rates), 2)
    log.info("10 mins average: " + str(avg))

    # Save average rate to file
    with open('avgRates', 'w+') as myfile:
        json.dump(avg, myfile)

    # Wait 2 seconds and earase rate list from file, saving only last rate
    time.sleep(2)
    saveRate([rates[-1]])
    

# Setting up scheduler to run 2 jobs
scheduler = BackgroundScheduler()
scheduler.add_job(func=getCurrentRate, trigger="interval", seconds=60)
scheduler.add_job(func=saveAvgRate, trigger="interval", seconds=600)
scheduler.start()
getCurrentRate()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

# Respond to an HTTP request with last Bitcoin rate and 10 minutes average rate
@app.route('/service-A')
def hello():
    rates = readRate()
    if len(rates) == 0:
        rates = [0]
    avg = readAvg()
    return 'Last Bitcoin Rate: ' + str(rates[-1]) + '\n10 minutes average: ' + str(avg)


if __name__ == "__main__":
    app.run(host='0.0.0.0')