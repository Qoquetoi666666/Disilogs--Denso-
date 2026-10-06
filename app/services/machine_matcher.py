from rapidfuzz import fuzz


def normalize_machine_token(value: str):
    if not value:
        return ""

    text = value.strip()

    prefixes = [
        "DIGILOG:",
        "DIGI-LOG:",
        "MACHINE:",
    ]

    upper_text = text.upper()

    for prefix in prefixes:
        if upper_text.startswith(prefix):
            text = text[len(prefix):]
            break

    return text.strip().upper()


def machine_search_text(machine):
    fields = [
        machine.machine_id,
        machine.asset_code,
        machine.manufacturer,
        machine.series,
        machine.model,
    ]

    return " ".join(
        str(field)
        for field in fields
        if field
    ).upper()


def match_machine_from_text(
    text,
    machines,
    limit=3,
):
    query = normalize_machine_token(text)

    if not query:
        return []

    results = []

    for machine in machines:
        machine_id = (
            machine.machine_id or ""
        ).upper()

        asset_code = (
            machine.asset_code or ""
        ).upper()

        if query == machine_id:
            score = 1.0

        elif query == asset_code:
            score = 0.99

        else:
            candidate = machine_search_text(
                machine
            )

            score = fuzz.token_set_ratio(
                query,
                candidate,
            ) / 100.0

        results.append(
            {
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
                "score":
                    round(score, 4),
            }
        )

def normalize_ocr_text(text):
    if not text:
        return ""

    return (
        str(text)
        .upper()
        .replace("\n", " ")
        .strip()
    )


def match_machine_from_ocr(
    text,
    machines,
    limit=3,
):
    query = normalize_ocr_text(
        text
    )

    results = []

    for machine in machines:
        machine_id = (
            machine.machine_id or ""
        ).upper()

        asset_code = (
            machine.asset_code or ""
        ).upper()

        manufacturer = (
            machine.manufacturer or ""
        ).upper()

        series = (
            machine.series or ""
        ).upper()

        model = (
            machine.model or ""
        ).upper()

        evidence = []

        if (
            machine_id
            and machine_id in query
        ):
            score = 1.0

            evidence.append(
                "machine_id"
            )

        elif (
            asset_code
            and asset_code in query
        ):
            score = 0.99

            evidence.append(
                "asset_code"
            )

        else:
            candidate = (
                f"{manufacturer} "
                f"{series} "
                f"{model}"
            )

            fuzzy_score = (
                fuzz.token_set_ratio(
                    query,
                    candidate,
                )
                / 100.0
            )

            bonus = 0.0

            if (
                manufacturer
                and manufacturer in query
            ):
                bonus += 0.12
                evidence.append(
                    "manufacturer"
                )

            if (
                series
                and series in query
            ):
                bonus += 0.10
                evidence.append(
                    "series"
                )

            if (
                model
                and model in query
            ):
                bonus += 0.20
                evidence.append(
                    "model"
                )

            score = min(
                0.98,
                fuzzy_score * 0.65
                + bonus,
            )

        results.append(
            {
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
                "score":
                    round(score, 4),
                "evidence":
                    evidence,
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:limit]
