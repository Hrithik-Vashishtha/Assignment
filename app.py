from flask import Flask, jsonify, request
from pymongo import MongoClient
import redis

app = Flask(__name__)

# Initialize MongoDB client
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['mydatabase']
project_collection = db['projects']

# Initialize Redis client
redis_client = redis.Redis(host='127.0.0.1', port=6379)

#1. Insert Data
@app.route('/insert', methods=['POST'])
def insert_data():
    payload = request.get_json()
    
    # Insert project data into MongoDB
    result = project_collection.insert_one(payload)

    # Get the inserted document's ID
    inserted_id = str(result.inserted_id)
    
    # Clear Redis cache for the inserted data (if exists)
    redis_client.delete(str(result.inserted_id))
    
    return jsonify({'message': 'Project created successfully!', 'id': inserted_id}), 201

#2. Retrieve Data
@app.route('/retrieve', methods=['GET'])
def get_data():
    # Check if the data exists in Redis cache 
    # import pdb
    # pdb.set_trace()
    cached_data = redis_client.get('project_data')
    if cached_data:
        return jsonify(cached_data.decode()), 200

    # Define the aggregation pipeline
    pipeline = [
        {
            '$project': {
                'prj_id': {
                    '$toString': '$_id'
                },
                'name': 1,
                'age': 1,
                'city': 1
            }
        }
    ]

    # Execute the aggregation pipeline
    data = list(project_collection.aggregate(pipeline))

    if data:
        # Store data in Redis cache
        redis_client.set('project_data', str(data))
        return jsonify(data), 200

    return jsonify(message='No project data found'), 404

if __name__ == '__main__':
    app.run(debug=True)
