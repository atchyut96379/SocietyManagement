import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";

function PortalProfileSetup() {

    const navigate = useNavigate();
    const [profile, setProfile] = useState(null);
    const [form, setForm] = useState({
        owner_name: "",
        phone_number: "",
        car_number: "",
        bike_number: "",
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

            const response = await api.get("/portal/profile");

            if (response.data.profile_completed) {
                navigate("/portal");
                return;
            }

            setProfile(response.data);
            setForm((prev) => ({
                ...prev,
                phone_number: response.data.phone_number || ""
            }));

        } catch {
            setError("Unable to load profile");
        }
    };

    const submit = async (event) => {

        event.preventDefault();
        setError("");

        if (form.new_password !== form.confirm_password) {
            setError("Passwords do not match");
            return;
        }

        setLoading(true);

        try {

            const response = await api.post("/portal/profile/complete", {
                owner_name: profile?.resident_type === "Tenant"
                    ? form.owner_name
                    : null,
                phone_number: form.phone_number,
                car_number: form.car_number || null,
                bike_number: form.bike_number || null,
                new_password: form.new_password
            });

            if (!response.data.success) {
                setError(response.data.message);
                return;
            }

            localStorage.removeItem("must_change_password");
            localStorage.removeItem("profile_completed");
            navigate("/portal");

        } catch (err) {

            setError(
                err.response?.data?.message ||
                "Unable to complete profile"
            );

        } finally {
            setLoading(false);
        }
    };

    if (!profile) {
        return (
            <div className="container mt-5">
                <p>{error || "Loading profile..."}</p>
            </div>
        );
    }

    return (
        <div className="container mt-5">
            <div className="row justify-content-center">
                <div className="col-md-6">
                    <div className="card shadow">
                        <div className="card-header">
                            <h4 className="mb-0">Complete Your Profile</h4>
                        </div>
                        <div className="card-body">
                            <p className="text-muted">
                                Flat <strong>{profile.flat_number}</strong>
                                {" "}· {profile.resident_type}
                            </p>

                            {error && (
                                <div className="alert alert-danger">{error}</div>
                            )}

                            <form onSubmit={submit}>
                                {profile.resident_type === "Tenant" && (
                                    <div className="mb-3">
                                        <label className="form-label">
                                            Owner Name *
                                        </label>
                                        <input
                                            className="form-control"
                                            value={form.owner_name}
                                            onChange={(e) =>
                                                setForm({
                                                    ...form,
                                                    owner_name: e.target.value
                                                })
                                            }
                                            required
                                        />
                                    </div>
                                )}

                                <div className="mb-3">
                                    <label className="form-label">
                                        Phone Number *
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

                                <div className="mb-3">
                                    <label className="form-label">
                                        Car Number (optional)
                                    </label>
                                    <input
                                        className="form-control"
                                        value={form.car_number}
                                        onChange={(e) =>
                                            setForm({
                                                ...form,
                                                car_number: e.target.value
                                            })
                                        }
                                    />
                                </div>

                                <div className="mb-3">
                                    <label className="form-label">
                                        Bike Number (optional)
                                    </label>
                                    <input
                                        className="form-control"
                                        value={form.bike_number}
                                        onChange={(e) =>
                                            setForm({
                                                ...form,
                                                bike_number: e.target.value
                                            })
                                        }
                                    />
                                </div>

                                <div className="mb-3">
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
                                                new_password: e.target.value
                                            })
                                        }
                                        required
                                    />
                                </div>

                                <div className="mb-3">
                                    <label className="form-label">
                                        Confirm Password *
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
        </div>
    );
}

export default PortalProfileSetup;
