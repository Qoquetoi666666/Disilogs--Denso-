from pathlib import Path

import qrcode


OUTPUT_DIR = Path(
    "data/samples/qr"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


MACHINES = [
    "CNC-001",
    "CNC-002",
    "CNC-003",
    "CNC-004",
    "CNC-005",
]


for machine_id in MACHINES:
    payload = (
        f"DIGILOG:{machine_id}"
    )

    image = qrcode.make(
        payload
    )

    output = (
        OUTPUT_DIR
        / f"{machine_id}.png"
    )

    image.save(
        output
    )

    print(
        f"Created: {output}"
    )


print("QR demo generation complete.")
