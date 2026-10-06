import json

import cv2
import numpy as np

from paddleocr import PaddleOCR


_ocr = None


def get_ocr():
    global _ocr

    if _ocr is None:
        _ocr = PaddleOCR(
            lang="en",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )

    return _ocr


def _result_to_dict(result):
    payload = result.json

    if callable(payload):
        payload = payload()

    if isinstance(payload, str):
        payload = json.loads(payload)

    if "res" in payload:
        payload = payload["res"]

    return payload


def extract_nameplate_text(
    image_bytes: bytes,
):
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
            "text": "",
            "lines": [],
            "avg_confidence": 0.0,
            "reason": "invalid_image",
        }

    ocr = get_ocr()

    results = ocr.predict(
        input=image
    )

    lines = []

    for result in results:
        payload = _result_to_dict(
            result
        )

        texts = payload.get(
            "rec_texts",
            [],
        )

        scores = payload.get(
            "rec_scores",
            [],
        )

        for text, score in zip(
            texts,
            scores,
        ):
            text = str(text).strip()

            if not text:
                continue

            lines.append(
                {
                    "text": text,
                    "confidence": round(
                        float(score),
                        4,
                    ),
                }
            )

    if not lines:
        return {
            "success": False,
            "text": "",
            "lines": [],
            "avg_confidence": 0.0,
            "reason": "no_text_detected",
        }

    full_text = " ".join(
        item["text"]
        for item in lines
    )

    avg_confidence = sum(
        item["confidence"]
        for item in lines
    ) / len(lines)

    return {
        "success": True,
        "text": full_text,
        "lines": lines,
        "avg_confidence": round(
            avg_confidence,
            4,
        ),
        "reason": None,
    }
