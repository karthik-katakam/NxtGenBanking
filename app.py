from flask import Flask
from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify, Response
import oracledb
import random
from datetime import datetime
import os
from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_bcrypt import Bcrypt
from flask_session import Session


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = os.urandom(24)

hostname = 'prophet.njit.edu'
port = 1521
sid = 'course'
username = 'kk749'
password = 'Kiri@23122001'
database = oracledb.makedsn(hostname, port, sid)
connection = oracledb.connect(user=username, password=password, dsn=database)

@app.route('/')
@app.route("/dashboard")
def dashboard():
    return render_template("home.html", home=True)

@app.route("/addcustomer" , methods=["GET", "POST"])
def addcustomer():
    if request.method == "POST":
        customerssn = int(request.form.get("cust_ssn_id"))
        Accounttype = request.form.get("accounttype")
        name = request.form.get("name")
        streetnumber = request.form.get("streetnum")
        zipcode= request.form.get("zipcode")
        aptnum= int(request.form.get("aptnum"))
        branchid= int(request.form.get("branchid"))
        personalbankerssn= int(request.form.get("personalbankerssn"))
        state = request.form.get("state")
        city = request.form.get("city")
        print(f"""
        Customer Details:
        SSN: {customerssn}
        Name: {name}
        Street Number: {streetnumber}
        Apartment Number: {aptnum}
        Zipcode: {zipcode}
        Branch ID: {branchid}
        Personal Banker SSN: {personalbankerssn}
        State: {state}
        City: {city}
        """)
        query = "SELECT * FROM CUSTOMER WHERE ssn = :1"
        cursor = connection.cursor()
        cursor.execute(query, [customerssn])
        customer = cursor.fetchone()
        if customer:
            return redirect('/dashboard')
        else:
            insert_query = """
            INSERT INTO CUSTOMER (SSN, NAME, STREETNUM, STATE, CITY, ZIPCODE, APTNUM, BRANCHID, PERSONALBANKERSSN)
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9)
            """
            cursor.execute(insert_query, [
            customerssn,  
            name,         
            streetnumber,    
            state,        
            city,         
            zipcode,      
            aptnum,       
            branchid,     
            personalbankerssn  
        ])
        connection.commit()
        return redirect(url_for('dashboard'))
    return render_template('addcustomer.html', addcustomer=True)


@app.route("/viewcustomer/<cust_ssn_id>")
@app.route("/viewcustomer" , methods=["GET", "POST"])
def viewcustomer():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "banker":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="banker":
        if request.method == "POST":
            cust_ssn_id = request.form.get("cust_ssn_id")
            query = "SELECT * FROM CUSTOMER WHERE ssn = :1"
            cursor = connection.cursor()            
            cursor.execute(query, [cust_ssn_id])
            customer = cursor.fetchone()
            if customer:
                data = {
                    'cust_ssn_id': customer[0],
                    'name': customer[1],
                    'StreetNumber': customer[2],
                    'State': customer[3],
                    'city': customer[4],
                    'Zipcode': customer[5],
                    'Aptnum': customer[6],
                    'BranchID': customer[7],
                    'PersonalBankerSSN': customer[8]
                }
                return render_template('viewcustomer.html', data=data, viewcustomer=True)
            else:
                return jsonify({"error": "Customer not found!"}), 404

    return render_template('viewcustomer.html', viewcustomer=True)

