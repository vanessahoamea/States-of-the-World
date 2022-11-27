from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "world_states"

mysql = MySQL(app)

@app.route("/")
def default():
    return "Hello world!"

@app.route("/add", methods = ["POST"])
def add_country():
    values = [request.json[key] if request.json[key] != None else "null" for key in request.json]
    value_types = ["'{}'" if type(request.json[key]) == str else "{}" for key in request.json]
    success = True

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("SELECT * FROM countries WHERE name = '{}'".format(request.json["name"]))
        if(len(cursor.fetchall())) > 0:
            raise Exception("country already exists")

        query = "INSERT INTO countries VALUES ({})".format(", ".join(value_types))
        cursor.execute(query.format(*values))
        mysql.connection.commit()
    except Exception as e:
        print("Problem inserting into database: " + request.json["name"] + " - " + str(e))
        success = False
    finally:
        cursor.close()
    
    return jsonify({"success": success})

if __name__ == "__main__":
    app.run(debug=True)