from pathlib import Path
import shelve, bs4, requests, lxml
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# GOAL:
#   - Log into desired Instagram account with user-inputted username and
#       password
#   - Access and collect list of Following
#   - Access each Following account and see if it Follows Back
#       - If not, then add to list of Guilty accounts (accounts.txt)
#           - If CONFIRM is off, immediately Unfollow as well
#   - Print list of Guilty accounts
# EDGE CASES:
#   - Account name changes after name was recorded, but before trying to
#   unfollow
# FEATURES:
#   - WHITELIST: Whitelist accounts to exempt them from being automatically unfollowed
#   - CONFIRM: Print list of Guilty accounts, then ask for confirmation to unfollow all
#   - Toggle need for CONFIRM (unfollow without asking for confirmation, so
#       user doesn't have to wait for script to get Guilty accounts)

print("hello world")
print(Path.cwd())

accounts = Path.cwd() / "accounts.txt"
if not accounts.is_file():
    print(accounts, "is NOT a valid file")
    raise FileNotFoundError()

print(accounts, "is a valid file")

##print("Contents of accounts.txt: ", accounts.read_text())
##accounts.write_text("Rick roll")
##print("Contents of accounts.txt: ", accounts.read_text())
### Clear accounts.txt
##accounts.write_text("")
##print("Contents of accounts.txt: ", accounts.read_text())

url = "https://www.instagram.com/jinsen2cold/"
# Configure res to get webpage in specific manner
# headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0"}
# Get user's insta page
# res = requests.get(url, headers=headers)
# Check for error
# res.raise_for_status()

# Open browser to user's Instagram page. It will be logged out
options = Options()
options.binary_location = r"/Applications/Firefox 2.app/Contents/MacOS/firefox"
browser = webdriver.Firefox(options=options)
browser.get(url)

# soup = bs4.BeautifulSoup(res.text, "lxml")
# Get user's "following"
# v if not logged in
# following = soup.select("li.xl565be:nth-child(3) > button:nth-child(1) > div:nth-child(1)")

file = open(accounts)
# open(accounts, 'w') for write mode
# open(accounts, 'a') for append mode
file.close()

# Use shelve module for whitelisted accounts
# To add to whitelist, prompt the user to input a single account name
