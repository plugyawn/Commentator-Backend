import datetime
import json
import os
import shutil
import time
import requests

import flask
from bson import json_util
from flask import jsonify, request
from flask_cors import CORS, cross_origin

from pymongo import MongoClient
# from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

API_URL = "https://api-inference.huggingface.co/models/sagorsarker/codeswitch-hineng-ner-lince"
headers = {"Authorization": f"Bearer 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"}

# tokenizer = AutoTokenizer.from_pretrained(
#     "sagorsarker/codeswitch-hineng-ner-lince")

# model = AutoModelForTokenClassification.from_pretrained(
#     "sagorsarker/codeswitch-hineng-ner-lince")

client = MongoClient(
    'mongodb+srv://root:sjjoshi@cluster0.5xthhz8.mongodb.net/test')

db = client.hinglish
app = flask.Flask(__name__)
app.config["DEBUG"] = True
CORS(app)


@app.route('/getWordFreqeucy', methods=['GET'])
@cross_origin()
def api_getWordFrequency():
    word = request.args.get("word")

    col1 = db.Frequency
    docs = col1.find({'Word': word})
    l = []
    for d in docs:
        del d['_id']
        l.append(d)
    return jsonify(json.loads(json_util.dumps(l)))


@app.route('/saveFrequency', methods=['POST'])
@cross_origin()
def update_whitelisting():
    if request.method == 'POST':
        data = request.json
        collection = db.Frequency
        col1 = db.Words

        for i in data:
            word = i['Word']
            tag = i['Tag']
            # print(word)
            # print(tag)
            docs = col1.find({'Word': word})
            curr = list(docs)
            if len(curr) == 0:
                dict = {
                    'Word': word,
                    'Tag': {
                        "person": 0,
                        "orgnz": 0,
                        "product": 0,
                        "date": 0,
                        "place": 0,
                        "slang": 0,
                        "none": 0,
                    }
                }
                # print(dict)

                dict1 = {'Word': word}
                x = col1.insert_one(dict1)
                z = collection.insert_one(dict)
            docs = collection.find({'Word': word})
            for d in docs:
                # print(d)
                dict2 = d["Tag"]
                # print(dict2)
                dict2[tag] += 1
                myquery = {'Word': word}
                newvalues = {"$set": {'Tag': dict2}}
                collection.update_one(myquery, newvalues)

        return jsonify({"msg": "successful"})


@app.route('/initialTagging', methods=['GET', 'POST'])
@cross_origin()
def api_initialtagging():
    if request.method == 'POST':
        # text = request.args.get("word")
        # ner_model = pipeline('ner', model=model, tokenizer=tokenizer)
        # x = ner_model(text)
        text = str(request.json["data"])
        payload = {
            "inputs": text
        }
        response = requests.post(API_URL, headers=headers, json=payload)
        # print(response.json())
        return jsonify(response.json())


app.run(host='0.0.0.0', port=8080)
client.close()
