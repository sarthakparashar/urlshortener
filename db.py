import mysql.connector
import sys
import hashlib
from utill import getRandomKey

connection = mysql.connector.connect(
    host="localhost",
    user="jay",
    password="iampassword",
    database="ShortenerDB",
    auth_plugin='mysql_native_password'
)

cur = connection.cursor()

# ---------------------------------------#
# --------- Data fetch functions ---------
# ---------------------------------------#

def checkEmail(email):
    emailCheckSQL = f"SELECT id from user where email = '{email}'"
    cur.execute(emailCheckSQL)
    result = cur.fetchone()

    return bool(result)


def checkLogin(email, password):
    loginCheckSQL = f"SELECT name, email, password from user where email = '{email}'"
    cur.execute(loginCheckSQL)
    result = cur.fetchone()

    if (result is None):
        return False

    if len(result) != 3:
        return False

    db_username = result[0]
    db_useremail = result[1]
    db_userpass = result[2]

    pw_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    if db_userpass == pw_hash:
        return [ db_username, db_useremail ]
    return False

def getUserID(email):
    userIdSQL = f"SELECT id from user where email = '{email}'"
    try:
        cur.execute(userIdSQL)
        result = cur.fetchone()

        if len(result) > 0:
            return result[0]
        else:
            return False
    except:
        False

def getUserDetail(email):
    userDetailSQL = f"SELECT id, email_verified, registration from user where email = '{email}'"
    try:
        cur.execute(userDetailSQL)
        result = cur.fetchone()

        if len(result) > 0:
            return result
        else:
            return False
    except:
        False

def getDomainsByUser(id):
    domainByUserSQL = f"SELECT short_key, domain from url where created_by = '{id}'"
    try:
        cur.execute(domainByUserSQL)
        result = cur.fetchall()

        return result
    except:
        False

def getDomain(key):
    domainSQL = f"SELECT domain from url where short_key='{key}'"
    try:
        cur.execute(domainSQL)
        result = cur.fetchone()

        if len(result) > 0:
            return result[0]
        else:
            return False
    except:
        False


# ---------------------------------------#
# --------- Data write functions ---------
# ---------------------------------------#

def createUser(name, email, password):
    hashpass = hashlib.sha256(password.encode('utf-8')).hexdigest()
    keySQL = f"INSERT INTO user (name, password, email)  VALUES (%s, %s, %s)"
    try:
        cur.execute(keySQL, (name, hashpass, email))
        connection.commit()
        if cur.rowcount > 0:
            return True
        else:
            return False
    except:
        return False


def createKey(domain, email):
    randomKey = getRandomKey()

    # Checking if randomKey is exist
    checkKeySQL = f"SELECT id from url where short_key = '{randomKey}'"
    cur.execute(checkKeySQL)
    result = cur.fetchone()

    if bool(result):
        # Since key exist, Now calling function again
        createKey(domain)

    userId = getUserID(email)
    if not userId:
        return False

    keySQL = f"INSERT INTO url (short_key, domain, created_by)  VALUES (%s, %s, %s)"
    try:
        cur.execute(keySQL, (randomKey, domain, userId))
        connection.commit()
        if cur.rowcount > 0:
            return randomKey
        else:
            return False
    except:
        return False
    
# ---------------------------------------#
# --------- Create tables functions ------
# ---------------------------------------#

def createUserTable():
    userTableSQL = """CREATE TABLE user ( 
        id INT NOT NULL AUTO_INCREMENT , 
        name VARCHAR(255) NOT NULL , 
        password TEXT NOT NULL ,
        email VARCHAR(255) NOT NULL , 
        email_verified BOOLEAN NOT NULL DEFAULT 0 , 
        registration DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ,
        
        PRIMARY KEY (id) ,
        UNIQUE (email)
    );"""
    cur.execute(userTableSQL)
    print("User table created")


def createUrlTable():
    urlTableSQL = """CREATE TABLE url ( 
        id INT NOT NULL AUTO_INCREMENT , 
        short_key VARCHAR(5) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL , 
        domain VARCHAR(2048) NOT NULL , 
        created_by INT NOT NULL , 
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP , 
        
        PRIMARY KEY (id) ,
        UNIQUE (short_key) ,
        FOREIGN KEY (created_by) REFERENCES user(id)
    );"""
    cur.execute(urlTableSQL)
    print("URL table created")


# ---------- CLI command -----------
if len(sys.argv) > 1:
    operation = sys.argv[1]

    if operation == "init":
        createUserTable()
        createUrlTable()
        print("-" * 35)
        print("Done")
