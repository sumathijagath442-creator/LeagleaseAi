import os
from datetime import date

import requests
import streamlit as st

from dotenv import load_dotenv

from services.document_export import (
    filename_for,
    format_docx,
    format_pdf,
    format_txt,
)

from services.text_utils import (
    text_to_preview_html,
)


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .hero {
        padding: 1.5rem 1.8rem;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            #111827,
            #263449
        );
        color: white;
        margin-bottom: 1.2rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.4rem;
    }

    .hero p {
        margin: .4rem 0 0;
        opacity: .85;
    }

    .preview {
        background: #111827;
        color: #f9fafb;
        padding: 1.4rem;
        border-radius: 14px;
        max-height: 650px;
        overflow-y: auto;
        line-height: 1.65;
    }

    .preview h3 {
        color: #93c5fd;
        margin-top: 1.1rem;
    }

    .notice {
        padding: .8rem 1rem;
        border-left: 4px solid #f59e0b;
        background: #fff7ed;
        color: #7c2d12;
        border-radius: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.markdown(
    """
    <div class="hero">

        <h1>⚖️ LegalEase</h1>

        <p>
            AI-assisted legal document drafting,
            editing, and export.
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="notice">

        <strong>Review required:</strong>

        AI-generated text is a draft,
        not legal advice.

        Verify facts, jurisdiction,
        clauses, and enforceability
        before signing or using it.

    </div>
    """,
    unsafe_allow_html=True,
)


st.write("")


# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------

if "document_text" not in st.session_state:

    st.session_state.document_text = ""


if "document_type" not in st.session_state:

    st.session_state.document_type = (
        "Non-Disclosure Agreement"
    )


# ---------------------------------------------------------
# Layout
# ---------------------------------------------------------

left, right = st.columns(
    [0.95, 1.25],
    gap="large",
)


# =========================================================
# LEFT COLUMN
# =========================================================

with left:

    st.subheader(
        "Document details"
    )

    document_type = st.selectbox(
        "Document type",
        [
            "Employment Contract",
            "Employment Offer Letter",
            "Non-Disclosure Agreement",
            "Lease Agreement",
            "Freelance Work Contract",
            "Service Agreement",
            "Partnership Agreement",
            "General Agreement",
            "Custom",
        ],
        index=2,
    )

    if document_type == "Custom":

        document_type = st.text_input(
            "Custom document type",
            value=st.session_state.document_type,
        )

    parties = st.text_area(
        "Parties involved",
        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),
        height=100,
    )

    terms = st.text_area(
        "Terms & conditions",
        placeholder=(
            "Payment within 30 days of invoice; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        height=150,
        help="Separate terms with semicolons.",
    )

    effective_date = st.date_input(
        "Effective date",
        value=date.today(),
    )

    jurisdiction = st.text_input(
        "Jurisdiction (optional)",
        placeholder="e.g. India, Tamil Nadu",
    )

    additional_instructions = st.text_area(
        "Additional instructions (optional)",
        placeholder=(
            "Use plain professional language "
            "and include a notice clause."
        ),
        height=100,
    )

    logo = st.file_uploader(
        "Optional logo",
        type=[
            "png",
            "jpg",
            "jpeg",
        ],
        help=(
            "The uploaded image is used only "
            "for the current DOCX/PDF export."
        ),
    )

    # -----------------------------------------------------
    # Generate
    # -----------------------------------------------------

    if st.button(
        "Generate Document",
        type="primary",
        use_container_width=True,
    ):

        if not parties.strip():

            st.error(
                "Please provide the parties."
            )

        elif not terms.strip():

            st.error(
                "Please provide at least one term."
            )

        elif not document_type.strip():

            st.error(
                "Please provide a document type."
            )

        else:

            payload = {
                "document_type": document_type.strip(),
                "parties": parties.strip(),
                "terms": terms.strip(),
                "effective_date": effective_date.isoformat(),
                "jurisdiction": jurisdiction.strip(),
                "additional_instructions": (
                    additional_instructions.strip()
                ),
            }

            with st.spinner(
                "Generating your draft with Gemini..."
            ):

                try:

                    response = requests.post(
                        f"{BACKEND_URL}/generate",
                        json=payload,
                        timeout=180,
                    )

                    if response.ok:

                        data = response.json()

                        st.session_state.document_text = (
                            data["content"]
                        )

                        st.session_state.document_type = (
                            document_type
                        )

                        st.success(
                            "Document generated successfully."
                        )

                    else:

                        try:

                            detail = response.json().get(
                                "detail",
                                response.text,
                            )

                        except ValueError:

                            detail = response.text

                        st.error(
                            f"Backend error "
                            f"({response.status_code}): "
                            f"{detail}"
                        )

                except requests.RequestException as exc:

                    st.error(
                        "Could not connect to the FastAPI backend. "
                        "Make sure Uvicorn is running."
                    )

                    st.caption(
                        str(exc)
                    )


# =========================================================
# RIGHT COLUMN
# =========================================================

with right:

    st.subheader(
        "Document preview"
    )

    if st.session_state.document_text:

        # -------------------------------------------------
        # Preview
        # -------------------------------------------------

        st.markdown(
            f"""
            <div class="preview">

                {
                    text_to_preview_html(
                        st.session_state.document_text
                    )
                }

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        # -------------------------------------------------
        # Editor
        # -------------------------------------------------

        edited = st.text_area(
            "Edit document",
            value=st.session_state.document_text,
            height=430,
        )

        st.session_state.document_text = edited

        # -------------------------------------------------
        # Logo bytes
        # -------------------------------------------------

        logo_bytes = (
            logo.getvalue()
            if logo
            else None
        )

        # -------------------------------------------------
        # Downloads
        # -------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            st.download_button(
                "Download TXT",
                data=format_txt(
                    st.session_state.document_text
                ),
                file_name=filename_for(
                    st.session_state.document_type,
                    "txt",
                ),
                mime="text/plain",
                use_container_width=True,
            )

        with col2:

            st.download_button(
                "Download DOCX",
                data=format_docx(
                    st.session_state.document_text,
                    st.session_state.document_type,
                    terms=terms,
                    logo_bytes=logo_bytes,
                ),
                file_name=filename_for(
                    st.session_state.document_type,
                    "docx",
                ),
                mime=(
                    "application/"
                    "vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                use_container_width=True,
            )

        with col3:

            st.download_button(
                "Download PDF",
                data=format_pdf(
                    st.session_state.document_text,
                    st.session_state.document_type,
                    terms=terms,
                    logo_bytes=logo_bytes,
                ),
                file_name=filename_for(
                    st.session_state.document_type,
                    "pdf",
                ),
                mime="application/pdf",
                use_container_width=True,
            )

    else:

        st.info(
            "Your generated document will appear here."
        )

        st.markdown(
            """
            ### Workflow

            **1.** Enter the parties and terms.

            **2.** Generate the document.

            **3.** Review and edit the generated text.

            **4.** Download TXT, DOCX, or PDF.
            """
        )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.divider()

st.caption(
    "LegalEase is an AI-assisted drafting application. "
    "It does not provide legal advice."
)