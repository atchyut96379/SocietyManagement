import { useEffect, useState } from "react";
import api from "../../services/api";
import LoadingState from "../ui/LoadingState";
import { payInvoice } from "../../utils/razorpay";

function MyDues() {

    const [status, setStatus] = useState(null);
    const [userInfo, setUserInfo] = useState(null);
    const [invoices, setInvoices] = useState([]);
    const [payments, setPayments] = useState([]);
    const [payingId, setPayingId] = useState(null);
    const [saving, setSaving] = useState(false);
    const [profileForm, setProfileForm] = useState({
        full_name: "",
        flat_number: ""
    });
    const [message, setMessage] = useState("");

    useEffect(() => {
        loadAll();
    }, []);

    const loadAll = async () => {

        try {

            const [statusRes, userRes] = await Promise.all([
                api.get("/my-dues/status"),
                api.get("/my-dues/user-info")
            ]);

            setStatus(statusRes.data);
            setUserInfo(userRes.data);

            setProfileForm({
                full_name: userRes.data.full_name || "",
                flat_number: statusRes.data.flat_number || ""
            });

            if (!statusRes.data.linked) {
                setMessage(statusRes.data.message);
                return;
            }

            const [invoiceRes, paymentRes] = await Promise.all([
                api.get("/my-dues/invoices"),
                api.get("/my-dues/payments")
            ]);

            setInvoices(
                Array.isArray(invoiceRes.data) ? invoiceRes.data : []
            );
            setPayments(
                Array.isArray(paymentRes.data) ? paymentRes.data : []
            );
            setMessage("");

        } catch (err) {

            const errorMessage =
                err.response?.data?.message ||
                err.response?.data?.detail ||
                "Unable to load dues";

            setStatus({ linked: false, message: errorMessage });
            setUserInfo({
                full_name: "",
                phone_number: "",
                linked: false
            });
            setMessage(errorMessage);
        }
    };

    const saveProfile = async (event) => {

        event.preventDefault();

        if (!profileForm.flat_number.trim()) {
            alert("Please enter your flat number");
            return;
        }

        setSaving(true);

        try {

            const response = await api.post("/my-dues/profile", {
                full_name: profileForm.full_name.trim(),
                flat_number: profileForm.flat_number.trim()
            });

            if (!response.data.success) {
                alert(response.data.message);
                return;
            }

            alert(
                `Profile linked successfully!\n\n` +
                `Flat: ${response.data.flat_number}\n` +
                `Name: ${response.data.full_name}`
            );

            loadAll();

        } catch (err) {

            alert(
                err.response?.data?.message ||
                "Unable to save profile"
            );

        } finally {
            setSaving(false);
        }
    };

    const payNow = async (invoiceId) => {

        setPayingId(invoiceId);

        try {

            const result = await payInvoice(invoiceId, api);

            alert(
                "Payment successful!\n\n" +
                `Receipt: ${result.receipt_number}\n` +
                "Download PDF from Payment History."
            );

            loadAll();

        } catch (err) {

            if (err.message !== "Payment cancelled") {
                alert(err.message || "Payment could not be completed");
            }

        } finally {
            setPayingId(null);
        }
    };

    const downloadReceipt = async (paymentId) => {

        try {

            const response = await api.get(
                `/my-dues/payments/${paymentId}/receipt`,
                { responseType: "blob" }
            );

            const url = window.URL.createObjectURL(response.data);
            const link = document.createElement("a");
            link.href = url;
            link.download = `receipt-${paymentId}.pdf`;
            link.click();
            window.URL.revokeObjectURL(url);

        } catch {

            alert("Unable to download PDF receipt");
        }
    };

    if (!status || !userInfo) {
        return <LoadingState message="Loading your dues..." />;
    }

    if (!status.linked) {
        return (
            <div className="card border-primary">
                <div className="card-header bg-primary text-white">
                    Update My Profile
                </div>
                <div className="card-body">
                    <p className="text-muted mb-3">
                        Enter your flat number to link your account
                        and pay maintenance bills.
                    </p>

                    {message && (
                        <div className="alert alert-info">{message}</div>
                    )}

                    <form onSubmit={saveProfile}>
                        <div className="row g-3">
                            <div className="col-md-4">
                                <label className="form-label">Full Name</label>
                                <input
                                    className="form-control"
                                    value={profileForm.full_name}
                                    onChange={(e) =>
                                        setProfileForm({
                                            ...profileForm,
                                            full_name: e.target.value
                                        })
                                    }
                                    required
                                />
                            </div>

                            <div className="col-md-3">
                                <label className="form-label">Mobile</label>
                                <input
                                    className="form-control"
                                    value={userInfo.phone_number || ""}
                                    readOnly
                                    disabled
                                />
                                <small className="text-muted">
                                    Login mobile (cannot change here)
                                </small>
                            </div>

                            <div className="col-md-3">
                                <label className="form-label">
                                    Flat Number *
                                </label>
                                <input
                                    className="form-control"
                                    placeholder="e.g. 408 or 119"
                                    value={profileForm.flat_number}
                                    onChange={(e) =>
                                        setProfileForm({
                                            ...profileForm,
                                            flat_number: e.target.value
                                        })
                                    }
                                    required
                                />
                                <small className="text-muted">
                                    Enter exactly as registered
                                </small>
                            </div>

                            <div className="col-md-2 d-flex align-items-end">
                                <button
                                    type="submit"
                                    className="btn btn-primary w-100"
                                    disabled={saving}
                                >
                                    {saving ? "Saving..." : "Save Profile"}
                                </button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        );
    }

    return (
        <div>
            <div className="card mb-4">
                <div className="card-body">
                    <h6 className="mb-2">My Profile</h6>
                    <p className="mb-0 text-muted">
                        <strong>{status.full_name}</strong>
                        {" "}· Flat <strong>{status.flat_number}</strong>
                        {" "}· {status.tower_name}
                        {" "}· Mobile {userInfo.phone_number}
                    </p>
                </div>
            </div>

            <h5>My Invoices</h5>
            <table className="table table-bordered">
                <thead>
                    <tr>
                        <th>Period</th>
                        <th>Amount</th>
                        <th>Due Date</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {invoices.length === 0 && (
                        <tr>
                            <td colSpan="5" className="text-center text-muted">
                                No invoices yet
                            </td>
                        </tr>
                    )}
                    {invoices.map((i) => (
                        <tr key={i.invoice_id}>
                            <td>{i.month} {i.year}</td>
                            <td>₹{i.amount}</td>
                            <td>{i.due_date}</td>
                            <td>{i.status}</td>
                            <td>
                                {i.status !== "Paid" ? (
                                    <button
                                        className="btn btn-primary btn-sm"
                                        onClick={() => payNow(i.invoice_id)}
                                        disabled={payingId === i.invoice_id}
                                    >
                                        {payingId === i.invoice_id
                                            ? "Opening gateway..."
                                            : "Pay Now"}
                                    </button>
                                ) : (
                                    <span className="text-success">Paid</span>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            <h5 className="mt-4">Payment History</h5>
            <table className="table table-bordered">
                <thead>
                    <tr>
                        <th>Period</th>
                        <th>Amount</th>
                        <th>Mode</th>
                        <th>Date</th>
                        <th>Receipt (PDF)</th>
                    </tr>
                </thead>
                <tbody>
                    {payments.length === 0 && (
                        <tr>
                            <td colSpan="5" className="text-center text-muted">
                                No payments yet
                            </td>
                        </tr>
                    )}
                    {payments.map((p) => (
                        <tr key={p.payment_id}>
                            <td>{p.month} {p.year}</td>
                            <td>₹{p.amount_paid}</td>
                            <td>{p.payment_mode}</td>
                            <td>{p.payment_date}</td>
                            <td>
                                {p.receipt_number && (
                                    <button
                                        className="btn btn-outline-secondary btn-sm"
                                        onClick={() =>
                                            downloadReceipt(p.payment_id)
                                        }
                                    >
                                        Download PDF
                                    </button>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default MyDues;
