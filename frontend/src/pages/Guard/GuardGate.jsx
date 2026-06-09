import { useState } from "react";
import GuardLayout from "../../components/GuardLayout/GuardLayout";
import PageHeader from "../../components/ui/PageHeader";
import api from "../../services/api";

function GuardGate() {

    const [verifyCode, setVerifyCode] = useState("");
    const [lookupResult, setLookupResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const lookupVisitorCode = async (event) => {

        event?.preventDefault();
        setLoading(true);

        try {

            const response = await api.get(
                `/visitor/lookup/${verifyCode.trim()}`
            );

            setLookupResult(response.data);

        } catch (err) {

            setLookupResult({
                success: false,
                message:
                    err.response?.data?.message ||
                    "Unable to look up entry code"
            });

        } finally {
            setLoading(false);
        }
    };

    const allowEntry = async () => {

        setLoading(true);

        try {

            const response = await api.post("/visitor/verify-code", {
                entry_code: verifyCode.trim()
            });

            setLookupResult(response.data);
            setVerifyCode("");

        } catch (err) {

            setLookupResult({
                success: false,
                message:
                    err.response?.data?.message ||
                    "Unable to verify entry code"
            });

        } finally {
            setLoading(false);
        }
    };

    const verifyAndAllow = async (event) => {

        event.preventDefault();
        await allowEntry();
    };

    return (
        <GuardLayout>
            <PageHeader
                title="Gate Entry"
                subtitle="Enter the 6-digit visitor code to verify and allow entry"
            />

            <div className="form-section-card card border-warning mb-4">
                <div className="card-header bg-warning fw-semibold">
                    Verify Visitor Code
                </div>
                <div className="card-body p-4">
                    <form onSubmit={verifyAndAllow}>
                        <label className="form-label fs-5">
                            Entry Code
                        </label>
                        <input
                            className="form-control form-control-lg gate-code-input mb-3"
                            placeholder="000000"
                            value={verifyCode}
                            onChange={(e) =>
                                setVerifyCode(
                                    e.target.value.replace(/\D/g, "").slice(0, 6)
                                )
                            }
                            inputMode="numeric"
                            maxLength={6}
                            autoFocus
                            required
                        />

                        <div className="d-flex gap-2 flex-wrap">
                            <button
                                type="button"
                                className="btn btn-outline-primary btn-lg"
                                disabled={verifyCode.length < 6 || loading}
                                onClick={(e) => lookupVisitorCode(e)}
                            >
                                Look Up
                            </button>

                            <button
                                type="submit"
                                className="btn btn-success btn-lg"
                                disabled={verifyCode.length < 6 || loading}
                            >
                                {loading
                                    ? "Processing..."
                                    : "Allow Entry"}
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            {lookupResult && (
                <div
                    className={`card ${
                        lookupResult.success
                            ? "border-success"
                            : "border-danger"
                    }`}
                >
                    <div
                        className={`card-header ${
                            lookupResult.success
                                ? "bg-success text-white"
                                : "bg-danger text-white"
                        }`}
                    >
                        {lookupResult.success
                            ? "Visitor Details"
                            : "Verification Failed"}
                    </div>
                    <div className="card-body">
                        <p className="mb-2">{lookupResult.message}</p>

                        {lookupResult.visitor && (
                            <div className="fs-5">
                                <div>
                                    <strong>Visitor:</strong>{" "}
                                    {lookupResult.visitor.visitor_name}
                                </div>
                                <div>
                                    <strong>Mobile:</strong>{" "}
                                    {lookupResult.visitor.mobile_number}
                                </div>
                                <div>
                                    <strong>Visiting:</strong>{" "}
                                    {lookupResult.visitor.resident_name}
                                    {" — Flat "}
                                    {lookupResult.visitor.flat_number}
                                </div>
                                <div>
                                    <strong>Purpose:</strong>{" "}
                                    {lookupResult.visitor.purpose}
                                </div>
                                <div>
                                    <strong>Status:</strong>{" "}
                                    <span
                                        className={
                                            lookupResult.visitor.status ===
                                            "Approved"
                                                ? "text-success fw-bold"
                                                : ""
                                        }
                                    >
                                        {lookupResult.visitor.status}
                                    </span>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </GuardLayout>
    );
}

export default GuardGate;
