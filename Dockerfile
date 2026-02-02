# ใช้ Python 3.9
FROM python:3.9

# ตั้งโฟลเดอร์ทำงาน
WORKDIR /code

# ลง Library สำหรับอ่านรูปภาพ (OpenCV) ที่ Server มักจะขาด
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# ก๊อปปี้ไฟล์ requirements และติดตั้ง
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# ก๊อปปี้โค้ดทั้งหมด
COPY . .

# สร้างโฟลเดอร์สำหรับ cache ของ matplotlib/yolo (แก้ปัญหา permission)
RUN mkdir -p /.config/Ultralytics && chmod -R 777 /.config

# เปิดพอร์ต 7860 (มาตรฐาน Hugging Face)
CMD ["gunicorn", "-b", "0.0.0.0:7860", "main:app"]
