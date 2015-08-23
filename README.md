# Helix
Script for demonstrating how easy it is to cheat in the "Helix Game" at Liseberg, Gothenburg

## Usage
Just put your ID, displayed at the bottom of the settings-screen in the Helix app, in the file udid.py in place of the X's.

The script can perform a few different actions.  
- -r, --register, --rename
  * Use to register a new ID, or change the username of an existing user (doesn't have to be your own)
- -n, --name
  * Retrieve the username for a specified ID
- -c, --code
  * Simply bruteforce and display the current 4-digit code required to play the game
- -s, --score
  * Simulate a full game session and submit an arbitrary score to the leaderboard (takes about 2 minutes)

In addition, the -u flag (or --udid) can be used to run the script with a provided ID, rather than reading from udid.py.

### Dependencies:
- Python 3
- [Requests](http://www.python-requests.org/)
