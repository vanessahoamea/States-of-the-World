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
    values = [request.json[key] for key in request.json]
    success = True

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("SELECT * FROM countries WHERE name = '{}'".format(request.json["name"]))
        if(len(cursor.fetchall())) > 0:
            raise Exception("country already exists")

        cursor.execute("INSERT INTO countries VALUES ('{}', '{}', '{}', {}, {}, {}, '{}', '{}', '{}')".format(*values))
        mysql.connection.commit()

        cursor.close()
    except Exception as e:
        print("Problem inserting into database: " + str(e))
        success = False
    
    return jsonify({"success": success})

if __name__ == "__main__":
    app.run(debug=True)