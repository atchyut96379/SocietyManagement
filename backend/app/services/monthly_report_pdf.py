import io
import zipfile
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.config.accounts import ACCOUNT_CORPUS, ACCOUNT_MAINTENANCE
from app.config.society_config import get_apartment_name


def _fmt_amount(value) -> str:
    if value is None:
        return "0"
    if float(value) == int(float(value)):
        return str(int(float(value)))
    return f"{float(value):.2f}"


def _money_table(rows, col_widths=None, bold_from_row=None):
    table = Table(rows, colWidths=col_widths or [4.2 * inch, 1.3 * inch])
    style = [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    if bold_from_row is not None:
        style.append((
            "FONTNAME", (0, bold_from_row), (-1, -1), "Helvetica-Bold"
        ))
    table.setStyle(TableStyle(style))
    return table


def _bold_row(label, amount):
    return [label, _fmt_amount(amount)]


def _append_account_section(story, styles, account_data: dict, account_label: str):
    collected_label = (
        f"Maintenance amount collected ({account_data['paid_flats_count']} flats)"
        if account_data["account"] == ACCOUNT_MAINTENANCE
        else (
            f"Maintenance paid to Corpus ({account_data['paid_flats_count']} flats)"
            if account_data["paid_flats_count"]
            else "Amount collected"
        )
    )

    income_rows = [
        ["Particulars", "Amount (₹)"],
        ["Opening balance", _fmt_amount(account_data["opening_balance"])],
        [collected_label, _fmt_amount(account_data["collected"])],
    ]

    income_rows.append(_bold_row("Total Income", account_data["total_income"]))

    story.append(Paragraph(
        f"<b>{account_label} — Income:</b>",
        styles["Normal"]
    ))
    story.append(Spacer(1, 4))
    story.append(_money_table(income_rows, bold_from_row=len(income_rows) - 1))
    story.append(Spacer(1, 0.15 * inch))

    expense_rows = [["Particulars", "Amount (₹)"]]
    for item in account_data.get("expenses") or []:
        label = item["expense_type"]
        if item.get("description") and item["description"] != label:
            label = f"{label} — {item['description']}"
        expense_rows.append([label, _fmt_amount(item["amount"])])

    expense_rows.append(
        _bold_row("Expenditures As of Now", account_data["expense_total"])
    )
    expense_rows.append(
        _bold_row("Closing Balance", account_data["closing_balance"])
    )

    story.append(Paragraph(
        f"<b>{account_label} — Expenditure:</b>",
        styles["Normal"]
    ))
    story.append(Spacer(1, 4))
    bold_start = len(expense_rows) - 2
    story.append(_money_table(expense_rows, bold_from_row=bold_start))
    story.append(Spacer(1, 0.2 * inch))


def build_monthly_report_pdf(report_data: dict, resident_annex: dict | None = None) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    styles = getSampleStyleSheet()
    story = []

    society_name = report_data.get("society_name") or get_apartment_name()
    reg_no = report_data.get("registration_number", "")
    address = report_data.get("society_address", "")

    title_style = ParagraphStyle(
        "title",
        parent=styles["Heading1"],
        fontSize=16,
        alignment=1,
        textColor=colors.HexColor("#1e4d8c"),
        spaceAfter=6,
    )
    center_style = ParagraphStyle(
        "center",
        parent=styles["Normal"],
        alignment=1,
        fontSize=10,
    )
    heading_style = ParagraphStyle(
        "heading",
        parent=styles["Heading2"],
        fontSize=13,
        alignment=1,
        spaceBefore=12,
        spaceAfter=10,
        underlineProportion=0.1,
    )

    story.append(Paragraph(society_name.upper(), title_style))
    if reg_no:
        story.append(Paragraph(f"(Regd No: {reg_no})", center_style))
    if address:
        story.append(Paragraph(address, center_style))
    story.append(Spacer(1, 0.15 * inch))

    period = f"{report_data['month']}-{report_data['year']}"
    story.append(Paragraph(
        f"Monthly Maintenance {period}",
        heading_style
    ))

    if resident_annex:
        story.append(Paragraph(
            f"<b>Resident Copy</b> — Flat {resident_annex.get('flat_number', '')} "
            f"({resident_annex.get('resident_name', '')})",
            ParagraphStyle("annex", fontSize=10, spaceAfter=8)
        ))

    maintenance = report_data.get("maintenance_account") or {}
    corpus = report_data.get("corpus_account") or {}

    _append_account_section(story, styles, maintenance, "Maintenance Account")

    corpus_payments = corpus.get("payments") or []
    if (
        corpus.get("collected")
        or corpus.get("opening_balance")
        or corpus.get("expense_total")
        or corpus.get("transfer_in")
        or corpus.get("transfer_out")
        or corpus_payments
    ):
        _append_account_section(story, styles, corpus, "Corpus Account")

    pending = report_data.get("pending_flats") or []
    if pending:
        story.append(Paragraph("<b>Maintenance Pending Flats:</b>", styles["Normal"]))
        story.append(Spacer(1, 4))
        pending_lines = [
            f"{p['flat_number']} : {p['resident_name']}"
            for p in pending
        ]
        story.append(Paragraph("<br/>".join(pending_lines), styles["Normal"]))
        story.append(Spacer(1, 0.15 * inch))

    corpus_pending = report_data.get("corpus_pending_flats") or []
    if corpus_pending:
        story.append(Paragraph(
            "<b>Corpus Fund Pending Flats:</b>",
            styles["Normal"]
        ))
        story.append(Spacer(1, 4))
        lines = [
            f"{p['flat_number']} : {p['resident_name']}"
            for p in corpus_pending
        ]
        story.append(Paragraph("<br/>".join(lines), styles["Normal"]))
        story.append(Spacer(1, 0.15 * inch))

    if resident_annex:
        story.append(Paragraph("<b>Your Flat Summary:</b>", styles["Normal"]))
        story.append(Spacer(1, 4))
        annex_rows = [
            ["Particulars", "Details"],
            ["Flat Number", resident_annex.get("flat_number", "-")],
            ["Resident Name", resident_annex.get("resident_name", "-")],
            ["Invoice Amount", _fmt_amount(resident_annex.get("invoice_amount", 0))],
            ["Amount Paid", _fmt_amount(resident_annex.get("amount_paid", 0))],
            ["Paid To Account", resident_annex.get("credit_account", "-")],
            ["Status", resident_annex.get("status", "-")],
        ]
        story.append(_money_table(annex_rows, [2.5 * inch, 3 * inch]))
        story.append(Spacer(1, 0.15 * inch))

    notes = report_data.get("notes") or []
    if notes:
        story.append(Paragraph("<b>Note:</b>", styles["Normal"]))
        story.append(Spacer(1, 4))
        for note in notes:
            story.append(Paragraph(f"➤ {note}", styles["Normal"]))
        story.append(Spacer(1, 0.2 * inch))

    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph("Regards,", styles["Normal"]))
    story.append(Paragraph(
        f"{society_name} Association.",
        styles["Normal"]
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        ParagraphStyle("small", fontSize=8, textColor=colors.grey)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def build_all_resident_reports_zip(report_data: dict) -> bytes:
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        society_pdf = build_monthly_report_pdf(report_data)
        period = f"{report_data['month']}_{report_data['year']}"
        zf.writestr(
            f"Monthly_Report_{period}_Society.pdf",
            society_pdf
        )

        for resident in report_data.get("residents") or []:
            annex = {
                "flat_number": resident.get("flat_number"),
                "resident_name": resident.get("resident_name"),
                "invoice_amount": resident.get("invoice_amount", 0),
                "amount_paid": resident.get("amount_paid", 0),
                "status": resident.get("status", "N/A"),
                "credit_account": resident.get("credit_account"),
            }
            pdf_bytes = build_monthly_report_pdf(report_data, annex)
            safe_flat = str(resident.get("flat_number", "flat")).replace("/", "-")
            safe_name = str(resident.get("resident_name", "resident")).replace(" ", "_")
            filename = f"Monthly_Report_{period}_{safe_flat}_{safe_name}.pdf"
            zf.writestr(filename, pdf_bytes)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()
