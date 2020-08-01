# COVID-19 Notifier
This application pulls down the most recent COVID-19 results from the state and then notifies the subscriber list about the counties that they have subscribed to.

## How to use:
1.  Clone the repo
	* `git clone https://github.com/exit107/covid-notifier.git`
2. Change into the repo directory
	* `cd covid-notifier`
3. Create an environment file based on the `env.example` file. _Note: we're using [python-dotenv](https://github.com/theskumar/python-dotenv#readme) to source the variables so make sure to save your env file in the same directory as this README as `.env`_
	* _Refer to `env.example` for syntax._
4. Pull down new data
    * `flask pull-updates`
5. Start the server
    * `flask run`

## Anything else?
This is very much a work in progress and nothing is sacred until we reach 1.0.
