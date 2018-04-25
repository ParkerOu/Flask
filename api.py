import os
from flask import Flask, jsonify, request, render_template
from flask_pymongo import PyMongo
from flask_uploads import UploadSet, configure_uploads, IMAGES
from similar_images.similarity import main
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

app = Flask(__name__)

# app.config['MONGO_DBNAME'] = 'databasename'
# app.config['MONGO_URI'] = 'mongodb://username:password@hostname:port/databasename'
# mongoDB
app.config['MONGO_DBNAME'] = 'missingdog'
app.config['MONGO_URI'] = 'mongodb://iii:dog@localhost:27017/missingdog'
mongo = PyMongo(app)
# upload images
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'query'
# sconfigure_uploads(app, photos)

#ES
client = Elasticsearch()
s = Search(using=client, index="thread")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/find')
def finddog():
    return render_template('findDog.html')

@app.route('/search', methods=['GET','POST'])
def searchtxt():

    start_date = request.form.get('st')
    end_date = request.form.get('et')
    searchfor = request.form.get('q')

    response = client.search(
    index="thread",
    body={
      "query" : {
  "bool": {
      "must": [
           { "match": { "title": searchfor }},
           { "match": { "content": searchfor }}
        ],
        "filter": {
        "range" : {
            "post_date" : {
                "gte": start_date,
                "lte": end_date,
                "format": "yyyy-dd-MM||yyyy"
            }
        }
    }}
},
    "highlight": {
        "fields" : {
            "title" : {},
            "content" : {}
        }
    },
  "_source" : {
  "excludes" : [
  "id",
  "_id",
  "page",
  "auhtor_info",
  "author_url"
  ]
 }
    }
)
    return render_template('search.html', response = response)


'''
# @app.route('/collection/<field>', methods=['GET'])
@app.route('/dogInfo/<id>', methods=['GET'])
def get_one_info(id):
    dogInfo = mongo.db.dogInfo

    q = dogInfo.find_one({"$or":[ {"名稱": id + '.jpg'}, {"名稱": id + '.png'}]})

    if q:
        output = {'ID' : q['_id'], 'location' : q['所在地'], 'breed' : q['狗種'], 'url' : q['網址']}
    else:
        output = 'No results found'

    return jsonify({'result' : output})
'''

@app.route('/upload', methods=['GET' ,'POST'])
def upload_file():

    if request.method == 'POST' and 'photo' in request.files:
        # filename = photos.save(request.files['photo'])
        file = request.files['photo']
        file.save(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], 'missing.jpg'))
        similist = main()
        # mongoDB
        dogInfo = mongo.db.dogInfo
        q0 = dogInfo.find_one({"$or":[ {"名稱": similist[0] + '.jpg'}, {"名稱": similist[0] + '.png'}]})
        q1 = dogInfo.find_one({"$or":[ {"名稱": similist[1] + '.jpg'}, {"名稱": similist[1] + '.png'}]})
        q2 = dogInfo.find_one({"$or":[ {"名稱": similist[2] + '.jpg'}, {"名稱": similist[2] + '.png'}]})
        q3 = dogInfo.find_one({"$or":[ {"名稱": similist[3] + '.jpg'}, {"名稱": similist[3] + '.png'}]})
        q4 = dogInfo.find_one({"$or":[ {"名稱": similist[4] + '.jpg'}, {"名稱": similist[4] + '.png'}]})
        
        return render_template('findDogResult.html', dog1ID=q0['_id'], dog1loc=q0['所在地'], dog1breed=q0['狗種'], dog1url=q0['網址'], dog2ID=q1['_id'], dog2loc=q1['所在地'], dog2breed=q1['狗種'], dog2url=q1['網址'], dog3ID=q2['_id'], dog3loc=q2['所在地'], dog3breed=q2['狗種'], dog3url=q2['網址'], dog4ID=q3['_id'], dog4loc=q3['所在地'], dog4breed=q3['狗種'], dog4url=q3['網址'], dog5ID=q4['_id'], dog5loc=q4['所在地'], dog5breed=q4['狗種'], dog5url=q4['網址'])

    return render_template('findDog.html')

if __name__ == '__main__':
    app.run(debug=True)
