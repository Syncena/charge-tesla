So you want your Powerall to charge to 100% or thereabouts during your
off-peak period, or you want to stop your Tesla car charging at the end
of your off-peak period rather than guessing where to set the percentage
slider in the app?

If so, this Python 3 script is for you.

First install TeslaPy (https://github.com/tdorssers/TeslaPy).

	$ pip install teslapy

Edit charge-tesla.json to add your details:
	{
		"email": "your-tesla-email-here",
		"enabled_Dory": true,
		"enabled_Tatsu": true,
		"home_lat": 0,
		"home_lon": 0,
		"enabled_powerwall": true,
		"off_backup_reserve_percent": "15",
		"on_backup_reserve_percent": "100"
	}

	"email": "your-tesla-email-here",
	This is your email address, as used for your Tesla account.

	"enabled_Dory": true,
	"enabled_Tatsu": true,
	This controls which of your Tesla cars need to have their charge
	stopped. The format is "enabled_<car-name>". If set to true, the
	script will tell the car to stop charging, but only if the car is
	reported as being near its home location. Multiple cars are
	supported; add a line for each.

	"home_lat": 0,
	"home_lon": 0,
	Specify the car's home location in latitude/longitude. The script
	will not attempt to stop charging if the car is far from this
	postition. Note: the script uses a very rough and ready method
	to determine if the car is "home". Some more work is needed here.

	"enabled_powerwall": true,
	If you have a Powerwall, this enables the script to control the
	standby reserve percentage. This is useful if you know tomorrow's
	power requirements are unlikely to be predicted correctly by
	Tesla's "AI". Set "enabled_powerwall" to true to enable this
	functionality.

	"off_backup_reserve_percent": "15",
	Set the standby reserve percentage. "off_backup_reserve_percent" is
	your normal resting standby reserve; used to set the standby
	reserve at the end of your off-peak period. Note: value must be
	a string.

	This is the percentage to set at the start of your off-peak period.
	"on_backup_reserve_percent": "100"

Once you've customised the above config file, copy it here:

	/usr/local/etc/tesla_api/charge-tesla.json

You will need to provide the Tesla SSO refresh token the first time you
run the script (or whenever Tesla de-auths your token, such as if you
change your Tesla password).

	$ ./charge-tesla.py status
	Not authorised
	Enter SSO refresh token:

I recommend using https://tesla-info.com/tesla-token.php to generate a
refresh token securely. Paste the entire refresh token at the above prompt
and hit return. The token is cached in /usr/loca/etc/tesla_api so this is
usually a one-time thing. You should now see a list of your Tesla products
and their current status.

Copy charge-tesla.py and charge-tesla.sh to /usr/local/sbin/charge-tesla.py.
The shell script arranges for logging to be written to /tmp/charge-tesla.log.
This can be useful to debug failures.

Assuming you have a Linux/MacOS/BSD server running 24/7, arrange for the
script to run via cron(8):

	$ crontab -e

If you're using the Octopus Go tariff in the UK, where you have a 4-hour
off-peak period between 0:30am and 4:30am, add the following lines to
the crontab.

  #minute hour    mday    month   wday    command
  # Set the standby reserve to force Powerwall to charge from off-peak
  31      0       *       *       *       /usr/local/sbin/charge-tesla.sh on
  35      0       *       *       *       /usr/local/sbin/charge-tesla.sh on
  40      0       *       *       *       /usr/local/sbin/charge-tesla.sh on
  45      0       *       *       *       /usr/local/sbin/charge-tesla.sh on

  # Reserve off.
  25      4       *       *       *       /usr/local/sbin/charge-tesla.sh off
  30      4       *       *       *       /usr/local/sbin/charge-tesla.sh off
  35      4       *       *       *       /usr/local/sbin/charge-tesla.sh off
  40      4       *       *       *       /usr/local/sbin/charge-tesla.sh off

Note: The script is invoked four times at 5 minute intervals in case of API
failure or network connectivity issues.


