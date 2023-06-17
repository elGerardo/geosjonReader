from flask import Flask, request
from dotenv import load_dotenv
from connection import Database
import os
import json
import uuid

app = Flask(__name__)

@app.route('/', methods=['POST'])
def upload():

    try:
        geojsonFile = request.files['geojson']
    except:
        return { "data": "geojson field not found" }
    
    _, extension = os.path.splitext(geojsonFile.filename)
    
    if(extension != ".geojson"):
        return { "data": "file is not .geojson" } 
    
    try:
        jsonData = json.loads(geojsonFile.read())
    except:
        return { "data": "invalid data file structure" }
    
    conn = Database.connect()
    cursor = conn.cursor()

    tilesetUuid = str(uuid.uuid4())

    sql = "INSERT INTO tilesets (id, name, type) VALUES (%s, %s, %s)"
    values = (tilesetUuid, jsonData["name"], jsonData["type"])
    cursor.execute(sql, values)
    conn.commit()

    for feature in jsonData["features"]:
        featureUuid = str(uuid.uuid4())
        sql = "INSERT INTO features (id, tileset_id, type) VALUES (%s, %s, %s)"
        values = (featureUuid, tilesetUuid, feature["type"])
        cursor.execute(sql, values)
        conn.commit()

        for field, value in feature['properties'].items():
            fieldUuid = str(uuid.uuid4())
            sql = "INSERT INTO fields(id, feature_id, name, value, is_seen) VALUES (%s, %s, %s, %s, %s)"
            values = (fieldUuid, featureUuid, field, value, True)
            cursor.execute(sql, values)
            conn.commit()

        geometryUuid = str(uuid.uuid4())
        sql = "INSERT INTO geometry(id, feature_id, type) VALUES (%s, %s, %s)"
        values = (geometryUuid, featureUuid, feature["geometry"]["type"])
        cursor.execute(sql, values)
        conn.commit()

        if(feature["geometry"]["type"] == "MultiPolygon"):
            for coordinates in feature["geometry"]["coordinates"][0]:
                sql = "INSERT INTO coordinates(geometry_id, long, lat) VALUES (%s, %s, %s)"
                values = (geometryUuid, coordinates[0], coordinates[1])
                cursor.execute(sql, values)
                conn.commit()
        
        if(feature["geometry"]["type"] == "Point"):
            sql = "INSERT INTO coordinates(geometry_id, long, lat) VALUES (%s, %s, %s)"
            values = (geometryUuid, feature["geometry"]["coordinates"][0], feature["geometry"]["coordinates"][1])
            cursor.execute(sql, values)
            conn.commit()

    cursor.close()
    conn.close()

    return jsonData

if __name__ == '__main__':
    load_dotenv('.flaskenv')
    app.run(debug=os.getenv('APP_DEBUG'), port=os.getenv('APP_PORT'), host=os.getenv('APP_HOST'))


