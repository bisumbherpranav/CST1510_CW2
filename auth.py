"""
auth.py - Week 9: register and log in from the terminal.

Passwords are hashed with bcrypt. Users are kept in DATA/users.txt, one per line: username,hash

Run it:  python auth.py
"""

from pathlib import Path

import bcrypt

# create the file path where the user accounts will be saved, inside the "DATA" folder
USERS_FILE = Path(__file__).parent / "DATA" / "users.txt"


def generate_hash(password):
    """Turn a password into a bcrypt hash (returned as text)."""
    
    # convert the password text into bytes
    byte_password = password.encode("utf-8")

    # create random "salt" so identical passwords look completely different when hashed
    salt = bcrypt.gensalt()

    # hashed the password together with the salt
    hashed = bcrypt.hashpw(byte_password, salt)

    # turn the hashed bytes back into normal text
    return hashed.decode("utf-8")


def is_valid_hash(password, hashed):
    """True if the password matches the stored hash."""

    # convert both to bytes and check if they match (returns True or False)
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def user_exists(username, path=USERS_FILE):
    """True if this username is already in the file."""

    # if the users file hasn't been created yet, nobody is registered
    if not path.exists():
        return False

    # open file, read it and check it line by line
    with open(path, "r") as file:
        for line in file:

            # remove extra spaces and split "username,password" at the comma
            stored_name, _ = line.strip().split(",", 1)

            # compare names in lowercase
            if stored_name.lower() == username.lower():
                return True

    # if checked the whole file and didn't find the name, it's available
    return False


def register_user(username, password, path=USERS_FILE):
    """Add a new user. Returns (True or False, a message)."""

    # remove any whitespaces before and after the username
    username = username.strip()

    # stop if the username is blank or has a comma --> comma would break file format
    if username == "" or "," in username:
        return False, "Username cannot be empty or contain a comma."

    # make sure password is at least 8 characters long
    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    # check if someone else already claimed this username
    if user_exists(username, path):
        return False, "That username is already taken."

    # crate the "DATA" folder automatically if it doesn't exist yet
    path.parent.mkdir(exist_ok=True)

    # open file in append mode --> add new user to the bottom
    with open(path, "a") as file:

        # save the username and hashed password on a new line
        file.write(f"{username},{generate_hash(password)}\n")
    return True, "Registered. You can log in now."


def login_user(username, password, path=USERS_FILE):
    """Check a username and password. Returns (True or False, a message)."""

    # only check the file if it actually exists
    if path.exists():

        # open the file in read mode, and check it line by line
        with open(path, "r") as file:
            for line in file:

                # split the line at the first comma to seperate the saved name and hashed password
                stored_name, stored_hash = line.strip().split(",", 1)

                # check if username matches
                if stored_name.lower() == username.strip().lower():

                    # check if the typed password matches the hashed one
                    if is_valid_hash(password, stored_hash):
                        return True, "Welcome back!"

                    # stop searching once username is found, even if the password was wrong
                    break

    # return an error message if the username wasn't found or the password didn't match
    return (
        False,
        "Wrong username or password.",
    )  # the same message for both problems, on purpose


def main():
    """A small menu to try it out."""

    # keep showing the menu over and over until the user chooses to exit
    while True:

        # print the three menu choices on seperate lines
        print("\n1. Register\n2. Log in\n3. Exit")
        choice = input("> ")

        # if the user types "3", say goodbye and terminate the program
        if choice == "3":
            print("Goodbye!")
            break

        # if the user chose "1" or "2", ask for their username and password
        if choice in ("1", "2"):
            name = input("Username: ")
            password = input("Password: ")

            # run either register_user or login_user depending on what they picked
            if choice == "1":
                ok, message = register_user(name, password)
            else:
                ok, message = login_user(name, password)

            # print "OK" if it worked, or "NO" if it failed
            print(("OK: " if ok else "NO: ") + message)


# only run the menu if this file is run directly
if __name__ == "__main__":
    main()
