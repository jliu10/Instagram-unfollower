from pathlib import Path
import shelve, bs4, requests, lxml, time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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
#       - Option to automatically whitelist accounts with a certain number of followers 
#   - CONFIRM: Print list of Guilty accounts, then ask for confirmation to unfollow all
#       - Ask user if there are any accounts from this list that they would like
#           to not unfollow, and/or add to whitelist
#   - Toggle need for CONFIRM (unfollow without asking for confirmation, so
#       user doesn't have to wait for script to get Guilty accounts)
#   - Customize timeout length

print("hello world")
print(Path.cwd())

username = input("Enter your Instagram username: ")
# ACCOUNT FOR WEIRD INPUTS
password = input("Enter your the password for @%s: " %username)


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

url = ("https://www.instagram.com/%s/" %username)

# Open browser to user's Instagram page. It will be logged out
options = Options()
options.binary_location = r"/Applications/Firefox 2.app/Contents/MacOS/firefox"
browser = webdriver.Firefox(options=options)
browser.get(url)

# Find the button whose div contains the text " In", as it could be "Log In" or
#   "Sign In" in the future
# login_XPATH = "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/nav/div[2]/div/div/div[3]/div/div[2]/div[1]/a/button/div"
login_XPATH = "//button/div[contains(text(), ' In')]"
login = 0
# Wait up to 10 seconds to find login button to account for page loading
for i in range(10):
#    print("iteration %d" %i)
    try:
        login = browser.find_element(By.XPATH, login_XPATH)
        print("login found")
        break
    except:
        time.sleep(1)

if isinstance(login, int):
    print("Unable to find 'Log in' button")

login.click()

#username_XPATH = "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[1]/div/label/input"
username_XPATH = "//input[@name='username']"
#password_XPATH = "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[2]/div/label/input"
password_XPATH = "//input[@name='password']"

for i in range(10):
    try:
        username_field = browser.find_element(By.XPATH, username_XPATH)
        print("Found username field")
        password_field = browser.find_element(By.XPATH, password_XPATH)
        print("Found password field")
        break
    except:
        time.sleep(1)

try:
    type(username_field)
    type(password_field)
except:
    print("Could not find username field or password field")

username_field.send_keys(username)
password_field.send_keys(password + Keys.ENTER)
# ACCOUNT FOR WHEN PASSWORD MAY FAIL
# Browser will take some time to load next page

# Don't save login info:
# not_now_XPATH = "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div/div/div/div/button"
not_now_XPATH = "//button[text()='Not Now']"
for i in range(10):
    try:
        not_now = browser.find_element(By.XPATH, not_now_XPATH)
        print("Found 'Not Now' button")
        break
    except:
        time.sleep(1)

try:
    type(not_now)
    not_now.click()
except:
    print("Could not find 'Not Now' button")

following_count_XPATH = ("//a[@href='/%s/following/']//child::div/span/span" %username)
for i in range(10):
    try:
        following_count = browser.find_element(By.XPATH, following_count_XPATH)
        print("Found following count")
        break
    except:
        time.sleep(1)

try:
    type(following_count)
except:
    print("Could not find following count")

try:
    # By knowing the following count, we can keep scrolling the following list
    #   until we revealed this many list child elementts
    following_count = int(following_count.text)
    print("Retrieved following count: %d" %following_count)
except:
    print("Could not retreive following count")


following_XPATH = ("//a[@href='/%s/following/']//child::div" %username)
try:
    following = browser.find_element(By.XPATH, following_XPATH)
    print("Found 'Following' button")
except:
    print("Could not find 'Following' button")

following.click()

# following_list_XPATH = "/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div[1]/div"
# List of usernames of following accounts
accounts_list = []
following_list_XPATH = "//button[div/div[text()='Following']]/../../.."
for i in range(5):
    try:
        following_list = browser.find_element(By.XPATH, following_list_XPATH)
        print("Found following list")
        break
    except:
        time.sleep(1)

try:
    type(following_list)       
except:
    print("Could not find following list")

# JavaScript to scroll until all following accounts are revealed
js = """
        const following_list_XPATH = "//button[div/div[text()='Following']]/../../..";
	const following_list = document.evaluate(following_list_XPATH, document).iterateNext();
	const intervalId = setInterval(() => {
            const goOn = following_list.children.length < %s
            if (goOn) {
                following_list.lastChild.scrollIntoView();
              } else {
                clearInterval(intervalId);
              }
        }, 3000);
""" % following_count
print("Executing script:\n%s" %js)

browser.execute_script(js)

print("got here")

file = open(accounts)
# open(accounts, 'w') for write mode
# open(accounts, 'a') for append mode
file.close()

# Use shelve module for whitelisted accounts
# To add to whitelist, prompt the user to input a single account name
