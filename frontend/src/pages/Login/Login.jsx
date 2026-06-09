import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import { getHomeRoute, hasValidSession } from "../../utils/auth";

function formatLoginError(err) {
    if (!err.response) {
        return (
            "Cannot reach API server. Start backend: " +
            "cd backend && .\\venv\\Scripts\\uvicorn.exe app.main:app --reload --port 8000"
        );
    }

    const data = err.response.data;

    if (data?.message) return data.message;

    if (data?.detail) {
        if (Array.isArray(data.detail)) {
            return data.detail
                .map((item) => item.msg || JSON.stringify(item))
                .join(". ");
        }
        return String(data.detail);
    }

    return "Login failed. Check mobile number and password.";
}

function Login() {

    const navigate = useNavigate();
    const [phoneNumber, setPhoneNumber] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (hasValidSession()) {
            navigate(getHomeRoute());
        }
    }, [navigate]);

    const login = async (event) => {

        event.preventDefault();
        setError("");
        setLoading(true);

        try {

            const response = await api.post("/login", {
                phone_number: phoneNumber.trim(),
                password
            });

            if (
                response.data.success === false ||
                !response.data.access_token
            ) {
                setError(
                    response.data.message ||
                    "Invalid mobile number or password"
                );
                return;
            }

            localStorage.setItem("token", response.data.access_token);
            localStorage.setItem("role_id", String(response.data.role_id));

            if (response.data.resident_id) {
                localStorage.setItem(
                    "resident_id",
                    String(response.data.resident_id)
                );
            } else {
                localStorage.removeItem("resident_id");
            }

            localStorage.setItem("user_name", response.data.user_name);

            if (response.data.must_change_password) {
                localStorage.setItem("must_change_password", "1");
            } else {
                localStorage.removeItem("must_change_password");
            }

            if (response.data.profile_completed === false) {
                localStorage.setItem("profile_completed", "0");
            } else {
                localStorage.removeItem("profile_completed");
            }

            if (response.data.role_id === 1) {
                navigate("/dashboard");
            } else if (response.data.role_id === 3) {
                if (
                    response.data.must_change_password ||
                    response.data.profile_completed === false
                ) {
                    navigate("/guard/setup");
                } else {
                    navigate(getHomeRoute());
                }
            } else if (
                response.data.must_change_password &&
                response.data.role_id === 4
            ) {
                navigate("/setup-profile");
            } else if (
                response.data.role_id === 2 &&
                (response.data.must_change_password ||
                    response.data.profile_completed === false)
            ) {
                navigate("/portal/setup");
            } else {
                navigate(getHomeRoute());
            }

        } catch (err) {
            setError(formatLoginError(err));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="login-card app-card">
                <div className="login-card-header">
                    <div className="login-logo">🏢</div>
                    <h3 className="mb-1">Society Management</h3>
                    <p className="text-muted mb-0 small">
                        Sign in with your mobile number
                    </p>
                </div>

                <div className="login-card-body">
                    {error && (
                        <div className="alert alert-danger py-2">{error}</div>
                    )}

                    <form onSubmit={login}>
                        <div className="mb-3">
                            <label className="form-label">Mobile Number</label>
                            <input
                                type="tel"
                                className="form-control"
                                placeholder="10-digit mobile"
                                value={phoneNumber}
                                onChange={(e) =>
                                    setPhoneNumber(e.target.value)
                                }
                                inputMode="numeric"
                                autoComplete="username"
                                maxLength={10}
                                required
                            />
                        </div>

                        <div className="mb-4">
                            <label className="form-label">Password</label>
                            <input
                                type="password"
                                className="form-control"
                                placeholder="Enter password"
                                value={password}
                                onChange={(e) =>
                                    setPassword(e.target.value)
                                }
                                autoComplete="current-password"
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            className="btn btn-primary w-100 py-2"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <span
                                        className="spinner-border spinner-border-sm me-2"
                                        role="status"
                                    />
                                    Signing in...
                                </>
                            ) : (
                                "Sign In"
                            )}
                        </button>
                    </form>

                    <details className="mt-4">
                        <summary className="text-muted small">
                            First-time login help
                        </summary>
                        <small className="text-muted d-block mt-2">
                            Admin: 9999999999 / Admin@123
                            <br />
                            Secretary default: MyGaSec
                            <br />
                            Guard default: MyGaGUA
                            <br />
                            Resident: MyGa + flat number (e.g. MyGa119)
                        </small>
                    </details>
                </div>
            </div>
        </div>
    );
}

export default Login;
