import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["imagechain_db"]

# Check all stored files
files = db["fs.files"].find({})
for file in files:
    print(file)
import gridfs
from bson import ObjectId

fs = gridfs.GridFS(db)

try:
    file_id = ObjectId("67d830fcfe80af38cfccceba")  # Replace with actual ID
    file_data = fs.get(file_id).read()
    print("Image retrieved successfully")
except Exception as e:
    print("Error:", e)
