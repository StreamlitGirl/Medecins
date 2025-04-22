from flask import Flask, request, jsonify
from geopy.distance import geodesic
import mysql.connector
import requests
from fastapi import FastAPI, Query
from deep_translator import GoogleTranslator
from langdetect import detect
from translate import Translator
#from googletrans import Translator
app = Flask(__name__) 
def NearDoctor(listDocs: list):
    listDistances = []
    user_Address = getUserAddressFromFlutter()
    user_Address = PositionToAddress(user_Address)
    if (user_Address is None):
                    msg = "Probleme de localisation user flutter" 
                    return {"success" : False , "msg" : msg}
    user_position = AddressToPosition(user_Address)
    i = 0
    for doc in listDocs:
                    d1 = AddressToPosition(doc[3])
                    listDistances.append({
                        "user_Address " : user_Address,
                        "user_Position " : user_position,
                        "DoctorPosition" : d1,
                        "distance": calculDistances(d1, user_position),
                        "nomDoc": doc[4],
                        "location": doc[3],
                        "speciality": doc[5],
                        "Mail": doc[1]
                    })
    listDistances.sort(key=lambda d: d["distance"])
    return {"success" : True, "msg" : listDistances}

                
               



# @app.route('/api/doctors', methods=['GET']) 
def AddressToPosition(address: str):
    api_key = "49cb9a1a5d7645e9a98dcc2e9aa7385d"
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        "q": address,
        "key": api_key,
        "limit": 1,
        "countrycode": "tn"  # restrict to Tunisia
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["results"]:
        lat = data["results"][0]["geometry"]["lat"]
        lon = data["results"][0]["geometry"]["lng"]
        return lat, lon
    else:
        return None
def PositionToAddress(mycurrentposition):
    
    api_key = "e52a9d80594a4c179caa51f8983d5360"
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        "q": mycurrentposition,
        "key": api_key,
        "limit": 1,
        "countrycode": "tn"  # restrict to Tunisia
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["results"]:
        return(data["results"][0]["formatted"])
    else :
         return None

def getUserAddressFromFlutter():
    address = request.args.get('mycurrentposition')
    if (address):
        #testingcode :

        return(address)
    else:
        return None


def calculDistances(d1, d2):
    if isinstance(d1, str):
        d1 = tuple(map(float, d1.split(',')))
    if isinstance(d2, str):
        d2 = tuple(map(float, d2.split(',')))
    return geodesic(d1, d2).km


@app.route('/api/doctors', methods=['GET'])
def getDocsFromDB():
    listDocs = listDoctors()
    if listDocs["success"] == False :
        msg  = listDocs["msg"]
        
        return jsonify({"success": False, "msg" :msg})
    else:
        listD : list = listDocs["msg"]
        listDistances = NearDoctor(listD);
        msg = listDistances["msg"]
    return jsonify({"success" : True , "msg": msg})

       
    
    
@app.route('/api/searchDoctors', methods = ['GET'])
def fetchingAdoctor ():
    v = request.args.get("v", "")
    translator_fr = Translator(to_lang="fr")
   
    lang = detect(v)
    if (lang != "fr"):
        
       # v = GoogleTranslator(source='auto', target='fr').translate(v)

         
    
    
        v = translator_fr.translate(v)
        

    listDocs = listDoctors()
    if listDocs["success"] == False :
        msg  = listDocs["msg"]
        
        return jsonify({"success": False, "msg" :msg})
    else:
        fetch : list = []
        listD : list = listDocs["msg"]
        v = v.lower()
        for doc in listD:
            if(v in doc[4].lower()  or v in  doc[5].lower() or v in doc[3].lower() or v in  doc[1].lower()):
                fetch.append(doc)
        filterList= NearDoctor(fetch)
        msg = filterList
        return jsonify({"success" : True , "msgFinal": msg, "listeAvantFilter" : fetch})



        
    

    
        
import os


if __name__ == "__main__":
    p = int(os.environ.get("PORT", 5000)) 

    app.run(host='0.0.0.0', port=p , debung = True)

