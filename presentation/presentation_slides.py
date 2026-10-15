# ==============================================================================
# TON_IoT Network Intrusion Detection: Manim Presentation Slides
# Information Security Lab (Lab #7) - Khulna University (CSEKU)
# Instructor: Dr. Anupam Kumar Bairagi, Professor, CSE Discipline
# Presenters: Md Siam Ahmed (230202), Kazi Rifat Morshed (230220)
# ==============================================================================

from datetime import datetime
from manim import *
from manim_slides import Slide

# Compile-time dynamic Month Year (e.g., "October 2026")
CURRENT_MONTH_YEAR = datetime.now().strftime("%B %Y")

# ==============================================================================
# NVIDIA Brand Color Theme (Light Academic Defense)
# ==============================================================================
NVIDIA_GREEN        = "#76B900"  # Signature NVIDIA Green
NVIDIA_DARK_GREEN   = "#265200"  # High-contrast accessible green (WCAG AAA)
NVIDIA_ACCENT_GREEN = "#3B7500"  # Structural border accent green
TEXT_MAIN           = "#1A1A1A"  # Deep charcoal for academic typography & LaTeX
TEXT_MUTED          = "#525B64"  # Slate gray for captions, subtitles, and notes
CARD_BG             = "#F8FAFC"  # Base canvas and container surface
CARD_BORDER         = "#E2E8F0"  # Subtle hairline boundary stroke
WHITE_COLOR         = "#FFFFFF"  # Pure white card surface
BLOCK_INACTIVE_FILL = "#F1F5F9"  # Hardware slate neutral tile fill
BLOCK_INACTIVE_STROKE = "#94A3B8"# Hardware neutral stroke border

# Configure base light canvas defaults
config.background_color = ManimColor(CARD_BG)
Tex.set_default(color=TEXT_MAIN)
MathTex.set_default(color=TEXT_MAIN)


