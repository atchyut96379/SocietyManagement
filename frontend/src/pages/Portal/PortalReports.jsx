import { useEffect, useState } from "react";
import PortalLayout from "../../components/PortalLayout/PortalLayout";
import api from "../../services/api";
import LoadingState from "../../components/ui/LoadingState";
import PageHeader from "../../components/ui/PageHeader";

const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
];

function AccountSummary({ title, account }) {

    if (!account) {
        return null;
    }

    const expenditures = account.expenditures ?? account.expense_total ?? 0;

    return (
        <div className="col-md-6 mb-3">
            <div className="app-card card h-100">
                <div className="card-header fw-semibold">{title}</div>
                <div className="card-body">
                    <div className="d-flex justify-content-between mb-3">
                        <span>Opening balance</span>
                        <span className="fw-semibold">
                            ₹{account.opening_balance}
                        </span>
                    </div>
                    <div className="d-flex justify-content-between mb-3">
                        <span>Collected amount</span>
                        <span className="fw-semibold">
                            ₹{account.collected}
                        </span>
                    </div>
                    <div className="d-flex justify-content-between">
                        <span>Expenditures As of Now</span>
                        <span className="fw-semibold text-danger">
                            ₹{expenditures}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
}

function PortalReports() {

    const [periods, setPeriods] = useState([]);
    const [reportMonth, setReportMonth] = useState(
        monthNames[new Date().getMonth()]
    );
    const [reportYear, setReportYear] = useState(new Date().getFullYear());
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(true);
    const [loadingReport, setLoadingReport] = useState(false);
    const [downloading, setDownloading] = useState(false);

    useEffect(() => {
        loadPeriods();
    }, []);

    const loadPeriods = async () => {

        setLoading(true);

        try {

            const response = await api.get("/portal/reports/periods");
            setPeriods(response.data || []);

            if (response.data?.length > 0) {
                setReportMonth(response.data[0].month);
                setReportYear(response.data[0].year);
            }

        } catch {

            setPeriods([]);

        } finally {

            setLoading(false);
        }
    };

    const loadReport = async () => {

        setLoadingReport(true);

        try {

            const response = await api.get("/portal/reports", {
                params: {
                    month: reportMonth,
                    year: reportYear
                }
            });

            setReport(response.data);

        } catch {

            alert("Unable to load monthly report");

        } finally {

            setLoadingReport(false);
        }
    };

    const downloadPdf = async () => {

        setDownloading(true);

        try {

            const response = await api.get("/portal/reports/pdf", {
                params: {
                    month: reportMonth,
                    year: reportYear
                },
                responseType: "blob"
            });

            const url = window.URL.createObjectURL(
                new Blob([response.data], { type: "application/pdf" })
            );
            const link = document.createElement("a");
            link.href = url;
            link.download = `Monthly_Report_${reportMonth}_${reportYear}.pdf`;
            link.click();
            window.URL.revokeObjectURL(url);

        } catch {

            alert("Unable to download report PDF");

        } finally {

            setDownloading(false);
        }
    };

    if (loading) {
        return (
            <PortalLayout>
                <LoadingState message="Loading reports..." />
            </PortalLayout>
        );
    }

    return (
        <PortalLayout>
            <PageHeader
                title="Monthly Finance Reports"
                subtitle="View and download society maintenance reports for full transparency."
            />

            <div className="app-card card mb-4">
                <div className="card-body">
                    <div className="d-flex flex-wrap gap-2 align-items-center">
                        <select
                            className="form-select form-select-sm"
                            style={{ maxWidth: "180px" }}
                            value={reportMonth}
                            onChange={(e) => setReportMonth(e.target.value)}
                        >
                            {monthNames.map((m) => (
                                <option key={m} value={m}>{m}</option>
                            ))}
                        </select>
                        <input
                            type="number"
                            className="form-control form-control-sm"
                            style={{ width: "110px" }}
                            value={reportYear}
                            onChange={(e) =>
                                setReportYear(Number(e.target.value))
                            }
                        />
                        <button
                            className="btn btn-sm btn-primary"
                            onClick={loadReport}
                            disabled={loadingReport}
                        >
                            {loadingReport ? "Loading…" : "View Report"}
                        </button>
                        <button
                            className="btn btn-sm btn-success"
                            onClick={downloadPdf}
                            disabled={downloading}
                        >
                            {downloading ? "Downloading…" : "Download PDF"}
                        </button>
                    </div>

                    {periods.length > 0 && (
                        <small className="text-muted d-block mt-2">
                            Available billing periods:{" "}
                            {periods
                                .slice(0, 6)
                                .map((p) => `${p.month} ${p.year}`)
                                .join(", ")}
                        </small>
                    )}
                </div>
            </div>

            {report && (
                <>
                    <div className="row mb-4">
                        <AccountSummary
                            title="Maintenance Account"
                            account={report.maintenance_account}
                        />
                        <AccountSummary
                            title="Corpus Account"
                            account={report.corpus_account}
                        />
                    </div>

                    {report.report_notes && (
                        <div className="app-card card mb-4">
                            <div className="card-header">Notes</div>
                            <div className="card-body">
                                {report.report_notes
                                    .split("\n")
                                    .filter((line) => line.trim())
                                    .map((line) => (
                                        <p key={line} className="mb-1">
                                            ➤ {line}
                                        </p>
                                    ))}
                            </div>
                        </div>
                    )}
                </>
            )}

            {!report && !loadingReport && (
                <div className="text-muted">
                    Select a month and year, then click View Report or
                    Download PDF.
                </div>
            )}
        </PortalLayout>
    );
}

export default PortalReports;
