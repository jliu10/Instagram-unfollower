from pathlib import Path

# EDGE CASE: Account name changes after name was recorded, but before trying to
#   unfollow
# FEATURES:
#   - Whitelist accounts to exempt them from being automatically unfollowed

print("hello world")
print(Path.cwd())

accounts = Path.cwd() / "accounts.txt"
if accounts.exists():
    print(accounts, "is a valid path")
else:
    print(accounts, "is NOT a valid path")
