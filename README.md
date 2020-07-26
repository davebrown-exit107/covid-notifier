# COVID-19 Notifier
This application pulls down the most recent COVID-19 results from the state and then notifies the subscriber list about the counties that they have subscribed to.

## How to use:
1.  Clone the repo
	* `git clone https://github.com/exit107/covid-notifier.git`
2. Change into the repo directory
	* `cd covid-notifier`
3. Create an environment file with the API keys for the messaging service of your choice.
	* _Refer to `env.example` for syntax._
4. Source your environment variables 
	* `source YOUR_ENVIRONMENT_FILE_HERE`.
5. Start the server
    * `flask run`
6. Connect to pull data for the first time
    * `curl http://localhost:5000/pull_new_data/`
7. Profit?

## Anything else?
This is very much a work in progress and nothing is sacred until we reach 1.0.
