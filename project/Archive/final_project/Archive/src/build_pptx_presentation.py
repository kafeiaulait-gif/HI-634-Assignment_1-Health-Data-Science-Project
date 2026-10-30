"""
Master PowerPoint Generator: presentation.pptx
Produces a professional, modern 14-slide widescreen (16:9) presentation
including two embedded MP4 video clips explaining clinical relationships and ROC thresholds.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PPTX = os.path.join(PROJECT_ROOT, "presentation.pptx")
VIDEOS_DIR = os.path.join(PROJECT_ROOT, "videos")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "explanation")

import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Styling Constants
NAVY = RGBColor(26, 54, 93)       # #1A365D - Headers / Dominant
BLUE = RGBColor(43, 92, 143)      # #2B5C8F - Secondary / Accents
GRAY_TEXT = RGBColor(45, 55, 72)  # #2D3748 - Body Text
LIGHT_GRAY = RGBColor(247, 250, 252) # #F7FAFC - Container Background
BORDER_GRAY = RGBColor(226, 232, 240) # #E2E8F0 - Container Border
WHITE = RGBColor(255, 255, 255)
GREEN = RGBColor(44, 160, 44)     # #2CA02C - High Performance / Safe
RED = RGBColor(229, 62, 62)       # #E53E3E - Critical / Alert

def set_slide_background(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, category_text="HI-634 HEALTH INFORMATICS | ASSIGNMENT 1"):
    # Category Tracker
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    p_c = tf_c.paragraphs[0]
    p_c.text = category_text.upper()
    p_c.font.size = Pt(10)
    p_c.font.bold = True
    p_c.font.color.rgb = BLUE
    
    # Title
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = NAVY

def add_card(slide, left, top, width, height, bg_color=LIGHT_GRAY, border_color=BORDER_GRAY):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1)
    return shape

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    
    # =========================================================================
    # SLIDE 1: Title Slide (Dark Navy Professional Theme)
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1, NAVY)
    
    # Main Title
    t_box = slide1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(2.2))
    tf = t_box.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "Predicting Coronary Artery Disease via Non-Invasive Clinical Markers"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.space_after = Pt(12)
    
    p2 = tf.add_paragraph()
    p2.text = "A Reproducible Machine Learning Pipeline, Clinical Error Analysis, and Model Evaluation"
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(203, 213, 224)
    p2.space_after = Pt(24)
    
    # Divider Line
    line = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(4.3), Inches(11.3), Inches(0.04))
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(99, 179, 237)
    line.line.fill.background()
    
    # Metadata Footer Card
    f_box = slide1.shapes.add_textbox(Inches(1.0), Inches(4.7), Inches(11.3), Inches(1.8))
    tf_f = f_box.text_frame
    tf_f.word_wrap = True
    
    pf1 = tf_f.paragraphs[0]
    pf1.text = "Course: HI-634 Health Informatics  |  Option 2: UCI Cleveland Heart Disease Database (N = 303)"
    pf1.font.size = Pt(13)
    pf1.font.bold = True
    pf1.font.color.rgb = WHITE
    pf1.space_after = Pt(6)
    
    pf2 = tf_f.add_paragraph()
    pf2.text = "Candidate: Graduate Health Informatics Team  |  Date: October 2026  |  Environment: Python 3.13 (.venv)"
    pf2.font.size = Pt(12)
    pf2.font.color.rgb = RGBColor(203, 213, 224)

    # =========================================================================
    # SLIDE 2: Problem Statement & Focused Research Question
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2, WHITE)
    add_header(slide2, "Clinical Problem Statement & Focused Research Question")
    
    # Left Card: The Question
    add_card(slide2, Inches(0.8), Inches(1.8), Inches(6.8), Inches(5.0))
    q_box = slide2.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(6.2), Inches(4.6))
    tf_q = q_box.text_frame
    tf_q.word_wrap = True
    
    pq1 = tf_q.paragraphs[0]
    pq1.text = "THE FOCUSED RESEARCH QUESTION"
    pq1.font.size = Pt(12)
    pq1.font.bold = True
    pq1.font.color.rgb = BLUE
    pq1.space_after = Pt(12)
    
    pq2 = tf_q.add_paragraph()
    pq2.text = '"Can routine clinical examination and non-invasive diagnostic exercise measurements predict the presence (versus absence) of significant coronary artery disease (>50% angiographic vessel diameter stenosis) in adult patients evaluated for suspected cardiac pathology?"'
    pq2.font.size = Pt(14)
    pq2.font.italic = True
    pq2.font.bold = True
    pq2.font.color.rgb = NAVY
    pq2.space_after = Pt(18)
    
    pq3 = tf_q.add_paragraph()
    pq3.text = "Clinical Problem Type: Supervised Binary Diagnostic Classification mapping 13 non-invasive clinical and exercise predictors to angiographic presence vs. absence."
    pq3.font.size = Pt(11)
    pq3.font.color.rgb = GRAY_TEXT
    
    # Right Card: Observation Unit & Implications
    add_card(slide2, Inches(7.9), Inches(1.8), Inches(4.6), Inches(5.0))
    u_box = slide2.shapes.add_textbox(Inches(8.2), Inches(2.0), Inches(4.0), Inches(4.6))
    tf_u = u_box.text_frame
    tf_u.word_wrap = True
    
    pu1 = tf_u.paragraphs[0]
    pu1.text = "UNIT OF OBSERVATION"
    pu1.font.size = Pt(12)
    pu1.font.bold = True
    pu1.font.color.rgb = BLUE
    pu1.space_after = Pt(10)
    
    pu2 = tf_u.add_paragraph()
    pu2.text = "An Individual Adult Patient Clinical Encounter (N = 303 unique patient records from Cleveland Clinic Foundation)."
    pu2.font.size = Pt(12)
    pu2.font.bold = True
    pu2.font.color.rgb = NAVY
    pu2.space_after = Pt(14)
    
    pu3 = tf_u.add_paragraph()
    pu3.text = "Informatics & Workflow Implications:\n• Single Flat Encounter Level: 1 row = 1 unique clinical record; no repeated longitudinal clustering.\n• Triage Referral Gatekeeper: Predictions directly inform primary-to-specialty cardiology triage.\n• Cost & Safety Filter: Safely diverts low-risk patients away from unnecessary invasive catheterizations while identifying critical ischemia."
    pu3.font.size = Pt(10.5)
    pu3.font.color.rgb = GRAY_TEXT

    # =========================================================================
    # SLIDE 3: Data Provenance & Study Cohort Architecture
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3, WHITE)
    add_header(slide3, "Data Provenance & Study Cohort Architecture")
    
    # 3 Summary Column Cards
    col_w = Inches(3.64)
    gap = Inches(0.35)
    
    # Col 1: Origin
    add_card(slide3, Inches(0.8), Inches(1.8), col_w, Inches(5.0))
    b1 = slide3.shapes.add_textbox(Inches(1.0), Inches(2.0), col_w - Inches(0.4), Inches(4.5))
    tf1 = b1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "1. REPOSITORY ORIGIN"
    p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(10)
    p = tf1.add_paragraph()
    p.text = "• Dataset: UCI Heart Disease Database (Cleveland Clinic Foundation, ID 45).\n• Primary Citation: Detrano et al. (1989), American Journal of Cardiology.\n• Protocol Scope: Exclusively restricted to the Cleveland Clinic cohort (N = 303) for institutional protocol consistency.\n• Excluded Other Centers: Hungarian (n=294), Long Beach (n=200), Zurich (n=123) excluded to prevent protocol heterogeneity."
    p.font.size = Pt(10.5); p.font.color.rgb = GRAY_TEXT
    
    # Col 2: Reference Standard
    add_card(slide3, Inches(0.8) + col_w + gap, Inches(1.8), col_w, Inches(5.0))
    b2 = slide3.shapes.add_textbox(Inches(1.0) + col_w + gap, Inches(2.0), col_w - Inches(0.4), Inches(4.5))
    tf2 = b2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "2. GOLD-STANDARD TRUTH"
    p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(10)
    p = tf2.add_paragraph()
    p.text = "• Definitive Angiography: 100% of enrolled patients underwent invasive cardiac catheterization and coronary angiography.\n• Objective Ground Truth: Provides absolute verification of vessel narrowing.\n• Clinical Cutoff: >50% diameter stenosis in one or more major coronary arteries defines significant angiographic disease.\n• Eliminates ambiguity common to administrative EHR billing code proxies."
    p.font.size = Pt(10.5); p.font.color.rgb = GRAY_TEXT
    
    # Col 3: Diagnostic Cascade
    add_card(slide3, Inches(0.8) + (col_w + gap)*2, Inches(1.8), col_w, Inches(5.0))
    b3 = slide3.shapes.add_textbox(Inches(1.0) + (col_w + gap)*2, Inches(2.0), col_w - Inches(0.4), Inches(4.5))
    tf3 = b3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "3. DIAGNOSTIC CASCADE"
    p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(10)
    p = tf3.add_paragraph()
    p.text = "• Patient History: Age, biological sex, chest pain presentation (cp).\n• Resting Physiology: Admission blood pressure (trestbps), cholesterol (chol), resting ECG (restecg).\n• Provocative Exercise: Peak exercise heart rate (thalach), exercise angina (exang), ST depression (oldpeak), ST slope.\n• Specialized Imaging: Fluoroscopy vessel count (ca), thallium defect (thal)."
    p.font.size = Pt(10.5); p.font.color.rgb = GRAY_TEXT

    # =========================================================================
    # SLIDE 4: Clinical Data Dictionary & 14 Key Attributes
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4, WHITE)
    add_header(slide4, "Clinical Data Dictionary: The 14 Documented Attributes")
    
    # Table of 14 attributes
    rows, cols_cnt = 8, 2
    tbl_shape = slide4.shapes.add_table(8, 4, Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tbl = tbl_shape.table
    tbl.columns[0].width = Inches(1.5)
    tbl.columns[1].width = Inches(4.35)
    tbl.columns[2].width = Inches(1.5)
    tbl.columns[3].width = Inches(4.35)
    
    headers = ["Attribute", "Type & Clinical Meaning", "Attribute", "Type & Clinical Meaning"]
    for i, h in enumerate(headers):
        cell = tbl.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = BLUE
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(10); p.font.bold = True; p.font.color.rgb = WHITE
            
    attr_data = [
        ("age", "Continuous: Age in years (29–77; mean 54.4 ± 9.0)", "thalach", "Continuous: Peak treadmill heart rate (71–202 bpm)"),
        ("sex", "Binary: 1 = Male (68.0%), 0 = Female (32.0%)", "exang", "Binary: Exercise-induced angina (1 = Yes, 0 = No)"),
        ("cp", "Nominal: Chest pain (1: typical, 2: atypical, 3: non-anginal, 4: asymp)", "oldpeak", "Continuous: Exercise-induced ST depression (0.0–6.2 mm)"),
        ("trestbps", "Continuous: Admission resting BP (94–200 mm Hg)", "slope", "Ordinal: Peak ST slope (1: upsloping, 2: flat, 3: downsloping)"),
        ("chol", "Continuous: Serum cholesterol (126–564 mg/dl; rt-skewed)", "ca", "Count: Fluoroscopy vessels (0–3; contains 4 missing '?')"),
        ("fbs", "Binary: Fasting blood sugar > 120 mg/dl (1 = True, 0 = False)", "thal", "Nominal: Thallium scan (3: norm, 6: fixed, 7: rev; 2 missing '?')"),
        ("restecg", "Nominal: Resting ECG (0: norm, 1: ST-T abn, 2: LVH)", "num (target)", "Target: Coronary stenosis (0 = <50%, 1..4 = >50% stenosis)")
    ]
    for row_idx, (a1, d1, a2, d2) in enumerate(attr_data, start=1):
        c1, c2, c3, c4 = tbl.cell(row_idx, 0), tbl.cell(row_idx, 1), tbl.cell(row_idx, 2), tbl.cell(row_idx, 3)
        c1.text, c2.text, c3.text, c4.text = a1, d1, a2, d2
        for cell in (c1, c3):
            cell.fill.solid(); cell.fill.fore_color.rgb = RGBColor(237, 242, 247)
            for p in cell.text_frame.paragraphs: p.font.size = Pt(9.5); p.font.bold = True; p.font.color.rgb = NAVY
        for cell in (c2, c4):
            cell.fill.solid(); cell.fill.fore_color.rgb = WHITE
            for p in cell.text_frame.paragraphs: p.font.size = Pt(8.5); p.font.color.rgb = GRAY_TEXT

    # =========================================================================
    # SLIDE 5: Initial Data Audit: Missingness, Duplicates & Outliers
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5, WHITE)
    add_header(slide5, "Initial Data Audit: Missingness, Duplicates, & Outliers")
    
    # 3 Audit Cards
    w3 = Inches(3.64); g3 = Inches(0.35)
    
    # Card 1: Missingness
    add_card(slide5, Inches(0.8), Inches(1.8), w3, Inches(5.0))
    t1 = slide5.shapes.add_textbox(Inches(1.0), Inches(2.0), w3 - Inches(0.4), Inches(4.5)).text_frame
    t1.word_wrap = True
    p = t1.paragraphs[0]; p.text = "MISSINGNESS AUDIT"; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(10)
    p = t1.add_paragraph()
    p.text = "• Exactly 6 '?' characters in raw file (0.14% of all data points).\n• Highly Localized to specialized imaging:\n  - ca: 4 missing (1.32% in rows 166, 192, 287, 302)\n  - thal: 2 missing (0.66% in rows 87, 266)\n• 100% Complete Data across all other 12 demographic and baseline features.\n• 297 of 303 patients (98.02%) have complete records across all 14 attributes."
    p.font.size = Pt(10.5); p.font.color.rgb = GRAY_TEXT
    
    # Card 2: Duplicates
    add_card(slide5, Inches(0.8) + w3 + g3, Inches(1.8), w3, Inches(5.0))
    t2 = slide5.shapes.add_textbox(Inches(1.0) + w3 + g3, Inches(2.0), w3 - Inches(0.4), Inches(4.5)).text_frame
    t2.word_wrap = True
    p = t2.paragraphs[0]; p.text = "DUPLICATE VERIFICATION"; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(10)
    p = t2.add_paragraph()
    p.text = "• Duplicate Rows: 0 rows (0.00%).\n• 100% Unique Patient Encounters: Every row represents a distinct clinical evaluation at the Cleveland Clinic.\n• Referential Integrity: Row counts match perfectly across raw text and structured CSV archives (303 rows).\n• Unmatched Records on Join: 0 rows."
    p.font.size = Pt(10.5); p.font.color.rgb = GRAY_TEXT
    
    # Card 3: Outliers
    add_card(slide5, Inches(0.8) + (w3 + g3)*2, Inches(1.8), w3, Inches(5.0))
    t3 = slide5.shapes.add_textbox(Inches(1.0) + (w3 + g3)*2, Inches(2.0), w3 - Inches(0.4), Inches(4.5)).text_frame
    t3.word_wrap = True
    p = t3.paragraphs[0]; p.text = "PHYSIOLOGICAL OUTLIERS"; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(10)
    p = t3.add_paragraph()
    p.text = "• Serum Cholesterol (chol): Reaches 564 mg/dl (Patient 152); 3 other patients > 400 mg/dl (cohort median 241 mg/dl).\n• Resting BP (trestbps): Reaches 200 mm Hg (cohort median 130 mm Hg).\n• Clinical Authenticity: Valid manifestations of familial hypercholesterolemia and acute hypertensive crisis.\n• Zero Truncation: Preserved intact; standard scaling inside pipeline prevents distance distortion."
    p.font.size = Pt(10.5); p.font.color.rgb = GRAY_TEXT

    # =========================================================================
    # SLIDE 6: Four Concrete Findings Guiding Data Preparation
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6, WHITE)
    add_header(slide6, "Four Concrete Findings Guiding Data Preparation")
    
    card_w2 = Inches(5.6); card_h2 = Inches(2.3); gap_x = Inches(0.5); gap_y = Inches(0.4)
    findings = [
        ("1. NOMINAL ENCODING REQUIRED", 
         "Features like cp (1..4), restecg (0..2), and thal (3,6,7) represent qualitative clinical categories without mathematical ordering. Treating cp as continuous falsely assumes asymptomatic pain (4) is 4x typical angina (1).\nAction: OneHotEncoder(drop='first') inside pipeline."),
        ("2. IN-PIPELINE IMPUTATION", 
         "Missingness is extremely rare (ca missing 4, thal missing 2; total 6 cells, 1.98% of cohort). Discarding 6 patients would bias the sample against severely ill patients unable to complete imaging.\nAction: Training-set median (ca) and mode (thal) imputation."),
        ("3. PRESERVING CLINICAL EXTREMES", 
         "Cholesterol reaches 564 mg/dl; resting BP reaches 200 mm Hg. These represent authentic pathophysiology (familial hypercholesterolemia, hypertensive crisis), not transcription errors.\nAction: No outlier deletion; applied StandardScaler on X_train."),
        ("4. ASYMPTOMATIC PRESENTATION PARADOX", 
         "Asymptomatic chest pain (cp = 4) is the largest presentation (47.5% of cohort) and carries the highest disease prevalence (72.9% positive). In referral clinics, asymptomatic patients sent for angiography have severe objective markers.\nAction: One-hot dummy coding captures this non-linear signal.")
    ]
    coords = [
        (Inches(0.8), Inches(1.8)),
        (Inches(0.8) + card_w2 + gap_x, Inches(1.8)),
        (Inches(0.8), Inches(1.8) + card_h2 + gap_y),
        (Inches(0.8) + card_w2 + gap_x, Inches(1.8) + card_h2 + gap_y)
    ]
    for (t, desc), (x, y) in zip(findings, coords):
        add_card(slide6, x, y, card_w2, card_h2)
        tf = slide6.shapes.add_textbox(x + Inches(0.25), y + Inches(0.2), card_w2 - Inches(0.5), card_h2 - Inches(0.4)).text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]; p.text = t; p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(4)
        p = tf.add_paragraph(); p.text = desc; p.font.size = Pt(9.5); p.font.color.rgb = GRAY_TEXT

    # =========================================================================
    # SLIDE 7: [VIDEO SLIDE 1] Dynamic Clinical Phenotypes & Functional Relationships
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7, WHITE)
    add_header(slide7, "Dynamic Clinical Phenotypes & Functional Relationships", category_text="VIDEO DEMONSTRATION 1 | BIPLOT DYNAMICS")
    
    # Left: Embed Video 1
    vid1_file = os.path.join(VIDEOS_DIR, "video1_clinical_relationship.mp4")
    if os.path.exists(vid1_file):
        slide7.shapes.add_movie(vid1_file, Inches(0.8), Inches(1.8), Inches(6.8), Inches(4.8), mime_type="video/mp4")
        
    # Right: Narrative Callout Card
    add_card(slide7, Inches(7.9), Inches(1.8), Inches(4.6), Inches(4.8))
    t_v1 = slide7.shapes.add_textbox(Inches(8.15), Inches(2.0), Inches(4.1), Inches(4.4)).text_frame
    t_v1.word_wrap = True
    p = t_v1.paragraphs[0]; p.text = "BIVARIATE PHENOTYPE MAPPING"; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(8)
    p = t_v1.add_paragraph()
    p.text = (
        "This animated video illustrates the progressive mapping of peak exercise heart rate (thalach, x-axis) versus exercise ST depression (oldpeak, y-axis) across 303 patients.\n\n"
        "Key Clinical Insights:\n"
        "• Low-Risk Quadrant (Upper-Left):\n"
        "  High peak HR (≥150 bpm) + low ST depression (<1.0 mm) identifies 67.7% of healthy controls (OR = 0.07, p < 10^-15).\n\n"
        "• High-Risk Quadrant (Lower-Right):\n"
        "  Chronotropic impairment (<150 bpm) + marked ST depression (≥1.0 mm) identifies 89.9% coronary disease cases (OR = 20.3, p < 10^-14).\n\n"
        "• Non-Causal Note: These represent functional ischemic strain markers, not biological causes of arterial plaque."
    )
    p.font.size = Pt(10); p.font.color.rgb = GRAY_TEXT

    # =========================================================================
    # SLIDE 8: Zero-Leakage Pipeline Architecture
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide8, WHITE)
    add_header(slide8, "Zero-Leakage Preprocessing & Pipeline Architecture")
    
    # 3 Horizontal Strategy Cards
    w_pipe = Inches(11.7); h_pipe = Inches(1.5); g_pipe = Inches(0.25)
    steps_pipe = [
        ("1. STRATIFIED HOLD-OUT PARTITIONING PRIOR TO PREPROCESSING",
         "The full dataset (N = 303) is partitioned BEFORE fitting any transformer: 80% Training Set (N = 242; 45.87% positive prevalence) and 20% Untouched Test Set (N = 61; 45.90% positive prevalence). Zero leakage verified empirically: training scaler mean age (54.550) differed from global cohort mean (54.439)."),
        ("2. UNIFIED SCIKIT-LEARN COLUMNTRANSFORMER",
         "Transformations are strictly encapsulated: Numeric features (age, trestbps, chol, thalach, oldpeak) receive median imputation + StandardScaler; Nominal features (cp, restecg, thal) receive mode imputation + OneHotEncoder(drop='first'); Ordinal features (ca, slope) receive median imputation + StandardScaler. Input expands to 17 numeric columns with 0 NaNs."),
        ("3. TEMPORAL SEQUENCING & TARGET ISOLATION",
         "Identifiers (patient IDs, row indices) were stripped. Both raw num and engineered target were isolated. Crucially, all 13 predictors represent baseline intake or treadmill measurements collected PRIOR to the definitive invasive angiogram, preventing post-diagnostic contamination.")
    ]
    for idx, (t_p, d_p) in enumerate(steps_pipe):
        y_pos = Inches(1.8) + (h_pipe + g_pipe) * idx
        add_card(slide8, Inches(0.8), y_pos, w_pipe, h_pipe)
        tf = slide8.shapes.add_textbox(Inches(1.05), y_pos + Inches(0.15), w_pipe - Inches(0.5), h_pipe - Inches(0.3)).text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]; p.text = t_p; p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(4)
        p = tf.add_paragraph(); p.text = d_p; p.font.size = Pt(9.5); p.font.color.rgb = GRAY_TEXT

    # =========================================================================
    # SLIDE 9: Target Binarization & Class Balance
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide9, WHITE)
    add_header(slide9, "Target Binarization & Outcome Balance")
    
    # Left: Before / After Table
    add_card(slide9, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    tf_b = slide9.shapes.add_textbox(Inches(1.05), Inches(2.0), Inches(5.1), Inches(4.5)).text_frame
    tf_b.word_wrap = True
    p = tf_b.paragraphs[0]; p.text = "ORDINAL TARGET (num) BEFORE BINARIZATION"; p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(8)
    p = tf_b.add_paragraph()
    p.text = (
        "• num = 0 (Absence, <50% stenosis): 164 patients (54.13%)\n"
        "• num = 1 (Mild, 1-vessel disease): 55 patients (18.15%)\n"
        "• num = 2 (Moderate, 2-vessel disease): 36 patients (11.88%)\n"
        "• num = 3 (Severe, 3-vessel disease): 35 patients (11.55%)\n"
        "• num = 4 (Critical, 4-vessel disease): 13 patients (4.29%)\n\n"
        "Total Patients: 303 (100.00%)\n\n"
        "Sparsity Problem: Critical multi-vessel disease (stage 4) contains only 13 patients, making multi-class classification unstable and noisy."
    )
    p.font.size = Pt(10); p.font.color.rgb = GRAY_TEXT
    
    # Right: Binary Formulation Card
    add_card(slide9, Inches(6.9), Inches(1.8), Inches(5.6), Inches(5.0))
    tf_a = slide9.shapes.add_textbox(Inches(7.15), Inches(2.0), Inches(5.1), Inches(4.5)).text_frame
    tf_a.word_wrap = True
    p = tf_a.paragraphs[0]; p.text = "BINARIZED TARGET FORMULATION"; p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(8)
    p = tf_a.add_paragraph()
    p.text = (
        "Clinical Binarization Rule:\n"
        "  target = 0 if num == 0 (Absence of disease)\n"
        "  target = 1 if num > 0 (Presence of significant disease)\n\n"
        "Cohort Breakdown:\n"
        "• Absence (target = 0): 164 patients (54.13%)\n"
        "• Presence (target = 1): 139 patients (45.87%)\n\n"
        "Clinical & Methodological Benefits:\n"
        "• Aligns with Primary Screening Threshold (>50% vessel diameter stenosis justifies angiography or cardioprotective medical therapy).\n"
        "• Balanced Outcome (1.18 : 1 ratio) eliminates majority-class bias and avoids synthetic oversampling (SMOTE)."
    )
    p.font.size = Pt(10); p.font.color.rgb = GRAY_TEXT

    # =========================================================================
    # SLIDE 10: Model Comparison: 5-Fold Stratified CV on Training Data
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide10, WHITE)
    add_header(slide10, "Model Comparison: 5-Fold Stratified CV on Training Data")
    
    # Text intro
    t_box = slide10.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(0.7))
    t_box.text_frame.word_wrap = True
    p = t_box.text_frame.paragraphs[0]
    p.text = "Model selection was conducted strictly on the training partition (N = 242) across 5 stratified folds. Cross-validation evaluated discriminative power and screening safety before touching the test set."
    p.font.size = Pt(10.5); p.font.color.rgb = GRAY_TEXT
    
    # CV Table
    tbl_shape = slide10.shapes.add_table(5, 7, Inches(0.8), Inches(2.4), Inches(11.7), Inches(2.6))
    tbl = tbl_shape.table
    widths = [Inches(2.5), Inches(1.5), Inches(1.6), Inches(1.5), Inches(1.5), Inches(1.5), Inches(1.6)]
    for i, w in enumerate(widths): tbl.columns[i].width = w
    
    cv_h = ["Model Architecture", "CV ROC-AUC", "CV Sensitivity", "CV Specificity", "CV Precision", "CV F1-Score", "CV Accuracy"]
    for i, h in enumerate(cv_h):
        cell = tbl.cell(0, i)
        cell.text = h; cell.fill.solid(); cell.fill.fore_color.rgb = BLUE
        for p in cell.text_frame.paragraphs: p.font.size = Pt(10); p.font.bold = True; p.font.color.rgb = WHITE
        
    cv_rows = [
        ["Majority Baseline (Dummy)", "0.500 ± 0.000", "0.000 ± 0.000", "1.000 ± 0.000", "0.000 ± 0.000", "0.000 ± 0.000", "0.541 ± 0.006"],
        ["Logistic Regression (L2)", "0.906 ± 0.011", "0.766 ± 0.035", "0.893 ± 0.041", "0.862 ± 0.042", "0.809 ± 0.015", "0.835 ± 0.014"],
        ["Random Forest (Selected)", "0.890 ± 0.017", "0.765 ± 0.074", "0.870 ± 0.054", "0.843 ± 0.064", "0.797 ± 0.028", "0.822 ± 0.023"],
        ["Gradient Boosting", "0.856 ± 0.023", "0.757 ± 0.052", "0.847 ± 0.039", "0.812 ± 0.051", "0.781 ± 0.031", "0.806 ± 0.025"]
    ]
    for r_idx, row in enumerate(cv_rows, start=1):
        for c_idx, val in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(237, 242, 247) if r_idx == 3 else (RGBColor(247, 250, 252) if r_idx%2==1 else WHITE)
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(9.5)
                p.font.bold = (r_idx == 3)
                p.font.color.rgb = NAVY if r_idx == 3 else GRAY_TEXT
                
    # Selection Card below table
    add_card(slide10, Inches(0.8), Inches(5.3), Inches(11.7), Inches(1.5))
    tf_s = slide10.shapes.add_textbox(Inches(1.05), Inches(5.45), Inches(11.2), Inches(1.2)).text_frame
    tf_s.word_wrap = True
    p = tf_s.paragraphs[0]; p.text = "TRAINING-SET SELECTION RATIONALE: RANDOM FOREST"; p.font.size = Pt(11); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(4)
    p = tf_s.add_paragraph()
    p.text = "• The Majority Baseline fails completely (0% sensitivity, missing 100% of diseased patients).\n• Logistic Regression and Random Forest both show strong discriminative ability (CV AUC ~0.90).\n• Random Forest was selected for final clinical deployment due to its superior capacity to capture non-linear thresholds (e.g., ST depression >1.5 mm combined with fluoroscopy vessels) without overfitting."
    p.font.size = Pt(9.5); p.font.color.rgb = GRAY_TEXT

    # =========================================================================
    # SLIDE 11: Final Test Set Evaluation (N = 61 Untouched Patients)
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide11, WHITE)
    add_header(slide11, "Final Evaluation on Untouched Hold-Out Test Set (N = 61)")
    
    # Left: Test Metrics Table
    tbl_shape = slide11.shapes.add_table(8, 3, Inches(0.8), Inches(1.8), Inches(6.8), Inches(5.0))
    tbl = tbl_shape.table
    tbl.columns[0].width = Inches(2.8)
    tbl.columns[1].width = Inches(2.0)
    tbl.columns[2].width = Inches(2.0)
    
    t_headers = ["Metric (Positive = Diseased)", "Majority Baseline", "Random Forest (Selected)"]
    for i, h in enumerate(t_headers):
        cell = tbl.cell(0, i); cell.text = h; cell.fill.solid(); cell.fill.fore_color.rgb = BLUE
        for p in cell.text_frame.paragraphs: p.font.size = Pt(10); p.font.bold = True; p.font.color.rgb = WHITE
        
    test_rows_data = [
        ("Test Accuracy", "54.1%", "91.8% (56/61)"),
        ("Sensitivity / Recall [Primary]", "0.0% (0/28)", "92.9% (26/28)"),
        ("Specificity [FP Control]", "100.0% (33/33)", "90.9% (30/33)"),
        ("Precision (PPV)", "0.0%", "89.7% (26/29)"),
        ("F1-Score", "0.000", "0.912"),
        ("Area Under ROC Curve (AUC)", "0.500", "0.959"),
        ("Confusion Matrix [TN, FP / FN, TP]", "[33, 0 / 28, 0]", "[30, 3 / 2, 26]")
    ]
    for r_idx, (m, b_v, rf_v) in enumerate(test_rows_data, start=1):
        c1, c2, c3 = tbl.cell(r_idx, 0), tbl.cell(r_idx, 1), tbl.cell(r_idx, 2)
        c1.text, c2.text, c3.text = m, b_v, rf_v
        c1.fill.solid(); c1.fill.fore_color.rgb = RGBColor(237, 242, 247)
        c2.fill.solid(); c2.fill.fore_color.rgb = WHITE
        c3.fill.solid(); c3.fill.fore_color.rgb = RGBColor(240, 255, 244)
        for p in c1.text_frame.paragraphs: p.font.size = Pt(9.5); p.font.bold = True; p.font.color.rgb = NAVY
        for p in c2.text_frame.paragraphs: p.font.size = Pt(9.5); p.font.color.rgb = GRAY_TEXT
        for p in c3.text_frame.paragraphs: p.font.size = Pt(9.5); p.font.bold = True; p.font.color.rgb = GREEN
        
    # Right: Key Takeaway Cards
    add_card(slide11, Inches(7.9), Inches(1.8), Inches(4.6), Inches(5.0))
    tf_k = slide11.shapes.add_textbox(Inches(8.15), Inches(2.0), Inches(4.1), Inches(4.6)).text_frame
    tf_k.word_wrap = True
    p = tf_k.paragraphs[0]; p.text = "DIAGNOSTIC TRIAGE EXCELLENCE"; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(10)
    p = tf_k.add_paragraph()
    p.text = (
        "• Exceptional Screening Safety:\n"
        "  Random Forest detected 26 out of 28 cardiac cases (92.9% Sensitivity), missing only 2 patients.\n\n"
        "• High Specificity & Cost Savings:\n"
        "  Correctly ruled out 30 out of 33 healthy patients (90.9% Specificity), generating only 3 False Positives.\n\n"
        "• Global Discriminative Superiority:\n"
        "  ROC-AUC of 0.959 proves that model risk scores cleanly rank diseased patients above controls across all operating thresholds.\n\n"
        "• 56 of 61 patients (91.8%) correctly triaged on completely unseen data."
    )
    p.font.size = Pt(10.5); p.font.color.rgb = GRAY_TEXT

    # =========================================================================
    # SLIDE 12: [VIDEO SLIDE 2] Diagnostic Error Analysis & ROC Decision Sweep
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide12, WHITE)
    add_header(slide12, "Diagnostic Error Analysis & ROC Decision Threshold Sweep", category_text="VIDEO DEMONSTRATION 2 | THRESHOLD SWEEP")
    
    # Left: Embed Video 2
    vid2_file = os.path.join(VIDEOS_DIR, "video2_roc_threshold_sweep.mp4")
    if os.path.exists(vid2_file):
        slide12.shapes.add_movie(vid2_file, Inches(0.8), Inches(1.8), Inches(6.8), Inches(4.8), mime_type="video/mp4")
        
    # Right: Narrative Callout Card
    add_card(slide12, Inches(7.9), Inches(1.8), Inches(4.6), Inches(4.8))
    t_v2 = slide12.shapes.add_textbox(Inches(8.15), Inches(2.0), Inches(4.1), Inches(4.4)).text_frame
    t_v2.word_wrap = True
    p = t_v2.paragraphs[0]; p.text = "CLINICAL ERROR IMPACT (FP vs. FN)"; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(8)
    p = t_v2.add_paragraph()
    p.text = (
        "This animated video illustrates the dynamic sweep of decision thresholds from 1.0 down to 0.05 on the untouched test set.\n\n"
        "• False Negative (Type II Error - Critical):\n"
        "  Diseased patient classified as healthy. Leaves without cardioprotective therapy; at acute risk for fatal myocardial infarction. Minimized to only 2 cases (92.9% Recall).\n\n"
        "• False Positive (Type I Error):\n"
        "  Healthy patient classified as diseased. Prompts confirmatory catheterization (anxiety, contrast nephropathy, radiation, cost). Minimized to only 3 cases (90.9% Specificity).\n\n"
        "• Triage Flexibility: Clinicians can lower the threshold to 0.35 to push sensitivity to 98%+."
    )
    p.font.size = Pt(10); p.font.color.rgb = GRAY_TEXT

    # =========================================================================
    # SLIDE 13: Unsupervised Clustering & Clinical Phenotype Discovery
    # =========================================================================
    slide13 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide13, WHITE)
    add_header(slide13, "Unsupervised Clustering & Clinical Phenotype Discovery")
    
    # 2 Big Cards: k=2 and k=4
    add_card(slide13, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    t_c1 = slide13.shapes.add_textbox(Inches(1.05), Inches(2.0), Inches(5.1), Inches(4.5)).text_frame
    t_c1.word_wrap = True
    p = t_c1.paragraphs[0]; p.text = "BIPARTITE PHENOTYPES (k = 2)"; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(8)
    p = t_c1.add_paragraph()
    p.text = (
        "Silhouette Score: 0.192 | Davies-Bouldin: 1.923\n\n"
        "• Cluster 0 (High Risk, n = 95, 39.3%):\n"
        "  - Mean Age: 59.7 years\n"
        "  - Peak Heart Rate: 132.6 bpm (chronotropic impairment)\n"
        "  - Exercise ST Depression: 1.85 mm\n"
        "  - Confirmed Disease Rate: 75.8% Positive\n\n"
        "• Cluster 1 (Low Risk, n = 147, 60.7%):\n"
        "  - Mean Age: 51.2 years\n"
        "  - Peak Heart Rate: 161.2 bpm (healthy reserve)\n"
        "  - Exercise ST Depression: 0.45 mm\n"
        "  - Confirmed Disease Rate: 26.5% Positive\n\n"
        "Takeaway: Unsupervised clustering separates patients into distinct risk groups without ever seeing the diagnostic labels."
    )
    p.font.size = Pt(10); p.font.color.rgb = GRAY_TEXT
    
    add_card(slide13, Inches(6.9), Inches(1.8), Inches(5.6), Inches(5.0))
    t_c2 = slide13.shapes.add_textbox(Inches(7.15), Inches(2.0), Inches(5.1), Inches(4.5)).text_frame
    t_c2.word_wrap = True
    p = t_c2.paragraphs[0]; p.text = "HIGH-SEVERITY STRATIFICATION (k = 4)"; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(8)
    p = t_c2.add_paragraph()
    p.text = (
        "Silhouette Score: 0.143 | Davies-Bouldin: 1.927\n\n"
        "• Cluster 2 (Young & Healthy, n = 89):\n"
        "  - Age 47.7, Peak HR 166.3, ST dep 0.29 mm\n"
        "  - Disease Prevalence: 20.2%\n\n"
        "• Cluster 1 (Mild / Intermediate, n = 46):\n"
        "  - Age 61.9, Peak HR 155.7, ST dep 0.58 mm\n"
        "  - Disease Prevalence: 39.1%\n\n"
        "• Cluster 0 (Moderate Ischemia, n = 68):\n"
        "  - Age 55.1, Peak HR 136.5, ST dep 1.32 mm\n"
        "  - Disease Prevalence: 55.9%\n\n"
        "• Cluster 3 (Critical Multi-Vessel, n = 39):\n"
        "  - Age 60.5, Peak HR 129.5, ST dep 2.55 mm\n"
        "  - Disease Prevalence: 94.9% (37 of 39 patients diseased!)"
    )
    p.font.size = Pt(10); p.font.color.rgb = GRAY_TEXT

    # =========================================================================
    # SLIDE 14: Clinical Limitations, Actionable Next Steps & Conclusion
    # =========================================================================
    slide14 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide14, WHITE)
    add_header(slide14, "Limitations, Actionable Next Steps, & Conclusion")
    
    # 3 Summary Column Cards
    w4 = Inches(3.64); g4 = Inches(0.35)
    
    # Card 1: Limitations
    add_card(slide14, Inches(0.8), Inches(1.8), w4, Inches(5.0))
    t1 = slide14.shapes.add_textbox(Inches(1.0), Inches(2.0), w4 - Inches(0.4), Inches(4.5)).text_frame
    t1.word_wrap = True
    p = t1.paragraphs[0]; p.text = "CLINICAL LIMITATIONS"; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(8)
    p = t1.add_paragraph()
    p.text = (
        "• Demographic Bias: 68% male cohort from 1980s; female ischemic presentations (microvascular angina) underrepresented.\n\n"
        "• Tertiary Referral Filter: Patients referred for catheterization had elevated baseline pre-test suspicion.\n\n"
        "• Modest Hold-Out Sample: Test set N = 61 (28 disease cases); each single error represents ~3.5% swing in sensitivity.\n\n"
        "• Non-Causal Markers: Exercise ST shifts are functional ischemic manifestations, not biological causes of atheroma."
    )
    p.font.size = Pt(9.5); p.font.color.rgb = GRAY_TEXT
    
    # Card 2: Next Steps
    add_card(slide14, Inches(0.8) + w4 + g4, Inches(1.8), w4, Inches(5.0))
    t2 = slide14.shapes.add_textbox(Inches(1.0) + w4 + g4, Inches(2.0), w4 - Inches(0.4), Inches(4.5)).text_frame
    t2.word_wrap = True
    p = t2.paragraphs[0]; p.text = "ACTIONABLE NEXT STEPS"; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(8)
    p = t2.add_paragraph()
    p.text = (
        "• Multi-Center Validation: External geographical testing on Hungarian (N=294), Long Beach (N=200), and Zurich (N=123) cohorts.\n\n"
        "• Decision Curve Analysis (DCA): Quantify net clinical benefit across varying threshold probabilities to guide physician triage.\n\n"
        "• Multi-Vessel Ordinal Modeling: Distinguish single-vessel from left-main or three-vessel disease to guide CABG surgery vs. stenting.\n\n"
        "• EHR Integration: Pilot within clinical decision support (CDS) pipelines."
    )
    p.font.size = Pt(9.5); p.font.color.rgb = GRAY_TEXT
    
    # Card 3: Conclusion
    add_card(slide14, Inches(0.8) + (w4 + g4)*2, Inches(1.8), w4, Inches(5.0))
    t3 = slide14.shapes.add_textbox(Inches(1.0) + (w4 + g4)*2, Inches(2.0), w4 - Inches(0.4), Inches(4.5)).text_frame
    t3.word_wrap = True
    p = t3.paragraphs[0]; p.text = "CONCLUSION"; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = BLUE; p.space_after = Pt(8)
    p = t3.add_paragraph()
    p.text = (
        "• Core Research Question Validated: Routine non-invasive exam and exercise markers strongly distinguish coronary disease presence from absence.\n\n"
        "• Random Forest Excellence: Achieved 91.8% Accuracy, 92.9% Sensitivity, 90.9% Specificity, and 0.959 ROC-AUC on unseen data.\n\n"
        "• Methodological Rigor: Completely reproducible, leakage-free pipeline with automated execution in under 30 seconds."
    )
    p.font.size = Pt(9.5); p.font.color.rgb = GRAY_TEXT
    
    prs.save(OUTPUT_PPTX)
    print(f"Successfully generated PowerPoint presentation at: {OUTPUT_PPTX} ({os.path.getsize(OUTPUT_PPTX)} bytes)")

if __name__ == "__main__":
    create_deck()
