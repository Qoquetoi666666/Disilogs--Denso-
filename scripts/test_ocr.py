from paddleocr import PaddleOCR


IMAGE = (
    "data/samples/nameplates/"
    "CNC-003_nameplate.png"
)


ocr = PaddleOCR(
    lang="en",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)


results = ocr.predict(
    input=IMAGE
)


for result in results:
    payload = result.json

    if callable(payload):
        payload = payload()

    if "res" in payload:
        payload = payload["res"]

    texts = payload.get(
        "rec_texts",
        [],
    )

    scores = payload.get(
        "rec_scores",
        [],
    )

    print("=== OCR RESULT ===")

    for text, score in zip(
        texts,
        scores,
    ):
        print(
            f"{score:.3f} | {text}"
        )
