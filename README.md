# COVID-19 Notifier
This application pulls down the most recent COVID-19 results from the state (Montana) and then notifies the subscriber list about the counties that they have subscribed to.

## How to use:
1.  Clone the repo
	* `git clone https://github.com/exit107/covid-notifier.git`
2. Change into the repo directory
	* `cd covid-notifier`
3. Update the env files
    * `cp env/db.env.example env/db.env && cp env/frontend.env.example env/frontend.env`
3. Update the Caddyfile
    * `cp caddy/Caddyfile.example caddy/Caddyfile`
4. Start the cluster
    * `docker-compose up`
5. Pull down new data
    * Open a web browser and navigate to `https://<SERVER_IP_OR_HOSTNAME>/pull_updates/`
6. Explore the data!
