from ultralytics import YOLO
from glob import glob
import json

files = glob("./implantdetect-backend/uploads/*.jpg")
model = YOLO('./models/train10/weights/best.pt')

print(files)
for file in files:
    print(file)
    results = model.predict(source=file,
                            conf=0.1,
                            )
    
    for r in results:
        print(json.loads(r.to_json())[0])
    