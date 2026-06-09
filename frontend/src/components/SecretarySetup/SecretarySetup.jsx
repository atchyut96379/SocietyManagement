import { useEffect, useState } from "react";
import api from "../../services/api";
import { isAdmin } from "../../utils/auth";

function SecretarySetup() {

    const [status, setStatus] = useState({ exists: false });
    const [form, setForm] = useState({
        full_name: "",
        email: "",
        phone_number: ""
    });
    const [message, setMessage] = useState("");
    const [createdCredentials, setCreatedCredentials] = useState(null);

    useEffect(() => {
        if (isAdmin()) {
            loadStatus();
        }
    }, []);

    const loadStatus = async () => {

        try {

            const response = await api.get("/admin/secretary");
            setStatus(response.data || { exists: false });

        } catch {

            setStatus({ exists: false });
            setMessage(
                "Unable to load secretary status. Is the backend running?"
            );
        }
    };

    const createSecretary = async (event) => {

        event.preventDefault();
        setMessage("");
        setCreatedCredentials(null);

        try {

            const payload = {
                full_name: form.full_name,
                phone_number: form.phone_number
            };

            if (form.email.trim()) {
                payload.email = form.email.trim();
            }

            const response = await api.post(
                "/admin/secretary",
                payload
            );

            setMessage(response.data.message);

            if (response.data.success) {
                setCreatedCredentials({
                    phone_number: response.data.phone_number,
                    password: response.data.password
                });
                setForm({
                    full_name: "",
                    email: "",
                    phone_number: ""
                });
                loadStatus();
            }

        } catch {

            setMessage("Unable to create secretary account");
        }
    };

    const deleteSecretary = async () => {

        if (!window.confirm(
            "Delete the current secretary account? Admin can create a new one after this."
        )) {
            return;
        }

        try {

            const response = await api.delete("/admin/secretary");
            setMessage(response.data.message);
            setCreatedCredentials(null);
            loadStatus();

        } catch {

            setMessage("Unable to delete secretary account");
        }
    };

    if (!isAdmin()) {
        return null;
    }

    return (
        <div className="card mb-4 border-warning">
            <div className="card-header bg-warning">
                Secretary Account (Admin Only)
            </div>
            <div className="card-body">

                <p className="text-muted">
                    Admin can only create or replace the secretary account.
                    Password is auto-generated (e.g. MyGaSec).
                </p>

                {status.exists ? (
                    <div>
                        <div className="alert alert-success">
                            Secretary:
                            <strong> {status.full_name}</strong>
                            {" "}| Mobile: <strong>{status.phone_number}</strong>
                            {status.email && (
                                <> | Email: {status.email}</>
                            )}
                        </div>
                        <button
                            type="button"
                            className="btn btn-outline-danger btn-sm"
                            onClick={deleteSecretary}
                        >
                            Delete Secretary
                        </button>
                    </div>
                ) : (
                    <form
                        className="row g-3"
                        onSubmit={createSecretary}
                    >
                        <div className="col-md-4">
                            <input
                                className="form-control"
                                placeholder="Full Name"
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
                        <div className="col-md-3">
                            <input
                                type="tel"
                                className="form-control"
                                placeholder="Mobile Number *"
                                value={form.phone_number}
                                onChange={(e) =>
                                    setForm({
                                        ...form,
                                        phone_number: e.target.value
                                    })
                                }
                                pattern="[0-9]{10}"
                                required
                            />
                        </div>
                        <div className="col-md-3">
                            <input
                                type="email"
                                className="form-control"
                                placeholder="Email (optional)"
                                value={form.email}
                                onChange={(e) =>
                                    setForm({
                                        ...form,
                                        email: e.target.value
                                    })
                                }
                            />
                        </div>
                        <div className="col-md-2">
                            <button
                                type="submit"
                                className="btn btn-warning w-100"
                            >
                                Create Secretary
                            </button>
                        </div>
                    </form>
                )}

                {createdCredentials && (
                    <div className="alert alert-info mt-3 mb-0">
                        <strong>Save these credentials:</strong>
                        <br />
                        Mobile: {createdCredentials.phone_number}
                        <br />
                        Password: {createdCredentials.password}
                    </div>
                )}

                {message && (
                    <small className="d-block mt-2">{message}</small>
                )}

            </div>
        </div>
    );
}

export default SecretarySetup;
