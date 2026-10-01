import os
from io import BytesIO

import requests
import streamlit as st
from dotenv import load_dotenv

from document_utils.docx_export import create_docx
from document_utils.pdf_export import create_pdf
from document_utils.html_preview import create_html_preview
from document_utils.sanitize import sanitize_text


load_dotenv()

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
)

BRAND_NAME = os.getenv(
    "LEGAL_EASE_BRAND",
    "LegalEase",
)


st.set_page_config(
    page_title=BRAND_NAME,
    page_icon="⚖️",
    layout="wide",
)


# ---------- Custom styling ----------

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #777;
        font-size: 18px;
        margin-bottom: 30px;
    }

    .preview-box {
        background-color: #111827;
        color: #f9fafb;
        padding: 25px;
        border-radius: 12px;
        min-height: 400px;
        max-height: 650px;
        overflow-y: auto;
        white-space: pre-wrap;
        line-height: 1.7;
        font-family: Georgia, serif;
    }

    .disclaimer {
        color: #777;
        font-size: 13px;
        text-align: center;
        margin-top: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Header ----------

st.markdown(
    f'<div class="main-title">⚖️ {BRAND_NAME}</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">AI-Powered Legal Document Drafting</div>',
    unsafe_allow_html=True,
)


# ---------- Session state ----------

if "document" not in st.session_state:
    st.session_state.document = ""

if "editing" not in st.session_state:
    st.session_state.editing = False


# ---------- Input section ----------

st.subheader("Create a Legal Document")

col1, col2 = st.columns(2)

with col1:
    document_type = st.text_input(
        "Document Type",
        placeholder="Example: Rental Agreement",
    )

    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Example:\n"
            "Landlord: Arun Kumar\n"
            "Tenant: Ravi Kumar"
        ),
        height=140,
    )

with col2:
    effective_date = st.text_input(
        "Effective Date",
        placeholder="Example: 01-10-2026",
    )

    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Enter terms separated by semicolons.\n\n"
            "Example:\n"
            "Monthly rent is ₹15,000; "
            "Security deposit is ₹30,000; "
            "Agreement period is 11 months."
        ),
        height=140,
    )


# ---------- Generate button ----------

if st.button(
    "Generate Document",
    type="primary",
    use_container_width=True,
):

    if not document_type.strip():
        st.error("Please enter the document type.")

    elif not parties.strip():
        st.error("Please enter the parties involved.")

    elif not terms.strip():
        st.error("Please enter the terms and conditions.")

    elif not effective_date.strip():
        st.error("Please enter the effective date.")

    else:

        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "effective_date": effective_date,
        }

        with st.spinner("Generating your legal document..."):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=120,
                )

                if response.status_code == 200:

                    result = response.json()

                    generated_document = result.get(
                        "document",
                        "",
                    )

                    if generated_document:

                        st.session_state.document = sanitize_text(
                            generated_document
                        )

                        st.session_state.editing = False

                        st.success(
                            "Legal document generated successfully."
                        )

                    else:
                        st.error(
                            "The backend returned an empty document."
                        )

                else:

                    try:
                        error_data = response.json()
                        error_message = error_data.get(
                            "detail",
                            response.text,
                        )
                    except Exception:
                        error_message = response.text

                    st.error(
                        f"Backend error ({response.status_code}): "
                        f"{error_message}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Cannot connect to the FastAPI backend. "
                    "Make sure the backend is running on "
                    f"{BACKEND_URL}."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The request timed out. "
                    "Please try again."
                )

            except Exception as exc:

                st.error(
                    f"Unexpected error: {exc}"
                )


# ---------- Generated document ----------

if st.session_state.document:

    st.divider()

    st.subheader("Generated Document")

    if not st.session_state.editing:

        preview_html = create_html_preview(
            st.session_state.document
        )

        st.markdown(
            preview_html,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([1, 1])

        with col1:

            if st.button(
                "✏️ Edit Document",
                use_container_width=True,
            ):
                st.session_state.editing = True
                st.rerun()

        with col2:

            if st.button(
                "🔄 Generate Again",
                use_container_width=True,
            ):
                st.session_state.document = ""
                st.session_state.editing = False
                st.rerun()

    else:

        edited_document = st.text_area(
            "Edit your document",
            value=st.session_state.document,
            height=600,
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "💾 Save Changes",
                type="primary",
                use_container_width=True,
            ):

                st.session_state.document = sanitize_text(
                    edited_document
                )

                st.session_state.editing = False

                st.rerun()

        with col2:

            if st.button(
                "Cancel Editing",
                use_container_width=True,
            ):

                st.session_state.editing = False

                st.rerun()


# ---------- Download section ----------

if st.session_state.document:

    st.divider()

    st.subheader("Download Document")

    document_text = st.session_state.document

    col1, col2, col3 = st.columns(3)

    # TXT
    with col1:

        st.download_button(
            label="📄 Download TXT",
            data=document_text.encode("utf-8"),
            file_name="LegalEase_Document.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # DOCX
    with col2:

        try:

            docx_data = create_docx(
                document_text,
                document_type,
            )

            if isinstance(docx_data, BytesIO):
                docx_bytes = docx_data.getvalue()
            else:
                docx_bytes = docx_data

            st.download_button(
                label="📝 Download DOCX",
                data=docx_bytes,
                file_name="LegalEase_Document.docx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                use_container_width=True,
            )

        except Exception as exc:

            st.error(
                f"DOCX export error: {exc}"
            )

    # PDF
    with col3:

        try:

            pdf_data = create_pdf(
                document_text,
                document_type,
            )

            if isinstance(pdf_data, BytesIO):
                pdf_bytes = pdf_data.getvalue()
            else:
                pdf_bytes = pdf_data

            st.download_button(
                label="📕 Download PDF",
                data=pdf_bytes,
                file_name="LegalEase_Document.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        except Exception as exc:

            st.error(
                f"PDF export error: {exc}"
            )


# ---------- Footer ----------

st.markdown(
    """
    <div class="disclaimer">
    LegalEase generates document drafts using AI.
    Generated documents should be reviewed by a qualified legal professional
    before use.
    </div>
    """,
    unsafe_allow_html=True,
)