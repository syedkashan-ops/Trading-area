import io
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Outlet Audit Generator", page_icon="📸", layout="wide"
)

# Application Styling
st.markdown(
    """
    <style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #182B49; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1rem; color: #555555; margin-bottom: 1.5rem; }
    .stButton>button { border-radius: 8px; font-weight: 600; }
    .pair-badge { background-color: #E8F0FE; color: #1E90FF; padding: 4px 12px; border-radius: 12px; font-weight: 600; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-header">📸 Outlet Before & After Presentation Builder</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Fill in the outlet details, sequentially upload image pairs, and construct a presentation.</div>',
    unsafe_allow_html=True,
)

# Session State Initialization
if "outlet_name" not in st.session_state:
    st.session_state.outlet_name = ""
if "outlet_code" not in st.session_state:
    st.session_state.outlet_code = ""
if "pairs" not in st.session_state:
    st.session_state.pairs = []
if "details_locked" not in st.session_state:
    st.session_state.details_locked = False


# PowerPoint Generation Function
def generate_pptx(outlet_name, outlet_code, pairs):
    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 Widescreen layout
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

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

    # --- Comparison Slides ---
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

        card_w = Inches(5.6)
        top_pos = Inches(1.4)
        before_left = Inches(0.8)
        after_left = Inches(6.9)

        # Before & After Header Badges
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

        # Embed Images
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


# --- FORM SECTION 1: Outlet Information ---
if not st.session_state.details_locked:
    st.markdown("### Step 1: Outlet Details")
    with st.form(key="outlet_info_form"):
        col1, col2 = st.columns(2)
        with col1:
            name_input = st.text_input(
                "Outlet Name", placeholder="e.g. Metro Store Downtown"
            )
        with col2:
            code_input = st.text_input(
                "Outlet Code", placeholder="e.g. OUT-8890"
            )

        submit_details = st.form_submit_button("Proceed to Upload Photos ➔")

        if submit_details:
            if name_input.strip() and code_input.strip():
                st.session_state.outlet_name = name_input.strip()
                st.session_state.outlet_code = code_input.strip()
                st.session_state.details_locked = True
                st.rerun()
            else:
                st.error("Please provide both Outlet Name and Outlet Code.")

# --- FORM SECTION 2: Iterative Photo Uploads ---
else:
    # Top info strip with option to reset
    st.markdown(
        f"**Active Outlet:** `{st.session_state.outlet_name}` | **Code:** `{st.session_state.outlet_code}`"
    )

    if st.button("🔄 Change Outlet Details"):
        st.session_state.details_locked = False
        st.session_state.pairs = []
        st.rerun()

    st.divider()

    current_pair_num = len(st.session_state.pairs) + 1
    st.markdown(f"### Upload Image Pair #{current_pair_num}")

    with st.form(key=f"upload_form_pair_{current_pair_num}", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            before_file = st.file_uploader(
                f"Before Photo (Pair #{current_pair_num})",
                type=["png", "jpg", "jpeg"],
            )
        with col_b:
            after_file = st.file_uploader(
                f"After Photo (Pair #{current_pair_num})",
                type=["png", "jpg", "jpeg"],
            )

        save_and_continue = st.form_submit_button(
            f"➕ Save Pair #{current_pair_num} & Add Next Pair"
        )

        if save_and_continue:
            if before_file and after_file:
                st.session_state.pairs.append(
                    {"before": before_file, "after": after_file}
                )
                st.success(f"Pair #{current_pair_num} added successfully!")
                st.rerun()
            else:
                st.error("Please select BOTH Before and After photos.")

    # Show list of added pairs
    if st.session_state.pairs:
        st.divider()
        st.markdown(f"### Uploaded Pairs ({len(st.session_state.pairs)})")

        for idx, pair in enumerate(st.session_state.pairs, 1):
            with st.expander(f"📷 Pair #{idx}", expanded=(idx == len(st.session_state.pairs))):
                p_col1, p_col2 = st.columns(2)
                p_col1.image(
                    pair["before"],
                    caption=f"Before #{idx}",
                    use_container_width=True,
                )
                p_col2.image(
                    pair["after"],
                    caption=f"After #{idx}",
                    use_container_width=True,
                )

        # --- SECTION 3: Final Presentation Download ---
        st.divider()
        st.markdown("### Generate Final Report")
        if st.button("🚀 Build & Download Presentation", type="primary"):
            pptx_data = generate_pptx(
                st.session_state.outlet_name,
                st.session_state.outlet_code,
                st.session_state.pairs,
            )

            file_filename = f"{st.session_state.outlet_name}_{st.session_state.outlet_code}_Report.pptx".replace(
                " ", "_"
            )

            st.download_button(
                label="📥 Download Presentation (.pptx)",
                data=pptx_data,
                file_name=file_filename,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )
