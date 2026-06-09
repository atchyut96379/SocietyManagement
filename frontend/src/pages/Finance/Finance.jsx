import { useEffect, useState } from "react";
import Layout from "../../components/Layout/Layout";
import api from "../../services/api";

const emptyInvoice = {
    resident_id: "",
    invoice_month: "",
    invoice_year: new Date().getFullYear(),
    amount: "",
    due_date: ""
};

const emptyCashPayment = {
    invoice_id: "",
    amount_paid: "",
    transaction_reference: "",
    proof_image: null,
    credit_account: "Maintenance"
};

const emptyExpense = {
    expense_type: "",
    amount: "",
    description: "",
    expense_date: new Date().toISOString().slice(0, 10),
    proof_image: null,
    paid_from_account: "Maintenance"
};

const emptyReportExtras = {
    notes: "",
    corpus_pending_flats: ""
};

const accountOptions = [
    { value: "Maintenance", label: "Maintenance Account" },
    { value: "Corpus", label: "Corpus Account" }
];

const emptyBulk = {
    invoice_month: "",
    invoice_year: new Date().getFullYear(),
    amount: "",
    due_date: ""
};

const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
];

function Finance() {

    const [finance, setFinance] = useState({
        total_invoices: 0,
        total_collected: 0,
        pending_dues: 0,
        total_expenses: 0,
        available_balance: 0,
        maintenance_balance: 0,
        corpus_balance: 0,
        period_month: "",
        period_year: new Date().getFullYear(),
        maintenance_account: null,
        corpus_account: null
    });

    const [invoices, setInvoices] = useState([]);
    const [payments, setPayments] = useState([]);
    const [expenses, setExpenses] = useState([]);
    const [residents, setResidents] = useState([]);

    const [invoiceForm, setInvoiceForm] = useState(emptyInvoice);
    const [cashForm, setCashForm] = useState(emptyCashPayment);
    const [expenseForm, setExpenseForm] = useState(emptyExpense);
    const [bulkForm, setBulkForm] = useState(emptyBulk);
    const [report, setReport] = useState(null);
    const [reportMonth, setReportMonth] = useState(
        monthNames[new Date().getMonth()]
    );
    const [reportYear, setReportYear] = useState(
        new Date().getFullYear()
    );
    const [reportExtras, setReportExtras] = useState(emptyReportExtras);
    const [downloadingPdf, setDownloadingPdf] = useState(false);
    const [downloadingZip, setDownloadingZip] = useState(false);

    const apiBase = process.env.REACT_APP_API_URL || "";

    const loadAll = async () => {
        await Promise.all([
            loadFinance(),
            loadInvoices(),
            loadPayments(),
            loadExpenses(),
            loadResidents()
        ]);
    };

    useEffect(() => {
        loadAll();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const loadFinance = async () => {

        try {

            const response =
                await api.get("/finance/dashboard");

            setFinance(response.data);

        } catch {

            alert("Unable to load finance data");
        }
    };

    const loadInvoices = async () => {

        const response = await api.get("/maintenance");
        setInvoices(response.data);
    };

    const loadPayments = async () => {

        const response = await api.get("/payment/history");
        setPayments(response.data);
    };

    const loadExpenses = async () => {

        const response = await api.get("/expense");
        setExpenses(response.data);
    };

    const loadResidents = async () => {

        const response = await api.get("/resident");
        setResidents(response.data);
    };

    const generateInvoice = async (event) => {

        event.preventDefault();

        try {

            await api.post("/maintenance/generate", {
                ...invoiceForm,
                resident_id: Number(invoiceForm.resident_id),
                invoice_year: Number(invoiceForm.invoice_year),
                amount: Number(invoiceForm.amount)
            });

            setInvoiceForm(emptyInvoice);
            loadAll();

        } catch {

            alert("Unable to generate invoice");
        }
    };

    const recordCashPayment = async (event) => {

        event.preventDefault();

        if (!cashForm.proof_image) {
            alert("Please upload payment proof screenshot or bill");
            return;
        }

        try {

            const formData = new FormData();
            formData.append(
                "invoice_id",
                String(Number(cashForm.invoice_id))
            );
            formData.append(
                "amount_paid",
                String(Number(cashForm.amount_paid))
            );
            formData.append(
                "transaction_reference",
                cashForm.transaction_reference
            );
            formData.append("proof_image", cashForm.proof_image);
            formData.append("credit_account", cashForm.credit_account);

            const response = await api.post("/payment/cash", formData, {
                headers: { "Content-Type": "multipart/form-data" }
            });

            if (!response.data.success) {
                alert(response.data.message);
                return;
            }

            alert(
                `Cash payment recorded.\nReceipt: ${response.data.receipt_number}`
            );

            setCashForm(emptyCashPayment);
            loadAll();

        } catch (err) {

            alert(
                err.response?.data?.message ||
                "Unable to record cash payment"
            );
        }
    };

    const addExpense = async (event) => {

        event.preventDefault();

        if (!expenseForm.proof_image) {
            alert("Please upload bill or payment proof image");
            return;
        }

        try {

            const formData = new FormData();
            formData.append("expense_type", expenseForm.expense_type);
            formData.append("amount", String(Number(expenseForm.amount)));
            formData.append("description", expenseForm.description);
            formData.append("expense_date", expenseForm.expense_date);
            formData.append(
                "paid_from_account",
                expenseForm.paid_from_account
            );
            formData.append("proof_image", expenseForm.proof_image);

            await api.post("/expense", formData, {
                headers: { "Content-Type": "multipart/form-data" }
            });

            setExpenseForm(emptyExpense);
            loadAll();

        } catch (err) {

            alert(
                err.response?.data?.message ||
                "Unable to add expense"
            );
        }
    };

    const generateBulkInvoices = async (event) => {

        event.preventDefault();

        try {

            const response = await api.post(
                "/maintenance/generate-bulk",
                {
                    ...bulkForm,
                    invoice_year: Number(bulkForm.invoice_year),
                    amount: Number(bulkForm.amount)
                }
            );

            alert(response.data.message);
            setBulkForm(emptyBulk);
            loadAll();

        } catch {

            alert("Unable to generate bulk invoices");
        }
    };

    const loadReport = async () => {

        try {

            const response = await api.get("/finance/report", {
                params: {
                    month: reportMonth,
                    year: reportYear
                }
            });

            setReport(response.data);

        } catch {

            alert("Unable to load monthly report");
        }
    };

    const printReport = () => {
        window.print();
    };

    const reportDownloadParams = () => ({
        month: reportMonth,
        year: Number(reportYear),
        notes: reportExtras.notes,
        corpus_pending_flats: reportExtras.corpus_pending_flats
    });

    const renderAccountSummary = (title, account) => {

        if (!account) {
            return null;
        }

        const expenditures = account.expenditures ?? account.expense_total ?? 0;

        return (
            <div className="col-md-6 mb-3">
                <div className="card h-100 border-secondary">
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
    };

    const downloadReportPdf = async () => {

        setDownloadingPdf(true);

        try {

            const response = await api.get("/finance/report/pdf", {
                params: reportDownloadParams(),
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

            alert("Unable to download monthly report PDF");

        } finally {

            setDownloadingPdf(false);
        }
    };

    const downloadAllResidentReports = async () => {

        setDownloadingZip(true);

        try {

            const response = await api.get("/finance/report/download-all", {
                params: reportDownloadParams(),
                responseType: "blob"
            });

            const url = window.URL.createObjectURL(
                new Blob([response.data], { type: "application/zip" })
            );
            const link = document.createElement("a");
            link.href = url;
            link.download = `Monthly_Reports_${reportMonth}_${reportYear}_All_Residents.zip`;
            link.click();
            window.URL.revokeObjectURL(url);

        } catch {

            alert("Unable to download resident reports");

        } finally {

            setDownloadingZip(false);
        }
    };

    return (

        <Layout>

            <h2 className="mb-4">Finance Dashboard</h2>

            <div className="row mb-4">

                <div className="col-md-2">
                    <div className="card p-3">
                        <h6>Total Invoices</h6>
                        <h4>₹{finance.total_invoices}</h4>
                    </div>
                </div>

                <div className="col-md-2">
                    <div className="card p-3">
                        <h6>Collected</h6>
                        <h4>₹{finance.total_collected}</h4>
                    </div>
                </div>

                <div className="col-md-2">
                    <div className="card p-3">
                        <h6>Pending Dues</h6>
                        <h4>₹{finance.pending_dues}</h4>
                    </div>
                </div>

                <div className="col-md-2">
                    <div className="card p-3 border-primary">
                        <h6>Maintenance Balance</h6>
                        <h4>₹{finance.maintenance_balance}</h4>
                    </div>
                </div>

                <div className="col-md-2">
                    <div className="card p-3 border-info">
                        <h6>Corpus Balance</h6>
                        <h4>₹{finance.corpus_balance}</h4>
                    </div>
                </div>

                <div className="col-md-2">
                    <div className="card p-3 border-success">
                        <h6>Total Balance</h6>
                        <h4>₹{finance.available_balance}</h4>
                    </div>
                </div>

            </div>

            <div className="row mb-4">
                <div className="col-12 mb-2">
                    <h5 className="mb-0">
                        Account Summary — {finance.period_month}{" "}
                        {finance.period_year}
                    </h5>
                </div>
                {renderAccountSummary(
                    "Maintenance Account",
                    finance.maintenance_account
                )}
                {renderAccountSummary(
                    "Corpus Account",
                    finance.corpus_account
                )}
            </div>

            <div className="card mb-4 border-primary">
                <div className="card-header bg-primary text-white">
                    Bulk Maintenance Billing (All Residents)
                </div>
                <div className="card-body">
                    <form
                        className="row g-3"
                        onSubmit={generateBulkInvoices}
                    >
                        <div className="col-md-3">
                            <select
                                className="form-select"
                                value={bulkForm.invoice_month}
                                onChange={(e) =>
                                    setBulkForm({
                                        ...bulkForm,
                                        invoice_month: e.target.value
                                    })
                                }
                                required
                            >
                                <option value="">Select Month</option>
                                {monthNames.map((m) => (
                                    <option key={m} value={m}>{m}</option>
                                ))}
                            </select>
                        </div>
                        <div className="col-md-2">
                            <input
                                type="number"
                                className="form-control"
                                placeholder="Year"
                                value={bulkForm.invoice_year}
                                onChange={(e) =>
                                    setBulkForm({
                                        ...bulkForm,
                                        invoice_year: e.target.value
                                    })
                                }
                                required
                            />
                        </div>
                        <div className="col-md-2">
                            <input
                                type="number"
                                className="form-control"
                                placeholder="Amount per flat"
                                value={bulkForm.amount}
                                onChange={(e) =>
                                    setBulkForm({
                                        ...bulkForm,
                                        amount: e.target.value
                                    })
                                }
                                required
                            />
                        </div>
                        <div className="col-md-2">
                            <input
                                type="date"
                                className="form-control"
                                value={bulkForm.due_date}
                                onChange={(e) =>
                                    setBulkForm({
                                        ...bulkForm,
                                        due_date: e.target.value
                                    })
                                }
                                required
                            />
                        </div>
                        <div className="col-md-3">
                            <button
                                type="submit"
                                className="btn btn-primary w-100"
                            >
                                Generate For All Flats
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <div className="row">

                <div className="col-lg-4 mb-4">

                    <div className="card h-100">
                        <div className="card-header">
                            Generate Maintenance Invoice
                        </div>
                        <div className="card-body">

                            <form onSubmit={generateInvoice}>

                                <select
                                    className="form-select mb-2"
                                    value={invoiceForm.resident_id}
                                    onChange={(e) =>
                                        setInvoiceForm({
                                            ...invoiceForm,
                                            resident_id: e.target.value
                                        })
                                    }
                                    required
                                >
                                    <option value="">Select Resident</option>
                                    {residents.map((r) => (
                                        <option
                                            key={r.resident_id}
                                            value={r.resident_id}
                                        >
                                            {r.full_name} ({r.flat_number})
                                        </option>
                                    ))}
                                </select>

                                <input
                                    className="form-control mb-2"
                                    placeholder="Month (e.g. January)"
                                    value={invoiceForm.invoice_month}
                                    onChange={(e) =>
                                        setInvoiceForm({
                                            ...invoiceForm,
                                            invoice_month: e.target.value
                                        })
                                    }
                                    required
                                />

                                <input
                                    type="number"
                                    className="form-control mb-2"
                                    placeholder="Year"
                                    value={invoiceForm.invoice_year}
                                    onChange={(e) =>
                                        setInvoiceForm({
                                            ...invoiceForm,
                                            invoice_year: e.target.value
                                        })
                                    }
                                    required
                                />

                                <input
                                    type="number"
                                    className="form-control mb-2"
                                    placeholder="Amount"
                                    value={invoiceForm.amount}
                                    onChange={(e) =>
                                        setInvoiceForm({
                                            ...invoiceForm,
                                            amount: e.target.value
                                        })
                                    }
                                    required
                                />

                                <input
                                    type="date"
                                    className="form-control mb-2"
                                    value={invoiceForm.due_date}
                                    onChange={(e) =>
                                        setInvoiceForm({
                                            ...invoiceForm,
                                            due_date: e.target.value
                                        })
                                    }
                                    required
                                />

                                <button
                                    type="submit"
                                    className="btn btn-primary w-100"
                                >
                                    Generate
                                </button>

                            </form>

                        </div>
                    </div>

                </div>

                <div className="col-lg-4 mb-4">

                    <div className="card h-100">
                        <div className="card-header">
                            Record Cash Payment
                        </div>
                        <div className="card-body">

                            <small className="text-muted d-block mb-2">
                                Choose which bank account received the payment.
                                If a flat owner paid maintenance into the Corpus
                                account, select Corpus here. Online Pay Now
                                always credits Maintenance.
                            </small>

                            <form onSubmit={recordCashPayment}>

                                <select
                                    className="form-select mb-2"
                                    value={cashForm.invoice_id}
                                    onChange={(e) =>
                                        setCashForm({
                                            ...cashForm,
                                            invoice_id: e.target.value
                                        })
                                    }
                                    required
                                >
                                    <option value="">Select Invoice</option>
                                    {invoices
                                        .filter((i) => i.status !== "Paid")
                                        .map((i) => (
                                            <option
                                                key={i.invoice_id}
                                                value={i.invoice_id}
                                            >
                                                #{i.invoice_id} - {i.resident_name} - ₹{i.amount}
                                            </option>
                                        ))}
                                </select>

                                <input
                                    type="number"
                                    className="form-control mb-2"
                                    placeholder="Amount Paid"
                                    value={cashForm.amount_paid}
                                    onChange={(e) =>
                                        setCashForm({
                                            ...cashForm,
                                            amount_paid: e.target.value
                                        })
                                    }
                                    required
                                />

                                <input
                                    className="form-control mb-2"
                                    placeholder="Reference / Receipt No"
                                    value={cashForm.transaction_reference}
                                    onChange={(e) =>
                                        setCashForm({
                                            ...cashForm,
                                            transaction_reference: e.target.value
                                        })
                                    }
                                    required
                                />

                                <select
                                    className="form-select mb-2"
                                    value={cashForm.credit_account}
                                    onChange={(e) =>
                                        setCashForm({
                                            ...cashForm,
                                            credit_account: e.target.value
                                        })
                                    }
                                    required
                                >
                                    {accountOptions.map((opt) => (
                                        <option
                                            key={opt.value}
                                            value={opt.value}
                                        >
                                            Credited to {opt.label}
                                        </option>
                                    ))}
                                </select>

                                <input
                                    type="file"
                                    className="form-control mb-2"
                                    accept="image/*,.pdf"
                                    onChange={(e) =>
                                        setCashForm({
                                            ...cashForm,
                                            proof_image: e.target.files[0]
                                        })
                                    }
                                    required
                                />

                                <button
                                    type="submit"
                                    className="btn btn-success w-100"
                                >
                                    Mark as Paid (Cash)
                                </button>

                            </form>

                        </div>
                    </div>

                </div>

                <div className="col-lg-4 mb-4">

                    <div className="card h-100">
                        <div className="card-header">
                            Add Expense
                        </div>
                        <div className="card-body">

                            <small className="text-muted d-block mb-2">
                                Select which account paid for this expense.
                                Most bills are from Maintenance; Corpus is
                                used only occasionally.
                            </small>

                            <form onSubmit={addExpense}>

                                <input
                                    className="form-control mb-2"
                                    placeholder="Expense Type"
                                    value={expenseForm.expense_type}
                                    onChange={(e) =>
                                        setExpenseForm({
                                            ...expenseForm,
                                            expense_type: e.target.value
                                        })
                                    }
                                    required
                                />

                                <input
                                    type="number"
                                    className="form-control mb-2"
                                    placeholder="Amount"
                                    value={expenseForm.amount}
                                    onChange={(e) =>
                                        setExpenseForm({
                                            ...expenseForm,
                                            amount: e.target.value
                                        })
                                    }
                                    required
                                />

                                <input
                                    className="form-control mb-2"
                                    placeholder="Description"
                                    value={expenseForm.description}
                                    onChange={(e) =>
                                        setExpenseForm({
                                            ...expenseForm,
                                            description: e.target.value
                                        })
                                    }
                                    required
                                />

                                <input
                                    type="date"
                                    className="form-control mb-2"
                                    value={expenseForm.expense_date}
                                    onChange={(e) =>
                                        setExpenseForm({
                                            ...expenseForm,
                                            expense_date: e.target.value
                                        })
                                    }
                                    required
                                />

                                <select
                                    className="form-select mb-2"
                                    value={expenseForm.paid_from_account}
                                    onChange={(e) =>
                                        setExpenseForm({
                                            ...expenseForm,
                                            paid_from_account: e.target.value
                                        })
                                    }
                                    required
                                >
                                    {accountOptions.map((opt) => (
                                        <option
                                            key={opt.value}
                                            value={opt.value}
                                        >
                                            Paid from {opt.label}
                                        </option>
                                    ))}
                                </select>

                                <input
                                    type="file"
                                    className="form-control mb-2"
                                    accept="image/*,.pdf"
                                    onChange={(e) =>
                                        setExpenseForm({
                                            ...expenseForm,
                                            proof_image: e.target.files[0]
                                        })
                                    }
                                    required
                                />

                                <button
                                    type="submit"
                                    className="btn btn-warning w-100"
                                >
                                    Add Expense
                                </button>

                            </form>

                        </div>
                    </div>

                </div>

            </div>

            <div className="row">

                <div className="col-lg-4 mb-4">
                    <h5>Invoices</h5>
                    <table className="table table-sm table-bordered">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Resident</th>
                                <th>Period</th>
                                <th>Amount</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {invoices.map((i) => (
                                <tr key={i.invoice_id}>
                                    <td>{i.invoice_id}</td>
                                    <td>
                                        {i.resident_name} ({i.flat_number})
                                    </td>
                                    <td>{i.month} {i.year}</td>
                                    <td>₹{i.amount}</td>
                                    <td>{i.status}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <div className="col-lg-4 mb-4">
                    <h5>Payments</h5>
                    <table className="table table-sm table-bordered">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Invoice</th>
                                <th>Amount</th>
                                <th>Mode</th>
                                <th>Account</th>
                                <th>Source</th>
                                <th>Recorded By</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {payments.map((p) => (
                                <tr key={p.payment_id}>
                                    <td>{p.payment_id}</td>
                                    <td>{p.invoice_id}</td>
                                    <td>₹{p.amount_paid}</td>
                                    <td>{p.payment_mode}</td>
                                    <td>{p.credit_account || "Maintenance"}</td>
                                    <td>{p.payment_source}</td>
                                    <td>{p.recorded_by}</td>
                                    <td>{p.payment_date}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <div className="col-lg-4 mb-4">
                    <h5>Expenses</h5>
                    <table className="table table-sm table-bordered">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Type</th>
                                <th>Amount</th>
                                <th>Account</th>
                                <th>Date</th>
                                <th>Bill</th>
                            </tr>
                        </thead>
                        <tbody>
                            {expenses.map((e) => (
                                <tr key={e.expense_id}>
                                    <td>{e.expense_id}</td>
                                    <td>{e.expense_type}</td>
                                    <td>₹{e.amount}</td>
                                    <td>{e.paid_from_account || "Maintenance"}</td>
                                    <td>{e.expense_date}</td>
                                    <td>
                                        {e.proof_url ? (
                                            <a
                                                href={`${apiBase}${e.proof_url}`}
                                                target="_blank"
                                                rel="noreferrer"
                                            >
                                                View
                                            </a>
                                        ) : (
                                            "-"
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

            </div>

            <div className="card mb-4" id="monthly-report">
                <div className="card-header d-flex justify-content-between align-items-center">
                    <span>Monthly Finance Report</span>
                    <div className="d-flex gap-2">
                        <select
                            className="form-select form-select-sm"
                            value={reportMonth}
                            onChange={(e) =>
                                setReportMonth(e.target.value)
                            }
                        >
                            {monthNames.map((m) => (
                                <option key={m} value={m}>{m}</option>
                            ))}
                        </select>
                        <input
                            type="number"
                            className="form-control form-control-sm"
                            style={{ width: "100px" }}
                            value={reportYear}
                            onChange={(e) =>
                                setReportYear(e.target.value)
                            }
                        />
                        <button
                            className="btn btn-sm btn-primary"
                            onClick={loadReport}
                        >
                            Load Report
                        </button>
                        <button
                            className="btn btn-sm btn-success"
                            onClick={downloadReportPdf}
                            disabled={downloadingPdf}
                        >
                            {downloadingPdf ? "Downloading…" : "Download PDF"}
                        </button>
                        <button
                            className="btn btn-sm btn-info text-white"
                            onClick={downloadAllResidentReports}
                            disabled={downloadingZip}
                        >
                            {downloadingZip
                                ? "Preparing ZIP…"
                                : "Download All Residents"}
                        </button>
                        {report && (
                            <button
                                className="btn btn-sm btn-secondary"
                                onClick={printReport}
                            >
                                Print
                            </button>
                        )}
                    </div>
                </div>

                <div className="card-body border-bottom bg-light">
                    <h6 className="mb-3">Report PDF Options</h6>
                    <div className="row g-3">
                        <div className="col-md-8">
                            <label className="form-label small">
                                Notes (one per line, shown in PDF)
                            </label>
                            <textarea
                                className="form-control form-control-sm"
                                rows={4}
                                placeholder="Flat Nos. 216 and 419 paid in April..."
                                value={reportExtras.notes}
                                onChange={(e) =>
                                    setReportExtras({
                                        ...reportExtras,
                                        notes: e.target.value
                                    })
                                }
                            />
                        </div>
                        <div className="col-md-4">
                            <label className="form-label small">
                                Corpus pending flats (flat : name)
                            </label>
                            <textarea
                                className="form-control form-control-sm"
                                rows={4}
                                placeholder="114 : L.Gayatri Devi"
                                value={reportExtras.corpus_pending_flats}
                                onChange={(e) =>
                                    setReportExtras({
                                        ...reportExtras,
                                        corpus_pending_flats: e.target.value
                                    })
                                }
                            />
                        </div>
                    </div>
                    <small className="text-muted d-block mt-2">
                        Maintenance and Corpus accounts are calculated
                        automatically. Notes are saved when you download PDF
                        and shown to all residents in their portal.
                    </small>
                </div>

                {report && (
                    <div className="card-body">
                        <h5>
                            {report.month} {report.year} Summary
                        </h5>
                        <div className="row mb-3">
                            <div className="col-md-2">
                                Invoices: ₹{report.summary.total_invoices}
                            </div>
                            <div className="col-md-2">
                                Collected: ₹{report.summary.total_collected}
                            </div>
                            <div className="col-md-2">
                                Pending: ₹{report.summary.pending_dues}
                            </div>
                            <div className="col-md-2">
                                Maintenance close: ₹
                                {report.summary.maintenance_balance}
                            </div>
                            <div className="col-md-2">
                                Corpus close: ₹{report.summary.corpus_balance}
                            </div>
                        </div>

                        <div className="row mb-4">
                            {renderAccountSummary(
                                "Maintenance Account",
                                report.maintenance_account
                            )}
                            {renderAccountSummary(
                                "Corpus Account",
                                report.corpus_account
                            )}
                        </div>

                        <h6>Invoices</h6>
                        <table className="table table-sm table-bordered mb-3">
                            <thead>
                                <tr>
                                    <th>Flat</th>
                                    <th>Resident</th>
                                    <th>Amount</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {report.invoices.map((item) => (
                                    <tr key={item.invoice_id}>
                                        <td>{item.flat_number}</td>
                                        <td>{item.resident_name}</td>
                                        <td>₹{item.amount}</td>
                                        <td>{item.status}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        <h6>Payments</h6>
                        <table className="table table-sm table-bordered mb-3">
                            <thead>
                                <tr>
                                    <th>Flat</th>
                                    <th>Resident</th>
                                    <th>Amount</th>
                                    <th>Mode</th>
                                    <th>Account</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                {report.payments.map((item) => (
                                    <tr key={item.payment_id}>
                                        <td>{item.flat_number}</td>
                                        <td>{item.resident_name}</td>
                                        <td>₹{item.amount_paid}</td>
                                        <td>{item.payment_mode}</td>
                                        <td>{item.credit_account}</td>
                                        <td>{item.payment_date}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        <h6>Expenses</h6>
                        <table className="table table-sm table-bordered">
                            <thead>
                                <tr>
                                    <th>Type</th>
                                    <th>Description</th>
                                    <th>Amount</th>
                                    <th>Account</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                {report.expenses.map((item) => (
                                    <tr key={item.expense_id}>
                                        <td>{item.expense_type}</td>
                                        <td>{item.description}</td>
                                        <td>₹{item.amount}</td>
                                        <td>{item.paid_from_account}</td>
                                        <td>{item.expense_date}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

        </Layout>
    );
}

export default Finance;
