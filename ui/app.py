from datetime import date, datetime

import pandas as pd
import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Digi-Logs",
    page_icon="🛠️",
    layout="wide",
)


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .digilog-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0px;
    }

    .digilog-subtitle {
        color: #777;
        font-size: 17px;
        margin-bottom: 25px;
    }

    .demo-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        border: 1px solid #d49a00;
        color: #d49a00;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 15px;
    }

    .machine-card {
        border: 1px solid #444;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 15px;
    }

    .alert-warning {
        border-left: 5px solid #ffb300;
        padding: 12px 16px;
        background: rgba(255, 179, 0, 0.08);
        border-radius: 5px;
        margin-bottom: 10px;
    }

    .alert-danger {
        border-left: 5px solid #e53935;
        padding: 12px 16px;
        background: rgba(229, 57, 53, 0.08);
        border-radius: 5px;
        margin-bottom: 10px;
    }

    .alert-ok {
        border-left: 5px solid #2e7d32;
        padding: 12px 16px;
        background: rgba(46, 125, 50, 0.08);
        border-radius: 5px;
        margin-bottom: 10px;
    }

    .source-label {
        font-size: 12px;
        color: #888;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_get(path):
    try:
        response = requests.get(
            f"{API_URL}{path}",
            timeout=5,
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as exc:
        st.error(
            f"Không kết nối được Digi-Logs API: {exc}"
        )
        return None


def api_post(path, payload):
    try:
        response = requests.post(
            f"{API_URL}{path}",
            json=payload,
            timeout=5,
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as exc:
        st.error(
            f"Không thể gửi dữ liệu: {exc}"
        )
        return None

def api_upload_document(
    machine_id,
    title,
    document_type,
    uploaded_file,
):
    try:
        response = requests.post(
            f"{API_URL}/documents/upload",
            data={
                "machine_id": machine_id,
                "title": title,
                "document_type": document_type,
            },
            files={
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf",
                )
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:
        st.error(
            f"Không thể upload tài liệu: {exc}"
        )
        return None


def api_scan_machine(uploaded_file):
    try:
        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type
                or "application/octet-stream",
            )
        }

        response = requests.post(
            f"{API_URL}/scan/machine",
            files=files,
            timeout=120,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:
        st.error(
            f"Machine Scanning thất bại: {exc}"
        )

        return None

def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()

    except ValueError:
        return None


def days_until(value):
    target = parse_date(value)

    if not target:
        return None

    return (target - date.today()).days


def maintenance_alert(machine):
    days = days_until(
        machine.get("next_maintenance")
    )

    if days is None:
        return (
            "warning",
            "Chưa có lịch bảo trì tiếp theo."
        )

    if days < 0:
        return (
            "danger",
            f"Đã quá hạn bảo trì {-days} ngày."
        )

    if days <= 14:
        return (
            "warning",
            f"Sắp đến hạn bảo trì: còn {days} ngày."
        )

    return (
        "ok",
        f"Lịch bảo trì còn {days} ngày."
    )


def warranty_alert(machine):
    days = days_until(
        machine.get("warranty_expiry")
    )

    if days is None:
        return (
            "warning",
            "Chưa có thông tin bảo hành."
        )

    if days < 0:
        return (
            "danger",
            f"Bảo hành đã hết hạn {-days} ngày."
        )

    if days <= 60:
        return (
            "warning",
            f"Bảo hành sắp hết: còn {days} ngày."
        )

    return (
        "ok",
        f"Bảo hành còn {days} ngày."
    )


def render_alert(kind, text):
    class_name = {
        "danger": "alert-danger",
        "warning": "alert-warning",
        "ok": "alert-ok",
    }.get(kind, "alert-warning")

    st.markdown(
        f"""
        <div class="{class_name}">
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    '<div class="digilog-title">Digi-Logs</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="digilog-subtitle">
        CNC Maintenance Knowledge &
        Digital Machine Log
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="demo-badge">
        SYNTHETIC DEMO DATA
    </div>
    """,
    unsafe_allow_html=True,
)


machines_data = api_get("/machines/")

if not machines_data:
    st.stop()


machines = machines_data.get(
    "machines",
    [],
)

if not machines:
    st.warning(
        "Chưa có máy trong Machine Registry."
    )
    st.stop()


machine_ids = [
    machine["machine_id"]
    for machine in machines
]

if "active_machine" not in st.session_state:
    st.session_state["active_machine"] = machine_ids[0]

if st.session_state["active_machine"] not in machine_ids:
    st.session_state["active_machine"] = machine_ids[0]


if "pending_machine" in st.session_state:
    pending = st.session_state.pop(
        "pending_machine"
    )

    if pending in machine_ids:
        st.session_state["active_machine"] = pending

        st.session_state.pop(
            "machine_select",
            None,
        )


if "scan_result" not in st.session_state:
    st.session_state["scan_result"] = None


with st.sidebar:
    st.header("Factory Context")

    selected_machine = st.selectbox(
        "Machine",
        machine_ids,
        index=machine_ids.index(
            st.session_state["active_machine"]
        ),
        key="machine_select",
    )

    st.session_state["active_machine"] = (
        selected_machine
    )

    st.divider()

    st.caption("Local MVP")

    st.write("Machine Registry ✓")
    st.write("Digi-Log ✓")
    st.write("Maintenance Memory ✓")
    st.write("Machine Scanning — M3")
    st.write("Library-RAG — M5")
    st.write("Virtual Assistant — M6")


digilog = api_get(
    f"/machines/{selected_machine}/digilog"
)

if not digilog:
    st.stop()


machine = digilog["machine"]

maintenance = digilog.get(
    "maintenance_history",
    [],
)

documents = digilog.get(
    "documents",
    [],
)

summary = digilog.get(
    "summary",
    {},
)

last_failure = digilog.get(
    "last_failure"
)


st.subheader(
    f"{selected_machine} · Digi-Log"
)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Status",
        machine.get("status", "UNKNOWN"),
    )

with col2:
    st.metric(
        "Maintenance Records",
        summary.get(
            "maintenance_count",
            0,
        ),
    )

with col3:
    st.metric(
        "Documents",
        summary.get(
            "document_count",
            0,
        ),
    )

with col4:
    days = days_until(
        machine.get("next_maintenance")
    )

    value = (
        f"{days} days"
        if days is not None
        else "N/A"
    )

    st.metric(
        "Next Maintenance",
        value,
    )


st.divider()


if "current_view" not in st.session_state:
    st.session_state["current_view"] = "Machine Overview"

if "pending_view" in st.session_state:
    st.session_state["current_view"] = (
        st.session_state.pop("pending_view")
    )

st.radio(
    "Navigation",
    [
        "Machine Overview",
        "Scan Machine",
        "Maintenance History",
        "Record Maintenance",
        "Documents",
        "Know-how Library",
    ],
    horizontal=True,
    key="current_view",
    label_visibility="collapsed",
)

def open_machine_from_scan(machine_id):
    st.session_state["active_machine"] = machine_id
    st.session_state["machine_select"] = machine_id
    st.session_state["scan_result"] = None
    st.session_state["pending_view"] = "Machine Overview"


if st.session_state["current_view"] == "Scan Machine":
    st.subheader("Machine Scanning")

    st.caption(
        "Upload ảnh QR hoặc nameplate. "
        "Digi-Logs sẽ nhận diện và đối chiếu "
        "với Machine Registry."
    )

    uploaded_machine_image = st.file_uploader(
        "Machine image",
        type=["png", "jpg", "jpeg"],
        key="machine_scan_upload",
    )

    if uploaded_machine_image:
        st.image(
            uploaded_machine_image,
            caption="Uploaded machine image",
            width=600,
        )

        identify_clicked = st.button(
            "Identify Machine",
            type="primary",
            use_container_width=True,
        )

        if identify_clicked:
            with st.spinner("Analyzing machine..."):
                st.session_state["scan_result"] = api_scan_machine(
                    uploaded_machine_image
                )

    scan_result = st.session_state.get("scan_result")

    if scan_result:
        status = scan_result.get("status")
        method = scan_result.get("method", "unknown")
        recognized = scan_result.get("recognized", False)

        if recognized:
            machine_info = scan_result.get("machine", {})
            detected_id = machine_info.get("machine_id")

            if (
                detected_id in machine_ids
                and st.session_state.get("active_machine") != detected_id
            ):
                st.session_state["pending_machine"] = detected_id
                st.rerun()

            st.success(
                f"Recognized Machine: {detected_id}"
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric(
                    "Recognition Method",
                    method.upper(),
                )

            with c2:
                match_confidence = scan_result.get(
                    "confidence",
                    0,
                )

                st.metric(
                    "Machine Match",
                    f"{match_confidence * 100:.2f}%",
                )

            with c3:
                ocr_confidence = scan_result.get(
                    "ocr_confidence"
                )

                if ocr_confidence is None:
                    st.metric(
                        "OCR Confidence",
                        "N/A",
                    )
                else:
                    st.metric(
                        "OCR Confidence",
                        f"{ocr_confidence * 100:.2f}%",
                    )

            st.write(
                "**Manufacturer:**",
                machine_info.get(
                    "manufacturer",
                    "N/A",
                ),
            )

            st.write(
                "**Series:**",
                machine_info.get(
                    "series",
                    "N/A",
                ),
            )

            st.write(
                "**Model:**",
                machine_info.get(
                    "model",
                    "N/A",
                ),
            )

            st.write(
                "**Asset Code:**",
                machine_info.get(
                    "asset_code",
                    "N/A",
                ),
            )

            evidence = scan_result.get(
                "evidence",
                [],
            )

            if evidence:
                st.caption(
                    "Match evidence: "
                    + ", ".join(evidence)
                )

            if method == "ocr":
                with st.expander("OCR Evidence"):
                    st.write(
                        scan_result.get(
                            "ocr_text",
                            "",
                        )
                    )

            if (
                detected_id
                and detected_id in machine_ids
            ):
                st.button(
                    f"Open {detected_id} Digi-Log",
                    type="primary",
                    use_container_width=True,
                    key=f"open_{detected_id}",
                    on_click=open_machine_from_scan,
                    args=(detected_id,),
                )

        elif status == "low_confidence":
            st.warning(
                "Low-confidence recognition. "
                "Technician confirmation required."
            )

            suggestions = scan_result.get(
                "suggestions",
                [],
            )

            if suggestions:
                st.write("### Suggested Machines")

                for item in suggestions:
                    machine_id = item.get(
                        "machine_id"
                    )

                    score = item.get(
                        "score",
                        0,
                    )

                    left, right = st.columns(
                        [3, 1]
                    )

                    with left:
                        st.write(
                            f"**{machine_id}** · "
                            f"{item.get('manufacturer')} · "
                            f"{item.get('model')} · "
                            f"{score * 100:.1f}%"
                        )

                    with right:
                        if st.button(
                            "Confirm",
                            key=f"confirm_{machine_id}",
                        ):
                            st.session_state[
                                "pending_machine"
                            ] = machine_id

                            st.session_state[
                                "scan_result"
                            ] = None

                            st.rerun()

        elif status == "unknown_qr":
            st.error(
                "QR hợp lệ nhưng máy không tồn tại "
                "trong Machine Registry."
            )

            st.caption(
                f"Detected value: "
                f"{scan_result.get('raw_value', '')}"
            )

            st.info(
                "Hãy chọn máy thủ công hoặc "
                "liên hệ kỹ sư."
            )

        else:
            st.warning(
                "Không nhận diện được máy "
                "với độ tin cậy đủ cao."
            )

            st.info(
                "Hãy chụp lại ảnh rõ hơn hoặc "
                "chọn máy thủ công."
            )


if st.session_state["current_view"] == "Machine Overview":
    left, right = st.columns(
        [1.25, 1]
    )

    with left:
        st.subheader("Machine Profile")

        profile = {
            "Machine ID":
                machine.get("machine_id"),
            "Asset Code":
                machine.get("asset_code"),
            "Manufacturer":
                machine.get("manufacturer"),
            "Series":
                machine.get("series"),
            "Model":
                machine.get("model"),
            "Location":
                machine.get("location"),
            "Install Date":
                machine.get("install_date"),
            "Warranty Expiry":
                machine.get("warranty_expiry"),
            "Last Maintenance":
                machine.get("last_maintenance"),
            "Next Maintenance":
                machine.get("next_maintenance"),
        }

        for key, value in profile.items():
            st.write(
                f"**{key}:** "
                f"{value or 'N/A'}"
            )

    with right:
        st.subheader("Alerts")

        kind, text = maintenance_alert(
            machine
        )

        render_alert(
            kind,
            text,
        )

        kind, text = warranty_alert(
            machine
        )

        render_alert(
            kind,
            text,
        )


    st.divider()

    st.subheader("Last Maintenance Event")

    if last_failure:
        st.markdown(
            f"""
            **Symptom**

            {last_failure.get(
                "symptom",
                "N/A"
            )}

            **Error Code**

            `{last_failure.get(
                "error_code",
                "N/A"
            )}`

            **Cause**

            {last_failure.get(
                "cause",
                "N/A"
            )}

            **Action**

            {last_failure.get(
                "action",
                "N/A"
            )}

            **Result**

            {last_failure.get(
                "result",
                "N/A"
            )}

            **Downtime**

            {last_failure.get(
                "downtime_min",
                "N/A"
            )} minutes
            """
        )

        source = last_failure.get(
            "source",
            "unknown"
        )

        st.caption(
            f"Source: {source}"
        )

    else:
        st.info(
            "Chưa có lịch sử bảo trì."
        )


if st.session_state["current_view"] == "Maintenance History":
    st.subheader(
        f"Maintenance History · "
        f"{selected_machine}"
    )

    if not maintenance:
        st.info(
            "Chưa có maintenance record."
        )

    else:
        rows = []

        for item in maintenance:
            rows.append(
                {
                    "ID":
                        item.get(
                            "id"
                        ),
                    "Error Code":
                        item.get(
                            "error_code"
                        ),
                    "Symptom":
                        item.get(
                            "symptom"
                        ),
                    "Cause":
                        item.get(
                            "cause"
                        ),
                    "Action":
                        item.get(
                            "action"
                        ),
                    "Parts":
                        item.get(
                            "parts"
                        ),
                    "Downtime (min)":
                        item.get(
                            "downtime_min"
                        ),
                    "Result":
                        item.get(
                            "result"
                        ),
                    "Technician":
                        item.get(
                            "technician"
                        ),
                    "Source":
                        item.get(
                            "source"
                        ),
                }
            )

        df = pd.DataFrame(rows)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.markdown(
            "### Convert Maintenance to Know-how"
        )

        st.caption(
            "Digi-Logs chuyển dữ liệu bảo trì "
            "thành Know-how Draft có cấu trúc. "
            "Kỹ thuật viên sẽ bổ sung phần suy luận "
            "còn thiếu và chuyên gia xác nhận "
            "trước khi đưa vào thư viện."
        )

        knowhow_payload = api_get(
            f"/knowhow/machine/{selected_machine}"
        ) or {}

        existing_knowhow = knowhow_payload.get(
            "knowhow",
            [],
        )

        linked_maintenance_ids = set()

        knowhow_by_record = {}

        for kh in existing_knowhow:
            linked_id = kh.get(
                "maintenance_record_id"
            )

            if linked_id is not None:
                linked_maintenance_ids.add(
                    linked_id
                )

                knowhow_by_record.setdefault(
                    linked_id,
                    [],
                ).append(kh)

        for item in maintenance:
            record_id = item.get(
                "id"
            )

            symptom = (
                item.get("symptom")
                or "Maintenance record"
            )

            cause = (
                item.get("cause")
                or ""
            )

            action = (
                item.get("action")
                or ""
            )

            result = (
                item.get("result")
                or ""
            )

            technician = (
                item.get("technician")
                or "technician"
            )

            error_code = (
                item.get("error_code")
                or ""
            )

            confidence = (
                item.get("confidence")
            )

            if confidence is None:
                confidence = 0.8

            try:
                confidence = float(
                    confidence
                )

            except (
                TypeError,
                ValueError,
            ):
                confidence = 0.8

            confidence = max(
                0.0,
                min(
                    confidence,
                    1.0,
                ),
            )

            title_preview = symptom

            if len(title_preview) > 80:
                title_preview = (
                    title_preview[:77]
                    + "..."
                )

            with st.expander(
                f"Maintenance Record "
                f"#{record_id} · "
                f"{title_preview}",
                expanded=False,
            ):
                c1, c2 = st.columns(2)

                with c1:
                    st.markdown(
                        "**Symptom / Observation**"
                    )
                    st.write(
                        symptom
                        or "—"
                    )

                    st.markdown(
                        "**Cause**"
                    )
                    st.write(
                        cause
                        or "—"
                    )

                with c2:
                    st.markdown(
                        "**Action**"
                    )
                    st.write(
                        action
                        or "—"
                    )

                    st.markdown(
                        "**Result**"
                    )
                    st.write(
                        result
                        or "—"
                    )

                if error_code:
                    st.caption(
                        f"Error Code: "
                        f"{error_code}"
                    )

                st.caption(
                    f"Technician: "
                    f"{technician}"
                )

                if (
                    record_id
                    in linked_maintenance_ids
                ):
                    linked_cases = (
                        knowhow_by_record.get(
                            record_id,
                            [],
                        )
                    )

                    st.success(
                        "Maintenance Record này "
                        "đã được liên kết với Know-how."
                    )

                    for kh in linked_cases:
                        kh_id = kh.get(
                            "knowhow_id",
                            "UNKNOWN",
                        )

                        kh_status = kh.get(
                            "status",
                            "UNKNOWN",
                        )

                        st.caption(
                            f"{kh_id} · "
                            f"{kh_status}"
                        )

                    if st.button(
                        "Open Know-how Library",
                        key=(
                            "open_knowhow_from_"
                            f"maintenance_{record_id}"
                        ),
                        width="stretch",
                    ):
                        st.session_state[
                            "pending_view"
                        ] = "Know-how Library"

                        st.rerun()

                else:
                    st.info(
                        "Record này chưa có "
                        "Know-how Case."
                    )

                    if st.button(
                        "Create Know-how Draft",
                        key=(
                            "create_knowhow_from_"
                            f"maintenance_{record_id}"
                        ),
                        width="stretch",
                    ):
                        evidence_text = (
                            f"Maintenance Record "
                            f"#{record_id}"
                        )

                        if symptom:
                            evidence_text += (
                                f" ghi nhận: "
                                f"{symptom}"
                            )

                        create_payload = {
                            "machine_id":
                                selected_machine,

                            "title":
                                symptom,

                            "observation":
                                symptom
                                or None,

                            "hypothesis":
                                cause
                                or None,

                            "evidence":
                                evidence_text,

                            "diagnostic_check":
                                None,

                            "ruled_out_causes":
                                None,

                            "recommended_action":
                                action
                                or None,

                            "verification":
                                None,

                            "result":
                                result
                                or None,

                            "maintenance_record_id":
                                record_id,

                            "document_id":
                                None,

                            "source_page":
                                None,

                            "source_type":
                                "maintenance_record",

                            "confidence":
                                confidence,

                            "created_by":
                                technician,
                        }

                        create_result = api_post(
                            "/knowhow/draft",
                            create_payload,
                        )

                        if create_result:
                            created_knowhow = (
                                create_result.get(
                                    "knowhow",
                                    {},
                                )
                            )

                            new_knowhow_id = (
                                created_knowhow.get(
                                    "knowhow_id",
                                    "UNKNOWN",
                                )
                            )

                            st.success(
                                "Đã tạo Know-how Draft: "
                                f"{new_knowhow_id}"
                            )

                            st.session_state[
                                "pending_view"
                            ] = "Know-how Library"

                            st.rerun()



if st.session_state["current_view"] == "Record Maintenance":
    st.subheader(
        "Record Maintenance Result"
    )

    st.caption(
        "KTV ghi lại kết quả sau khi "
        "can thiệp máy."
    )

    with st.form(
        "maintenance_form"
    ):
        symptom = st.text_area(
            "Symptom *",
            placeholder=(
                "Ví dụ: Trục chính "
                "rung bất thường..."
            ),
        )

        error_code = st.text_input(
            "Error Code",
        )

        cause = st.text_area(
            "Cause",
        )

        action = st.text_area(
            "Action *",
        )

        parts = st.text_input(
            "Parts",
        )

        downtime = st.number_input(
            "Downtime (minutes)",
            min_value=0.0,
            step=1.0,
        )

        result = st.text_area(
            "Result",
        )

        technician = st.text_input(
            "Technician",
            value="KTV-01",
        )

        submitted = st.form_submit_button(
            "Confirm & Save to Digi-Log",
            use_container_width=True,
        )

        if submitted:
            if not symptom.strip():
                st.error(
                    "Symptom là trường bắt buộc."
                )

            elif not action.strip():
                st.error(
                    "Action là trường bắt buộc."
                )

            else:
                payload = {
                    "machine_id":
                        selected_machine,
                    "symptom":
                        symptom,
                    "error_code":
                        error_code or None,
                    "cause":
                        cause or None,
                    "action":
                        action,
                    "parts":
                        parts or None,
                    "downtime_min":
                        downtime,
                    "result":
                        result or None,
                    "technician":
                        technician or None,
                }

                response = api_post(
                    "/maintenance/",
                    payload,
                )

                if response:
                    st.success(
                        "Maintenance record "
                        "đã được lưu vào Digi-Log."
                    )

                    st.rerun()


if st.session_state["current_view"] == "Documents":
    st.subheader(
        f"Documents · {selected_machine}"
    )

    document_payload = api_get(
        f"/documents/{selected_machine}"
    ) or {}

    documents = document_payload.get(
        "documents",
        [],
    )

    total_pages = sum(
        doc.get("page_count", 0) or 0
        for doc in documents
    )

    total_characters = sum(
        doc.get("total_characters", 0) or 0
        for doc in documents
    )

    ready_count = sum(
        1
        for doc in documents
        if doc.get("status") == "READY"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Documents",
            len(documents),
        )

    with col2:
        st.metric(
            "Total Pages",
            total_pages,
        )

    with col3:
        st.metric(
            "Characters",
            total_characters,
        )

    with col4:
        st.metric(
            "Ready",
            ready_count,
        )

    st.divider()

    st.markdown(
        "### Upload Technical Document"
    )

    with st.form(
        "document_upload_form",
        clear_on_submit=True,
    ):
        document_title = st.text_input(
            "Document title",
            placeholder=(
                "Example: CNC-003 Maintenance Manual"
            ),
        )

        document_type = st.selectbox(
            "Document type",
            [
                "MAINTENANCE_MANUAL",
                "TECHNICAL_GUIDE",
                "INSPECTION_GUIDE",
                "SOP",
                "DEMO_MAINTENANCE_GUIDE",
                "OTHER",
            ],
        )

        uploaded_pdf = st.file_uploader(
            "PDF document",
            type=["pdf"],
            key="document_pdf_upload",
        )

        upload_clicked = (
            st.form_submit_button(
                "Upload & Extract",
                width="stretch",
            )
        )

    if upload_clicked:
        if not document_title.strip():
            st.warning(
                "Hãy nhập tên tài liệu."
            )

        elif uploaded_pdf is None:
            st.warning(
                "Hãy chọn một file PDF."
            )

        else:
            with st.spinner(
                "Uploading and extracting PDF..."
            ):
                upload_result = (
                    api_upload_document(
                        selected_machine,
                        document_title.strip(),
                        document_type,
                        uploaded_pdf,
                    )
                )

            if upload_result:
                doc = upload_result.get(
                    "document",
                    {},
                )

                st.success(
                    "Document uploaded successfully. "
                    f"{doc.get('page_count', 0)} pages, "
                    f"{doc.get('total_characters', 0)} characters."
                )

                st.rerun()

    st.divider()

    st.markdown(
        "### Document Library"
    )

    if not documents:
        st.info(
            "Chưa có tài liệu cho máy này."
        )

    else:
        for doc in documents:
            with st.container(
                border=True
            ):
                st.markdown(
                    f"#### {doc.get('title', 'Untitled')}"
                )

                c1, c2, c3, c4 = st.columns(4)

                with c1:
                    st.metric(
                        "Pages",
                        doc.get(
                            "page_count",
                            0,
                        ),
                    )

                with c2:
                    st.metric(
                        "Characters",
                        doc.get(
                            "total_characters",
                            0,
                        ),
                    )

                with c3:
                    st.metric(
                        "Status",
                        doc.get(
                            "status",
                            "UNKNOWN",
                        ),
                    )

                with c4:
                    indexed = doc.get(
                        "indexed",
                        False,
                    )

                    st.metric(
                        "RAG Index",
                        (
                            "INDEXED"
                            if indexed
                            else "NOT INDEXED"
                        ),
                    )

                st.caption(
                    "Type: "
                    f"{doc.get('document_type', 'document')} "
                    "· File: "
                    f"{doc.get('filename', 'N/A')} "
                    "· Key: "
                    f"{doc.get('document_key', 'N/A')}"
                )

                if st.button(
                    "View Extracted Content",
                    key=(
                        f"view_document_"
                        f"{doc.get('id')}"
                    ),
                    width="stretch",
                ):
                    detail = api_get(
                        "/documents/item/"
                        f"{doc.get('id')}"
                    )

                    if not detail:
                        st.error(
                            "Không đọc được nội dung tài liệu."
                        )

                    else:
                        extracted = detail.get(
                            "extracted"
                        )

                        if not extracted:
                            st.warning(
                                "Không tìm thấy extracted text."
                            )

                        else:
                            st.markdown(
                                "##### Extracted Pages"
                            )

                            for page in extracted.get(
                                "pages",
                                [],
                            ):
                                page_number = page.get(
                                    "page",
                                    "?"
                                )

                                chars = page.get(
                                    "characters",
                                    0,
                                )

                                with st.expander(
                                    f"Page {page_number} "
                                    f"· {chars} characters",
                                    expanded=(
                                        page_number == 1
                                    ),
                                ):
                                    page_text = (
                                        page.get(
                                            "text",
                                            "",
                                        )
                                    )

                                    if page_text:
                                        st.text(
                                            page_text
                                        )
                                    else:
                                        st.caption(
                                            "No text extracted."
                                        )



if st.session_state["current_view"] == "Know-how Library":
    st.subheader(
        f"Know-how Library · {selected_machine}"
    )

    st.caption(
        "Human-validated maintenance knowledge "
        "linked to each machine."
    )

    knowhow_payload = api_get(
        f"/knowhow/machine/{selected_machine}"
    ) or {}

    counts = knowhow_payload.get(
        "counts",
        {},
    )

    knowhow_items = knowhow_payload.get(
        "knowhow",
        [],
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Approved",
            counts.get(
                "approved",
                0,
            ),
        )

    with c2:
        st.metric(
            "Draft",
            counts.get(
                "draft",
                0,
            ),
        )

    with c3:
        st.metric(
            "Under Review",
            counts.get(
                "under_review",
                0,
            ),
        )

    with c4:
        st.metric(
            "Rejected",
            counts.get(
                "rejected",
                0,
            ),
        )

    st.divider()

    st.markdown(
        "### Create Know-how Draft"
    )

    with st.expander(
        "Create a new Know-how Case",
        expanded=False,
    ):
        with st.form(
            "knowhow_create_form",
            clear_on_submit=True,
        ):
            kh_title = st.text_input(
                "Title",
                placeholder=(
                    "Example: Tiếng ồn bất thường "
                    "khi chạy trục X"
                ),
            )

            kh_observation = st.text_area(
                "Observation",
                placeholder=(
                    "Dấu hiệu hoặc hiện tượng "
                    "quan sát được"
                ),
            )

            kh_hypothesis = st.text_area(
                "Hypothesis / Cause",
                placeholder=(
                    "Nguyên nhân nghi ngờ "
                    "hoặc nguyên nhân đã xác định"
                ),
            )

            kh_evidence = st.text_area(
                "Evidence",
                placeholder=(
                    "Maintenance record, "
                    "document hoặc bằng chứng liên quan"
                ),
            )

            kh_diagnostic = st.text_area(
                "Diagnostic Check",
                placeholder=(
                    "Các bước kiểm tra cần thực hiện"
                ),
            )

            kh_ruled_out = st.text_area(
                "Ruled-out Causes",
                placeholder=(
                    "Các nguyên nhân đã được loại trừ"
                ),
            )

            kh_action = st.text_area(
                "Recommended Action",
                placeholder=(
                    "Hành động xử lý đề xuất"
                ),
            )

            kh_verification = st.text_area(
                "Verification",
                placeholder=(
                    "Cách xác minh sau xử lý"
                ),
            )

            kh_result = st.text_area(
                "Result",
                placeholder=(
                    "Kết quả sau xử lý"
                ),
            )

            src1, src2, src3 = st.columns(3)

            with src1:
                kh_maintenance_id = st.text_input(
                    "Maintenance Record ID",
                    placeholder="Optional",
                )

            with src2:
                kh_document_id = st.text_input(
                    "Document ID",
                    placeholder="Optional",
                )

            with src3:
                kh_source_page = st.text_input(
                    "Source Page",
                    placeholder="Optional",
                )

            kh_source_type = st.selectbox(
                "Source Type",
                [
                    "technician",
                    "maintenance_record",
                    "document",
                    "combined",
                ],
            )

            kh_confidence = st.slider(
                "Confidence",
                min_value=0.0,
                max_value=1.0,
                value=0.8,
                step=0.05,
            )

            kh_created_by = st.text_input(
                "Created by",
                value="technician_demo",
            )

            create_knowhow_clicked = (
                st.form_submit_button(
                    "Create Draft",
                    width="stretch",
                )
            )

        if create_knowhow_clicked:
            if not kh_title.strip():
                st.warning(
                    "Hãy nhập tiêu đề Know-how."
                )

            else:
                try:
                    maintenance_id_value = (
                        int(
                            kh_maintenance_id
                        )
                        if kh_maintenance_id.strip()
                        else None
                    )

                    document_id_value = (
                        int(
                            kh_document_id
                        )
                        if kh_document_id.strip()
                        else None
                    )

                    source_page_value = (
                        int(
                            kh_source_page
                        )
                        if kh_source_page.strip()
                        else None
                    )

                except ValueError:
                    st.error(
                        "Maintenance ID, Document ID "
                        "và Source Page phải là số."
                    )

                else:
                    create_payload = {
                        "machine_id":
                            selected_machine,

                        "title":
                            kh_title.strip(),

                        "observation":
                            kh_observation.strip()
                            or None,

                        "hypothesis":
                            kh_hypothesis.strip()
                            or None,

                        "evidence":
                            kh_evidence.strip()
                            or None,

                        "diagnostic_check":
                            kh_diagnostic.strip()
                            or None,

                        "ruled_out_causes":
                            kh_ruled_out.strip()
                            or None,

                        "recommended_action":
                            kh_action.strip()
                            or None,

                        "verification":
                            kh_verification.strip()
                            or None,

                        "result":
                            kh_result.strip()
                            or None,

                        "maintenance_record_id":
                            maintenance_id_value,

                        "document_id":
                            document_id_value,

                        "source_page":
                            source_page_value,

                        "source_type":
                            kh_source_type,

                        "confidence":
                            kh_confidence,

                        "created_by":
                            kh_created_by.strip()
                            or "technician",
                    }

                    create_result = api_post(
                        "/knowhow/draft",
                        create_payload,
                    )

                    if create_result:
                        created = (
                            create_result.get(
                                "knowhow",
                                {},
                            )
                        )

                        st.success(
                            "Đã tạo Know-how Draft: "
                            f"{created.get('knowhow_id')}"
                        )

                        st.rerun()

    st.divider()

    st.markdown(
        "### Know-how Cases"
    )

    if not knowhow_items:
        st.info(
            "Chưa có Know-how Case "
            "cho máy này."
        )

    else:
        for item in knowhow_items:
            knowhow_id = item.get(
                "knowhow_id",
                "UNKNOWN",
            )

            title = item.get(
                "title",
                "Untitled",
            )

            status = (
                item.get(
                    "status",
                    "UNKNOWN",
                )
                or "UNKNOWN"
            ).upper()

            confidence = item.get(
                "confidence",
                0.0,
            ) or 0.0

            with st.container(
                border=True
            ):
                top1, top2, top3 = (
                    st.columns(
                        [3, 1, 1]
                    )
                )

                with top1:
                    st.markdown(
                        f"#### {knowhow_id}"
                    )

                    st.markdown(
                        f"**{title}**"
                    )

                with top2:
                    st.metric(
                        "Status",
                        status,
                    )

                with top3:
                    st.metric(
                        "Confidence",
                        f"{confidence * 100:.0f}%",
                    )

                st.divider()

                left, right = st.columns(2)

                with left:
                    st.markdown(
                        "**Observation**"
                    )
                    st.write(
                        item.get(
                            "observation"
                        )
                        or "—"
                    )

                    st.markdown(
                        "**Hypothesis / Cause**"
                    )
                    st.write(
                        item.get(
                            "hypothesis"
                        )
                        or "—"
                    )

                    st.markdown(
                        "**Evidence**"
                    )
                    st.write(
                        item.get(
                            "evidence"
                        )
                        or "—"
                    )

                    st.markdown(
                        "**Diagnostic Check**"
                    )
                    st.write(
                        item.get(
                            "diagnostic_check"
                        )
                        or "—"
                    )

                    st.markdown(
                        "**Ruled-out Causes**"
                    )
                    st.write(
                        item.get(
                            "ruled_out_causes"
                        )
                        or "—"
                    )

                with right:
                    st.markdown(
                        "**Recommended Action**"
                    )
                    st.write(
                        item.get(
                            "recommended_action"
                        )
                        or "—"
                    )

                    st.markdown(
                        "**Verification**"
                    )
                    st.write(
                        item.get(
                            "verification"
                        )
                        or "—"
                    )

                    st.markdown(
                        "**Result**"
                    )
                    st.write(
                        item.get(
                            "result"
                        )
                        or "—"
                    )

                st.divider()

                source_parts = []

                maintenance_record_id = (
                    item.get(
                        "maintenance_record_id"
                    )
                )

                document_id = item.get(
                    "document_id"
                )

                source_page = item.get(
                    "source_page"
                )

                if maintenance_record_id:
                    source_parts.append(
                        "Maintenance Record "
                        f"#{maintenance_record_id}"
                    )

                if document_id:
                    doc_source = (
                        f"Document #{document_id}"
                    )

                    if source_page:
                        doc_source += (
                            f" · Page {source_page}"
                        )

                    source_parts.append(
                        doc_source
                    )

                if source_parts:
                    st.caption(
                        "Source: "
                        + " · ".join(
                            source_parts
                        )
                    )

                else:
                    st.caption(
                        "Source: "
                        f"{item.get('source_type', 'N/A')}"
                    )

                creator = item.get(
                    "created_by"
                )

                reviewer = item.get(
                    "reviewed_by"
                )

                if creator:
                    st.caption(
                        f"Created by: {creator}"
                    )

                if reviewer:
                    st.caption(
                        f"Reviewed by: {reviewer}"
                    )

                review_note = item.get(
                    "review_note"
                )

                if review_note:
                    st.info(
                        "Review note: "
                        f"{review_note}"
                    )

                if status in (
                    "DRAFT",
                    "REJECTED",
                ):
                    if st.button(
                        "Submit for Review",
                        key=(
                            f"submit_"
                            f"{knowhow_id}"
                        ),
                        width="stretch",
                    ):
                        try:
                            response = requests.post(
                                f"{API_URL}"
                                f"/knowhow/"
                                f"{knowhow_id}"
                                "/submit",
                                timeout=5,
                            )

                            response.raise_for_status()

                            st.success(
                                "Know-how đã được "
                                "gửi để review."
                            )

                            st.rerun()

                        except requests.RequestException as exc:
                            st.error(
                                "Không thể submit: "
                                f"{exc}"
                            )

                elif status == "UNDER_REVIEW":
                    st.markdown(
                        "##### Human Review"
                    )

                    reviewer_name = st.text_input(
                        "Reviewer",
                        value=(
                            "senior_technician_demo"
                        ),
                        key=(
                            f"reviewer_"
                            f"{knowhow_id}"
                        ),
                    )

                    reviewer_note = st.text_area(
                        "Review note",
                        key=(
                            f"review_note_"
                            f"{knowhow_id}"
                        ),
                    )

                    approve_col, reject_col = (
                        st.columns(2)
                    )

                    with approve_col:
                        approve_clicked = (
                            st.button(
                                "Approve",
                                key=(
                                    f"approve_"
                                    f"{knowhow_id}"
                                ),
                                width="stretch",
                            )
                        )

                    with reject_col:
                        reject_clicked = (
                            st.button(
                                "Reject",
                                key=(
                                    f"reject_"
                                    f"{knowhow_id}"
                                ),
                                width="stretch",
                            )
                        )

                    review_payload = {
                        "reviewer":
                            reviewer_name.strip()
                            or "reviewer",

                        "note":
                            reviewer_note.strip()
                            or None,
                    }

                    if approve_clicked:
                        result = api_post(
                            "/knowhow/"
                            f"{knowhow_id}"
                            "/approve",
                            review_payload,
                        )

                        if result:
                            st.success(
                                "Know-how APPROVED."
                            )
                            st.rerun()

                    if reject_clicked:
                        result = api_post(
                            "/knowhow/"
                            f"{knowhow_id}"
                            "/reject",
                            review_payload,
                        )

                        if result:
                            st.warning(
                                "Know-how REJECTED."
                            )
                            st.rerun()

                elif status == "APPROVED":
                    st.success(
                        "Human-validated Know-how. "
                        "Eligible for future RAG retrieval."
                    )


st.divider()

st.caption(
    "Digi-Logs Local MVP · "
    "Machine-specific maintenance knowledge"
)
