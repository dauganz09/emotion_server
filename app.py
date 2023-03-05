from flask import Flask, request
from flask import jsonify
import numpy as np
import pandas as pd
import pickle
from flask_cors import CORS
from flask import Response
from flask_mysqldb import MySQL


app = Flask(__name__)

app.config['MYSQL_HOST'] = 'sql545.main-hosting.eu'
app.config['MYSQL_USER'] = 'u972026743_admin'
app.config['MYSQL_PASSWORD'] = 'Admin123'
app.config['MYSQL_DB'] = 'u972026743_caring'

mysql = MySQL(app)

CORS(app)
model = pickle.load(open('model.pkl', 'rb'))


@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()


@app.route('/analyze/', methods=['POST'])
def analyze_api():
    cursor = mysql.connection.cursor()
    data = request.get_json(force=True)
    # prediction = model.predict([data["comment"]])
    # output = prediction[0]
    emotions = []
    for comment in data['questions']:

        prediction = model.predict([comment["comment"]])

        output = prediction[0]
        cursor.execute('INSERT INTO tbl_emotions (question_id,user_id,comment,emotion) values (%s,%s,%s,%s)',
                       (comment["question_id"], data['user_id'], comment["comment"], output))
        mysql.connection.commit()
        em = {'qid': comment["question_id"], 'emotion': output}
        emotions.append(em)
    # cursor.execute('INSERT INTO tbl_emotions values (NULL,%s,%s,%s,%s)',
    #                (data["question_id"], data["user_id"], data["comment"], output))
    # mysql.connection.commit()

    return jsonify(emotions=emotions)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
