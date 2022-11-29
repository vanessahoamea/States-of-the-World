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
    body = request.json
    values = [body[key] if body[key] != None else "null" for key in body]
    success = True

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("SELECT * FROM countries WHERE name = %s", [body["name"]])
        if cursor.fetchone():
            raise Exception("country already exists")

        cursor.close()

        cursor = None
        cursor = mysql.connection.cursor()

        query = "INSERT INTO countries VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, values)

        mysql.connection.commit()
    except Exception as e:
        print("Problem inserting into database: " + body["name"] + " - " + str(e))
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

        query = "SELECT * FROM countries ORDER BY {} DESC".format(parameter)
        cursor.execute(query)
        records = cursor.fetchall()[:10]

        result = []
        for record in records:
            country = {
                "name": record[0],
                "capital": record[1],
                "language": record[2],
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

@app.route("/all", methods=["GET"])
def get_all():
    args = request.args.to_dict()
    pairs = []
    values = []

    for key in ["name", "capital", "population", "density", "area", "currency"]:
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
            split = value.split("+") if "+" in value else value.split("-")
            sign = "+" if "+" in value else "-"

            pairs.append("lower(time_zone) = %s OR lower(time_zone) = %s OR lower(time_zone) = %s OR lower(time_zone) = %s")
            values.append(value)
            values.append(value + ":00")
            values.append(split[0] + sign + "0" + split[1])
            values.append(split[0] + sign + "0" + split[1] + ":00")
    
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
                "language": record[2],
                "population": record[3],
                "density (per km2)": record[4],
                "area (km2)": record[5],
                "time_zone": record[6],
                "currency": record[7],
                "government": record[8]
            }
            result.append(country)

        result = Response(json.dumps(result), mimetype="application/json")
    except Exception as e:
        print(str(e))
        result = jsonify({
            "message": "There was a problem reading from the database."
        })
    finally:
        cursor.close()

    return result

if __name__ == "__main__":
    app.run(debug=True)