@app.route('/editcustomer')
@app.route("/editcustomer/<int:cust_ssn_id>", methods=["GET", "POST"])
def editcustomer(cust_ssn_id):
    if request.method == "GET":
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM CUSTOMER WHERE SSN = {cust_ssn_id}")
        customer = cursor.fetchone()
        if customer:
            data = {
                'cust_ssn_id': customer[0],
                'name': customer[1],
                'StreetNumber': customer[2],
                'State': customer[3],
                'city': customer[4],
                'Zipcode': customer[5],
                'Aptnum': customer[6],
                'BranchID': customer[7],
                'PersonalBankerSSN': customer[8]
            }
            return render_template('editcustomer.html', data=data)

    if request.method == "POST":
        customerssn = request.form.get("cust_ssn_id")
        name = request.form.get("name")
        streetnumber = request.form.get("streetnum")
        zipcode= request.form.get("zipcode")
        aptnum= request.form.get("aptnum")
        branchid= request.form.get("branchid")
        personalbankerssn= request.form.get("personalbankerssn")
        state = request.form.get("state")
        city = request.form.get("city")

        update_fields = []
        update_values = {}
        print(customerssn)
        update_values['SSN'] = cust_ssn_id  # Ensure SSN is added here
        print(f"Update values: {update_values}")  # Debugging

        if name:
            update_fields.append("NAME = :NAME")
            update_values['NAME'] = name
        if streetnumber:
            update_fields.append("STREETNUM = :StreetNumber")
            update_values['STREETNUM'] = streetnumber
        if state:
            update_fields.append("STATE = :state")
            update_values['STATE'] = state
        if city:
            update_fields.append("CITY = :city")
            update_values['CITY'] = city
        if zipcode:
            update_fields.append("ZIPCODE = :zipcode")
            update_values['ZIPCODE'] = zipcode
        if aptnum:
            update_fields.append("APTNUM = :aptnum")
            update_values['APTNUM'] = aptnum
        if branchid:
            update_fields.append("BRANCHID = :branchid")
            update_values['BRANCHID'] = branchid
        if personalbankerssn:
            update_fields.append("PERSONALBANKERSSN = :PERSONALBANKERSSN")
            update_values['PERSONALBANKERSSN'] = personalbankerssn

        if not update_fields:
            return "No fields to update", 400
        
        update_values['SSN'] = cust_ssn_id
        print(update_fields)
        print(update_values)
        update_query = f"UPDATE CUSTOMER SET {', '.join(update_fields)} WHERE SSN = :SSN"
        print(update_query)  

        cursor = connection.cursor()
        cursor.execute(update_query, update_values)
        connection.commit()

        return redirect(url_for('viewcustomer', cust_id=customerssn))

@app.route('/deletecustomer')
@app.route('/deletecustomer/<cust_id>')
def deletecustomer(cust_id=None):
    # if 'user' not in session:
    #     return redirect(url_for('login'))
    # if session['usert'] != "banker":
    #     flash("You don't have access to this page","warning")
    #     return redirect(url_for('dashboard'))
    # if session['usert']=="banker":
    #     if cust_id is not None:
    #         cust_id = int(cust_id)
    #         query = "SELECT * FROM CUSTOMER WHERE ssn = :1"
    #         cursor = connection.cursor()            
    #         cursor.execute(query, [cust_id])
    #         customer = cursor.fetchone()            
    #         if customer is not None :
    #             query = "DELETE FROM CUSTOMER WHERE ssn = :1"
    #             cursor = connection.cursor()
    #             cursor.execute(query, [cust_id])
    #             connection.commit()
    #             flash(f"Customer is deleted.","success")
    #             return redirect(url_for('dashboard'))
    #         else:
    #             flash(f'Customer with id : {cust_id} is already deactivated or not present in database.','warning')
    # return redirect(url_for('viewcustomer'))
    pass

@app.route("/addaccount" , methods=["GET", "POST"])
def addaccount():
    if request.method == "POST":
        cust_id = int(request.form.get("cust_id"))
        acc_type = request.form.get("acc_type")
        balance= float(request.form.get("Balance"))
        query = "SELECT * FROM CUSTOMER WHERE ssn = :1"
        AccountNumber = random.randint(1000, 9000)
        cursor = connection.cursor()
        cursor.execute(query, [cust_id])
        customer = cursor.fetchone()
        if customer:
            print(f"""
            Account Details:
            SSN: {cust_id}
            acc_type: {acc_type}
            balance: {balance}
            """)
            insert_query = """
            INSERT INTO ACCOUNTS (CUSTOMER_SSN, BALANCE, ACCOUNTTYPE, AccountNumber )
            VALUES (:1, :2, :3, :4)
            """
            cursor.execute(insert_query,[
            cust_id,  
            balance,         
            acc_type,    
            AccountNumber ])
            connection.commit()
            message = "Account successfully created"
        else:
            redirect(url_for('addcustomer'))
    return render_template('addaccount.html')


