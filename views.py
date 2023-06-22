from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from main import accountManagment, atm

accManag = accountManagment
atmManag = atm

views = Blueprint(__name__, "views")

@views.route("/")
def auth():
    return render_template("auth.html")
#account management stuff
@views.route("/login", methods=["GET", "POST"]) #type: ignore
def loginPage():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        customer_password = request.form['customer_password']
        if accManag.login(customer_name, customer_password) != "no_customer": # type: ignore
            return redirect(url_for("views.accountPage", customer_name = customer_name))
        else: 
            print("Login failed")
            return render_template("auth/login.html", success="false")
    return render_template("auth/login.html")

@views.route("/account")
def accountPage():
    args = request.args
    customer_name = args.get("customer_name")
    return render_template("auth/accountStuff/account.html", customer_name = customer_name)

@views.route("/account/changePass", methods=["GET", "POST"]) #type: ignore
def changePassPage():
    args = request.args
    customer_name = args.get("customer_name")
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        customer_old_password = request.form['old_customer_password']
        customer_new_password = request.form['new_customer_password']
        if accManag.changePassword(customer_name, customer_old_password, customer_new_password): # type: ignore
            return redirect(url_for("views.accountPage", customer_name = customer_name))
        else: 
            print("Change Password failed")
            return render_template("auth/accountStuff/changePass.html", success="false")
    return render_template("auth/accountStuff/changePass.html", customer_name = customer_name)

@views.route("/account/delete", methods=["GET", "POST"]) #type: ignore
def deletePage():
    args = request.args
    customer_name = args.get("customer_name")
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        customer_password = request.form['customer_password']
        if accManag.deleteAcc(customer_name, customer_password): # type: ignore
            return redirect(url_for("views.loginPage"))
        else: 
            print("Delete failed")
            return render_template("auth/accountStuff/delete.html", success="false")
    return render_template("auth/accountStuff/delete.html", customer_name = customer_name)

@views.route("/register", methods=["GET", "POST"]) #type: ignore
def registerPage():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        customer_password = request.form['customer_password']
        if accManag.register(customer_name, customer_password): # type: ignore
            return redirect(url_for("views.accountPage", customer_name = customer_name))
        else: 
            print("Registration failed")
            return render_template("auth/register.html", success="false")
    return render_template("auth/register.html")

#atm stuff
@views.route("/atm") #type: ignore
def atmPage():
    args = request.args
    customer_name = args.get("customer_name")

    return render_template("auth/accountStuff/atm/atm.html", customer_name = customer_name, customer_cash = atm.getCashAmount(customer_name))

@views.route("/atm/deposit", methods=["GET", "POST"]) #type: ignore
def depositPage():
    args = request.args
    customer_name = args.get("customer_name")
    if request.method == 'POST':
        cash = request.form['cash']
        if atmManag.deposit(customer_name, cash): # type: ignore
            return redirect(url_for("views.accountPage", customer_name = customer_name))
        else: 
            print(f"Deposit failed {cash}")
            return render_template("auth/accountStuff/atm/deposit.html", success="false")
    return render_template("auth/accountStuff/atm/deposit.html", customer_name = customer_name)

@views.route("/atm/withdraw", methods=["GET", "POST"]) #type: ignore
def withdrawPage():
    args = request.args
    customer_name = args.get("customer_name")
    if request.method == 'POST':
        cash = request.form['cash']
        if atmManag.withdraw(customer_name, cash): # type: ignore
            return redirect(url_for("views.accountPage", customer_name = customer_name))
        else: 
            print("Withdraw failed")
            return render_template("auth/accountStuff/atm/withdraw.html", success="false")
    return render_template("auth/accountStuff/atm/withdraw.html", customer_name = customer_name)

@views.route("/atm/send", methods=["GET", "POST"]) #type: ignore
def sendPage():
    args = request.args
    customer_name = args.get("customer_name")
    if request.method == 'POST':
        cash = request.form['cash']
        taker = request.form['taker']
        if atmManag.send(customer_name, cash, taker): # type: ignore
            print("Sending...")
            return redirect(url_for("views.accountPage", customer_name = customer_name))
        else: 
            print("Sending failed")
            return render_template("auth/accountStuff/atm/send.html", success="false")
    return render_template("auth/accountStuff/atm/send.html", customer_name = customer_name)


@views.route("/json")
def get_json():
    return jsonify({"name": "zxc", "color": "balck"})


@views.route("/data")
def get_data():
    data = request.json
    return jsonify(data)


@views.route("/go-to-home")
def go_to_home():
    return redirect(url_for("views.name"))