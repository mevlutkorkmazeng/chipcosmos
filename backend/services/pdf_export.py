"""Bir soru-cevabı, kaynaklarıyla birlikte biçimlendirilmiş bir PDF rapora dönüştürür.

vectorvault-enterprise'daki "Executive Analysis" PDF export özelliğinin
sadeleştirilmiş bir karşılığı.
"""

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BRAND_TEAL = colors.HexColor("#0f766e")
BRAND_DARK_BLUE = colors.HexColor("#0c4a6e")
TEXT_MUTED = colors.HexColor("#64748b")


def build_pdf(question: str, answer: str, topic: str, sources: list[dict]) -> bytes:
    """(question, answer, topic, sources) -> PDF bytes.

    sources: [{"title": str, "score": float}, ...]
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=22 * mm,
        rightMargin=22 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], textColor=BRAND_DARK_BLUE, fontSize=18, spaceAfter=4
    )
    meta_label_style = ParagraphStyle(
        "MetaLabel", parent=styles["Normal"], textColor=TEXT_MUTED, fontSize=9
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Heading2"], textColor=BRAND_TEAL, fontSize=13, spaceBefore=14, spaceAfter=6
    )
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10.5, leading=15)
    source_title_style = ParagraphStyle(
        "SourceTitle", parent=styles["Normal"], textColor=BRAND_DARK_BLUE, fontSize=10, fontName="Helvetica-Bold"
    )
    source_score_style = ParagraphStyle(
        "SourceScore", parent=styles["Normal"], textColor=TEXT_MUTED, fontSize=9
    )

    story = []
    story.append(Paragraph("LOCAL RAG ASSISTANT — INTELLIGENCE REPORT", title_style))
    story.append(HRFlowable(width="100%", color=BRAND_TEAL, thickness=1.2, spaceAfter=10))

    meta_rows = [
        ["Query:", question],
        ["Topic:", topic],
        ["Generated:", datetime.now().strftime("%d %B %Y, %H:%M")],
        ["Source:", "Microsoft Foundry Local (100% offline inference)"],
    ]
    meta_table = Table(meta_rows, colWidths=[28 * mm, None])
    meta_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("TEXTCOLOR", (0, 0), (0, -1), TEXT_MUTED),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(meta_table)

    story.append(Paragraph("Analysis", section_style))
    for paragraph in answer.strip().split("\n\n"):
        story.append(Paragraph(paragraph.replace("\n", "<br/>"), body_style))
        story.append(Spacer(1, 6))

    if sources:
        story.append(Paragraph("References", section_style))
        for i, source in enumerate(sources, start=1):
            story.append(
                Paragraph(f"[{i}] {source['title']}", source_title_style)
            )
            story.append(
                Paragraph(f"Similarity score: {source['score']:.2f}", source_score_style)
            )
            story.append(Spacer(1, 6))

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#e2e8f0"), thickness=0.8))
    story.append(
        Paragraph(
            "Generated locally by Local RAG Assistant — no data left this machine.",
            ParagraphStyle("Footer", parent=styles["Normal"], textColor=TEXT_MUTED, fontSize=8, spaceBefore=6),
        )
    )

    doc.build(story)
    return buffer.getvalue()
