from pathlib import Path
import shelve, bs4, requests, lxml, time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pyinputplus as pyip

# GOAL:
#   - Log into desired Instagram account with user-inputted username and
#       password
#   - Access and collect list of Following
#   - Access each Following account and see if it Follows Back
#       - If not, then add to list of Guilty accounts
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
#   - Input firefox.exe path

shelfFile = shelve.open("mydata")
if not shelfFile["whitelist"]:
    shelfFile["whitelist"] = []
shelfFile.close()

def menu():
    text = """\n******************** MENU ********************
    Welcome to Instagram Unfollower (made by Justin Liu).
    
    NOTE: You can exit the entire program at any point by entering Ctrl + C in the Python shell
    """
    print(text)
    choices = ["About",
               "Manage whitelist",
               "Run unfollowing script"]
    choice = pyip.inputMenu(prompt="What would you like to do?\n", choices=choices, numbered=True)

    if choice == choices[0]:
        return about()
    elif choice == choices[1]:
        return whitelist()
    elif choice == choices[2]:
        return script()

def about():
    info = """\n******************** ABOUT ********************
"""
    print(info)
    print("Go back to menu?")
    while True:
        if pyip.inputYesNo() == 'yes':
            break
    return menu()

def whitelist():
    info = """\n******************** WHITELIST ********************
    Here, you can add/remove accounts from the whitelist. Whitelisted accounts
    are exempt from being unfollowed by the unfollowing script. You may want to
    whitelist accounts such as celebrities. The whitelist should be saved even
    aftering exiting this program.
"""
    print(info)
    choices = ["View current whitelist",
               "Edit whitelist",
               "Back to menu"]
    choice = pyip.inputMenu(prompt="What would you like to do?\n", choices=choices, numbered=True)
    if choice == choices[0]:
        shelfFile = shelve.open("mydata")
        print("Current whitelist:")
        for a in shelfFile["whitelist"]:
            print("\t@" + a)
        shelfFile.close()
        print("Go back?")
        while True:
            if pyip.inputYesNo() == 'yes':
                break
        return whitelist()
    elif choice == choices[1]:
        choice2 = pyip.inputMenu(prompt="What what you like to do with the whitelist?\n", choices=["Add accounts","Remove accounts"], numbered=True)
        if choice2 == "Add accounts":
            accountsToAdd = input("Enter the usernames of each account you would like to add, separated by spaces (e.g. user1 user2):\n")
            accountsToAdd = accountsToAdd.split(' ')
            # Remove empty string from list
            while '' in accountsToAdd:
                accountsToAdd.remove('')
            shelfFile = shelve.open("mydata")
            for a in accountsToAdd:
                if a not in shelfFile["whitelist"]:
                    temp = shelfFile["whitelist"]
                    temp.append(a.lower())
                    shelfFile["whitelist"] = temp
                    print("\tAdded @%s to whitelist" %a)
                else:
                    print("\t@%s already in whitelist" %a)
            shelfFile.close()
            return whitelist()
        elif choice2 == "Remove accounts":
            accountsToRemove = input("Enter the usernames of each account you would like to remove, separated by spaces (e.g. user1 user2):\n")
            accountsToRemove = accountsToRemove.split(' ')
            while '' in accountsToRemove:
                accountsToRemove.remove('')
            shelfFile = shelve.open("mydata")
            for a in accountsToRemove:
                if a in shelfFile["whitelist"]:
                    temp = shelfFile["whitelist"]
                    temp.remove(a.lower())
                    shelfFile["whitelist"] = temp
                    print("\tRemoved @%s from whitelist" %a)
                else:
                    print("\t@%s not in whitelist" %a)
            shelfFile.close()
            return whitelist()
    elif choice == choices[2]:
        return menu()
    

