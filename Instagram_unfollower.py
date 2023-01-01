from pathlib import Path

# EDGE CASE: Account name changes after name was recorded, but before trying to
#   unfollow
# FEATURES:
#   - Whitelist accounts to exempt them from being automatically unfollowed

print("hello world")
print(Path.cwd())

accounts = Path.cwd() / "accounts.txt"
if not accounts.is_file():
    print(accounts, "is NOT a valid file")
    raise FileNotFoundError()

print(accounts, "is a valid file")

print("Contents of accounts.txt: ", accounts.read_text())
accounts.write_text("Rick roll")
print("Contents of accounts.txt: ", accounts.read_text())
