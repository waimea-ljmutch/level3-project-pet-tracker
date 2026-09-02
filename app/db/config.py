#============================================================================
# Database schema and seed data configuration
#============================================================================


#----------------------------------------------------------------------------
# Table definitions
#----------------------------------------------------------------------------
# Define your tables with a name, a schema and optional seed/sample data,
# using this format, and then add the tables to the Table Registry below:
#
# class TableName:
#     NAME      = "name"
#     SCHEMA    = "CREATE TABLE name (...)"
#     SEED_DATA = "INSERT INTO name (...)" or None
#----------------------------------------------------------------------------

class UserTable:

    NAME = "users"

    SCHEMA = """
        CREATE TABLE users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname  TEXT NOT NULL,
            lastname   TEXT NOT NULL,
            username  TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """

    SEED_DATA = """
        INSERT INTO users (firstname, lastname, username, password_hash)
        VALUES("test", "user", "person", "scrypt:32768:8:1$n7eJTucLbaGmUpAM$c1776374a8d456a6eaf61bccc08db5e1fcc4ff3b3983d364c45ab13074255eeae0a393afb11f99a9fe63fb1d980992ace17a72ba70324523b11e92e36cbe4252")
    """

# Add more table classes here...
class MessageTable:

    NAME ="messages"

    SCHEMA = """
         CREATE TABLE messages (
         id         INTEGER PRIMARY KEY AUTOINCREMENT,
         pet        TEXT NOT NULL,
         location   TEXT NOT NULL,
         user_id    INTEGER NOT NULL,

         FOREIGN KEY (user_id) REFERENCES user(id)
         )
    """
    SEED_DATA = """
        INSERT INTO messages (pet, location, user_id)
            VALUES ("pancakes are awsome", "do you know the muffin man!", 1),
                    ("waffles are better tho", "did you that labs cna be hunting dogs they are also very cute and fun dogs to hang with", 1),
                    ("helldive!", "helldivers is a peak game for demicratic situations", 1),
                    ("jack", "maccas is a pretty yummy place to go to when you wanna get good burgers", 1)
    """


#----------------------------------------------------------------------------
# Table registry
#----------------------------------------------------------------------------
# Register all of your tables by adding them to the TABLES list here:
#
# TABLES = [
#     Table1Name,
#     Table2Name,
#     etc.
# ]
#
# Note: The table order is important - Create the tables that have
# foreign keys *after* the tables they link to have been created
#----------------------------------------------------------------------------

TABLES = [
    UserTable,
    MessageTable,
    # Add more tables here...
]

