from flask import Flask, render_template, request, session, redirect, url_for
from os import urandom

from db import checkEmail, checkLogin, createUser, \
    createKey, getDomain, getUserDetail, getDomainsByUser

app = Flask(__name__)

app.config["SECRET_KEY"] = urandom(24)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    elif request.method == "POST":
        # Extracting data from request
        data = request.form

        username = data.get("uname", "").strip()
        useremail = data.get("uemail", "").strip()
        userpass = data.get("upass", "").strip()
        confirmpass = data.get("cfmpass", "").strip()

        # Checking necessary data
        if "" in (username, useremail, userpass, confirmpass):
            return render_template("error.html",
                        msg="Necessary data is missing in registration form."
                    )

        # Confirming password
        if userpass != confirmpass:
            return render_template("error.html",
                        msg="Entered password does not match."
                    )

        # Checking if email exist before
        if checkEmail(useremail):
            return render_template("error.html",
                        msg="Entered email already have an account."
                    )

        # Creating user
        result = createUser( username, useremail, userpass)
        if not result:
                return render_template("error.html",
                        msg="Something went wrong."
                    )
        
        session["username"] = username
        session["useremail"] = useremail
        
        return redirect(url_for("dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    elif request.method == "POST":
        # Extracting data from request
        data = request.form

        useremail = data.get("uemail", "").strip()
        userpass = data.get("upass", "").strip()

        # Checking necessary data
        if "" in (useremail, userpass):
            return render_template("error.html",
                        msg="Necessary data is missing in registration form."
                    )
        
        # Validating user
        result = checkLogin( useremail, userpass)

        if result == False:
            return render_template("error.html",
                        msg="Wrong credential is given."
                    )

        session["username"] = result[0]
        session["useremail"] = result[1]
        
        return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if not getCurrentUser():
        return render_template("error.html",
                    msg="Permission denied. You need to login first."
                )
    userDetail = getUserDetail( session.get('useremail') )
    print(userDetail)

    domains = getDomainsByUser( userDetail[0] )
    return render_template("dashboard.html", userDetail=userDetail, domains=domains )


@app.route("/logout")
def logout():
    del session["username"]
    del session["useremail"]

    return redirect(url_for("home"))


@app.route("/generate", methods=["POST"])
def generate():
    # Extracting data from request
    data = request.form
    inputURL = data.get("inputUrl", "").strip()

    # Checking necessary data
    if inputURL == "":
        return render_template("error.html",
                    msg="URL data is missing in input form."
                )
    result = createKey(inputURL, session.get("useremail", "") )

    if not result:
        return render_template("error.html",
                msg="Something went wrong."
            )
    link = url_for('short', key=result, _external=True)
    htmlOutput = f"""
        Here is your short URL: <a href='{link}' target='_blank'>{link}</a>
    """
    return render_template( 'success.html', msg= htmlOutput)

@app.route("/<string:key>")
def short(key):
    domain = getDomain(key)

    if not domain:
        return render_template("error.html",
                msg="There is no link with this URI."
            )
    return redirect( domain )

# ------- Helping function -------
def getCurrentUser():
    if session.get('username') is None:
        return False
    return {
        "username": session.get("username"),
        "useremail": session.get("useremail")
    }

@app.context_processor
def inject_base_variables():
    return {
        "logged": getCurrentUser() is not False,
        "user": getCurrentUser()
    }

if __name__ == "__main__":
    app.run(port=8081, debug=True)
