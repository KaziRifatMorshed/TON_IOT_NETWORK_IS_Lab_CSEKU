# ==============================================================================
# TON_IoT Network Intrusion Detection: Manim Presentation Slides
# Information Security Lab (Lab #7) - Khulna University (CSEKU)
# Instructor: Dr. Anupam Kumar Bairagi, Professor, CSE Discipline
# Presenters: Md Siam Ahmed (230202), Kazi Rifat Morshed (230220)
# ==============================================================================

from datetime import datetime
from manim import *
from manim_slides import Slide  # pyright: ignore[reportAttributeAccessIssue]  # manim-slides does not expose complete type information

# Dynamic Month Year (e.g., "October 2026")
CURRENT_MONTH_YEAR = datetime.now().strftime("%B %Y")

# ==============================================================================
# NVIDIA Brand Color Theme (Light Academic Defense)
# ==============================================================================
NVIDIA_GREEN = "#76B900"  # Signature NVIDIA Green
NVIDIA_DARK_GREEN = "#265200"  # High-contrast accessible green (WCAG AAA)
NVIDIA_ACCENT_GREEN = "#3B7500"  # Structural border accent green
TEXT_MAIN = "#1A1A1A"  # Deep charcoal for academic typography & LaTeX
TEXT_MUTED = "#525B64"  # Slate gray for captions, subtitles, and notes
CARD_BG = "#F8FAFC"  # Base canvas and container surface
CARD_BORDER = "#E2E8F0"  # Subtle hairline boundary stroke
WHITE_COLOR = "#FFFFFF"  # Pure white card surface
BLOCK_INACTIVE_FILL = "#F1F5F9"  # Hardware slate neutral tile fill
BLOCK_INACTIVE_STROKE = "#94A3B8"  # Hardware neutral stroke border

# Configure base light canvas defaults
config.background_color = ManimColor(CARD_BG)
Tex.set_default(color=TEXT_MAIN)
MathTex.set_default(color=TEXT_MAIN)

TOTAL_SLIDES = 13


