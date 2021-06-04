from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pyrebase
from  flask_cors import CORS
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

firebaseConfig= {
  'apiKey':'AIzaSyBlySymF9LkMTlOr9UhmRQnIns-11lKeVc',
  'authDomain': 'api-carpex.firebaseapp.com',
  'projectId': 'api-carpex',
  'storageBucket': 'api-carpex.appspot.com',
  'messagingSenderId': '329220669040',
  'appId': '1:329220669040:web:e2a3ea638be7939d4e7eb5',
  'measurementId': 'G-98X1P6NTVK',
  'databaseURL': 'https://api-carpex.firebaseio.com'
}


# Use a service account
firebase = pyrebase.initialize_app(firebaseConfig)
auth=firebase.auth()

# Use a service account
cred = credentials.Certificate('json/credential.json')
firebase_admin.initialize_app(cred)

db = firestore.client()
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/api/login', methods=['POST'])
def login():
    if request.method == 'POST' and 'email' in request.json and 'password' in request.json:

        # Create variables for easy access
        email = request.json['email']
        password = request.json['password']
        try:
            login = auth.sign_in_with_email_and_password(email,password)
            docs = db.collection(u'users').where(u'email', u'==', email).stream()

            data = ""
            cc = ""
            for doc in docs:
                cc=doc.id
                data = doc.to_dict()
                print(data)

            data["cc"] = cc
            return jsonify(data), 200
        except:
            return jsonify({"password": "credenciales incorrectas"}),400

    elif ('email' not in request.json and 'password' in request.json):
        return jsonify({"email":" email not found"}), 400

    elif ('password' not in request.json and 'email' in request.json):
        return jsonify({"password":" password not found"}), 400
    else:
        return jsonify({"email":" email not found","password":" password not found"}), 400
        

@app.route('/api/singup', methods=['POST'])
def singup():
    if request.method == 'POST' and 'email' in request.json and 'password' in request.json and 'name' in request.json and 'address' in request.json and 'cc' in request.json:

        email = request.json['email']
        password = request.json['password']
        name = request.json['name']
        address = request.json['address']
        cc = request.json['cc']

        if len(password)<6:
            return jsonify({"password":" password less than 6 characters"}), 400 

        try:
            user=auth.create_user_with_email_and_password(email,password)
            doc_ref = db.collection(u'users').document(cc)
            doc_ref.set({
                
                u'name': name,
                u'address': address,
                u'email': email
            })
        
            return jsonify("user created successfully"), 201

        except:
            return jsonify({"email" : "email already registered"}), 400
    else:
      return jsonify({"error":" formulario incompleto"}), 400   
if __name__ == "__main__":
    app.run(port=8080, debug=True, host="0.0.0.0")