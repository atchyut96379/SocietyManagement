import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import { getHomeRoute, getRoleLabel, getUserName } from "../../utils/auth";

function FirstLoginSetup() {

    const navigate = useNavigate();
    const [form, setForm] = useState({
        current_password: "",
        new_password: "",
        confirm_password: ""
    });
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const submit = async (event) => {

        event.preventDefault();
        setError("");

        if (form.new_password !== form.confirm_password) {
            setError("New passwords do not match");
            return;
        }

        if (form.new_password.length < 6) {
            setError("Password must be at least 6 characters");
            return;
        }

        setLoading(true);

        try {

            const response = await api.post("/change-password", {
                current_password: form.current_password,
                new_password: form.new_password
            });

            if (!response.data.success) {
                setError(response.data.message);
                return;
            }

            localStorage.removeItem("must_change_password");
            localStorage.removeItem("profile_completed");
            navigate(getHomeRoute());

        } catch (err) {

            setError(
                err.response?.data?.message ||
                "Unable to update password"
            );

        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="setup-page">
            <div className="col-md-5 w-100" style={{ maxWidth: "480px" }}>
                    <div className="app-card card shadow">
                        <div className="card-header">
                            <h4 className="mb-0">First Login Setup</h4>
                        </div>
                        <div className="card-body">
                            <p className="text-muted">
                                Welcome <strong>{getUserName()}</strong>
                                {" "}({getRoleLabel()}).
                                Please change your default password to continue.
                            </p>

                            {error && (
                                <div className="alert alert-danger">{error}</div>
                            )}

                            <form onSubmit={submit}>
                                <div className="mb-3">
                                    <label className="form-label">
                                        Current Password
                                    </label>
                                    <input
                                        type="password"
                                        className="form-control"
                                        value={form.current_password}
                                        onChange={(e) =>
                                            setForm({
                                                ...form,
                                                current_password: e.target.value
                                            })
                                        }
                                        required
                                    />
                                    <small className="text-muted">
                                        Use the password shared by admin
                                        (e.g. MyGaSec)
                                    </small>
                                </div>

                                <div className="mb-3">
                                    <label className="form-label">
                                        New Password
                                    </label>
                                    <input
                                        type="password"
                                        className="form-control"
                                        value={form.new_password}
                                        onChange={(e) =>
                                            setForm({
                                                ...form,
                                                new_password: e.target.value
                                            })
                                        }
                                        required
                                    />
                                </div>

                                <div className="mb-3">
                                    <label className="form-label">
                                        Confirm New Password
                                    </label>
                                    <input
                                        type="password"
                                        className="form-control"
                                        value={form.confirm_password}
                                        onChange={(e) =>
                                            setForm({
                                                ...form,
                                                confirm_password: e.target.value
                                            })
                                        }
                                        required
                                    />
                                </div>

                                <button
                                    type="submit"
                                    className="btn btn-primary w-100"
                                    disabled={loading}
                                >
                                    {loading ? "Saving..." : "Save & Continue"}
                                </button>
                            </form>
                        </div>
                    </div>
            </div>
        </div>
    );
}

export default FirstLoginSetup;