def script():
    print("\n******************** STARTING SCRIPT ********************")
    username = input("Enter your Instagram username: ")
    # ACCOUNT FOR WEIRD INPUTS
    password = input("Enter your the password for @%s: " %username)

    url = ("https://www.instagram.com/%s/" %username)

    # Open browser to user's Instagram page. It will be logged out
    options = Options()
    options.binary_location = r"/Applications/Firefox 2.app/Contents/MacOS/firefox"
    browser = webdriver.Firefox(options=options)
    browser.get(url)

    # Find the button whose div contains the text " In", as it could be "Log In" or
    #   "Sign In" in the future
    login_XPATH = "//button/div[contains(text(), ' In')]"
    login = 0
    # Wait up to 10 seconds to find login button to account for page loading
    for i in range(10):
    #    print("iteration %d" %i)
        try:
            login = browser.find_element(By.XPATH, login_XPATH)
            print("Found login button")
            break
        except:
            time.sleep(1)

    if isinstance(login, int):
        print("Unable to find 'Log in' button")

    login.click()

    username_XPATH = "//input[@name='username']"
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
        # Remove commas from number
        following_count = int((following_count.text).replace(',',''))
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
    # Use a 1-second interval because it takes about 1 second for more accounts to
    #   load on the list. Not necessary but will save work
    js = """
            const following_list_XPATH = "//button[div/div[text()='Following']]/../../..";
            const following_list = document.evaluate(following_list_XPATH, document).iterateNext();
            const intervalId = setInterval(() => {
                const goOn = following_list.children.length < %d
                if (goOn) {
                    following_list.lastChild.scrollIntoView();
                  } else {
                    clearInterval(intervalId);
                  }
            }, 1000);
    """ % following_count
    print("Executing script:\n%s" %js)

    browser.execute_script(js)

    # List of children of following_list, each representing an account
    try:
        children = following_list.find_elements(By.XPATH, "./child::div")
        while len(children) < following_count:
            # Sleep to match JavaScript interval
            time.sleep(1)
            children = following_list.find_elements(By.XPATH, "./child::div")
            print("Number of children: %d" %len(children))
    except:
        print("Could not find children of following_list")

    # List of usernames of following accounts
    handle_list = []
    print("Getting usernames...")
    handle_XPATH = ".//a/span/child::div"
    for child in children:
        try:
            handle = child.find_element(By.XPATH, handle_XPATH)
            handle = handle.text
            if "\nVerified" in handle:
                handle = handle[:handle.index("\nVerified")]
            print(handle)
            handle_list.append(handle)
        except:
            print("Could not find handle")

    guilty_accounts = []
    shelfFile = shelve.open("mydata")
    # Analyze each account that you're following:
    for handle in handle_list:
        print("Analyzing @%s:" %handle)
        # If username is whitelisted, don't do anything
        if handle in shelfFile["whitelist"]:
            print("\tAccount is whitelisted")
            continue

        url = ("https://www.instagram.com/%s/" %handle)
        browser.get(url)

        following_XPATH = ("//header/section/ul/li[3]")
        link_XPATH = "./a"
        # Indicate whether account follows 0 accounts
        no_accounts = False
        # While the "following" link isn't loaded
        for i in range(10):
            try:
                following = browser.find_element(By.XPATH, following_XPATH)
                try:
                    link = following.find_element(By.XPATH, link_XPATH)
                    print("\tFound @%s's 'following' link" %handle)
                    break
                except:
                    print("\t@%s doesn't follow any accounts" %handle)
                    no_accounts = True
                    break
            except:
                print("\tWaiting for @%s's page to load..." %handle)
                # Give the page time to load
                time.sleep(1)
        try:
            following.click()
            print("\tClicked 'following'")
        except:
            print("\tCould not find @%s's 'following' link")
            continue

        if no_accounts:
            guilty_accounts.append(handle)
            continue

        # If an account follows you, the first account in its following list should
        #   be your account
        
        # First account in following list
        first_account_XPATH = "//div[@role='dialog']//a"
        for i in range(5):
            try:
                first_account = browser.find_element(By.XPATH, first_account_XPATH)
                print("\tFound first account in following list")
                break
            except:
                time.sleep(1)
        try:
            type(first_account)
        except:
            print("\tCould not find first account in following list")
        href = first_account.get_attribute("href")
        # print("\thref = %s" %href)
        
        # Extract username from href
        href = href[:-1]
        href = href[href.rindex('/')+1:]
        print("\tUsername of first account: %s" %href)

        # If the first account isn't yourself, it means this person isn't following
        #   you
        if href != username:
            print("\t@%s DOES NOT follow you back" %handle)
            guilty_accounts.append(handle)
        else:
            print("\t@%s follows you back" %handle)
        
        #break
    shelfFile.close()

    print("Guilty accounts:")
    for a in guilty_accounts:
        print("\t@%s" %a)

    unfollow_all = pyip.inputYesNo(prompt="Unfollow guilty accounts? ")
    if unfollow_all == "yes":
        for guilty in guilty_accounts:
            if unfollow_account(guilty, 5):
                print("Successfully unfollowed @%s" %guilty)
            else:
                print("Could not unfollow @%s" %guilty)

    print("GOT HERE")


# Unfollows handle's account, waiting up to timeout seconds before timing out.
#   Returns true if successful at unfollowing, false otherwise
def unfollow_account(handle: str, timeout: int) -> bool:
    # If CONFIRM is off, unfollow should be called right after determining that
    #   this account doesn't follow you back. Thus, the browser should be at
    #   "https://www.instagram.com/$s/following" %handle
    if browser.current_url == ("https://www.instagram.com/%s/following/" %handle):
        x_XPATH = "//div[@role='dialog']//button"
        for i in range(timeout):
            try:
                x = browser.find_element(By.XPATH, x_XPATH)
                print("Found X button")
                break
            except:
                time.sleep(1)
        try:
            type(x)
            # Clicking the X is faster than reentering the browser URL
            x.click()
        except:
            print("Could not find X button")
            return False
    else:
        browser.get("https://www.instagram.com/%s/" %handle)
    
    following_button_XPATH = "//button/div/div[text()='Following']"
    for i in range(timeout):
        try:
            following_button = browser.find_element(By.XPATH, following_button_XPATH)
            print("Found 'Following' button")
            break            
        except:
            time.sleep(1)
    try:
        type(following_button)
        following_button.click()
        print("Clicked 'Following' button")
    except:
        print("Could not find 'Following' button")
        return False
    
    unfollow_XPATH = "//div[@role='dialog']//div[text()='Unfollow']"
    for i in range(timeout):
        try:
            unfollow = browser.find_element(By.XPATH, unfollow_XPATH)
            print("Found 'Unfollow' button")
            break            
        except:
            time.sleep(1)
    try:
        type(unfollow)
    except:
        print("Could not find 'Unfollow' button")
        return False
    unfollow.click()
    return True

menu()
