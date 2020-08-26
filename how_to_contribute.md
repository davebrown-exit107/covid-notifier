# Contributing

## How to setup a development server
1.  Clone the repo
	* `git clone https://github.com/exit107/covid-notifier.git`
2. Change into the repo directory
	* `cd covid-notifier`
4. Install requirements and activate your environment.
    * `poetry install && poetry shell`
5. Start the database
    * `docker build --name db ./db && docker run -d -p 5432:5432 db`
6. Build the environment file
    * `sed 's/^/export /g' ./env/frontend.env.example > ./env_file`
    * `source ./env_file`
7. Initialize the database
    * `flask db upgrade`
Start the development server
    * `flask run`
8. Hack away!!!

## Any other advice?
Not really. I'm a rather inexperienced Python programmer who just does fun stuff like this in his free time. If you have thoughts on how I can be better as a programmer or person in general, please email me, Thanks!
