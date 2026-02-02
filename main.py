import os
from flask import Flask, request, jsonify
from ultralytics import YOLO
import requests

app = Flask(__name__)

# โหลดโมเดล
model = YOLO('best.pt')

# --- ตั้งค่า AppSheet API ---
APPSHEET_APP_ID = "93ca0421-6084-4e8e-a8ee-01d5749bec5d"
APPSHEET_ACCESS_KEY = "V2-n6Jyt-BU3fK-lDSTw-KOoV9-pOXyz-OgIH2-ifo01-PTpGf"
TABLE_NAME = "V.1 AI YOLO"
COLUMN_NAME_TO_UPDATE = "AI_Type"  # ชื่อคอลัมน์เก็บผลลัพธ์

@app.route('/', methods=['GET'])
def home():
    return "Plastic AI Detection is Running!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        print("Received data:", data)
        
        image_url = data.get('image_url')
        row_id = data.get('row_id')

        if not image_url or not row_id:
            return jsonify({"error": "Missing image_url or row_id"}), 400

        # 1. ให้ AI ทำนาย (Detection Mode)
        results = model(image_url)
        
        # ดึงผลลัพธ์แบบ Object Detection (Boxes)
        if len(results[0].boxes) > 0:
            # เอาวัตถุชิ้นแรกที่เจอ (ที่มีความมั่นใจสูงสุด)
            box = results[0].boxes[0]
            class_id = int(box.cls[0])
            predicted_class = results[0].names[class_id]
            confidence = box.conf[0].item() # ค่าความมั่นใจ (เช่น 0.97)
        else:
            predicted_class = "Not Found"
            confidence = 0.0
        
        print(f"Result: {predicted_class} ({confidence:.2f})")

        # 2. ส่งผลกลับไป AppSheet
        url = f"https://api.appsheet.com/api/v2/apps/{APPSHEET_APP_ID}/tables/{TABLE_NAME}/Action"
        
        payload = {
            "Action": "Edit",
            "Properties": {
                "Locale": "en-US",
                "Timezone": "Asia/Bangkok"
            },
            "Rows": [
                {
                    "Student ID": row_id,  # <--- แก้เป็น Student ID ตามคีย์จริงของคุณ
                    COLUMN_NAME_TO_UPDATE: predicted_class,
                    "AI_Confidence": f"{confidence:.2f}" # ส่งค่าความมั่นใจกลับไปด้วย
                }
            ]
        }
        
        headers = {
            "ApplicationAccessKey": APPSHEET_ACCESS_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        print("AppSheet Response:", response.text)

        return jsonify({
            "status": "success", 
            "prediction": predicted_class,
            "confidence": confidence
        })

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)