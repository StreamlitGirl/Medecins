from flask import Flask, request, jsonify
from geopy.distance import geodesic
import mysql.connector
import requests

app = Flask(__name__)

# @app.route('/api/doctors', methods=['GET']) 
def AddressToPosition(address: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "your-app-name"  # Required by Nominatim!
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    if data:
        lat = float(data[0]["lat"])
        lng = float(data[0]["lon"])
        return (lat, lng)
    else:
        return None


#ef PositionToAddress(lat, lng)
def getUserAddressFromFlutter():
    address = request.args.get('mycurrentposition')
    if (address):
        return(address)
    else:
        return None


def calculDistances(d1, d2):
    return geodesic(d1, d2).km


@app.route('/api/doctors', methods=['GET'])
def getDocsFromDB():
    listDocs: list = []
    try:
        connection = mysql.connector.connect(
            host="mysql.railway.internal",
            user="root",
            password = "WxMcKJBKaOyynAhtzjCwccIpQcJXuvGE",

            database="railway"
        )

        if connection.is_connected():
            page = int(request.args.get('page', 1))
            limit = 5
            offset = (page - 1) * limit
            sql = f'select * from docteur LIMIT {limit} OFFSET {offset}'

            if sql:
                cursor = connection.cursor()
                cursor.execute(sql)
                listDocs = cursor.fetchall()
                if not listDocs:
                    msg = "There s NO doctor in the database"
                    return jsonify({"message " : msg})
                listDistances = []
                user_Address = getUserAddressFromFlutter()
                if (user_Address is None):
                    msg = "Probleme de localisation user flutter" 
                    return jsonify({"message " : msg})
                user_position = AddressToPosition(user_Address)
                i = 0
                for doc in listDocs:
                    d1 = AddressToPosition(doc[3])
                    listDistances.append({
                        "distance": calculDistances(d1, user_position),
                        "nomDoc": doc[4],
                        "location": doc[3],
                        "speciality": doc[5],
                        "Mail": doc[1]
                    })
                listDistances.sort(key=lambda d: d["distance"])
                return jsonify(listDistances)

            else:
                msg = "Probleme de requete de recherche des medecins , mais la connection avec la DB fonctionne "

        else:
            msg = "Probleme de connection avec la DB "

    except Exception as e:
        msg = f"Error: {str(e)}"

    return jsonify({"message" : msg}) 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

