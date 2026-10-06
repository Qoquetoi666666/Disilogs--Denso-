from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
)

from sqlalchemy.orm import Session

from app import models
from app.db import get_db

from app.services.qr_service import (
    decode_qr,
)

from app.services.ocr_service import (
    extract_nameplate_text,
)

from app.services.machine_matcher import (
    normalize_machine_token,
    match_machine_from_ocr,
)


router = APIRouter(
    prefix="/scan",
    tags=["Machine Scanning"],
)


OCR_AUTO_ACCEPT_THRESHOLD = 0.85
OCR_SUGGEST_THRESHOLD = 0.55


def machine_payload(machine):
    return {
        "machine_id":
            machine.machine_id,
        "asset_code":
            machine.asset_code,
        "manufacturer":
            machine.manufacturer,
        "series":
            machine.series,
        "model":
            machine.model,
        "location":
            machine.location,
    }


def find_exact_machine(
    token,
    machines,
):
    token = (
        token or ""
    ).strip().upper()

    for machine in machines:
        machine_id = (
            machine.machine_id or ""
        ).upper()

        asset_code = (
            machine.asset_code or ""
        ).upper()

        if token == machine_id:
            return machine

        if token == asset_code:
            return machine

    return None


@router.post("/machine")
async def scan_machine(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    image_bytes = await file.read()

    machines = (
        db.query(models.Machine)
        .order_by(
            models.Machine.machine_id
        )
        .all()
    )

    if not machines:
        return {
            "status":
                "no_machine_catalog",
            "recognized":
                False,
            "message":
                "Machine Registry is empty.",
        }

    # -------------------------
    # STAGE 1: QR
    # -------------------------

    qr_result = decode_qr(
        image_bytes
    )

    if qr_result["success"]:
        raw_value = (
            qr_result["value"]
        )

        token = normalize_machine_token(
            raw_value
        )

        machine = find_exact_machine(
            token,
            machines,
        )

        if machine:
            return {
                "status":
                    "recognized",
                "recognized":
                    True,
                "method":
                    "qr",
                "raw_value":
                    raw_value,
                "machine_token":
                    token,
                "confidence":
                    1.0,
                "machine":
                    machine_payload(
                        machine
                    ),
                "decision":
                    "auto_open_digilog",
            }

        return {
            "status":
                "unknown_qr",
            "recognized":
                False,
            "method":
                "qr",
            "raw_value":
                raw_value,
            "machine_token":
                token,
            "confidence":
                0.0,
            "message": (
                "QR hợp lệ nhưng máy "
                "không tồn tại trong "
                "Machine Registry."
            ),
            "fallback": [
                "manual_machine_selection",
                "contact_engineer",
            ],
        }

    # -------------------------
    # STAGE 2: OCR
    # -------------------------

    ocr_result = extract_nameplate_text(
        image_bytes
    )

    if not ocr_result["success"]:
        return {
            "status":
                "not_recognized",
            "recognized":
                False,
            "method":
                "ocr",
            "qr_status":
                qr_result.get(
                    "reason"
                ),
            "ocr_status":
                ocr_result.get(
                    "reason"
                ),
            "message": (
                "Không đọc được QR "
                "hoặc nameplate."
            ),
            "fallback": [
                "retake_image",
                "manual_machine_selection",
            ],
        }

    matches = match_machine_from_ocr(
        ocr_result["text"],
        machines,
        limit=3,
    )

    if not matches:
        return {
            "status":
                "not_found",
            "recognized":
                False,
            "method":
                "ocr",
            "ocr": ocr_result,
            "fallback": [
                "manual_machine_selection",
            ],
        }

    best = matches[0]

    # -------------------------
    # STAGE 3: Confidence Gate
    # -------------------------

    if (
        best["score"]
        >= OCR_AUTO_ACCEPT_THRESHOLD
    ):
        return {
            "status":
                "recognized",
            "recognized":
                True,
            "method":
                "ocr",
            "confidence":
                best["score"],
            "ocr_confidence":
                ocr_result[
                    "avg_confidence"
                ],
            "ocr_text":
                ocr_result["text"],
            "evidence":
                best.get(
                    "evidence",
                    [],
                ),
            "machine":
                best,
            "decision":
                "auto_open_digilog",
        }

    if (
        best["score"]
        >= OCR_SUGGEST_THRESHOLD
    ):
        return {
            "status":
                "low_confidence",
            "recognized":
                False,
            "method":
                "ocr",
            "confidence":
                best["score"],
            "ocr_confidence":
                ocr_result[
                    "avg_confidence"
                ],
            "ocr_text":
                ocr_result["text"],
            "suggestions":
                matches,
            "decision":
                "technician_confirmation",
        }

    return {
        "status":
            "not_found",
        "recognized":
            False,
        "method":
            "ocr",
        "confidence":
            best["score"],
        "ocr_confidence":
            ocr_result[
                "avg_confidence"
            ],
        "ocr_text":
            ocr_result["text"],
        "suggestions":
            matches,
        "message": (
            "Không có máy nào đủ "
            "độ tin cậy để tự nhận diện."
        ),
        "fallback": [
            "retake_image",
            "manual_machine_selection",
        ],
    }
