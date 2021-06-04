from flask import Flask, render_template, request, jsonify
import pyrebase
from  flask_cors import CORS
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import re
from datetime import datetime
import os
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
storage=firebase.storage()
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

cred = credentials.Certificate('json/credential.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/api/upload/<string:cc>', methods=['POST'])
def upload(cc):
  if request.method == 'POST':
    try:

      f = request.files['file']
      substring = "\."
      filename = f.filename
      
      matches = re.finditer(substring, filename)
      matches_positions = [match.start() for match in matches]
      lastpoint = matches_positions[-1]

      
      name = filename[0:lastpoint]
      typeFile = filename[lastpoint+1:len(filename)]

      path_on_cloud = cc + "/" + name

      storage.child(path_on_cloud).put(f, "123456")

      link = storage.child(path_on_cloud).get_url("123456")
      dt = datetime.now()
      doc_ref = db.collection(u'files').document()
      doc_ref.set({
          u'name': name,
          u'type': typeFile,
          u'url': link,
          u'cc': cc,
          'last_time' : dt,
          'autenticated' : False

      })
  
      return jsonify("file uploaded successfully"), 201

    except:
      return jsonify("Error"), 400

@app.route('/api/download/<string:cc>', methods=['POST'])
def download(cc):
  if request.method == 'POST':
    try:

      name = request.json['name']
                    
      path_on_cloud =cc + "/" + name
      print(path_on_cloud)
      storage.child(path_on_cloud).download(filename=name,token="123456")



      return jsonify("file download successfully"), 201

    except:
      return jsonify("Error"), 400

@app.route('/api/open-recently/<string:cc>', methods=['GET'])
def openRecently(cc):
      
      files_ref = db.collection(u'files').where(u'cc', u'==', cc).order_by('last_time',direction=firestore.Query.DESCENDING).limit(7).stream()


      data = []

      for doc in files_ref:
        print(doc)
        data.append(doc.to_dict())
      print(data)
      
      return jsonify(data), 200

@app.route('/api/listFiles/<string:cc>', methods=['GET'])
def listFiles(cc):
  print(cc)
  docs = db.collection(u'files').where(u'cc', u'==', cc).stream()
  data = []

  for doc in docs:
    print(doc)
    data.append(doc.to_dict())
  print(data)

  return jsonify(data), 200

@app.route('/api/autenticated/<string:cc>', methods=['GET'])
def autenticatedFiles(cc):
      
  files_ref = db.collection(u'files').where(u'cc', u'==', cc).where(u'autenticated', u'==', True).stream()
  data = []

  for doc in files_ref:
    print(doc)
    data.append(doc.to_dict())

  print(data)
  
  return jsonify(data), 200

@app.route('/api/update-date/<string:cc>', methods=['PUT'])
def updatedate(cc):
  name = request.json['name']
  files_ref = db.collection(u'files').where(u'cc', u'==', cc).where(u'name', u'==', name).stream()

  docid = ""
  for doc in files_ref:
    docid=doc.id
  
  dt = datetime.now()
  db.collection("files").document(docid).update({"last_time": dt})

  return jsonify("fecha actualizada"), 200

@app.route('/api/autenticate-file/<string:cc>', methods=['PUT'])
def authF(cc):
  name = request.json['name']

  files_ref = db.collection(u'files').where(u'cc', u'==', cc).where(u'name', u'==', name).stream()

  docid = ""
  for doc in files_ref:
    docid=doc.id
  
  db.collection("files").document(docid).update({"autenticated": True})

  return jsonify("Archivo autenticado"), 200

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5001)))