@app.route("/delaccount" , methods=["GET", "POST"])
def delaccount():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "banker":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="banker":
        if request.method == "POST":
            acc_id = int(request.form.get("acc_id"))
            acc_type = request.form.get("acc_type")
            query = "SELECT * FROM ACCOUNTS WHERE ACCOUNTNUMBER = :1"
            cursor = connection.cursor()            
            cursor.execute(query, [acc_id])
            account = cursor.fetchone()            
            if account is not None :
                query = "DELETE FROM ACCOUNTS WHERE ACCOUNTNUMBER = :1"
                cursor = connection.cursor()
                cursor.execute(query, [acc_id])
                connection.commit()
                flash(f"Customer account is Deactivated Successfully.","success")
                return redirect(url_for('dashboard'))
            else:
                flash(f'Account with id : {acc_id} is not present in database.','warning')
    return render_template('delaccount.html', delaccount=True)

@app.route("/viewaccount" , methods=["GET", "POST"])
def viewaccount():
    if request.method == "POST":
        cust_id = request.form.get("cust_id")
        accid=request.form.get("acc_id")
        query = "SELECT * FROM ACCOUNTS WHERE ACCOUNTNUMBER = :1"
        cursor = connection.cursor()            
        cursor.execute(query, [accid])
        Account = cursor.fetchone()
        querycust = "SELECT * FROM ACCOUNTS WHERE CUSTOMER_SSN = :1"
        cursorcust = connection.cursor()            
        cursorcust.execute(querycust, [cust_id])
        Customer = cursorcust.fetchall()
        print(querycust)
        if Account:
            data = [{
                'AccountNumber': Account[0],
                'Balance': Account[1],
                'LastaccessedDate': Account[2],
                'AccountType': Account[3],
                'CustomerSSN': Account[4]
            }]
            print(data)
            return render_template('viewaccount.html', data=data, viewcustomer=True)
        elif Customer:
            print(Customer)  # Debug: Check the output
            data = [
            {
                'AccountNumber': row[0],
                'Balance': row[1],
                'LastaccessedDate': row[2],
                'AccountType': row[3],
                'CustomerSSN': row[4]
            }
            for row in Customer
            ]
            return render_template('viewaccount.html', data=data, viewcustomer=True)
        else:
            return jsonify({"error": "Customer not found!"}), 404
        # else:
            # redirect(url_for('addcustomer'))
            # return jsonify({"error": "User Doesnt Have access!"}), 404

    return render_template('viewaccount.html', viewcustomer=True)



@app.route('/deposit',methods=['GET','POST'])
@app.route('/deposit/<acc_id>',methods=['GET','POST'])
def deposit():
    pass

@app.route('/withdraw',methods=['GET','POST'])
@app.route('/withdraw/<acc_id>',methods=['GET','POST'])
def withdraw():
    pass

@app.route('/transfer',methods=['GET','POST'])
@app.route('/transfer/<cust_id>',methods=['GET','POST'])
def transfer():
    pass

@app.route("/statement" , methods=["GET", "POST"])
def statement():
    pass

@app.route('/pdf_xl_statement/<acc_id>')
@app.route('/pdf_xl_statement/<acc_id>/<ftype>')
def pdf_xl_statement():
    pass

@app.route('/customerlog', methods=["GET", "POST"])
@app.route('/api/v1/customerlog', methods=["GET", "POST"])
def customerlog():
    pass

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    if request.method == "POST":
        usern = request.form.get("username")
        passw = request.form.get("password")  # Keep it as a string
        query = "SELECT * FROM Login WHERE USERNAME = :1"
        cursor = connection.cursor()            
        cursor.execute(query, [usern])
        user = cursor.fetchone()
        print(usern)
        print(user)
        if user is not None:
            # Assuming the password is in the second field of the user tuple
            # If using an index-based approach, ensure correct index for password hash (typically user[1] or user[2])
            stored_hash = user[1]  # Assuming the hashed password is in the second position
            if stored_hash == passw:  # Pass the plain password as a string
                session['user'] = usern
                session['namet'] = user[0]  # Assuming username is at index 0
                session['usert'] = user[2]
                session['custid']= user[3] # Assuming user privilege is at index 2
                print(user[3])
                flash(f"{user[0].capitalize()}, you are successfully logged in!", "success")
                return redirect(url_for('dashboard'))
        
        flash("Sorry, Username or password not match.", "danger")
    return render_template("login.html", login=True)


if __name__ == '__main__':
    app.run(debug=True)
