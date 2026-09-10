# ⚜️ Le Grand Versailles - Hôtel & Résidences Royales
> เว็บไซต์จองโรงแรมพระราชวังแวร์ซายส์เสมือนจริง (Versailles Palace Virtual Experience) พร้อมระบบสำรวจ 360 องศา และระบบหลังบ้านป้องกัน Concurrency Race Condition

---

## 🌟 จุดเด่นของโปรเจกต์ (Key Pillars)

1. **Visual-First Elegance (สุนทรียภาพแห่งศิลปะราชสำนักฝรั่งเศส):**
   - ธีมสี Royal Gold, Velvet Burgundy และหินอ่อน พร้อมเอฟเฟกต์ละอองทองคำ (Gold Dust Canvas)
   - ฟอนต์หรูหรา Cinzel, Playfair Display และ Noto Serif Thai
   - ดนตรีบรรเลงสไตล์ฮาร์ปซิคอร์ดบารอก (Baroque Ambience Synthesizer) เปิด-ปิดได้
   - รองรับการแสดงผลทุกหน้าจออย่างสมบูรณ์แบบ (Fully Mobile & Tablet Responsive)

2. **Immersive 360° Exploration (สำรวจพระราชวังรอบทิศทาง):**
   - ฝังระบบ **Pannellum 360° Virtual Tour** สามารถลากหมุนชมห้องได้รอบทิศ
   - **ระบบหมุนตามเมาส์ (Mouse Follow Mode):** เพียงขยับเมาส์ กล้องจะแพนตามตำแหน่งเมาส์ทันที
   - **แถบปุ่มลัดเลือกดูแต่ละฝั่ง:** ฝั่งซ้าย, ฝั่งขวา, เพดาน & แชนเดอเลียร์, พื้นห้อง, และกลับหลัง 180°
   - สลับชมได้ 3 โซน: *La Chambre du Roi*, *Galerie des Glaces*, และ *L'Orangerie*

3. **Robust Backend Architecture (ระบบหลังบ้านป้องกันการจองซ้อน):**
   - พัฒนาด้วย **Python (FastAPI)**
   - สถาปัตยกรรม **Concurrency Lock / Atomic Reservation Guard**
   - ป้องกันปัญหา Race Condition เมื่อมีผู้ใช้งานหลายคนกดจองห้องชุดห้องสุดท้ายพร้อมกันในเสี้ยววินาทีเดียวกัน
   - หน้าเว็บมี **Live Concurrency Simulator Console** สำหรับทดสอบการแย่งจองห้องจริง

---

## 🚀 วิธีการรันโปรเจกต์ (Getting Started)

### วิธีที่ 1: เปิดดูหน้าเว็บทันที (Frontend Only)
- ดับเบิลคลิกเปิดไฟล์ `index.html` บนเว็บเบราว์เซอร์ (Google Chrome, Microsoft Edge, Safari) ได้ทันที

### วิธีที่ 2: รันระบบเซิร์ฟเวอร์หลังบ้าน (FastAPI Backend + Frontend)
1. ติดตั้งแพ็กเกจที่จำเป็น:
   ```bash
   pip install -r requirements.txt
   # หรือ
   pip install fastapi uvicorn pydantic
   ```
2. รันเซิร์ฟเวอร์:
   ```bash
   python backend_app.py
   ```
3. เซิร์ฟเวอร์จะเปิดทำงานที่ `http://127.0.0.1:8000` และเปิดหน้าต่างเบราว์เซอร์ให้อัตโนมัติ:
   - **หน้าเว็บไซต์หลัก:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - **เอกสาร API (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
