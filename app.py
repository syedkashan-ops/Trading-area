import io
import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt
import streamlit as st

# Page setup
st.set_page_config(
    page_title="Outlet Audit Report Generator", page_icon="📸", layout="wide"
)

# Custom CSS for polished interface
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #182B49;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #555555;
        margin-bottom: 2rem;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-header">📸 Outlet Before/After Presentation Generator</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Upload outlet data, add comparison image pairs, and export a polished PowerPoint report.</div>',
    unsafe_allow_html=True,
)

# Session state initialization
if "pairs" not in st.session_state:
    st.session_state.pairs = []
if "outlet_name" not in st.session_state:
    st.session_state.outlet_name = ""
if "outlet_code" not in st.session_state:
    st.session_state.outlet_code = ""


def generate_pptx(outlet_name, outlet_code, pairs):
    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 widescreen
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Theme colors
    dark_blue = RGBColor(24, 43, 73)
    white = RGBColor(255, 255, 255)
    brand_blue = RGBColor(30, 144, 255)

    # --- Title Slide ---
    slide = prs.slides.add_slide(blank_layout)
    bg = slide.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = dark_blue
    bg.line.fill.background()

    tb = slide.shapes.add_textbox(
        Inches(1), Inches(2.3), Inches(11.333), Inches(3.0)
    )
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "OUTLET AUDIT REPORT"
    p.font.bold = True
    p.font.size = Pt(22)
    p.font.color.rgb = brand_blue

    p2 = tf.add_paragraph()
    p2.text = f"{outlet_name}"
    p2.font.bold = True
    p2.font.size = Pt(44)
    p2.font.color.rgb = white

    p3 = tf.add_paragraph()
    p3.text = f"Outlet Code: {outlet_code}"
    p3.font.size = Pt(20)
    p3.font.color.rgb = RGBColor(180, 190, 205)

    # --- Photo Comparison Slides ---
    for idx, pair in enumerate(pairs, 1):
        slide = prs.slides.add_slide(blank_layout)

        # Header bar
        bar = slide.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(1.1))
        bar.fill.solid()
        bar.fill.fore_color.rgb = dark_blue
        bar.line.fill.background()

        tb = slide.shapes.add_textbox(
            Inches(0.8), Inches(0.15), Inches(11.7), Inches(0.8)
        )
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = f"{outlet_name} ({outlet_code})"
        p.font.bold = True
        p.font.size = Pt(20)
        p.font.color.rgb = white

        p_sub = tf.add_paragraph()
        p_sub.text = f"Comparison Pair #{idx}"
        p_sub.font.size = Pt(13)
        p_sub.font.color.rgb = brand_blue

        card_w, card_h = Inches(5.6), Inches(5.5)
        top_pos = Inches(1.4)
        before_left = Inches(0.8)
        after_left = Inches(6.9)

        # Labels
        b_box = slide.shapes.add_textbox(
            before_left, top_pos, card_w, Inches(0.4)
        )
        p = b_box.text_frame.paragraphs[0]
        p.text = "BEFORE"
        p.font.bold = True
        p.font.size = Pt(16)
        p.font.color.rgb = RGBColor(220, 53, 69)

        a_box = slide.shapes.add_textbox(
            after_left, top_pos, card_w, Inches(0.4)
        )
        p = a_box.text_frame.paragraphs[0]
        p.text = "AFTER"
        p.font.bold = True
        p.font.size = Pt(16)
        p.font.color.rgb = RGBColor(40, 167, 69)

        # Insert images
        if pair["before"]:
            slide.shapes.add_picture(
                io.BytesIO(pair["before"].getvalue()),
                before_left,
                top_pos + Inches(0.4),
                width=card_w,
            )

        if pair["after"]:
            slide.shapes.add_picture(
                io.BytesIO(pair["after"].getvalue()),
                after_left,
                top_pos + Inches(0.4),
                width=card_w,
            )

    ppt_bytes = io.BytesIO()
    prs.save(ppt_bytes)
    ppt_bytes.seek(0)
    return ppt_bytes


# --- STEP 1: Excel Data Entry ---
st.markdown("### Step 1: Select Outlet Details")
uploaded_excel = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])

if uploaded_excel:
    df = pd.read_excel(uploaded_excel)
    st.dataframe(df.head(3), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        name_col = st.selectbox("Select Name Column", options=df.columns)
    with col2:
        code_col = st.selectbox("Select Code Column", options=df.columns)

    outlet_row = st.selectbox(
        "Select Outlet Row",
        options=range(len(df)),
        format_func=lambda x: f"{df.iloc[x][name_col]} ({df.iloc[x][code_col]})",
    )

    if st.button("Confirm Outlet Selection"):
        st.session_state.outlet_name = str(df.iloc[outlet_row][name_col])
        st.session_state.outlet_code = str(df.iloc[outlet_row][code_col])
        st.success(
            f"Active Outlet: **{st.session_state.outlet_name}** ({st.session_state.outlet_code})"
        )

st.divider()

# --- STEP 2: Sequential Image Upload ---
if st.session_state.outlet_name:
    st.markdown(
        f"### Step 2: Upload Photos for **{st.session_state.outlet_name}**"
    )
    st.info(f"Pairs collected: **{len(st.session_state.pairs)}**")

    with st.form(key="photo_pair_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            before_file = st.file_uploader(
                "BEFORE Photo", type=["png", "jpg", "jpeg"]
            )
        with col_b:
            after_file = st.file_uploader(
                "AFTER Photo", type=["png", "jpg", "jpeg"]
            )

        submit_pair = st.form_submit_button("➕ Save Pair & Next")

        if submit_pair:
            if before_file and after_file:
                st.session_state.pairs.append(
                    {"before": before_file, "after": after_file}
                )
                st.rerun()
            else:
                st.error("Please provide both BEFORE and AFTER files.")

    # Show preview gallery of uploaded pairs
    if st.session_state.pairs:
        st.markdown("#### Uploaded Pairs Preview")
        for idx, pair in enumerate(st.session_state.pairs, 1):
            with st.expander(f"Pair #{idx}", expanded=False):
                p_col1, p_col2 = st.columns(2)
                p_col1.image(
                    pair["before"], caption="Before", use_container_width=True
                )
                p_col2.image(
                    pair["after"], caption="After", use_container_width=True
                )

    st.divider()

    # --- STEP 3: PowerPoint Export ---
    if st.session_state.pairs:
        st.markdown("### Step 3: Generate Presentation")
        if st.button("🚀 Build PPTX Presentation", type="primary"):
            pptx_data = generate_pptx(
                st.session_state.outlet_name,
                st.session_state.outlet_code,
                st.session_state.pairs,
            )

            file_name = f"{st.session_state.outlet_name}_{st.session_state.outlet_code}_Report.pptx".replace(
                " ", "_"
            )

            st.download_button(
                label="📥 Download Presentation (.pptx)",
                data=pptx_data,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )
else:
    st.warning("Upload an Excel file and confirm an outlet above to begin.")
