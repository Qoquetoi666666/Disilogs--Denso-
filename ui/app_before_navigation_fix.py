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


(
    tab_overview,
    tab_scan,
    tab_history,
    tab_record,
    tab_documents,
) = st.tabs(
    [
        "Machine Overview",
        "Scan Machine",
        "Maintenance History",
        "Record Maintenance",
        "Documents",
    ]
)

def open_machine_from_scan(machine_id):
    st.session_state["active_machine"] = machine_id
    st.session_state["machine_select"] = machine_id
    st.session_state["scan_result"] = None


with tab_scan:
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


with tab_overview:
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


with tab_history:
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


with tab_record:
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


with tab_documents:
    st.subheader(
        "Technical Documents"
    )

    if not documents:
        st.info(
            "Chưa có tài liệu được lập chỉ mục. "
            "Document Library sẽ được xây ở M4."
        )

    else:
        for doc in documents:
            st.write(
                f"**{doc.get('title')}**"
            )

            st.caption(
                doc.get(
                    "document_type",
                    "document"
                )
            )


st.divider()

st.caption(
    "Digi-Logs Local MVP · "
    "Machine-specific maintenance knowledge"
)
