from app.db import Base, SessionLocal, engine
from app.models import Machine, MaintenanceRecord


Base.metadata.create_all(bind=engine)


MACHINES = [
    {
        "machine_id": "CNC-001",
        "asset_code": "ASSET-CNC-001",
        "manufacturer": "DMG MORI",
        "series": "CMX",
        "model": "CMX-1100V",
        "location": "Area A - Line 1",
        "install_date": "2021-03-15",
        "warranty_expiry": "2027-03-15",
        "status": "ACTIVE",
        "last_maintenance": "2026-09-22",
        "next_maintenance": "2026-10-22",
    },
    {
        "machine_id": "CNC-002",
        "asset_code": "ASSET-CNC-002",
        "manufacturer": "MAZAK",
        "series": "VCN",
        "model": "VCN-530C",
        "location": "Area A - Line 2",
        "install_date": "2020-06-10",
        "warranty_expiry": "2026-12-31",
        "status": "ACTIVE",
        "last_maintenance": "2026-09-15",
        "next_maintenance": "2026-10-15",
    },
    {
        "machine_id": "CNC-003",
        "asset_code": "ASSET-CNC-003",
        "manufacturer": "OKUMA",
        "series": "GENOS",
        "model": "M560-V",
        "location": "Area B - Line 1",
        "install_date": "2019-11-03",
        "warranty_expiry": "2025-11-03",
        "status": "ACTIVE",
        "last_maintenance": "2026-09-05",
        "next_maintenance": "2026-11-05",
    },
    {
        "machine_id": "CNC-004",
        "asset_code": "ASSET-CNC-004",
        "manufacturer": "FANUC",
        "series": "ROBODRILL",
        "model": "α-D21MiB5",
        "location": "Area B - Line 2",
        "install_date": "2022-01-20",
        "warranty_expiry": "2028-01-20",
        "status": "ACTIVE",
        "last_maintenance": "2026-09-28",
        "next_maintenance": "2026-10-28",
    },
    {
        "machine_id": "CNC-005",
        "asset_code": "ASSET-CNC-005",
        "manufacturer": "HAAS",
        "series": "VF",
        "model": "VF-2",
        "location": "Area C - Line 1",
        "install_date": "2018-08-12",
        "warranty_expiry": "2024-08-12",
        "status": "MAINTENANCE",
        "last_maintenance": "2026-10-01",
        "next_maintenance": "2026-10-08",
    },
]


MAINTENANCE = [
    {
        "machine_id": "CNC-001",
        "symptom": "Trục chính xuất hiện rung bất thường ở tốc độ cao.",
        "error_code": "SPINDLE-VIB-01",
        "cause": "Độ căng dây đai trục chính giảm.",
        "action": "Kiểm tra và điều chỉnh lại độ căng dây đai.",
        "parts": "Không thay linh kiện",
        "downtime_min": 42,
        "result": "Máy chạy ổn định sau khi căn chỉnh.",
        "technician": "KTV-01",
    },
    {
        "machine_id": "CNC-001",
        "symptom": "Bề mặt chi tiết xuất hiện vết dao không đồng đều.",
        "error_code": "SURFACE-02",
        "cause": "Tool holder có độ đảo cao hơn giới hạn kiểm tra.",
        "action": "Vệ sinh taper và thay tool holder.",
        "parts": "Tool holder",
        "downtime_min": 55,
        "result": "Bề mặt gia công trở lại bình thường.",
        "technician": "KTV-02",
    },
    {
        "machine_id": "CNC-002",
        "symptom": "Máy báo nhiệt độ spindle tăng cao.",
        "error_code": "TEMP-SP-03",
        "cause": "Lưu lượng nước làm mát thấp.",
        "action": "Vệ sinh lọc và kiểm tra đường nước làm mát.",
        "parts": "Filter coolant",
        "downtime_min": 38,
        "result": "Nhiệt độ spindle trở về vùng vận hành bình thường.",
        "technician": "KTV-03",
    },
    {
        "machine_id": "CNC-003",
        "symptom": "Xuất hiện tiếng ồn bất thường khi chạy trục X.",
        "error_code": "AXIS-X-07",
        "cause": "Thiếu bôi trơn tại cụm dẫn hướng.",
        "action": "Kiểm tra hệ thống bôi trơn và bổ sung dầu.",
        "parts": "Lubrication oil",
        "downtime_min": 30,
        "result": "Tiếng ồn giảm và trục hoạt động ổn định.",
        "technician": "KTV-01",
    },
    {
        "machine_id": "CNC-004",
        "symptom": "Tool changer dừng giữa chu trình đổi dao.",
        "error_code": "ATC-12",
        "cause": "Cảm biến vị trí ATC bị lệch.",
        "action": "Căn chỉnh lại vị trí cảm biến ATC.",
        "parts": "Không thay linh kiện",
        "downtime_min": 48,
        "result": "Thử 20 chu trình đổi dao, không tái diễn lỗi.",
        "technician": "KTV-04",
    },
    {
        "machine_id": "CNC-005",
        "symptom": "Áp suất khí nén giảm trong quá trình vận hành.",
        "error_code": "AIR-05",
        "cause": "Rò khí tại đầu nối gần cụm van.",
        "action": "Thay đầu nối và kiểm tra lại đường khí.",
        "parts": "Pneumatic fitting",
        "downtime_min": 63,
        "result": "Áp suất duy trì ổn định sau sửa chữa.",
        "technician": "KTV-02",
    },
]


def seed():
    db = SessionLocal()

    try:
        print("=== DIGI-LOGS DEMO SEED ===")

        for item in MACHINES:
            existing = (
                db.query(Machine)
                .filter(
                    Machine.machine_id
                    == item["machine_id"]
                )
                .first()
            )

            if existing:
                print(
                    f"SKIP machine: "
                    f"{item['machine_id']}"
                )
                continue

            machine = Machine(**item)

            db.add(machine)

            print(
                f"ADD machine: "
                f"{item['machine_id']}"
            )

        db.commit()

        for item in MAINTENANCE:
            existing = (
                db.query(MaintenanceRecord)
                .filter(
                    MaintenanceRecord.machine_id
                    == item["machine_id"],
                    MaintenanceRecord.error_code
                    == item["error_code"],
                )
                .first()
            )

            if existing:
                print(
                    f"SKIP maintenance: "
                    f"{item['machine_id']} "
                    f"{item['error_code']}"
                )
                continue

            record = MaintenanceRecord(
                **item,
                source="synthetic_demo",
                confidence=1.0,
                review_status="approved",
                approved_by="DEMO-SEED",
            )

            db.add(record)

            print(
                f"ADD maintenance: "
                f"{item['machine_id']} "
                f"{item['error_code']}"
            )

        db.commit()

        machine_count = (
            db.query(Machine)
            .count()
        )

        maintenance_count = (
            db.query(MaintenanceRecord)
            .count()
        )

        print()
        print("=== COMPLETE ===")
        print(
            f"Machines: {machine_count}"
        )
        print(
            f"Maintenance records: "
            f"{maintenance_count}"
        )

    finally:
        db.close()


if __name__ == "__main__":
    seed()
