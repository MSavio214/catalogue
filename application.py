import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, euro

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Adds custom euro template
app.jinja_env.filters["euro"] = euro

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///catalog.db")

@app.route("/")
@login_required
def index():
    # data = db.execute("SELECT * FROM user_master WHERE user_id = :user_id", user_id=session["user_id"])

    products = db.execute("SELECT * FROM product_master")
    return render_template("index.html", products=products)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # return apology("TODO")
    if request.method == "POST":
        # return redirect("/sell")

        if (request.form.get("password") != request.form.get("confirmation")):
            # return apology("Password and confirmation does not match!", 403)
            flash("Passwords do not match!")
            return redirect("/register")

        rows = db.execute("SELECT * FROM user_master WHERE email=:email", email=request.form.get("email"))

        if len(rows) != 0:
            # return apology("This email already exists", 403)
            flash("This email already exists!")
            return redirect("/register")

        db.execute("INSERT INTO user_master (user_name, email, mobile, password) VALUES (:name, :email, :mobile, :password)", name=request.form.get("name"), email=request.form.get("email"), mobile=request.form.get("mobile"), password=generate_password_hash(request.form.get("password")))

        # db.execute("INSERT INTO users (username, hash) VALUES (:username, :password)", username=request.form.get("username"), password=generate_password_hash(request.form.get("password")))

        return redirect("/")

    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        rows = db.execute("SELECT * FROM user_master WHERE email = :email",
                          email=request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            # return apology("invalid email and/or password", 403)
            flash("Invalid email and/or password!")
            return render_template("login.html")


        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # db.execute("INSERT INTO order_header (user_id) VALUES (:user_id)", user_id=session["user_id"])

        # order = db.execute("SELECT * FROM order_header WHERE order_no = (SELECT MAX(order_no) FROM order_header)")

        # session["order_no"] = order[0]["order_no"]


        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/order", methods=["GET", "POST"])
@login_required
def order():

    number = int(request.form.get("items"))
    code = request.form.get("product_code")
    price = float(request.form.get("price"))
    product_description = request.form.get("product_description")
    # orders = db.execute("SELECT order_no FROM order_header WHERE user_id = :user_id", user_id=session["user_id"])
    product = db.execute("SELECT * FROM product_master WHERE product_code = :code", code=code)
    basket = db.execute("SELECT * FROM basket WHERE user_id = :user_id AND product_code = :code", user_id = session["user_id"], code=code)

    if len(basket) == 0:
        db.execute("INSERT INTO basket (product_code, product_description, price, order_qty, user_id) VALUES (:code, :desc, :price, :number, :user_id)", code=code, desc=product_description, price=price, number=number, user_id=session["user_id"])
    else:
        quantity = int(basket[0]["order_qty"])
        db.execute("UPDATE basket SET order_qty = :newQty WHERE user_id = :user_id AND product_code = :code", newQty = quantity + number, user_id = session["user_id"], code=code)

    db.execute("UPDATE product_master SET stock = :newStock WHERE product_code = :code", newStock = product[0]["stock"] - number,code=code)

    return redirect("/")

@app.route("/basket", methods=["GET", "POST"])
@login_required
def basket():
    rows = db.execute("SELECT * FROM basket WHERE user_id = :user_id", user_id=session["user_id"])

    total = 0

    for row in rows:
        total += (row["price"] * row["order_qty"])

    return render_template("basket.html", rows=rows, total=total)

@app.route("/remove", methods=["POST"])
@login_required
def remove():

    number = int(request.form.get("items"))
    code = request.form.get("product_code")
    product = db.execute("SELECT * FROM product_master WHERE product_code = :code", code=code)
    stock = product[0]["stock"]
    basket = db.execute("SELECT * FROM basket WHERE user_id = :user_id AND product_code = :code", user_id = session["user_id"], code=code)
    quantity = int(basket[0]["order_qty"])

    newQty = quantity - number
    newStock = stock + number
    if newQty > 0:

        db.execute("UPDATE basket SET order_qty = :newQty WHERE user_id = :user_id AND product_code = :code", newQty = newQty, user_id=session["user_id"], code=code)
    else:
        db.execute("DELETE FROM basket WHERE user_id = :user_id AND product_code = :code", user_id = session["user_id"], code=code)

    db.execute("UPDATE product_master SET stock = :stock WHERE product_code = :code", stock = newStock, code=code)

    return redirect("/basket")

@app.route("/removeFromCheckout", methods=["POST"])
@login_required
def removeFromCheckout():

    number = int(request.form.get("items"))
    code = request.form.get("product_code")
    product = db.execute("SELECT * FROM product_master WHERE product_code = :code", code=code)
    stock = product[0]["stock"]
    basket = db.execute("SELECT * FROM basket WHERE user_id = :user_id AND product_code = :code", user_id = session["user_id"], code=code)
    quantity = int(basket[0]["order_qty"])

    newQty = quantity - number
    newStock = stock + number
    if newQty > 0:

        db.execute("UPDATE basket SET order_qty = :newQty WHERE user_id = :user_id AND product_code = :code", newQty = newQty, user_id=session["user_id"], code=code)
    else:
        db.execute("DELETE FROM basket WHERE user_id = :user_id AND product_code = :code", user_id = session["user_id"], code=code)

    db.execute("UPDATE product_master SET stock = :stock WHERE product_code = :code", stock = newStock, code=code)

    return redirect("/checkout")

# @app.route("/removeAll", methods=["POST"])
# @login_required
# def removeAll():

#     products = db.execute("SELECT * FROM product_master")
#     code = request.form.get("product_code")

#     db.execute("DELETE FROM basket")
#     return redirect("/basket")

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    if request.method == "GET":

        rows = db.execute("SELECT * FROM basket WHERE user_id = :user_id", user_id=session["user_id"])
        total = 0

        for row in rows:
            total += (row["price"] * row["order_qty"])

        return render_template("checkout.html", rows=rows, total=total)

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        addr_1 = request.form.get("address1")
        addr_2 = request.form.get("address2")

        user_data = db.execute("SELECT * FROM user_master WHERE user_id = :user_id", user_id = session["user_id"])
        user_data = user_data[0]

        if (email != user_data["email"]) or check_password_hash(password, user_data["password"]):
            # return apology("Invalid email or password", 403)
            flash("Invalid email or password!")
            return redirect("/checkout")

        db.execute("INSERT INTO order_header (order_date, addr_1, addr_2, user_id) VALUES (CURRENT_DATE, :addr_1, :addr_2, :user_id)", addr_1=addr_1, addr_2=addr_2,user_id = session["user_id"])

        header = db.execute("SELECT MAX(order_no) FROM order_header WHERE user_id = :user_id", user_id = session["user_id"])

        current_order = header[0]["MAX(order_no)"]

        db.execute("UPDATE basket SET order_no = :current_order WHERE user_id = :user_id", current_order = current_order, user_id = session["user_id"])
        # db.execute("INSERT INTO order_detail (product_code, product_description, price, order_qty, item_value, user_id, date_created, time_created) SELECT (product_code, product_description, price, order_qty, item_value, user_id, date_created, time_created) FROM basket")

        # db.execute("INSERT INTO order_detail(order_no, product_code, product_description) VALUES (1, (SELECT product_code FROM basket),(SELECT product_description FROM basket))")

        db.execute("INSERT INTO order_detail SELECT * FROM basket")

        db.execute("DELETE FROM basket")
        return redirect("/")

@app.route("/change", methods = ["GET", "POST"])
@login_required
def change():
    if request.method == "GET":
        return render_template("change.html")

    if request.method == "POST":
        rows = db.execute("SELECT password FROM user_master WHERE user_id = :user_id", user_id = session["user_id"])

        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("current")):
            # return apology("invalid password", 403)
            flash("Invalid password!")
            return redirect("/change")

        if request.form.get("newPassword") != request.form.get("confirmation"):
            # return apology("Passwords must match!")
            flash("Passwords must match!")
            return redirect("/change")

        db.execute("UPDATE user_master SET password = :password WHERE user_id = :user_id", password = generate_password_hash(request.form.get("newPassword")), user_id = session["user_id"])

        return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""
    # current_order = db.execute("SELECT * FROM order_detail WHERE order_no = :order_no", order_no=session["order_no"])
    # if len(current_order) == 0:
    #     db.execute("DELETE FROM order_header WHERE order_no = :order_no", order_no=session["order_no"])
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
