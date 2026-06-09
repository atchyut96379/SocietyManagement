import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import { getHomeRoute, getRoleLabel, getUserName } from "../../utils/auth";

function GuardSetup() {

    const navigate = useNavigate();
    const [form, setForm] = useState({
        full_name: "",
        phone_number: "",
        email: "",
        identity_card_type: "Aadhar",
        identity_card_number: "",
        current_password: "",
        new_password: "",
        confirm_password: ""
    });
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadProfile();
    }, []);

    const loadProfile = async () => {

        try {

            const response = await api.get("/guard/profile");

            if (response.data.success === false) {
                return;
            }

            setForm((prev) => ({
                ...prev,
                full_name: response.data.full_name || "",
                phone_number: response.data.phone_number || "",
                email: response.data.email || "",
                identity_card_type:
                    response.data.identity_card_type || "Aadhar",
                identity_card_number:
                    response.data.identity_card_number || ""
            }));

        } catch {
            // Profile load is optional for empty first-time form
        }
    };

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

        if (!form.identity_card_number.trim()) {
            setError("Identity card number is required");
            return;
        }

        setLoading(true);

        try {

            const response = await api.post("/guard/profile", {
                full_name: form.full_name.trim(),
                phone_number: form.phone_number.trim(),
                email: form.email?.trim() || null,
                identity_card_type: form.identity_card_type,
                identity_card_number: form.identity_card_number.trim(),
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
                "Unable to save profile"
            );

        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="setup-page">
            <div className="col-md-6 w-100" style={{ maxWidth: "640px" }}>
                    <div className="app-card card shadow">
                        <div className="card-header">
                            <h4 className="mb-0">Guard Profile Setup</h4>
                        </div>
                        <div className="card-body">
                            <p className="text-muted">
                                Welcome <strong>{getUserName()}</strong>
                                {" "}({getRoleLabel()}).
                                Complete your profile and set a new password
                                to access the Guard Portal.
                            </p>

                            {error && (
                                <div className="alert alert-danger">{error}</div>
                            )}

                            <form onSubmit={submit}>
                                <div className="row g-3">
                                    <div className="col-md-6">
                                        <label className="form-label">
                                            Full Name *
                                        </label>
                                        <input
                                            className="form-control"
                                            value={form.full_name}
                                            onChange={(e) =>
                                                setForm({
                                                    ...form,
                                                    full_name: e.target.value
                                                })
                                            }
                                            required
                                        />
                                    </div>

                                    <div className="col-md-6">
                                        <label className="form-label">
                                            Mobile Number *
                                        </label>
                                        <input
                                            type="tel"
                                            className="form-control"
                                            value={form.phone_number}
                                            onChange={(e) =>
                                                setForm({
                                                    ...form,
                                                    phone_number: e.target.value
                                                })
                                            }
                                            required
                                        />
                                    </div>

                                    <div className="col-md-6">
                                        <label className="form-label">
                                            Email
                                        </label>
                                        <input
                                            type="email"
                                            className="form-control"
                                            value={form.email}
                                            onChange={(e) =>
                                                setForm({
                                                    ...form,
                                                    email: e.target.value
                                                })
                                            }
                                        />
                                    </div>

                                    <div className="col-md-6">
                                        <label className="form-label">
                                            ID Type *
                                        </label>
                                        <select
                                            className="form-select"
                                            value={form.identity_card_type}
                                            onChange={(e) =>
                                                setForm({
                                                    ...form,
                                                    identity_card_type:
                                                        e.target.value
                                                })
                                            }
                                        >
                                            <option value="Aadhar">
                                                Aadhar
                                            </option>
                                            <option value="PAN">PAN</option>
                                        </select>
                                    </div>

                                    <div className="col-12">
                                        <label className="form-label">
                                            Identity Card Number *
                                        </label>
                                        <input
                                            className="form-control"
                                            placeholder="Aadhar or PAN number"
                                            value={form.identity_card_number}
                                            onChange={(e) =>
                                                setForm({
                                                    ...form,
                                                    identity_card_number:
                                                        e.target.value
                                                })
                                            }
                                            required
                                        />
                                    </div>

                                    <div className="col-12">
                                        <hr />
                                        <label className="form-label">
                                            Current Password *
                                        </label>
                                        <input
                                            type="password"
                                            className="form-control"
                                            value={form.current_password}
                                            onChange={(e) =>
                                                setForm({
                                                    ...form,
                                                    current_password:
                                                        e.target.value
                                                })
                                            }
                                            required
                                        />
                                        <small className="text-muted">
                                            Use the default password shared by
                                            secretary (e.g. MyGaGUA)
                                        </small>
                                    </div>

                                    <div className="col-md-6">
                                        <label className="form-label">
                                            New Password *
                                        </label>
                                        <input
                                            type="password"
                                            className="form-control"
                                            value={form.new_password}
                                            onChange={(e) =>
                                                setForm({
                                                    ...form,
                                                    new_password:
                                                        e.target.value
                                                })
                                            }
                                            required
                                        />
                                    </div>

                                    <div className="col-md-6">
                                        <label className="form-label">
                                            Confirm New Password *
                                        </label>
                                        <input
                                            type="password"
                                            className="form-control"
                                            value={form.confirm_password}
                                            onChange={(e) =>
                                                setForm({
                                                    ...form,
                                                    confirm_password:
                                                        e.target.value
                                                })
                                            }
                                            required
                                        />
                                    </div>
                                </div>

                                <button
                                    type="submit"
                                    className="btn btn-primary w-100 mt-4"
                                    disabled={loading}
                                >
                                    {loading
                                        ? "Saving..."
                                        : "Save & Continue to Guard Portal"}
                                </button>
                            </form>
                        </div>
                    </div>
            </div>
        </div>
    );
}

export default GuardSetup;
