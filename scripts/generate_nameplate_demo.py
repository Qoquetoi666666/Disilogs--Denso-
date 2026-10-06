from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT_DIR = Path("data/samples/nameplates")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_font(size, bold=False):
    paths = []

    if bold:
        paths.append(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        )

    paths.append(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    )

    for path in paths:
        try:
            return ImageFont.truetype(
                path,
                size=size,
            )
        except OSError:
            pass

    return ImageFont.load_default()


def create_nameplate():
    width = 1600
    height = 900

    image = Image.new(
        "RGB",
        (width, height),
        "white",
    )

    draw = ImageDraw.Draw(image)

    title_font = load_font(
        64,
        bold=True,
    )

    label_font = load_font(
        46,
        bold=True,
    )

    value_font = load_font(
        48,
        bold=False,
    )

    draw.rectangle(
        (35, 35, width - 35, height - 35),
        outline="black",
        width=8,
    )

    draw.text(
        (90, 80),
        "DEMO CNC NAMEPLATE",
        fill="black",
        font=title_font,
    )

    rows = [
        ("MANUFACTURER", "OKUMA"),
        ("SERIES", "GENOS"),
        ("MODEL", "M560-V"),
        ("ASSET CODE", "ASSET-CNC-003"),
        ("MACHINE ID", "CNC-003"),
    ]

    y = 220

    for label, value in rows:
        draw.text(
            (100, y),
            label,
            fill="black",
            font=label_font,
        )

        draw.text(
            (650, y),
            value,
            fill="black",
            font=value_font,
        )

        y += 115

    output = (
        OUT_DIR
        / "CNC-003_nameplate.png"
    )

    image.save(output)

    print(f"Created: {output}")


if __name__ == "__main__":
    create_nameplate()
