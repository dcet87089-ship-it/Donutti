"""
Bonnie Resort & Sanctuary Chiang Mai - Robust Backend System
FastAPI Backend Architecture with Concurrency Lock & Double-Booking Prevention

คำอธิบาย:
ระบบหลังบ้านนี้สร้างด้วย Python (FastAPI) โดยใช้กลไก Concurrency Atomic Locking
เพื่อรับประกันว่า แม้มีผู้ใช้งานกดจองวิลล่าห้องเดียวกันในเสี้ยววินาทีเดียวกัน
ระบบจะยอมรับการจองได้เพียง 1 คำขอเท่านั้น และแจ้งสถานะห้องเต็มแก่คำขอที่ชนกันอย่างถูกต้อง 100%
"""

import os
import sys
import asyncio
import threading
import webbrowser
from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# ป้องกัน UnicodeEncodeError บน Windows terminal (cp1252)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

app = FastAPI(
    title="Bonnie Resort Chiang Mai Reservation API",
    description="High-concurrency robust booking engine for Bonnie Resort Chiang Mai",
    version="1.0.0"
)

# อนุญาต CORS สำหรับการเรียกใช้งานจากหน้าเว็บ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# 1. Models & Schemas
# ----------------------------------------------------
class Room(BaseModel):
    id: str
    name_th: str
    name_fr: str
    description: str
    price_per_night: float
    total_inventory: int
    available_inventory: int
    image_360_url: str

class ReservationRequest(BaseModel):
    room_id: str
    guest_name: str
    guest_email: str
    check_in: str
    check_out: str
    guests_count: int = Field(default=2, ge=1, le=10)

class ReservationResponse(BaseModel):
    success: bool
    booking_token: str
    message: str
    room_name: str
    check_in: str
    check_out: str
    total_amount: float
    timestamp: str

# ----------------------------------------------------
# 2. Database State & Concurrency Distributed Locks
# ----------------------------------------------------
# จำลองคลังห้องพักในระบบ
ROOM_DATABASE: Dict[str, Room] = {
    "room_king_suite": Room(
        id="room_king_suite",
        name_th="บอนนี่ แกรนด์ ล้านนา สวีท (Bonnie Grand Lanna Suite)",
        name_fr="Signature Teak Villa",
        description="เรือนไม้สักทองโบราณผสมผสานความหรูหราร่วมสมัย เตียงคิงไซส์ผ้าไหมสันกำแพงทอมือ พร้อมระเบียงกว้างเปิดรับสายหมอก",
        price_per_night=28500.0,
        total_inventory=1,  # ห้องพิเศษเอกสิทธิ์ มีเพียง 1 ห้องเท่านั้น!
        available_inventory=1,
        image_360_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?q=80&w=2071"
    ),
    "room_hall_mirrors": Room(
        id="room_hall_mirrors",
        name_th="ดอยสุเทพ ซันเซ็ต พูลวิลล่า (Doi Suthep Sunset Pool Villa)",
        name_fr="Doi Suthep Horizon View",
        description="พูลวิลล่าส่วนตัวพร้อมสระว่ายน้ำอินฟินิตี้หันหน้าสู่ยอดดอยสุเทพ สัมผัสแสงสีทองยามเย็นและสายหมอกยามเช้า",
        price_per_night=22000.0,
        total_inventory=2,
        available_inventory=2,
        image_360_url="https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?q=80&w=2070"
    ),
    "room_orangerie": Room(
        id="room_orangerie",
        name_th="แม่ริม ฟอเรสต์ แซงค์ทัวรี (Mae Rim Forest Sanctuary)",
        name_fr="Botanical Garden Villa",
        description="วิลล่ากระจกพาโนรามาท่ามกลางป่าธรรมชาติและสวนพฤกษศาสตร์เมืองเหนือ ดื่มด่ำความเงียบสงบและธารน้ำไหล",
        price_per_night=16500.0,
        total_inventory=3,
        available_inventory=3,
        image_360_url="https://images.unsplash.com/photo-1578683010236-d716f9a3f461?q=80&w=2070"
    )
}

# Concurrency Locks: ใช้ Lock แยกตาม Room ID เพื่อประสิทธิภาพสูงสุด (Fine-grained Lock)
# ป้องกัน Race Condition เมื่อมี request เข้ามาในเสี้ยว millisecond เดียวกัน
ROOM_LOCKS: Dict[str, asyncio.Lock] = {
    room_id: asyncio.Lock() for room_id in ROOM_DATABASE.keys()
}

