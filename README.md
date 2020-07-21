# COVID-19 Notifier
This application pulls down the most recent COVID-19 results from the state and then notifies the subscriber list about the counties that they have subscribed to.

## How to use:
1.  Clone the repo
	* `git clone https://github.com/exit107/covid-notifier.git`
2. Change into the repo directory
	* `cd covid-notifier`
3. Create an environment file with the API keys for the messaging service of your choice.
	* _Refer to `env.example` for syntax._
4. Create a `sensitive.py` to indicate which counties to monitor, which endpoints to notifiy, and if a statewide rollup is desired.
	* _Refer to `sensitive.py.example` for syntax._
6. Source your environment variables 
	* `source YOUR_ENVIRONMENT_FILE_HERE`.
7. Pull down the most recent data: 
	* `./pull_data.py`
8. Send notifications: 
	* `./notifications.py`

## Anything else?
This is very much a work in progress and nothing is sacred until we reach 1.0.
