import cv2
import numpy as np


def decode_qr(image_bytes: bytes):
    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8,
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR,
    )

    if image is None:
        return {
            "success": False,
            "value": None,
            "reason": "invalid_image",
        }

    detector = cv2.QRCodeDetector()

    value, points, _ = detector.detectAndDecode(
        image
    )

    if not value:
        return {
            "success": False,
            "value": None,
            "reason": "qr_not_found",
        }

    value = value.strip()

    return {
        "success": True,
        "value": value,
        "reason": None,
    }