class TonIoTPresentation(Slide):
    def construct(self):
        # Enforce exact canvas background color for Manim-Slides
        self.camera.background_color = ManimColor(CARD_BG)

        # ----------------------------------------------------------------------
        # Global Footer Builder (Persistent across all slides)
        # ----------------------------------------------------------------------
        def build_footer(slide_num, total_slides):
            footer_bar = Rectangle(
                width=config.frame_width + 1.0,
                height=0.42,
                fill_color=NVIDIA_GREEN,
                fill_opacity=1.0,
                stroke_width=0
            ).to_edge(DOWN, buff=-0.01)

            page_info = Tex(
                rf"\textbf{{Slide {slide_num}/{total_slides}}} \hspace{{0.2cm}} \textbar \hspace{{0.2cm}} "
                r"\textsf{TON\_IoT Network Intrusion Detection (100\% GPU)}",
                font_size=15,
                color=CARD_BG
            ).to_edge(LEFT, buff=0.4).match_y(footer_bar)

            presenter_info = Tex(
                r"\textsf{Md Siam Ahmed (230202), Kazi Rifat Morshed (230220) \hspace{0.2cm} \textbar \hspace{0.2cm} "
                + CURRENT_MONTH_YEAR
                + r"}",
                font_size=14,
                color=CARD_BG
            ).to_edge(RIGHT, buff=0.4).match_y(footer_bar)

            return VGroup(footer_bar, page_info, presenter_info)

        # ----------------------------------------------------------------------
        # Persistent Content Header Builder
        # ----------------------------------------------------------------------
        def build_header(category_tex_str, section_tex_str):
            header_bar = Rectangle(
                width=config.frame_width + 1.0,
                height=0.72,
                fill_color=WHITE_COLOR,
                fill_opacity=1.0,
                stroke_color=CARD_BORDER,
                stroke_width=1.0
            ).to_edge(UP, buff=-0.01)

            header_stripe = Line(
                LEFT * (config.frame_width / 2 + 0.5),
                RIGHT * (config.frame_width / 2 + 0.5),
                color=NVIDIA_GREEN,
                stroke_width=2.5
            ).next_to(header_bar, DOWN, buff=0)

            header_tracker = Tex(
                rf"\textbf{{\textsf{{{category_tex_str}}}}} \hspace{{0.15cm}}\textbar\hspace{{0.15cm}} \textsf{{\footnotesize {section_tex_str}}}",
                font_size=15,
                color=NVIDIA_DARK_GREEN
            ).to_edge(LEFT, buff=0.4).match_y(header_bar)

            header_logo = ImageMobject("kucse_full_logo.png").set(height=0.42).to_edge(RIGHT, buff=0.4).match_y(header_bar)
            return Group(header_bar, header_stripe, header_tracker, header_logo), header_stripe

        TOTAL_SLIDES = 8

        # ======================================================================
        # SLIDE 1: Cover / Defense Title Slide
        # ======================================================================
        discipline_info = Tex(
            r"\textbf{Computer Science and Engineering Discipline}\\[0.06cm]\textbf{Khulna University}",
            font_size=22,
            color=NVIDIA_DARK_GREEN
        )
        univ_logo = ImageMobject("ku_emblem_clean.png").set(height=0.82)
        title_slide_header = Group(discipline_info, univ_logo).arrange(RIGHT, buff=0.35)
        title_slide_header.to_edge(UP, buff=0.45)

        # Main Title Group
        main_title = Tex(r"\textbf{TON\_IoT Network Intrusion Detection}", font_size=38, color=TEXT_MAIN)
        title_accent = Line(LEFT * 2.3, RIGHT * 2.3, color=NVIDIA_GREEN, stroke_width=3.5)
        main_subtitle = Tex(
            r"\textit{Classifying DoS, DDoS, and Normal Traffic with 100\% NVIDIA GPU Acceleration}",
            font_size=21,
            color=TEXT_MUTED
        )
        title_block = VGroup(main_title, title_accent, main_subtitle).arrange(DOWN, buff=0.18)
        title_block.next_to(title_slide_header, DOWN, buff=0.42)

        # Presenters (Two Students)
        s1 = VGroup(
            Tex(r"\textbf{Md Siam Ahmed}", font_size=22, color=TEXT_MAIN),
            Tex(r"Student ID: 230202", font_size=18, color=TEXT_MUTED)
        ).arrange(DOWN, buff=0.06)

        s2 = VGroup(
            Tex(r"\textbf{Kazi Rifat Morshed}", font_size=22, color=TEXT_MAIN),
            Tex(r"Student ID: 230220", font_size=18, color=TEXT_MUTED)
        ).arrange(DOWN, buff=0.06)

        students_row = VGroup(s1, s2).arrange(RIGHT, buff=1.6)
        presented_by = Tex(r"\textbf{\textsf{\footnotesize PRESENTED BY}}", font_size=15, color=NVIDIA_DARK_GREEN)
        students_group = VGroup(presented_by, students_row).arrange(DOWN, buff=0.12)

        # Supervisor / Course Teacher Information
        supervisor_header = Tex(r"\textbf{\textsf{\footnotesize COURSE INSTRUCTOR \& SUPERVISOR}}", font_size=15, color=NVIDIA_DARK_GREEN)
        sup_name = Tex(r"\textbf{Dr. Anupam Kumar Bairagi}", font_size=22, color=TEXT_MAIN)
        sup_desig = Tex(r"Professor, Computer Science and Engineering Discipline", font_size=18, color=TEXT_MUTED)
        sup_dept = Tex(r"Khulna University, Khulna-9208, Bangladesh", font_size=18, color=TEXT_MUTED)
        supervisor_group = VGroup(supervisor_header, sup_name, sup_desig, sup_dept).arrange(DOWN, buff=0.06)

        lab_badge = Tex(r"\textbf{Information Security Lab (Lab \#7)}", font_size=18, color=NVIDIA_ACCENT_GREEN)

        defense_info = VGroup(students_group, supervisor_group, lab_badge).arrange(DOWN, buff=0.25)
        defense_info.next_to(title_block, DOWN, buff=0.35)

        current_footer = build_footer(1, TOTAL_SLIDES)

        self.play(FadeIn(title_slide_header), FadeIn(current_footer))
        self.play(Write(main_title), Create(title_accent))
        self.play(FadeIn(main_subtitle))
        self.play(FadeIn(defense_info))
        self.wait(0.2)
        self.next_slide()  # Advance to Slide 2

        # ======================================================================
        # SLIDE 2: Problem Formulation & Threat Model
        # ======================================================================
        slide1_content = Group(title_slide_header, title_block, defense_info)
        content_header, stripe = build_header(r"PROBLEM FORMULATION", r"INFORMATION SECURITY LAB")

        slide2_title = Tex(r"\textbf{IoT Threat Landscape: DoS vs DDoS vs Normal Traffic}", font_size=32, color=TEXT_MAIN)
        slide2_title.next_to(stripe, DOWN, buff=0.28)
        slide2_accent = Line(LEFT * 1.8, RIGHT * 1.8, color=NVIDIA_GREEN, stroke_width=2.5).next_to(slide2_title, DOWN, buff=0.12)

        def make_threat_card(title_str, badge_color, desc_lines, card_width=3.9, card_height=3.4):
            bg = RoundedRectangle(corner_radius=0.10, width=card_width, height=card_height, fill_color=WHITE_COLOR, fill_opacity=1.0, stroke_color=CARD_BORDER, stroke_width=1.5)
            top_bar = RoundedRectangle(corner_radius=0.06, width=card_width, height=0.42, fill_color=badge_color, fill_opacity=1.0, stroke_width=0).align_to(bg, UP)
            badge_text = Tex(rf"\textbf{{{title_str}}}", font_size=18, color=WHITE_COLOR).move_to(top_bar.get_center())
            body_tex = Tex(desc_lines, font_size=15, color=TEXT_MAIN).next_to(top_bar, DOWN, buff=0.2).set(width=card_width - 0.4)
            return VGroup(bg, top_bar, badge_text, body_tex)

        card1 = make_threat_card(
            "Normal Traffic",
            "#2E7D32",
            r"\textbf{Benign IoT Telemetry:}\\[0.1cm]"
            r"$\bullet$ Legitimate sensor chatter (MQTT, Modbus, Node-RED)\\[0.1cm]"
            r"$\bullet$ Periodic local DNS queries\\[0.1cm]"
            r"$\bullet$ Normal completed TCP handshakes (\texttt{SF} state)\\[0.1cm]"
            r"$\bullet$ Balanced packet ratios"
        )
        card2 = make_threat_card(
            "DoS (Denial of Service)",
            "#E65100",
            r"\textbf{Single-Source Flood:}\\[0.1cm]"
            r"$\bullet$ Originates from single attacker IP address\\[0.1cm]"
            r"$\bullet$ Targeted TCP SYN / UDP floods\\[0.1cm]"
            r"$\bullet$ Unanswered connection attempts (\texttt{S0} state)\\[0.1cm]"
            r"$\bullet$ High packet volume to victim port"
        )
        card3 = make_threat_card(
            "DDoS (Distributed DoS)",
            "#C62828",
            r"\textbf{Multi-Botnet Volumetric:}\\[0.1cm]"
            r"$\bullet$ Coordinated flood across multiple distributed IPs\\[0.1cm]"
            r"$\bullet$ Massive asynchronous traffic spikes\\[0.1cm]"
            r"$\bullet$ Ephemeral port cycling\\[0.1cm]"
            r"$\bullet$ Exhausts edge gateway bandwidth"
        )
        cards_row = VGroup(card1, card2, card3).arrange(RIGHT, buff=0.35).next_to(slide2_accent, DOWN, buff=0.3)

        next_footer = build_footer(2, TOTAL_SLIDES)
        self.play(
            FadeOut(slide1_content),
            Transform(current_footer, next_footer),
            FadeIn(content_header),
            Write(slide2_title),
            Create(slide2_accent),
            FadeIn(cards_row)
        )
        self.wait(0.2)
        self.next_slide()  # Advance to Slide 3

        # ======================================================================
        # SLIDE 3: TON_IoT Dataset Profile & Preprocessing
        # ======================================================================
        slide2_content = Group(slide2_title, slide2_accent, cards_row)
        content_header, stripe = build_header(r"DATASET \& PIPELINE", r"UNSW CANBERRA TESTBED")

        slide3_title = Tex(r"\textbf{Dataset Profile \& Zero-Leakage Preprocessing}", font_size=32, color=TEXT_MAIN)
        slide3_title.next_to(stripe, DOWN, buff=0.28)
        slide3_accent = Line(LEFT * 1.8, RIGHT * 1.8, color=NVIDIA_GREEN, stroke_width=2.5).next_to(slide3_title, DOWN, buff=0.12)

        # Left Card: Dataset Stats
        ds_card_bg = RoundedRectangle(corner_radius=0.10, width=5.8, height=3.5, fill_color=WHITE_COLOR, fill_opacity=1.0, stroke_color=CARD_BORDER, stroke_width=1.5)
        ds_bar = RoundedRectangle(corner_radius=0.06, width=5.8, height=0.4, fill_color=NVIDIA_DARK_GREEN, fill_opacity=1.0, stroke_width=0).align_to(ds_card_bg, UP)
        ds_badge = Tex(r"\textbf{TON\_IoT Network Dataset Profile}", font_size=18, color=WHITE_COLOR).move_to(ds_bar.get_center())
        ds_body = Tex(
            r"\textbf{Total Records}: 300,000 Zeek Network Flows\\[0.12cm]"
            r"\textbf{Feature Count}: 46 Raw Network Telemetry Attributes\\[0.12cm]"
            r"\textbf{Class Balance} (Perfect 1:1:1 Distribution):\\[0.08cm]"
            r"$\bullet$ \texttt{normal} : 100,000 flows (33.33\%)\\[0.06cm]"
            r"$\bullet$ \texttt{dos}    : 100,000 flows (33.33\%)\\[0.06cm]"
            r"$\bullet$ \texttt{ddos}   : 100,000 flows (33.33\%)\\[0.12cm]"
            r"\textbf{Testbed}: Heterogeneous Edge-Fog-Cloud (UNSW)",
            font_size=16,
            color=TEXT_MAIN
        ).next_to(ds_bar, DOWN, buff=0.2).set(width=5.4)
        ds_card = VGroup(ds_card_bg, ds_bar, ds_badge, ds_body)

        # Right Card: Preprocessing Pipeline & Defense Focus
        prep_card_bg = RoundedRectangle(corner_radius=0.10, width=6.2, height=3.5, fill_color=WHITE_COLOR, fill_opacity=1.0, stroke_color=CARD_BORDER, stroke_width=1.5)
        prep_bar = RoundedRectangle(corner_radius=0.06, width=6.2, height=0.4, fill_color=NVIDIA_GREEN, fill_opacity=1.0, stroke_width=0).align_to(prep_card_bg, UP)
        prep_badge = Tex(r"\textbf{Leakage-Free Preprocessing Pipeline}", font_size=18, color=WHITE_COLOR).move_to(prep_bar.get_center())
        prep_body = Tex(
            r"\textbf{1. De-duplication}: Removed redundant capture rows.\\[0.12cm]"
            r"\textbf{2. Target Leakage Elimination}:\\ "
            r"\textit{Explicitly dropped raw} \texttt{label} \textit{column to prevent}\\"
            r"\textit{trivial 100\% artificial accuracy when predicting} \texttt{type}.\\[0.12cm]"
            r"\textbf{3. IP Numerical Decomposition}:\\ "
            r"Converted text IPs into 64-bit high/low numeric integers\\ "
            r"(\texttt{src\_ip\_high}, \texttt{src\_ip\_low}, \texttt{dst\_ip\_high}, \texttt{dst\_ip\_low}).\\[0.12cm]"
            r"\textbf{4. Encoding}: Categorical LabelEncoding + constant removal.",
            font_size=15,
            color=TEXT_MAIN
        ).next_to(prep_bar, DOWN, buff=0.2).set(width=5.8)
        prep_card = VGroup(prep_card_bg, prep_bar, prep_badge, prep_body)

        slide3_row = VGroup(ds_card, prep_card).arrange(RIGHT, buff=0.4).next_to(slide3_accent, DOWN, buff=0.3)

        next_footer = build_footer(3, TOTAL_SLIDES)
        self.play(
            FadeOut(slide2_content),
            Transform(current_footer, next_footer),
            Write(slide3_title),
            Create(slide3_accent),
            FadeIn(slide3_row)
        )
        self.wait(0.2)
        self.next_slide()  # Advance to Slide 4

        # ======================================================================
        # SLIDE 4: NVIDIA GPU Acceleration Architecture
        # ======================================================================
        slide3_content = Group(slide3_title, slide3_accent, slide3_row)
        content_header, stripe = build_header(r"HARDWARE ACCELERATION", r"NVIDIA GPU PIPELINE")

        slide4_title = Tex(r"\textbf{GPU Architecture: Accelerated Model Training}", font_size=32, color=TEXT_MAIN)
        slide4_title.next_to(stripe, DOWN, buff=0.28)
        slide4_accent = Line(LEFT * 1.8, RIGHT * 1.8, color=NVIDIA_GREEN, stroke_width=2.5).next_to(slide4_title, DOWN, buff=0.12)

        # Hardware Badge Banner
        hw_bg = RoundedRectangle(corner_radius=0.08, width=12.2, height=0.7, fill_color=WHITE_COLOR, fill_opacity=1.0, stroke_color=CARD_BORDER, stroke_width=1.2)
        hw_text = Tex(
            r"\textbf{Dual-Lab Hardware Setup}: \hspace{0.2cm} "
            r"\textbf{Host 1}: NVIDIA RTX 3060 12GB (Ampere SM 8.6, TF32) \hspace{0.4cm}\textbar\hspace{0.4cm} "
            r"\textbf{Host 2}: NVIDIA RTX 5070 Ti 16GB (Blackwell SM 12.0)",
            font_size=16,
            color=NVIDIA_DARK_GREEN
        ).move_to(hw_bg.get_center())
        hw_banner = VGroup(hw_bg, hw_text).next_to(slide4_accent, DOWN, buff=0.22)

        def make_gpu_engine_card(title_str, tech_str, details_str):
            bg = RoundedRectangle(corner_radius=0.10, width=3.8, height=2.6, fill_color=WHITE_COLOR, fill_opacity=1.0, stroke_color=CARD_BORDER, stroke_width=1.5)
            side_stripe = RoundedRectangle(corner_radius=0.05, width=0.08, height=2.6, fill_color=NVIDIA_GREEN, fill_opacity=1.0, stroke_width=0).align_to(bg, LEFT)
            t_tex = Tex(rf"\textbf{{{title_str}}}", font_size=18, color=TEXT_MAIN)
            tech_tex = Tex(rf"\textbf{{\textsf{{{tech_str}}}}}", font_size=14, color=NVIDIA_DARK_GREEN)
            d_tex = Tex(details_str, font_size=14, color=TEXT_MUTED).set(width=3.4)
            content = VGroup(t_tex, tech_tex, d_tex).arrange(DOWN, aligned_edge=LEFT, buff=0.14).move_to(bg.get_center()).shift(RIGHT * 0.1)
            return VGroup(bg, side_stripe, content)

        m1 = make_gpu_engine_card(
            "GPU Random Forest",
            "CUDA HISTOGRAM TREES",
            r"$\bullet$ 200 Parallel de-correlated trees\\[0.06cm]"
            r"$\bullet$ Exact parallel split finding\\[0.06cm]"
            r"$\bullet$ Built directly in GPU VRAM\\[0.06cm]"
            r"$\bullet$ Zero CPU threading overhead"
        )
        m2 = make_gpu_engine_card(
            "GPU XGBoost",
            "NVIDIA CUDA ACCELERATED",
            r"$\bullet$ Gradient boosted decision trees\\[0.06cm]"
            r"$\bullet$ \texttt{tree\_method='hist'}, \texttt{device='cuda'}\\[0.06cm]"
            r"$\bullet$ Second-order gradient optimization\\[0.06cm]"
            r"$\bullet$ Sub-second convergence"
        )
        m3 = make_gpu_engine_card(
            "PyTorch Deep MLP",
            "TENSOR CORES (TF32)",
            r"$\bullet$ Deep Neural Network (256-128-64)\\[0.06cm]"
            r"$\bullet$ Batch Normalization + Dropout\\[0.06cm]"
            r"$\bullet$ TensorFloat-32 acceleration\\[0.06cm]"
            r"$\bullet$ AdamW optimizer with cross-entropy"
        )
        gpu_engines_row = VGroup(m1, m2, m3).arrange(RIGHT, buff=0.35).next_to(hw_banner, DOWN, buff=0.25)

        next_footer = build_footer(4, TOTAL_SLIDES)
        self.play(
            FadeOut(slide3_content),
            Transform(current_footer, next_footer),
            Write(slide4_title),
            Create(slide4_accent),
            FadeIn(hw_banner),
            FadeIn(gpu_engines_row)
        )
        self.wait(0.2)
        self.next_slide()  # Advance to Slide 5

        # ======================================================================
        # SLIDE 5: Experimental Performance & Results Matrix
        # ======================================================================
        slide4_content = Group(slide4_title, slide4_accent, hw_banner, gpu_engines_row)
        content_header, stripe = build_header(r"EXPERIMENTAL RESULTS", r"GPU PERFORMANCE BENCHMARK")

        slide5_title = Tex(r"\textbf{Experimental Results: Model Accuracy \& Latency Matrix}", font_size=32, color=TEXT_MAIN)
        slide5_title.next_to(stripe, DOWN, buff=0.28)
        slide5_accent = Line(LEFT * 1.8, RIGHT * 1.8, color=NVIDIA_GREEN, stroke_width=2.5).next_to(slide5_title, DOWN, buff=0.12)

        # Performance Table Card
        table_card_bg = RoundedRectangle(corner_radius=0.10, width=12.2, height=2.4, fill_color=WHITE_COLOR, fill_opacity=1.0, stroke_color=CARD_BORDER, stroke_width=1.5)
        table_stripe = RoundedRectangle(corner_radius=0.06, width=0.08, height=2.4, fill_color=NVIDIA_GREEN, fill_opacity=1.0, stroke_width=0).align_to(table_card_bg, LEFT)

        table_tex = Tex(
            r"\renewcommand{\arraystretch}{1.2}"
            r"\begin{tabular}{lcccccccc}"
            r"\hline"
            r"\textbf{Model} & \textbf{Hardware} & \textbf{Train Time} & \textbf{Latency} & \textbf{Accuracy} & \textbf{Macro F1} & \textbf{MCC} & \textbf{ROC-AUC} \\"
            r"\hline"
            r"\textbf{GPU Random Forest} & NVIDIA CUDA & \textbf{0.99 s} & 2.27 $\mu$s & \textbf{99.99\%} & \textbf{99.99\%} & \textbf{0.9998} & \textbf{1.0000} \\"
            r"\textbf{GPU XGBoost}       & NVIDIA CUDA & \textbf{0.36 s} & 1.85 $\mu$s & \textbf{99.99\%} & \textbf{99.99\%} & \textbf{0.9998} & \textbf{1.0000} \\"
            r"\textbf{PyTorch Deep MLP}  & NVIDIA CUDA & 2.41 s          & \textbf{0.94 $\mu$s} & 99.84\% & 99.83\% & 0.9976 & 0.9999 \\"
            r"\hline"
            r"\end{tabular}",
            font_size=18,
            color=TEXT_MAIN
        ).move_to(table_card_bg.get_center()).shift(RIGHT * 0.1)
        perf_table = VGroup(table_card_bg, table_stripe, table_tex).next_to(slide5_accent, DOWN, buff=0.25)

        def make_stat_box(metric_str, caption_str, box_color=NVIDIA_DARK_GREEN):
            bg = RoundedRectangle(corner_radius=0.08, width=3.8, height=1.1, fill_color=WHITE_COLOR, fill_opacity=1.0, stroke_color=CARD_BORDER, stroke_width=1.2)
            m = Tex(rf"\textbf{{{metric_str}}}", font_size=23, color=box_color)
            c = Tex(caption_str, font_size=15, color=TEXT_MUTED)
            v = VGroup(m, c).arrange(DOWN, buff=0.05).move_to(bg.get_center())
            return VGroup(bg, v)

        sb1 = make_stat_box("< 1.0 Second", "GPU Tree Training Time", NVIDIA_DARK_GREEN)
        sb2 = make_stat_box("0.94 - 2.27 us", "Ultra-Low Inference Latency", NVIDIA_DARK_GREEN)
        sb3 = make_stat_box("> 400,000 pkt/s", "Real-Time Line-Rate Throughput", NVIDIA_DARK_GREEN)
        stats_row = VGroup(sb1, sb2, sb3).arrange(RIGHT, buff=0.35).next_to(perf_table, DOWN, buff=0.25)

        next_footer = build_footer(5, TOTAL_SLIDES)
        self.play(
            FadeOut(slide4_content),
            Transform(current_footer, next_footer),
            Write(slide5_title),
            Create(slide5_accent),
            FadeIn(perf_table),
            FadeIn(stats_row)
        )
        self.wait(0.2)
        self.next_slide()  # Advance to Slide 6

        # ======================================================================
        # SLIDE 6: Confusion Matrix & ROC-AUC Analysis
        # ======================================================================
        slide5_content = Group(slide5_title, slide5_accent, perf_table, stats_row)
        content_header, stripe = build_header(r"CLASSIFICATION METRICS", r"ZERO-ERROR DISCRIMINATION")

        slide6_title = Tex(r"\textbf{Classification Accuracy: Confusion Matrix \& ROC Curves}", font_size=32, color=TEXT_MAIN)
        slide6_title.next_to(stripe, DOWN, buff=0.28)
        slide6_accent = Line(LEFT * 1.8, RIGHT * 1.8, color=NVIDIA_GREEN, stroke_width=2.5).next_to(slide6_title, DOWN, buff=0.12)

        # Left Card: Confusion Matrix Visual Breakdown
        cm_card_bg = RoundedRectangle(corner_radius=0.10, width=5.8, height=3.5, fill_color=WHITE_COLOR, fill_opacity=1.0, stroke_color=CARD_BORDER, stroke_width=1.5)
        cm_bar = RoundedRectangle(corner_radius=0.06, width=5.8, height=0.4, fill_color=NVIDIA_DARK_GREEN, fill_opacity=1.0, stroke_width=0).align_to(cm_card_bg, UP)
        cm_badge = Tex(r"\textbf{Per-Class Confusion Matrix (Test Set)}", font_size=18, color=WHITE_COLOR).move_to(cm_bar.get_center())
        cm_table = Tex(
            r"\renewcommand{\arraystretch}{1.2}"
            r"\begin{tabular}{l|ccc|c}"
            r"& \textbf{Pred Normal} & \textbf{Pred DoS} & \textbf{Pred DDoS} & \textbf{Recall} \\"
            r"\hline"
            r"\textbf{Normal} & \textbf{3,308} & 0 & 0 & 100.0\% \\"
            r"\textbf{DoS}    & 0 & \textbf{2,703} & 1 & 99.96\% \\"
            r"\textbf{DDoS}   & 0 & 0 & \textbf{3,327} & 100.0\% \\"
            r"\hline"
            r"\textbf{Precision} & 100.0\% & 100.0\% & 99.97\% & \textbf{99.99\%} \\"
            r"\end{tabular}",
            font_size=16,
            color=TEXT_MAIN
        ).next_to(cm_bar, DOWN, buff=0.25).set(width=5.3)
        cm_card = VGroup(cm_card_bg, cm_bar, cm_badge, cm_table)

        # Right Card: Multi-Class ROC Curves Insight
        roc_card_bg = RoundedRectangle(corner_radius=0.10, width=6.2, height=3.5, fill_color=WHITE_COLOR, fill_opacity=1.0, stroke_color=CARD_BORDER, stroke_width=1.5)
        roc_bar = RoundedRectangle(corner_radius=0.06, width=6.2, height=0.4, fill_color=NVIDIA_GREEN, fill_opacity=1.0, stroke_width=0).align_to(roc_card_bg, UP)
        roc_badge = Tex(r"\textbf{Multi-Class ROC-AUC (One-vs-Rest)}", font_size=18, color=WHITE_COLOR).move_to(roc_bar.get_center())
        roc_body = Tex(
            r"\textbf{Area Under Curve (AUC) by Class}:\\[0.1cm]"
            r"$\bullet$ \textbf{Normal Class} (AUC = \textbf{1.000}): Ideal benign discrimination\\[0.08cm]"
            r"$\bullet$ \textbf{DoS Class} (AUC = \textbf{1.000}): Complete single-source separation\\[0.08cm]"
            r"$\bullet$ \textbf{DDoS Class} (AUC = \textbf{1.000}): Complete botnet flood separation\\[0.14cm]"
            r"\textbf{Cybersecurity Implication}:\\[0.08cm]"
            r"Zero False Positives: Benign IoT sensor telemetry is \textit{never}\\"
            r"flagged as an intrusion, preventing false alarms and alert fatigue.",
            font_size=15,
            color=TEXT_MAIN
        ).next_to(roc_bar, DOWN, buff=0.2).set(width=5.8)
        roc_card = VGroup(roc_card_bg, roc_bar, roc_badge, roc_body)

        slide6_row = VGroup(cm_card, roc_card).arrange(RIGHT, buff=0.4).next_to(slide6_accent, DOWN, buff=0.3)

        next_footer = build_footer(6, TOTAL_SLIDES)
        self.play(
            FadeOut(slide5_content),
            Transform(current_footer, next_footer),
            Write(slide6_title),
            Create(slide6_accent),
            FadeIn(slide6_row)
        )
        self.wait(0.2)
        self.next_slide()  # Advance to Slide 7

        # ======================================================================
        # SLIDE 7: Feature Importance & Attack Signatures
        # ======================================================================
        slide6_content = Group(slide6_title, slide6_accent, slide6_row)
        content_header, stripe = build_header(r"FEATURE IMPORTANCE", r"CYBERSECURITY ATTACK SIGNATURES")

        slide7_title = Tex(r"\textbf{Feature Importance: What Gives Away DoS \& DDoS Attacks?}", font_size=32, color=TEXT_MAIN)
        slide7_title.next_to(stripe, DOWN, buff=0.28)
        slide7_accent = Line(LEFT * 1.8, RIGHT * 1.8, color=NVIDIA_GREEN, stroke_width=2.5).next_to(slide7_title, DOWN, buff=0.12)

        def make_feature_bar(rank_str, name_str, imp_val, imp_pct, desc_str):
            bg = RoundedRectangle(corner_radius=0.08, width=12.2, height=0.62, fill_color=WHITE_COLOR, fill_opacity=1.0, stroke_color=CARD_BORDER, stroke_width=1.0)
            tag = Tex(rf"\textbf{{{rank_str}}}", font_size=16, color=NVIDIA_DARK_GREEN).align_to(bg, LEFT).shift(RIGHT * 0.25)
            fname = Tex(rf"\texttt{{{name_str}}}", font_size=16, color=TEXT_MAIN).next_to(tag, RIGHT, buff=0.25)
            bar_fill = Rectangle(width=3.2 * imp_val, height=0.22, fill_color=NVIDIA_GREEN, fill_opacity=1.0, stroke_width=0).next_to(fname, RIGHT, buff=0.3)
            pct_tex = Tex(rf"\textbf{{{imp_pct}}}", font_size=15, color=NVIDIA_ACCENT_GREEN).next_to(bar_fill, RIGHT, buff=0.15)
            meaning = Tex(desc_str, font_size=14, color=TEXT_MUTED).align_to(bg, RIGHT).shift(LEFT * 0.25)
            return VGroup(bg, tag, fname, bar_fill, pct_tex, meaning)

        f1 = make_feature_bar(r"\#1", "ts (Timestamp)", 0.241, r"24.1\%", r"Periodic burst timing \& packet arrival intervals")
        f2 = make_feature_bar(r"\#2", r"src\_port", 0.124, r"12.4\%", "Ephemeral port cycling vs fixed IoT telemetry ports")
        f3 = make_feature_bar(r"\#3", r"dst\_ip\_bytes", 0.111, r"11.1\%", "Asymmetric flood volume directed at victim server")
        f4 = make_feature_bar(r"\#4", r"conn\_state", 0.097, r"9.7\%", "Unfinished SYN handshakes (S0/OTH) in flood attacks")
        f5 = make_feature_bar(r"\#5", r"dst\_port", 0.091, r"9.1\%", "Victim targeted services (HTTP 80, MQTT 1883)")

        feature_bars = VGroup(f1, f2, f3, f4, f5).arrange(DOWN, buff=0.16).next_to(slide7_accent, DOWN, buff=0.3)

        next_footer = build_footer(7, TOTAL_SLIDES)
        self.play(
            FadeOut(slide6_content),
            Transform(current_footer, next_footer),
            Write(slide7_title),
            Create(slide7_accent),
            FadeIn(feature_bars)
        )
        self.wait(0.2)
        self.next_slide()  # Advance to Slide 8

        # ======================================================================
        # SLIDE 8: Conclusion & Defense Q&A
        # ======================================================================
        slide7_content = Group(slide7_title, slide7_accent, feature_bars)
        content_header, stripe = build_header(r"CONCLUSION \& DEFENSE", r"LAB \#7 WRAP-UP")

        slide8_title = Tex(r"\textbf{Conclusion: 100\% GPU-Accelerated IoT Defense}", font_size=32, color=TEXT_MAIN)
        slide8_title.next_to(stripe, DOWN, buff=0.28)
        slide8_accent = Line(LEFT * 1.8, RIGHT * 1.8, color=NVIDIA_GREEN, stroke_width=2.5).next_to(slide8_title, DOWN, buff=0.12)

        c1 = make_threat_card(
            r"1. 100\% GPU Acceleration",
            NVIDIA_DARK_GREEN,
            r"$\bullet$ Zero CPU model training bottleneck\\[0.08cm]"
            r"$\bullet$ GPU Random Forest + XGBoost + Deep MLP\\[0.08cm]"
            r"$\bullet$ Sub-second training across 300K records\\[0.08cm]"
            r"$\bullet$ Tested on RTX 3060 \& RTX 5070 Ti",
            card_width=3.9,
            card_height=2.8
        )
        c2 = make_threat_card(
            r"2. Leakage-Free Design",
            "#1565C0",
            r"$\bullet$ Explicitly eliminated \texttt{label} leakage\\[0.08cm]"
            r"$\bullet$ Mathematical 64-bit IP decomposition\\[0.08cm]"
            r"$\bullet$ Robust stratified 80/20 train-test split\\[0.08cm]"
            r"$\bullet$ Defensible academic methodology",
            card_width=3.9,
            card_height=2.8
        )
        c3 = make_threat_card(
            r"3. Ultra-High Reliability",
            "#2E7D32",
            r"$\bullet$ 99.99\% accuracy with 0.9998 MCC\\[0.08cm]"
            r"$\bullet$ Zero false positives on benign IoT data\\[0.08cm]"
            r"$\bullet$ Microsecond inference ($< 2.5\ \mu$s)\\[0.08cm]"
            r"$\bullet$ Capable of 400K+ pkt/s line rate",
            card_width=3.9,
            card_height=2.8
        )
        concl_row = VGroup(c1, c2, c3).arrange(RIGHT, buff=0.35).next_to(slide8_accent, DOWN, buff=0.25)

        thanks_bg = RoundedRectangle(corner_radius=0.08, width=12.2, height=0.68, fill_color=NVIDIA_GREEN, fill_opacity=1.0, stroke_width=0)
        thanks_text = Tex(
            r"\textbf{Thank you! We welcome any questions.}",
            font_size=18,
            color=WHITE_COLOR
        ).move_to(thanks_bg.get_center())
        thanks_banner = VGroup(thanks_bg, thanks_text).next_to(concl_row, DOWN, buff=0.22)

        next_footer = build_footer(8, TOTAL_SLIDES)
        self.play(
            FadeOut(slide7_content),
            Transform(current_footer, next_footer),
            Write(slide8_title),
            Create(slide8_accent),
            FadeIn(concl_row),
            FadeIn(thanks_banner)
        )
        self.wait(0.2)
