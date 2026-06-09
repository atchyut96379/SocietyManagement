from fastapi import APIRouter, Depends, Form
from fastapi.responses import Response

from app.auth.roles import require_management
from app.services.finance_service import (
    build_monthly_report_pdf_data,
    get_finance_dashboard,
    get_monthly_report,
)
from app.services.monthly_report_pdf import (
    build_all_resident_reports_zip,
    build_monthly_report_pdf,
)
from app.services.report_settings_service import save_report_settings

router = APIRouter(
    prefix="/finance",
    tags=["Finance"]
)


@router.get("/dashboard")
def dashboard(
    user=Depends(require_management)
):
    return get_finance_dashboard()


@router.get("/report")
def monthly_report(
    month: str,
    year: int,
    user=Depends(require_management)
):
    return get_monthly_report(month, year)


@router.post("/report/settings")
def save_monthly_report_settings(
    month: str = Form(...),
    year: int = Form(...),
    notes: str = Form(""),
    corpus_pending_flats: str = Form(""),
    user=Depends(require_management)
):
    return save_report_settings(
        month=month,
        year=year,
        notes=notes,
        corpus_pending_flats=corpus_pending_flats,
    )


@router.get("/report/pdf")
def monthly_report_pdf(
    month: str,
    year: int,
    notes: str = "",
    corpus_pending_flats: str = "",
    user=Depends(require_management)
):
    save_report_settings(
        month=month,
        year=year,
        notes=notes,
        corpus_pending_flats=corpus_pending_flats,
    )
    data = build_monthly_report_pdf_data(
        month=month,
        year=year,
        notes=notes,
        corpus_pending_flats=corpus_pending_flats,
    )
    pdf_bytes = build_monthly_report_pdf(data)
    filename = f"Monthly_Report_{data['month']}_{year}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/report/download-all")
def download_all_resident_reports(
    month: str,
    year: int,
    notes: str = "",
    corpus_pending_flats: str = "",
    user=Depends(require_management)
):
    save_report_settings(
        month=month,
        year=year,
        notes=notes,
        corpus_pending_flats=corpus_pending_flats,
    )
    data = build_monthly_report_pdf_data(
        month=month,
        year=year,
        notes=notes,
        corpus_pending_flats=corpus_pending_flats,
    )
    zip_bytes = build_all_resident_reports_zip(data)
    filename = f"Monthly_Reports_{data['month']}_{year}_All_Residents.zip"

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