CONFIRMED_BOOKINGS: List[dict] = []

# ----------------------------------------------------
# 3. API Endpoints
# ----------------------------------------------------
@app.get("/api/rooms", response_model=List[Room])
async def get_rooms():
    """ดึงข้อมูลห้องพักและจำนวนห้องว่างแบบ Real-time"""
    return list(ROOM_DATABASE.values())

@app.get("/api/rooms/{room_id}", response_model=Room)
async def get_room(room_id: str):
    if room_id not in ROOM_DATABASE:
        raise HTTPException(status_code=404, detail="ไม่พบห้องพักที่ระบุ")
    return ROOM_DATABASE[room_id]

@app.post("/api/reserve", response_model=ReservationResponse)
async def reserve_room(req: ReservationRequest):
    """
    ระบบจองห้องแบบ Robust Concurrency Guard
    ใช้ Async Lock ป้องกันการจองห้องเดียวกันพร้อมกัน (Race Condition / Double Booking)
    """
    if req.room_id not in ROOM_DATABASE:
        raise HTTPException(status_code=404, detail="รหัสห้องพักไม่ถูกต้อง")

    room_lock = ROOM_LOCKS[req.room_id]
    
    # ดักจับ Concurrency Lock อย่างเข้มงวด
    async with room_lock:
        room = ROOM_DATABASE[req.room_id]
        
        # จำลองการตรวจสอบ I/O หรือ Database Check (50ms)
        await asyncio.sleep(0.05)
        
        # ตรวจสอบว่ายังมีห้องว่างเหลือหรือไม่
        if room.available_inventory <= 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"ขออภัยอย่างสูง ห้องพัก '{room.name_th}' ถูกจองเต็มแล้วในขณะนี้ (Concurrency Conflict Blocked)"
            )
            
        # ลดจำนวนห้องว่างทันทีแบบ Atomic Operation
        room.available_inventory -= 1
        
        # คำนวณราคาและออกรหัสยืนยันแบบพระราชวัง
        token = f"BONNIE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{req.room_id[:4].upper()}"
        
        booking_record = {
            "token": token,
            "room_id": req.room_id,
            "guest_name": req.guest_name,
            "check_in": req.check_in,
            "check_out": req.check_out,
            "created_at": datetime.now().isoformat()
        }
        CONFIRMED_BOOKINGS.append(booking_record)
        
        return ReservationResponse(
            success=True,
            booking_token=token,
            message="การจองห้องพักพระราชวังของท่านได้รับการยืนยันเรียบร้อยแล้ว",
            room_name=room.name_th,
            check_in=req.check_in,
            check_out=req.check_out,
            total_amount=room.price_per_night * 2,
            timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        )

@app.post("/api/reset-inventory")
async def reset_inventory():
    """รีเซ็ตจำนวนห้องสำหรับการทดสอบ Concurrency Simulation"""
    ROOM_DATABASE["room_king_suite"].available_inventory = 1
    ROOM_DATABASE["room_hall_mirrors"].available_inventory = 2
    ROOM_DATABASE["room_orangerie"].available_inventory = 3
    CONFIRMED_BOOKINGS.clear()
    return {"status": "success", "message": "คลังห้องพักได้รับการรีเซ็ตแล้ว"}

@app.get("/", response_class=FileResponse)
async def serve_index():
    """แสดงหน้าเว็บจองโรงแรมสไตล์แวร์ซายส์ที่หน้าแรก"""
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    return FileResponse(html_path)

def find_available_port(start_port=8000, max_tries=10):
    import socket
    for p in range(start_port, start_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', p)) != 0:
                return p
    return start_port

if __name__ == "__main__":
    import uvicorn
    port = find_available_port(8000)
    server_url = f"http://127.0.0.1:{port}"

    print("=================================================================")
    print(f" Bonnie Resort Server is starting on: {server_url}")
    print(f" API Documentation (Swagger UI): {server_url}/docs")
    print(" Automatically opening web browser in 1.5 seconds...")
    print(" Press Ctrl + C in this terminal to stop the server")
    print("=================================================================")

    # เปิดเบราว์เซอร์แสดงหน้าเว็บอัตโนมัติ
    threading.Timer(1.5, lambda: webbrowser.open(server_url)).start()
    uvicorn.run(app, host="127.0.0.1", port=port)