class TonIoTPresentation(Slide):
    def construct(self):
        # Enforce exact canvas background color for Manim-Slides
        self.camera.background_color = ManimColor(CARD_BG)

        # ===========================================================
        # HELPER: Global Footer (Persistent across all content slides)
        # ===========================================================
        def build_footer(slide_num):
            footer_bar = Rectangle(
                width=config.frame_width + 1.0,
                height=0.42,
                fill_color=NVIDIA_GREEN,
                fill_opacity=1.0,
                stroke_width=0,
            ).to_edge(DOWN, buff=-0.01)

            page_info = (
                Tex(
                    rf"\textbf{{Slide {slide_num}/{TOTAL_SLIDES}}} \hspace{{0.2cm}} \textbar \hspace{{0.2cm}} "
                    r"\textsf{TON\_IoT Network Intrusion Detection}",
                    font_size=15,
                    color=CARD_BG,
                )
                .to_edge(LEFT, buff=0.4)
                .match_y(footer_bar)
            )

            presenter_info = (
                Tex(
                    r"\textsf{Md Siam Ahmed (230202), Kazi Rifat Morshed (230220) \hspace{0.2cm} \textbar \hspace{0.2cm} "
                    + CURRENT_MONTH_YEAR
                    + r"}",
                    font_size=14,
                    color=CARD_BG,
                )
                .to_edge(RIGHT, buff=0.4)
                .match_y(footer_bar)
            )

            return VGroup(footer_bar, page_info, presenter_info)

        # ===========================================================
        # HELPER: Persistent Content Header
        # ===========================================================
        def build_header(category_tex_str, section_tex_str):
            header_bar = Rectangle(
                width=config.frame_width + 1.0,
                height=0.72,
                fill_color=WHITE_COLOR,
                fill_opacity=1.0,
                stroke_color=CARD_BORDER,
                stroke_width=1.0,
            ).to_edge(UP, buff=-0.01)

            header_stripe = Line(
                LEFT * (config.frame_width / 2 + 0.5),
                RIGHT * (config.frame_width / 2 + 0.5),
                color=NVIDIA_GREEN,
                stroke_width=2.5,
            ).next_to(header_bar, DOWN, buff=0)

            header_tracker = (
                Tex(
                    rf"\textbf{{\textsf{{{category_tex_str}}}}} \hspace{{0.15cm}}\textbar\hspace{{0.15cm}} \textsf{{\footnotesize {section_tex_str}}}",
                    font_size=15,
                    color=NVIDIA_DARK_GREEN,
                )
                .to_edge(LEFT, buff=0.6)
                .match_y(header_bar)
            )

            header_logo = (
                ImageMobject("kucse_full_logo.png")
                .set(height=0.42)
                .to_edge(RIGHT, buff=0.4)
                .match_y(header_bar)
            )
            return Group(
                header_bar, header_stripe, header_tracker, header_logo
            ), header_stripe

        # ===========================================================
        # HELPER: Rounded card with coloured header bar
        # ===========================================================
        def make_card(
            header_text,
            header_color,
            body_tex_str,
            body_font=15,
            card_width=5.8,
            card_height=3.5,
        ):
            bg = RoundedRectangle(
                corner_radius=0.10,
                width=card_width,
                height=card_height,
                fill_color=WHITE_COLOR,
                fill_opacity=1.0,
                stroke_color=CARD_BORDER,
                stroke_width=1.5,
            )
            top_bar = RoundedRectangle(
                corner_radius=0.06,
                width=card_width,
                height=0.42,
                fill_color=header_color,
                fill_opacity=1.0,
                stroke_width=0,
            ).align_to(bg, UP)
            badge = Tex(
                rf"\textbf{{{header_text}}}", font_size=18, color=WHITE_COLOR
            ).move_to(top_bar.get_center())
            body = (
                Tex(body_tex_str, font_size=body_font, color=TEXT_MAIN)
                .next_to(top_bar, DOWN, buff=0.20)
                .set(width=card_width - 0.45)
            )
            return VGroup(bg, top_bar, badge, body)

        # ===========================================================
        # HELPER: Slide title + green accent line
        # ===========================================================
        def slide_title(text, stripe, font=29):
            """Build the slide title and green accent line as a single Group,
            and add them to the slide so they are properly cleared on exit."""
            title = Tex(rf"\textbf{{{text}}}", font_size=font, color=TEXT_MAIN)
            title.next_to(stripe, DOWN, buff=0.26)
            accent = Line(
                LEFT * 2.0, RIGHT * 2.0, color=NVIDIA_GREEN, stroke_width=2.5
            ).next_to(title, DOWN, buff=0.10)
            return VGroup(title, accent)

        # ===========================================================
        # SLIDE 1 — Title / Cover
        # ===========================================================
        discipline_info = Tex(
            r"\textbf{Computer Science and Engineering Discipline}\\[0.04cm]\textbf{Khulna University}",
            font_size=22,
            color=NVIDIA_DARK_GREEN,
        )
        univ_logo = ImageMobject("ku_emblem_clean.png").set(height=0.86)
        title_slide_header = Group(discipline_info, univ_logo).arrange(RIGHT, buff=0.35)
        title_slide_header.to_edge(UP, buff=0.44)

        main_title = Tex(
            r"\textbf{TON\_IoT Network Traffic Classification}\\[0.04cm]\textbf{Using Random Forest}",
            font_size=36,
            color=TEXT_MAIN,
        )
        title_accent = Line(
            LEFT * 2.5, RIGHT * 2.5, color=NVIDIA_GREEN, stroke_width=3.5
        )
        main_subtitle = Tex(
            r"\textit{Intrusion Detection Workflow}", font_size=22, color=TEXT_MUTED
        )
        title_block = VGroup(main_title, title_accent, main_subtitle).arrange(
            DOWN, buff=0.18
        )
        title_block.next_to(title_slide_header, DOWN, buff=0.36)

        lab_strip_bg = Rectangle(
            width=config.frame_width + 1.0,
            height=0.52,
            fill_color=NVIDIA_GREEN,
            fill_opacity=1.0,
            stroke_width=0,
        ).to_edge(DOWN, buff=-0.01)
        lab_strip_text = Tex(
            r"\textbf{Information Security Laboratory \hspace{0.3cm} | \hspace{0.3cm} "
            r"Khulna University, Khulna}",
            font_size=18,
            color=WHITE_COLOR,
        ).move_to(lab_strip_bg.get_center())
        lab_strip = Group(lab_strip_bg, lab_strip_text)

        self.play(FadeIn(title_slide_header), FadeIn(lab_strip))
        self.play(Write(main_title), Create(title_accent))
        self.play(FadeIn(main_subtitle))
        self.wait(0.2)
        self.next_slide()

        # ===========================================================
        # SLIDE 2 — Presented By / Presented To
        # ===========================================================
        s1_content = Group(title_slide_header, title_block)
        footer = build_footer(2)
        header, stripe = build_header(r"PRESENTERS", r"INFORMATION SECURITY LAB \#7")

        s2_title = slide_title(
            r"Presented By \hspace{0.4cm} / \hspace{0.4cm} Presented To",
            stripe,
            font=26,
        )

        # LEFT — Presented By
        by_header_bg = RoundedRectangle(
            corner_radius=0.08,
            width=5.6,
            height=0.46,
            fill_color=NVIDIA_DARK_GREEN,
            fill_opacity=1.0,
            stroke_width=0,
        )
        by_header_text = Tex(
            r"\textbf{PRESENTED BY}", font_size=18, color=WHITE_COLOR
        ).move_to(by_header_bg.get_center())
        by_header = VGroup(by_header_bg, by_header_text)

        s1_name = Tex(r"\textbf{Md Siam Ahmed}", font_size=22, color=TEXT_MAIN)
        s1_id = Tex(r"Student ID: 230202", font_size=18, color=TEXT_MUTED)
        s2_name = Tex(r"\textbf{Kazi Rifat Morshed}", font_size=22, color=TEXT_MAIN)
        s2_id = Tex(r"Student ID: 230220", font_size=18, color=TEXT_MUTED)
        div_line = Line(LEFT * 2.4, RIGHT * 2.4, color=CARD_BORDER, stroke_width=1.0)
        dept_by = Tex(
            r"Computer Science \& Engineering Discipline\\[0.04cm]Khulna University, Khulna",
            font_size=19,
            color=TEXT_MUTED,
        )
        sem_info = Tex(
            r"\textit{4th Year, 1st Term}", font_size=18, color=NVIDIA_ACCENT_GREEN
        )

        by_body = VGroup(
            VGroup(s1_name, s1_id).arrange(DOWN, buff=0.05),
            VGroup(s2_name, s2_id).arrange(DOWN, buff=0.05),
            div_line,
            dept_by,
            sem_info,
        ).arrange(DOWN, buff=0.18)

        by_bg = RoundedRectangle(
            corner_radius=0.10,
            width=5.6,
            height=4.5,
            fill_color=WHITE_COLOR,
            fill_opacity=1.0,
            stroke_color=CARD_BORDER,
            stroke_width=1.5,
        )
        by_header.next_to(by_bg, UP, buff=0).align_to(by_bg, UP)
        by_body.next_to(by_header, DOWN, buff=0.22)
        by_card = VGroup(by_bg, by_header, by_body)

        # RIGHT — Presented To
        to_header_bg = RoundedRectangle(
            corner_radius=0.08,
            width=5.6,
            height=0.46,
            fill_color=NVIDIA_GREEN,
            fill_opacity=1.0,
            stroke_width=0,
        )
        to_header_text = Tex(
            r"\textbf{PRESENTED TO}", font_size=18, color=WHITE_COLOR
        ).move_to(to_header_bg.get_center())
        to_header = VGroup(to_header_bg, to_header_text)

        sup_name = Tex(
            r"\textbf{Dr. Anupam Kumar Bairagi}", font_size=22, color=TEXT_MAIN
        )
        sup_desig = Tex(r"Professor", font_size=18, color=TEXT_MUTED)
        div_line2 = Line(LEFT * 2.4, RIGHT * 2.4, color=CARD_BORDER, stroke_width=1.0)
        sup_dept = Tex(
            r"Computer Science \& Engineering Discipline\\[0.04cm]Khulna University, Khulna",
            font_size=19,
            color=TEXT_MUTED,
        )
        course_tag = Tex(
            r"\textit{Course: Information Security Laboratory} \\ \textit{Course Code: 0714 02 CSE 4107}",
            font_size=18,
            color=NVIDIA_ACCENT_GREEN,
        )
        to_body = VGroup(
            VGroup(sup_name, sup_desig).arrange(DOWN, buff=0.05),
            div_line2,
            sup_dept,
            course_tag,
        ).arrange(DOWN, buff=0.20)

        to_bg2 = RoundedRectangle(
            corner_radius=0.10,
            width=5.6,
            height=4.5,
            fill_color=WHITE_COLOR,
            fill_opacity=1.0,
            stroke_color=CARD_BORDER,
            stroke_width=1.5,
        )
        to_header.next_to(to_bg2, UP, buff=0).align_to(to_bg2, UP)
        to_body.next_to(to_header, DOWN, buff=0.28)
        to_card = VGroup(to_bg2, to_header, to_body)

        both_cards = VGroup(by_card, to_card).arrange(RIGHT, buff=0.5)
        both_cards.next_to(s2_title, DOWN, buff=0.3)

        self.play(
            FadeOut(s1_content),
            FadeOut(lab_strip),
            FadeIn(header),
            FadeIn(footer),
            FadeIn(s2_title),
        )
        self.play(FadeIn(both_cards))
        self.wait(0.2)
        self.next_slide()

        # ===========================================================
        # SLIDE 3 — Problem & Objective
        # ===========================================================
        prev_content = Group(s2_title, both_cards)
        new_footer = build_footer(3)
        next_header, stripe = build_header(
            r"PROBLEM \& OBJECTIVE", r"MOTIVATION FOR THIS WORK"
        )

        s3_title = slide_title(r"Problem and Objective", stripe)

        prob_card = make_card(
            "THE PROBLEM",
            "#B71C1C",
            r"\begin{flushleft}"
            r"$\bullet$ Thousands of traffic events arrive every second in IoT/IIoT\\[0.04cm]"
            r"networks.\\[0.10cm]"
            r"$\bullet$ Manual review cannot reliably separate Normal, DoS,\\[0.04cm]"
            r"and DDoS traffic.\\[0.10cm]"
            r"$\bullet$ Attackers disguise malicious flows to resemble\\[0.04cm]"
            r"legitimate traffic.\\[0.10cm]"
            r"$\bullet$ Detection must be fast enough for real-time response."
            r"\end{flushleft}",
            body_font=22,
            card_width=5.8,
            card_height=3.6,
        )
        obj_card = make_card(
            "OBJECTIVE",
            NVIDIA_DARK_GREEN,
            r"Building an automated multi-class IDS that classifies each\\[0.04cm]"
            r"flow as:\\[0.08cm]"
            r"\hspace{0.3cm}\textbf{Normal} \hspace{0.4cm} \textbf{DoS} \hspace{0.4cm} \textbf{DDoS}\\[0.12cm]"
            r"Using \textbf{Random Forest, XGBoost, Deep MLP} to learn attack patterns from\\[0.04cm]"
            r"cleaned features CSV and save the model, metrics, and figures.\\[0.32cm]"
            r"\textit{Outcome: A fast, reproducible classifier for\\[0.04cm]"
            r"Normal, DoS, and DDoS traffic.}",
            body_font=22,
            card_width=5.8,
            card_height=3.6,
        )
        s3_row = VGroup(prob_card, obj_card).arrange(RIGHT, buff=0.45)
        s3_row.next_to(s3_title, DOWN, buff=0.28)

        self.play(
            FadeOut(prev_content),
            Transform(footer, new_footer),
            FadeOut(header),
        )
        header = next_header
        self.play(FadeIn(header), FadeIn(s3_title))
        self.play(FadeIn(s3_row))
        self.wait(0.2)
        self.next_slide()

        # ===========================================================
        # SLIDE 4 — Dataset Overview
        # ===========================================================
        prev_content = Group(s3_title, s3_row)
        new_footer = build_footer(4)
        next_header, stripe = build_header(
            r"DATASET OVERVIEW", r"TON\_IoT NETWORK TRAFFIC RECORDS"
        )

        s4_title = slide_title(r"Dataset Overview", stripe)

        # Left: attribute table card
        attr_card_bg = RoundedRectangle(
            corner_radius=0.10,
            width=5.4,
            height=4.2,
            fill_color=WHITE_COLOR,
            fill_opacity=1.0,
            stroke_color=CARD_BORDER,
            stroke_width=1.5,
        )
        attr_bar = RoundedRectangle(
            corner_radius=0.06,
            width=5.4,
            height=0.42,
            fill_color=NVIDIA_DARK_GREEN,
            fill_opacity=1.0,
            stroke_width=0,
        ).align_to(attr_card_bg, UP)
        attr_badge = Tex(
            r"\textbf{Dataset Attributes}", font_size=18, color=WHITE_COLOR
        ).move_to(attr_bar.get_center())
        attr_table = (
            Tex(
                r"\renewcommand{\arraystretch}{1.35}"
                "\n"
                r"\begin{tabular}{ll}"
                "\n"
                r"\hline"
                "\n"
                r"\textbf{Attribute} & \textbf{Value} \\"
                "\n"
                r"\hline"
                "\n"
                r"Dataset        & TON\_IoT Network Traffic \\"
                "\n"
                r"Dataset Author        & Nour Moustafa, Associate Professor\\"
                "\n"
                r"        & UNSW Canberra, Australia \\"
                "\n"
                r"Total Records  & 10,336,716 flows (\~10.3 Million)\\"
                "\n"
                r"Dataset Size & 1.2 GiB \\"
                "\n"
                r"Target Column  & \texttt{type} (Normal, DoS, DDoS) \\"
                "\n"
                r"Dedicated Split & 80\% Train / 20\% Test \\"
                "\n"
                r"Pipeline Scale & 8.27M Train / 2.06M Test \\"
                "\n"
                r"\hline"
                "\n"
                r"\end{tabular}",
                font_size=18,
                color=TEXT_MAIN,
            )
            .next_to(attr_bar, DOWN, buff=0.25)
            .set(width=4.9)
        )
        attr_card = VGroup(attr_card_bg, attr_bar, attr_badge, attr_table)

        # Right: feature groups card
        feat_card_bg = RoundedRectangle(
            corner_radius=0.10,
            width=6.2,
            height=4.2,
            fill_color=WHITE_COLOR,
            fill_opacity=1.0,
            stroke_color=CARD_BORDER,
            stroke_width=1.5,
        )
        feat_bar = RoundedRectangle(
            corner_radius=0.06,
            width=6.2,
            height=0.42,
            fill_color=NVIDIA_GREEN,
            fill_opacity=1.0,
            stroke_width=0,
        ).align_to(feat_card_bg, UP)
        feat_badge = Tex(
            r"\textbf{Feature Groups}", font_size=18, color=TEXT_MAIN
        ).move_to(feat_bar.get_center())
        feat_body = (
            Tex(
                r"\begin{flushleft}"
                r"\textbf{Network Identity:}\hspace{0.3cm} IP addresses, ports\\[0.14cm]"
                r"\textbf{Protocol Behavior:}\hspace{0.2cm} protocol, service, conn\_state\\[0.14cm]"
                r"\textbf{Traffic Volume:}\hspace{0.35cm} packet counts, byte counts\\[0.14cm]"
                r"\textbf{Timing Features:}\hspace{0.3cm} duration and flow timing\\[0.14cm]"
                r"\textbf{Application Fields:}\hspace{0.1cm} HTTP, DNS, SSL indicators",
                r"\end{flushleft}",
                font_size=19,
                color=TEXT_MAIN,
            )
            .next_to(feat_bar, DOWN, buff=0.50)
            .set(width=5.75)
        )
        feat_note = (
            Tex(
                r"\textit{The dataset provides network-flow level information suitable for}\\[0.02cm]"
                r"\textit{supervised intrusion detection using Random Forest.}",
                font_size=18,
                color=TEXT_MUTED,
            )
            .next_to(feat_body, DOWN, buff=0.32)
            .set(width=5.7)
        )
        feat_card = VGroup(feat_card_bg, feat_bar, feat_badge, feat_body, feat_note)

        s4_row = VGroup(attr_card, feat_card).arrange(RIGHT, buff=0.45)
        s4_row.next_to(s4_title, DOWN, buff=0.28)

        self.play(
            FadeOut(prev_content),
            Transform(footer, new_footer),
            FadeOut(header),
        )
        header = next_header
        self.play(FadeIn(header), FadeIn(s4_title))
        self.play(FadeIn(s4_row))
        self.wait(0.2)
        self.next_slide()

        # ===========================================================
        # SLIDE 5 — Class Distribution (embedded figures)
        # ===========================================================
        prev_content = Group(s4_title, s4_row)
        new_footer = build_footer(5)
        next_header, stripe = build_header(
            r"CLASS DISTRIBUTION", r"BALANCED 1:1:1 DATASET"
        )

        s5_title = slide_title(r"Class Distribution", stripe)

        binary_img = ImageMobject(
            "../outputs/figures/rf_workflow_binary_class_distribution.png"
        ).set(height=3.9)
        multi_img = ImageMobject(
            "../outputs/figures/rf_workflow_multiclass_distribution.png"
        ).set(height=3.9)

        binary_label = Tex(
            r"\textbf{Binary Distribution}", font_size=19, color=NVIDIA_DARK_GREEN
        )
        multi_label = Tex(
            r"\textbf{Multiclass Distribution}", font_size=19, color=NVIDIA_DARK_GREEN
        )

        binary_col = Group(binary_label, binary_img).arrange(DOWN, buff=0.14)
        multi_col = Group(multi_label, multi_img).arrange(DOWN, buff=0.14)

        s5_row = Group(binary_col, multi_col).arrange(RIGHT, buff=0.55)
        s5_row.next_to(s5_title, DOWN, buff=0.22)

        caption = (
            Tex(
                r"\textit{Training dataset (8,271,593 records): DDoS: 4,932,721 (59.6\%), DoS: 2,701,550 (32.7\%), Normal: 637,322 (7.7\%). "
                r"Held-out test set (2,065,123 records) preserves the identical distribution.}",
                font_size=14,
                color=TEXT_MUTED,
            )
            .next_to(s5_row, DOWN, buff=0.40)
            .set(width=10.2)
        )

        self.play(
            FadeOut(prev_content),
            Transform(footer, new_footer),
            FadeOut(header),
        )
        header = next_header
        self.play(FadeIn(header), FadeIn(s5_title))
        self.play(FadeIn(s5_row), FadeIn(caption))
        self.wait(0.2)
        self.next_slide()

        # ===========================================================
        # SLIDE 6 — Data Preprocessing Steps (6-step cards)
        # ===========================================================
        prev_content = Group(s5_title, caption)
        prev_imgs = Group(s5_row)
        new_footer = build_footer(6)
        next_header, stripe = build_header(
            r"DATA PREPROCESSING", r"LEAKAGE-FREE PIPELINE"
        )

        s6_title = slide_title(r"Data Preprocessing Steps", stripe)

        def make_step_card(num_str, step_title_str, step_body_str):
            bg = RoundedRectangle(
                corner_radius=0.10,
                width=5.7,
                height=1.55,
                fill_color=WHITE_COLOR,
                fill_opacity=1.0,
                stroke_color=CARD_BORDER,
                stroke_width=1.4,
            )
            num_circle = (
                Circle(
                    radius=0.26,
                    fill_color=NVIDIA_GREEN,
                    fill_opacity=1.0,
                    stroke_width=0,
                )
                .align_to(bg, LEFT)
                .shift(RIGHT * 0.34)
                .align_to(bg, UP)
                .shift(DOWN * 0.38)
            )
            num_tex = Tex(
                rf"\textbf{{{num_str}}}", font_size=19, color=WHITE_COLOR
            ).move_to(num_circle.get_center())
            title_tex = (
                Tex(
                    rf"\textbf{{{step_title_str}}}",
                    font_size=17,
                    color=NVIDIA_DARK_GREEN,
                )
                .next_to(num_circle, RIGHT, buff=0.18)
                .align_to(num_circle, UP)
            )
            body_tex = (
                Tex(step_body_str, font_size=15, color=TEXT_MAIN)
                .next_to(title_tex, DOWN, buff=0.10)
                .align_to(title_tex, LEFT)
                .set(width=4.0)
            )
            return VGroup(bg, num_circle, num_tex, title_tex, body_tex)

        step1 = make_step_card(
            "01",
            "Data Ingestion",
            r"Process 10,336,716 flow records from\\[0.03cm]"
            r"dedicated \texttt{train} (8.27M) and \texttt{test} (2.06M) sets.",
        )
        step2 = make_step_card(
            "02",
            "Out-of-Core Cache",
            r"Stream chunks into binary \texttt{np.memmap}\\[0.03cm]"
            r"files, keeping RAM strictly \textbf{$<$ 1.5 GB}.",
        )
        step3 = make_step_card(
            "03",
            "Normalize Labels",
            r"Standardize \texttt{type}; separate target from features.\\[0.03cm]"
            r"Drop \texttt{label} to \textbf{prevent data leakage}.",
        )
        step4 = make_step_card(
            "04",
            "Encode Fields",
            r"Convert IPs into 64-bit high/low numeric parts.\\[0.03cm]"
            r"Encode protocol, service, conn\_state, and other categories.",
        )
        step5 = make_step_card(
            "05",
            "Clean Matrix",
            r"Replace NaN/Inf with \texttt{-1}; remove constant columns\\[0.03cm]"
            r"(e.g., \texttt{http\_referrer}). Final: \textbf{45 features}.",
        )
        step6 = make_step_card(
            "06",
            "Train / Test Split",
            r"Use an \textbf{80/20 stratified split} with\\[0.03cm]"
            r"\texttt{random\_state=42} to preserve class proportions.",
        )

        col_left = VGroup(step1, step3, step5).arrange(DOWN, buff=0.14)
        col_right = VGroup(step2, step4, step6).arrange(DOWN, buff=0.14)
        s6_grid = VGroup(col_left, col_right).arrange(RIGHT, buff=0.30)
        s6_grid.next_to(s6_title, DOWN, buff=0.20)

        result_banner_bg = RoundedRectangle(
            corner_radius=0.06,
            width=12.0,
            height=0.46,
            fill_color=NVIDIA_DARK_GREEN,
            fill_opacity=0.10,
            stroke_color=NVIDIA_DARK_GREEN,
            stroke_width=1.0,
        )
        result_banner_tx = (
            Tex(
                r"\textit{Result: a clean numeric feature matrix ready for training and evaluation.}",
                font_size=16,
                color=NVIDIA_DARK_GREEN,
            )
            .set(width=11.5)
            .move_to(result_banner_bg.get_center())
        )
        result_banner = VGroup(result_banner_bg, result_banner_tx)
        result_banner.next_to(s6_grid, DOWN, buff=0.16)

        self.play(
            FadeOut(prev_content),
            FadeOut(prev_imgs),
            Transform(footer, new_footer),
            FadeOut(header),
        )
        header = next_header
        self.play(FadeIn(header), FadeIn(s6_title))
        self.play(FadeIn(s6_grid), FadeIn(result_banner))
        self.wait(0.2)
        self.next_slide()

        # ===========================================================
        # SLIDE 7 — Machine Learning Pipeline (horizontal flowchart)
        # ===========================================================
        prev_content = Group(s6_title, s6_grid, result_banner)
        new_footer = build_footer(7)
        next_header, stripe = build_header(
            r"ML PIPELINE", r"END-TO-END TRAINING WORKFLOW"
        )

        s7_title = slide_title(r"Machine Learning Pipeline", stripe)

        # Eight pipeline stages
        stage_labels = [
            r"\textbf{Raw Data}",
            r"\textbf{Load Data}",
            r"\textbf{Clean Data}",
            r"\textbf{Feature Matrix}",
            r"\textbf{Train/Test Split}",
            r"\textbf{Random Forest}",
            r"\textbf{Evaluate}",
            r"\textbf{Save Outputs}",
        ]
        stage_sub = [
            r"TON\_IoT\\CSV records",
            r"Read\\dataset.csv",
            r"Remove\\duplicates",
            r"Encode numeric\\inputs",
            r"80/20\\stratified",
            r"Train\\200 trees",
            r"Metrics\\and plots",
            r"Model\\and reports",
        ]

        stage_boxes = VGroup()
        for label, sub in zip(stage_labels, stage_sub):
            box_bg = RoundedRectangle(
                corner_radius=0.08,
                width=1.38,
                height=1.10,
                fill_color=WHITE_COLOR,
                fill_opacity=1.0,
                stroke_color=NVIDIA_GREEN,
                stroke_width=1.8,
            )
            lbl = Tex(label, font_size=13, color=NVIDIA_DARK_GREEN)
            sub_tex = Tex(sub, font_size=12, color=TEXT_MUTED)
            content = (
                VGroup(lbl, sub_tex)
                .arrange(DOWN, buff=0.06)
                .move_to(box_bg.get_center())
            )
            stage_boxes.add(VGroup(box_bg, content))

        stage_boxes.arrange(RIGHT, buff=0.08)

        # Arrows between boxes
        arrows = VGroup()
        for i in range(len(stage_boxes) - 1):
            arr = Arrow(
                stage_boxes[i].get_right(),
                stage_boxes[i + 1].get_left(),
                buff=0.05,
                stroke_width=2.0,
                color=NVIDIA_ACCENT_GREEN,
                max_tip_length_to_length_ratio=0.25,
            )
            arrows.add(arr)

        pipeline_flow = Group(stage_boxes, arrows)
        pipeline_flow.next_to(s7_title, DOWN, buff=0.38)

        # Phase labels below
        phase_data = [
            (0, 1, "DATA INGESTION", "#1565C0"),
            (2, 3, "PREPROCESSING", "#6A1B9A"),
            (4, 5, "MODELING", NVIDIA_DARK_GREEN),
            (6, 7, "OUTPUT", "#B71C1C"),
        ]
        phase_group = VGroup()
        for start, end, label, color in phase_data:
            x_start = stage_boxes[start].get_left()[0]
            x_end = stage_boxes[end].get_right()[0]
            x_mid = (x_start + x_end) / 2
            y_pos = stage_boxes[0].get_bottom()[1] - 0.30
            ph_line = Line(
                (x_start, y_pos + 0.08, 0),
                (x_end, y_pos + 0.08, 0),
                color=color,
                stroke_width=2.0,
            )
            ph_tex = Tex(
                rf"\textbf{{\textsf{{{label}}}}}", font_size=14, color=color
            ).move_to((x_mid, y_pos - 0.14, 0))
            phase_group.add(VGroup(ph_line, ph_tex))

        pipeline_caption_bg = RoundedRectangle(
            corner_radius=0.06,
            width=12.0,
            height=0.46,
            fill_color=NVIDIA_DARK_GREEN,
            fill_opacity=0.08,
            stroke_color=NVIDIA_DARK_GREEN,
            stroke_width=1.0,
        )
        pipeline_caption_tx = (
            Tex(
                r"\textit{The trained model, evaluation metrics, figures, and run config are saved.}",
                font_size=8,
                color=NVIDIA_DARK_GREEN,
            )
            .set(width=9.5)
            .move_to(pipeline_caption_bg.get_center())
        )
        pipeline_caption = VGroup(pipeline_caption_bg, pipeline_caption_tx)
        pipeline_caption.next_to(phase_group, DOWN, buff=0.34)

        gpu_img = ImageMobject("../outputs/figures/memmap_gpu_comparison.png").set(
            height=3.8
        )
        gpu_label = Tex(
            r"\textbf{GPU Model Benchmark Comparison (10,336,716 Records)} \hspace{0.2cm}\textbar\hspace{0.2cm} "
            r"\textsf{Evaluated on 2,065,123 Test Flows}",
            font_size=17,
            color=TEXT_MUTED,
        ).set(width=11.5)

        self.play(
            FadeOut(prev_content),
            Transform(footer, new_footer),
            FadeOut(header),
        )
        header = next_header
        self.play(FadeIn(header), FadeIn(s7_title))
        self.play(FadeIn(stage_boxes), FadeIn(arrows))
        self.play(FadeIn(phase_group), FadeIn(pipeline_caption))
        self.wait(0.2)
        self.next_slide()

        # ===========================================================
        # SLIDE 8 — Random Forest Model Architecture
        # ===========================================================
        prev_content = Group(
            s7_title, stage_boxes, arrows, phase_group, pipeline_caption
        )
        new_footer = build_footer(8)
        next_header, stripe = build_header(
            r"RANDOM FOREST MODEL", r"ENSEMBLE CLASSIFIER ARCHITECTURE"
        )

        s8_title = slide_title(r"Random Forest Model", stripe)

        # Left explanation card
        left_card = make_card(
            "WHAT IS RANDOM FOREST?",
            NVIDIA_DARK_GREEN,
            r"\begin{flushleft}"
            r"\textbf{Ensemble classifier} that trains Decision\\[0.03cm]"
            r"Trees and combines their votes for the final class.\\[0.10cm]"
            r"\textbf{Why it fits this IDS task:}\\[0.06cm]"
            r"$\bullet$ Strong on tabular network-flow features\\[0.04cm]"
            r"$\bullet$ Handles numeric and encoded fields\\[0.04cm]"
            r"$\bullet$ Learns nonlinear attack patterns\\[0.04cm]"
            r"$\bullet$ Balanced weights reduce class bias\\[0.04cm]"
            r"$\bullet$ Feature importance supports explanations\\[0.10cm]"
            r"\textit{Many trees vote: Normal / DoS / DDoS}"
            r"\end{flushleft}",
            card_width=5.6,
            card_height=4.3,
            body_font=18,
        )
        left_card[3].align_to(left_card[0], LEFT).shift(RIGHT * 0.28)

        # Right parameters card
        right_card_bg = RoundedRectangle(
            corner_radius=0.10,
            width=6.0,
            height=4.3,
            fill_color=WHITE_COLOR,
            fill_opacity=1.0,
            stroke_color=CARD_BORDER,
            stroke_width=1.5,
        )
        right_bar = RoundedRectangle(
            corner_radius=0.06,
            width=6.0,
            height=0.42,
            fill_color=NVIDIA_GREEN,
            fill_opacity=1.0,
            stroke_width=0,
        ).align_to(right_card_bg, UP)
        right_badge = Tex(
            r"\textbf{MODEL PARAMETERS}", font_size=18, color=WHITE_COLOR
        ).move_to(right_bar.get_center())
        param_table = (
            Tex(
                r"\renewcommand{\arraystretch}{1.22}"
                "\n"
                r"\begin{tabular}{lll}"
                "\n"
                r"\hline"
                "\n"
                r"\textbf{Parameter} & \textbf{Value} & \textbf{Purpose} \\"
                "\n"
                r"\hline"
                "\n"
                r"n\_estimators   & 100        & Number of trees \\"
                "\n"
                r"criterion       & gini       & Split quality \\"
                "\n"
                r"max\_depth      & 8          & Tree depth limit \\"
                "\n"
                r"tree\_method    & hist (CUDA)& GPU acceleration \\"
                "\n"
                r"subsample       & 0.8        & Row subsampling \\"
                "\n"
                r"colsample       & 0.8        & Feature subsampling \\"
                "\n"
                r"learning\_rate  & 1.0        & Parallel forest mode \\"
                "\n"
                r"device          & cuda       & RTX 3060 acceleration \\"
                "\n"
                r"random\_state   & 42         & Reproducible run \\"
                "\n"
                r"\hline"
                "\n"
                r"\end{tabular}",
                font_size=18,
                color=TEXT_MAIN,
            )
            .next_to(right_bar, DOWN, buff=0.28)
            .set(width=5.6)
        )
        param_note = (
            Tex(
                r"\textit{Configured for stable, reproducible multi-class traffic classification.}",
                font_size=18,
                color=TEXT_MUTED,
            )
            .next_to(param_table, DOWN, buff=0.14)
            .set(width=5.6)
        )
        right_card = VGroup(
            right_card_bg, right_bar, right_badge, param_table, param_note
        )

        s8_row = VGroup(left_card, right_card).arrange(RIGHT, buff=0.45)
        s8_row.next_to(s8_title, DOWN, buff=0.28)

        self.play(
            FadeOut(prev_content),
            Transform(footer, new_footer),
            FadeOut(header),
        )
        header = next_header
        self.play(FadeIn(header), FadeIn(s8_title))
        self.play(FadeIn(s8_row))
        self.wait(0.2)
        self.next_slide()

        # ===========================================================
        # SLIDE 9 — Confusion Matrix 1: GPU Random Forest
        # ===========================================================
        prev_content = Group(s8_title, s8_row)
        new_footer = build_footer(9)
        next_header, stripe = build_header(
            r"CONFUSION MATRIX (1/3)", r"GPU RANDOM FOREST — 2,065,123 TEST FLOWS"
        )

        s9_title = slide_title(r"GPU Random Forest Confusion Matrix", stripe)

        cm_rf_img = ImageMobject(
            "../outputs/figures/memmap_gpu_rf_confusion_matrix.png"
        ).set(height=4.0)

        rf_card_bg = RoundedRectangle(
            corner_radius=0.10,
            width=5.4,
            height=4.0,
            fill_color=WHITE_COLOR,
            fill_opacity=1.0,
            stroke_color=CARD_BORDER,
            stroke_width=1.5,
        )
        rf_bar = RoundedRectangle(
            corner_radius=0.06,
            width=5.4,
            height=0.42,
            fill_color=NVIDIA_DARK_GREEN,
            fill_opacity=1.0,
            stroke_width=0,
        ).align_to(rf_card_bg, UP)
        rf_badge = Tex(
            r"\textbf{GPU Random Forest (CUDA)}", font_size=18, color=WHITE_COLOR
        ).move_to(rf_bar.get_center())
        rf_body = (
            Tex(
                r"\textbf{Architecture:}\hspace{0.2cm} 100 Parallel Trees on CUDA\\[0.08cm]"
                r"\textbf{Test Scale:}\hspace{0.2cm} 2,065,123 Network Flows\\[0.08cm]"
                r"\textbf{Accuracy:}\hspace{0.2cm} \textbf{99.57\%} (2,056,332 correct)\\[0.08cm]"
                r"\textbf{Macro F1:}\hspace{0.2cm} \textbf{99.05\%} \textbar\ \textbf{Recall:} 98.57\%\\[0.08cm]"
                r"\textbf{Precision:}\hspace{0.2cm} 99.54\% \textbar\ \textbf{MCC:} 0.9920\\[0.08cm]"
                r"\textbf{ROC-AUC:}\hspace{0.2cm} 0.9998 \textbar\ \textbf{Latency:} 0.56 $\mu$s\\[0.08cm]"
                r"\textbf{Training Time:}\hspace{0.2cm} \textbf{13.73 s} on RTX 3060\\[0.14cm]"
                r"\textit{Near-zero off-diagonal errors confirm high resilience against DoS/DDoS confusion.}",
                font_size=18,
                color=TEXT_MAIN,
            )
            .next_to(rf_bar, DOWN, buff=0.20)
            .set(width=4.9)
        )
        rf_card = VGroup(rf_card_bg, rf_bar, rf_badge, rf_body)

        s9_row = Group(cm_rf_img, rf_card).arrange(RIGHT, buff=0.45)
        s9_row.next_to(s9_title, DOWN, buff=0.24)

        self.play(
            FadeOut(prev_content),
            Transform(footer, new_footer),
            FadeOut(header),
        )
        header = next_header
        self.play(FadeIn(header), FadeIn(s9_title))
        self.play(FadeIn(s9_row))
        self.wait(0.2)
        self.next_slide()

        # ===========================================================
        # SLIDE 10 — Confusion Matrix 2: GPU XGBoost
        # ===========================================================
        prev_content = Group(s9_title, s9_row)
        new_footer = build_footer(10)
        next_header, stripe = build_header(
            r"CONFUSION MATRIX (2/3)", r"GPU XGBOOST — 2,065,123 TEST FLOWS"
        )

        s10_title = slide_title(r"GPU XGBoost Confusion Matrix", stripe)

        cm_xgb_img = ImageMobject(
            "../outputs/figures/memmap_gpu_xgboost_confusion_matrix.png"
        ).set(height=4.0)

        xgb_card_bg = RoundedRectangle(
            corner_radius=0.10,
            width=5.4,
            height=4.0,
            fill_color=WHITE_COLOR,
            fill_opacity=1.0,
            stroke_color=CARD_BORDER,
            stroke_width=1.5,
        )
        xgb_bar = RoundedRectangle(
            corner_radius=0.06,
            width=5.4,
            height=0.42,
            fill_color=NVIDIA_GREEN,
            fill_opacity=1.0,
            stroke_width=0,
        ).align_to(xgb_card_bg, UP)
        xgb_badge = Tex(
            r"\textbf{GPU XGBoost (Top Classifier)}", font_size=18, color=WHITE_COLOR
        ).move_to(xgb_bar.get_center())
        xgb_body = (
            Tex(
                r"\textbf{Architecture:}\hspace{0.2cm} Gradient Boosted Trees (CUDA)\\[0.08cm]"
                r"\textbf{Test Scale:}\hspace{0.2cm} 2,065,123 Network Flows\\[0.08cm]"
                r"\textbf{Accuracy:}\hspace{0.2cm} \textbf{99.87\%} (2,062,483 correct)\\[0.08cm]"
                r"\textbf{Macro F1:}\hspace{0.2cm} \textbf{99.80\%} \textbar\ \textbf{Recall:} 99.76\%\\[0.08cm]"
                r"\textbf{Precision:}\hspace{0.2cm} 99.83\% \textbar\ \textbf{MCC:} 0.9976\\[0.08cm]"
                r"\textbf{ROC-AUC:}\hspace{0.2cm} 1.0000 \textbar\ \textbf{Latency:} 0.51 $\mu$s\\[0.08cm]"
                r"\textbf{Training Time:}\hspace{0.2cm} \textbf{13.28 s} on RTX 3060\\[0.14cm]"
                r"\textit{Best overall performance; virtually zero false alarms on benign flows.}",
                font_size=18,
                color=TEXT_MAIN,
            )
            .next_to(xgb_bar, DOWN, buff=0.20)
            .set(width=4.9)
        )
        xgb_card = VGroup(xgb_card_bg, xgb_bar, xgb_badge, xgb_body)

        s10_row = Group(cm_xgb_img, xgb_card).arrange(RIGHT, buff=0.45)
        s10_row.next_to(s10_title, DOWN, buff=0.24)

        self.play(
            FadeOut(prev_content),
            Transform(footer, new_footer),
            FadeOut(header),
        )
        header = next_header
        self.play(FadeIn(header), FadeIn(s10_title))
        self.play(FadeIn(s10_row))
        self.wait(0.2)
        self.next_slide()

        # ===========================================================
        # SLIDE 11 — Confusion Matrix 3: PyTorch Deep MLP
        # ===========================================================
        prev_content = Group(s10_title, s10_row)
        new_footer = build_footer(11)
        next_header, stripe = build_header(
            r"CONFUSION MATRIX (3/3)", r"PYTORCH DEEP MLP — 2,065,123 TEST FLOWS"
        )

        s11_title = slide_title(r"PyTorch Deep Neural Network Confusion Matrix", stripe)

        cm_mlp_img = ImageMobject(
            "../outputs/figures/memmap_gpu_mlp_confusion_matrix.png"
        ).set(height=4.0)

        mlp_card_bg = RoundedRectangle(
            corner_radius=0.10,
            width=5.4,
            height=4.0,
            fill_color=WHITE_COLOR,
            fill_opacity=1.0,
            stroke_color=CARD_BORDER,
            stroke_width=1.5,
        )
        mlp_bar = RoundedRectangle(
            corner_radius=0.06,
            width=5.4,
            height=0.42,
            fill_color=NVIDIA_DARK_GREEN,
            fill_opacity=1.0,
            stroke_width=0,
        ).align_to(mlp_card_bg, UP)
        mlp_badge = Tex(
            r"\textbf{PyTorch Deep MLP (TF32 CUDA)}", font_size=18, color=WHITE_COLOR
        ).move_to(mlp_bar.get_center())
        mlp_body = (
            Tex(
                r"\textbf{Architecture:}\hspace{0.2cm} 4-Layer MLP with BatchNorm\\[0.08cm]"
                r"\textbf{Test Scale:}\hspace{0.2cm} 2,065,123 Network Flows\\[0.08cm]"
                r"\textbf{Accuracy:}\hspace{0.2cm} \textbf{94.59\%} (1,953,506 correct)\\[0.08cm]"
                r"\textbf{Macro F1:}\hspace{0.2cm} \textbf{88.87\%} \textbar\ \textbf{Recall:} 86.21\%\\[0.08cm]"
                r"\textbf{Precision:}\hspace{0.2cm} 92.69\% \textbar\ \textbf{MCC:} 0.8972\\[0.08cm]"
                r"\textbf{ROC-AUC:}\hspace{0.2cm} 0.9722 \textbar\ \textbf{Latency:} \textbf{0.15 $\mu$s}\\[0.08cm]"
                r"\textbf{Training Time:}\hspace{0.2cm} 436.71 s (5 Epochs)\\[0.14cm]"
                r"\textit{Deep neural network exhibits rapid 0.15 $\mu$s inference throughput on GPU Tensor Cores.}",
                font_size=18,
                color=TEXT_MAIN,
            )
            .next_to(mlp_bar, DOWN, buff=0.20)
            .set(width=4.9)
        )
        mlp_card = VGroup(mlp_card_bg, mlp_bar, mlp_badge, mlp_body)

        s11_row = Group(cm_mlp_img, mlp_card).arrange(RIGHT, buff=0.45)
        s11_row.next_to(s11_title, DOWN, buff=0.24)

        self.play(
            FadeOut(prev_content),
            Transform(footer, new_footer),
            FadeOut(header),
        )
        header = next_header
        self.play(FadeIn(header), FadeIn(s11_title))
        self.play(FadeIn(s11_row))
        self.wait(0.2)
        self.next_slide()

        # ===========================================================
        # SLIDE 12 — Model Benchmark Comparison & Evaluation
        # ===========================================================
        prev_content = Group(s11_title, s11_row)
        new_footer = build_footer(12)
        next_header, stripe = build_header(
            r"MODEL BENCHMARK COMPARISON", r"PERFORMANCE EVALUATION \& BEST MODEL"
        )

        s12_title = slide_title(
            r"Model Comparison and Benchmark Evaluation", stripe, font=25
        )

        comp_img = ImageMobject("../outputs/figures/memmap_gpu_comparison.png").set(
            width=5.8
        )
        comp_caption = Tex(
            r"\textbf{Figure:} Metric Comparison on 2,065,123 Test Flows",
            font_size=15,
            color=TEXT_MUTED,
        )
        comp_col = Group(comp_img, comp_caption).arrange(DOWN, buff=0.10)

        # Right table card
        table_card_bg = RoundedRectangle(
            corner_radius=0.10,
            width=6.6,
            height=4.3,
            fill_color=WHITE_COLOR,
            fill_opacity=1.0,
            stroke_color=CARD_BORDER,
            stroke_width=1.5,
        )
        table_bar = RoundedRectangle(
            corner_radius=0.06,
            width=6.6,
            height=0.42,
            fill_color=NVIDIA_DARK_GREEN,
            fill_opacity=1.0,
            stroke_width=0,
        ).align_to(table_card_bg, UP)
        table_badge = Tex(
            r"\textbf{Benchmark Results (2,065,123 Test Flows)}",
            font_size=17,
            color=WHITE_COLOR,
        ).move_to(table_bar.get_center())

        bench_table = (
            Tex(
                r"\renewcommand{\arraystretch}{1.26}"
                "\n"
                r"\begin{tabular}{lcccc}"
                "\n"
                r"\hline"
                "\n"
                r"\textbf{Model} & \textbf{Accuracy} & \textbf{Macro F1} & \textbf{Train Time} & \textbf{Latency} \\"
                "\n"
                r"\hline"
                "\n"
                r"\textbf{GPU XGBoost}    & \textbf{99.87\%} & \textbf{99.80\%} & \textbf{13.28 s} & 0.51 $\mu$s \\"
                "\n"
                r"GPU Random Forest       & 99.57\%          & 99.05\%          & 13.73 s          & 0.56 $\mu$s \\"
                "\n"
                r"PyTorch Deep MLP        & 94.59\%          & 88.87\%          & 436.71 s         & \textbf{0.15 $\mu$s} \\"
                "\n"
                r"\hline"
                "\n"
                r"\end{tabular}",
                font_size=17,
                color=TEXT_MAIN,
            )
            .next_to(table_bar, DOWN, buff=0.16)
            .set(width=6.2)
        )

        winner_box_bg = RoundedRectangle(
            corner_radius=0.06,
            width=6.2,
            height=1.35,
            fill_color=CARD_BG,
            fill_opacity=1.0,
            stroke_color=NVIDIA_GREEN,
            stroke_width=1.5,
        )
        winner_text = (
            Tex(
                r"\textbf{BEST PERFORMING MODEL: GPU XGBOOST}\\[0.05cm]"
                r"$\bullet$ \textbf{Top Score:} 99.87\% Accuracy, 99.80\% Macro F1\\[0.03cm]"
                r"$\bullet$ \textbf{Speed:} Trained in 13.28 s on 8.27M rows (RTX 3060)\\[0.03cm]"
                r"$\bullet$ \textbf{Reliability:} 1.0000 ROC-AUC with near-zero false alarms",
                font_size=16,
                color=NVIDIA_DARK_GREEN,
            )
            .set(width=5.9)
            .move_to(winner_box_bg.get_center())
        )
        winner_box = VGroup(winner_box_bg, winner_text)
        winner_box.next_to(bench_table, DOWN, buff=0.14)

        table_card = VGroup(
            table_card_bg, table_bar, table_badge, bench_table, winner_box
        )

        s12_row = Group(comp_col, table_card).arrange(RIGHT, buff=0.40)
        s12_row.next_to(s12_title, DOWN, buff=0.20)

        self.play(
            FadeOut(prev_content),
            Transform(footer, new_footer),
            FadeOut(header),
        )
        header = next_header
        self.play(FadeIn(header), FadeIn(s12_title))
        self.play(FadeIn(s12_row))
        self.wait(0.2)
        self.next_slide()

        # ===========================================================
        # SLIDE 13 — Thank You / Q&A
        # ===========================================================
        prev_content = Group(s12_title, s12_row)
        new_footer = build_footer(13)
        next_header, stripe = build_header(r"THANK YOU", r"QUESTIONS \& DISCUSSION")

        # Large centered "Thank You"
        ty_main = Tex(r"\textbf{Thank You}", font_size=68, color=TEXT_MAIN)
        ty_accent = Line(LEFT * 2.2, RIGHT * 2.2, color=NVIDIA_GREEN, stroke_width=4.0)
        ty_sub = Tex(r"\textit{Any Questions?}", font_size=32, color=TEXT_MUTED)

        repo_bg = RoundedRectangle(
            corner_radius=0.08,
            width=9.0,
            height=0.70,
            fill_color=WHITE_COLOR,
            fill_opacity=1.0,
            stroke_color=CARD_BORDER,
            stroke_width=1.4,
        )
        repo_tex = (
            Tex(
                r"\textbf{Repository:}\hspace{0.3cm}"
                r"\texttt{https://github.com/KaziRifatMorshed/TON\_IOT\_NETWORK\_IS\_Lab\_CSEKU}",
                font_size=18,
                color=NVIDIA_DARK_GREEN,
            )
            .set(width=8.5)
            .move_to(repo_bg.get_center())
        )
        repo_card = VGroup(repo_bg, repo_tex)

        ty_group = VGroup(ty_main, ty_accent, ty_sub).arrange(DOWN, buff=0.22)
        ty_group.move_to(ORIGIN).shift(UP * 0.5)
        repo_card.next_to(ty_group, DOWN, buff=0.50)

        self.play(
            FadeOut(prev_content),
            Transform(footer, new_footer),
            FadeOut(header),
        )
        header = next_header
        self.play(FadeIn(header))
        self.play(Write(ty_main), Create(ty_accent))
        self.play(FadeIn(ty_sub), FadeIn(repo_card))
        self.wait(0.5)
