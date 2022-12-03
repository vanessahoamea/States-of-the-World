"""
This module handles implementing the API to which a client will make
calls to, in order to obtain information about various countries.
"""

__version__ = "0.1"
__author__ = "Vanessa Hoamea"

import json
from flask import Flask, request, jsonify, Response
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configuring the database
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "world_states"

mysql = MySQL(app)

"""The default endpoint. Returns a welcome message."""
@app.route("/")
def default():
    return "Welcome to the States of the World API!"

"""
The /add endpoint. Used by the crawler for adding new entries to the
'countries' table.
"""
@app.route("/add", methods=["POST"])
def add_country():
    body = request.json
    values = [body[key] if body[key] != None else "null" for key in body]
    success = True

    try:
        cursor = mysql.connection.cursor()

        # If the given country already exists in the database, we won't
        # store it in twice
        query = "SELECT * FROM countries WHERE name = %s"
        cursor.execute(query, [body["name"]])
        if cursor.fetchone():
            raise Exception("country already exists")

        cursor.close()
        cursor = None
        query = None

        cursor = mysql.connection.cursor()

        query = "INSERT INTO countries VALUES \
                 (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, values)

        mysql.connection.commit()
    except Exception as e:
        print("Problem inserting into database: " 
              + body["name"] + " - " + str(e))
        success = False
    finally:
        cursor.close()
    
    return jsonify({"success": success})

"""
The /top-10 endpoint. Returns the top 10 countries sorted by the given
parameter. If none is provided, it will default to 'population'.
"""
@app.route("/top-10", methods=["GET"])
def get_top_10_default():
    return get_top_10("population")

@app.route("/top-10/<parameter>", methods=["GET"])
def get_top_10(parameter):
    parameter = parameter.lower().strip()

    if parameter not in ["population", "area", "density"]:
        result = jsonify({
            "message": "The only valid parameters for this \
                        endpoint are: population, area, density."
        })
        return result

    try:
        cursor = mysql.connection.cursor()

        query = "SELECT * FROM countries ORDER BY {} DESC".format(parameter)
        cursor.execute(query)
        records = cursor.fetchall()[:10]

        result = []
        for record in records:
            country = {
                "name": record[0],
                "capital": record[1],
                "language": record[2].replace("\"", ""),
                "population": record[3],
                "density (per km2)": record[4],
                "area (km2)": record[5],
                "time_zone": record[6],
                "currency": record[7],
                "government": record[8]
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

"""
The /all endpoint. Returns every entry in the database that fulfills
a certain condition, given by the query parameters.
"""
@app.route("/all", methods=["GET"])
def get_all():
    args = request.args
    pairs = []
    values = []

    # The format of the database query depends on which set
    # of query parameters was given
    for key in ["name", "capital", "population", 
                "density", "area", "currency"]:
        if key in args:
            pairs.append("lower(" + key + ") = %s")
            values.append(args[key].lower().strip())

    for key in ["language", "government"]:
        if key in args:
            pairs.append("lower(" + key + ") LIKE %s")
            values.append("%" + args[key].lower().strip() + "%")
    
    if "time_zone" in args:
        value = args["time_zone"].lower().strip()

        if ("+" not in value) and ("-" not in value):
            pairs.append("lower(time_zone) = %s")
            values.append(value)
        else:
            if "+" in value:
                split = value.split("+")
                sign = "+"
            else:
                split = value.split("-")
                sign = "-"

            pairs.append("lower(time_zone) = %s \
                          OR lower(time_zone) = %s \
                          OR lower(time_zone) = %s \
                          OR lower(time_zone) = %s")
            values.append(value)
            values.append(value + ":00")
            values.append(split[0] + sign + "0" + split[1])
            values.append(split[0] + sign + "0" + split[1] + ":00")
    
    # If no valid query parameters are provided, it will return
    # information about every single country found in the database
    if len(pairs) == 0:
        pairs = ["1"]
    
    try:
        cursor = mysql.connection.cursor()

        query = "SELECT * FROM countries WHERE {}".format(" AND ".join(pairs))
        cursor.execute(query, values)
        records = cursor.fetchall()

        result = []
        for record in records:
            country = {
                "name": record[0],
                "capital": record[1],
                "language": record[2].replace("\"", ""),
                "population": record[3],
                "density (per km2)": record[4],
                "area (km2)": record[5],
                "time_zone": record[6],
                "currency": record[7],
                "government": record[8]
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

"""The main function that allows the API to run."""
if __name__ == "__main__":
    app.run(debug=True)