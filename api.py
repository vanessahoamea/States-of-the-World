from flask import Flask, request, jsonify, Response
from flask_mysqldb import MySQL
import json

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "world_states"

mysql = MySQL(app)

@app.route("/")
def default():
    return "Hello world!"

@app.route("/add", methods=["POST"])
def add_country():
    values = [request.json[key] if request.json[key] != None else "null" for key in request.json]
    success = True

    try:
        cursor = mysql.connection.cursor()

        query = "SELECT * FROM countries WHERE name = %s"
        cursor.execute(query, [request.json["name"]])

        if cursor.fetchone():
            raise Exception("country already exists")
    except Exception as e:
        print("Problem inserting into database: " + request.json["name"] + " - " + str(e))
        success = False
    finally:
        cursor.close()
        return jsonify({"success": success})

    try:
        cursor = mysql.connection.cursor()

        query = "INSERT INTO countries VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, values)

        mysql.connection.commit()
    except Exception as e:
        print("Problem inserting into database: " + request.json["name"] + " - " + str(e))
        success = False
    finally:
        cursor.close()
        return jsonify({"success": success})

@app.route("/top-10/<parameter>", methods=["GET"])
def get_top_10(parameter):
    parameter = parameter.lower().strip()

    if parameter not in ["population", "area", "density"]:
        result = jsonify({
            "message": "The only valid parameters for this endpoint are: population, area, density."
        })
        return result

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("SELECT name, {} FROM countries ORDER BY {} DESC".format(parameter, parameter))
        records = cursor.fetchall()[:10]

        if parameter == "area":
            parameter += " (km2)"
        if parameter == "density":
            parameter += " (per km2)"

        result = []
        for record in records:
            country = {
                "name": record[0],
                parameter: record[1]
            }
            result.append(country)

        result = Response(json.dumps(result), mimetype="application/json")
    except:
        result = jsonify({
            "message": "There was a problem reading from the database."
        })
    finally:
        cursor.close()
    
    return result

if __name__ == "__main__":
    app.run(debug=True)