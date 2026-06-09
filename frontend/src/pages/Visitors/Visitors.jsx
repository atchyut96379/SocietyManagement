import { useEffect, useState } from "react";
import Layout from "../../components/Layout/Layout";
import HomeSummary from "../../components/HomeSummary/HomeSummary";
import PageHeader from "../../components/ui/PageHeader";
import EntryCodeBanner from "../../components/ui/EntryCodeBanner";
import api from "../../services/api";
import { isManagement } from "../../utils/auth";

const emptyForm = {
    visitor_name: "",
    mobile_number: "",
    resident_id: "",
    purpose: ""
};

const emptyGuardForm = {
    full_name: "",
    phone_number: "",
    email: ""
};

function Visitors() {

    const [visitors, setVisitors] = useState([]);
    const [residents, setResidents] = useState([]);
    const [form, setForm] = useState(emptyForm);
    const [showForm, setShowForm] = useState(false);
    const [lastCode, setLastCode] = useState(null);
    const [guardForm, setGuardForm] = useState(emptyGuardForm);
    const [showGuardForm, setShowGuardForm] = useState(false);
    const [guards, setGuards] = useState([]);

    const managementView = isManagement();

    useEffect(() => {
        loadVisitors();
        loadResidents();
        loadGuards();
    }, []);

    const loadVisitors = async () => {

        try {

            const response = await api.get("/visitor");
            setVisitors(response.data);

        } catch {

            alert("Unable to load visitors");
        }
    };

    const loadResidents = async () => {

        try {

            const response = await api.get("/resident");
            setResidents(response.data);

        } catch {
            setResidents([]);
        }
    };

    const loadGuards = async () => {

        try {

            const response = await api.get("/security-guards");
            setGuards(response.data);

        } catch {
            setGuards([]);
        }
    };

    const addVisitor = async (event) => {

        event.preventDefault();

        try {

            const response = await api.post("/visitor", {
                ...form,
                resident_id: Number(form.resident_id)
            });

            setLastCode({
                code: response.data.entry_code,
                validUntil: response.data.valid_until,
                visitorName: form.visitor_name
            });

            setForm(emptyForm);
            setShowForm(false);
            loadVisitors();

        } catch {

            alert("Unable to register visitor");
        }
    };

    const approveVisitor = async (id) => {

        await api.post(`/visitor/${id}/approve`);
        loadVisitors();
    };

    const markExit = async (id) => {

        await api.post(`/visitor/${id}/exit`);
        loadVisitors();
    };

    const createGuardAccount = async (event) => {

        event.preventDefault();

        try {

            const response = await api.post(
                "/register-security",
                guardForm
            );

            if (response.data.success === false) {
                alert(response.data.message);
                return;
            }

            alert(
                "Guard account created!\n\n" +
                `Mobile: ${response.data.phone_number}\n` +
                `Default Password: ${response.data.password}\n\n` +
                "Guard must complete profile setup on first login " +
                "(name, ID, email, new password)."
            );

            setGuardForm(emptyGuardForm);
            setShowGuardForm(false);
            loadGuards();

        } catch (err) {

            alert(
                err.response?.data?.message ||
                "Unable to create guard account"
            );
        }
    };

    const copyCode = (code) => {
        navigator.clipboard.writeText(code);
        alert(`Entry code ${code} copied. Share it with security at the gate.`);
    };

    return (

        <Layout>

            {managementView && (
                <>
                    <h2>Home</h2>
                    <div className="mb-4">
                        <HomeSummary />
                    </div>
                </>
            )}

            <PageHeader
                title="Visitors"
                subtitle="Register visitors, connect guards, and manage entry codes"
            >
                {managementView && (
                    <button
                        type="button"
                        className="btn btn-outline-secondary"
                        onClick={() => setShowGuardForm(!showGuardForm)}
                    >
                        {showGuardForm
                            ? "Cancel Guard Setup"
                            : "Add Guard Login"}
                    </button>
                )}
                {managementView && (
                    <button
                        type="button"
                        className="btn btn-primary"
                        onClick={() => setShowForm(!showForm)}
                    >
                        {showForm ? "Cancel" : "Register Visitor"}
                    </button>
                )}
            </PageHeader>

            {managementView && showGuardForm && (
                <div className="card mb-4">
                    <div className="card-body">
                        <h5>Connect Guard</h5>
                        <p className="text-muted">
                            Default password is auto-generated (e.g. MyGaGUA).
                            Guard completes profile and sets a new password
                            on first login.
                        </p>

                        <form
                            className="row g-3"
                            onSubmit={createGuardAccount}
                        >
                            <div className="col-md-3">
                                <input
                                    className="form-control"
                                    placeholder="Guard Name *"
                                    value={guardForm.full_name}
                                    onChange={(e) =>
                                        setGuardForm({
                                            ...guardForm,
                                            full_name: e.target.value
                                        })
                                    }
                                    required
                                />
                            </div>

                            <div className="col-md-2">
                                <input
                                    className="form-control"
                                    placeholder="Mobile *"
                                    value={guardForm.phone_number}
                                    onChange={(e) =>
                                        setGuardForm({
                                            ...guardForm,
                                            phone_number: e.target.value
                                        })
                                    }
                                    required
                                />
                            </div>

                            <div className="col-md-4">
                                <input
                                    className="form-control"
                                    placeholder="Email (optional)"
                                    value={guardForm.email}
                                    onChange={(e) =>
                                        setGuardForm({
                                            ...guardForm,
                                            email: e.target.value
                                        })
                                    }
                                />
                            </div>

                            <div className="col-md-3">
                                <button
                                    type="submit"
                                    className="btn btn-success w-100"
                                >
                                    Create Guard
                                </button>
                            </div>
                        </form>

                        {guards.length > 0 && (
                            <div className="mt-4">
                                <h6>Connected Guards</h6>
                                <table className="table table-sm table-bordered mb-0">
                                    <thead className="table-light">
                                        <tr>
                                            <th>Name</th>
                                            <th>Mobile</th>
                                            <th>Email</th>
                                            <th>ID</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {guards.map((guard) => (
                                            <tr key={guard.user_id}>
                                                <td>{guard.full_name}</td>
                                                <td>{guard.phone_number}</td>
                                                <td>{guard.email || "-"}</td>
                                                <td>
                                                    {guard.identity_card_type
                                                        ? `${guard.identity_card_type}: ${guard.identity_card_number || "-"}`
                                                        : "-"}
                                                </td>
                                                <td>
                                                    {guard.profile_completed
                                                        ? "Active"
                                                        : "Pending Setup"}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {lastCode && managementView && (
                <EntryCodeBanner
                    code={lastCode.code}
                    validUntil={lastCode.validUntil}
                    visitorName={lastCode.visitorName}
                    onCopy={copyCode}
                />
            )}

            {managementView && showForm && (

                <div className="card mb-4">
                    <div className="card-body">

                        <form
                            className="row g-3"
                            onSubmit={addVisitor}
                        >

                            <div className="col-md-3">
                                <input
                                    className="form-control"
                                    placeholder="Visitor Name"
                                    value={form.visitor_name}
                                    onChange={(e) =>
                                        setForm({
                                            ...form,
                                            visitor_name: e.target.value
                                        })
                                    }
                                    required
                                />
                            </div>

                            <div className="col-md-2">
                                <input
                                    className="form-control"
                                    placeholder="Mobile"
                                    value={form.mobile_number}
                                    onChange={(e) =>
                                        setForm({
                                            ...form,
                                            mobile_number: e.target.value
                                        })
                                    }
                                    required
                                />
                            </div>

                            <div className="col-md-3">
                                <select
                                    className="form-select"
                                    value={form.resident_id}
                                    onChange={(e) =>
                                        setForm({
                                            ...form,
                                            resident_id: e.target.value
                                        })
                                    }
                                    required
                                >
                                    <option value="">
                                        Select Resident
                                    </option>
                                    {residents.map((r) => (
                                        <option
                                            key={r.resident_id}
                                            value={r.resident_id}
                                        >
                                            {r.full_name} ({r.flat_number})
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="col-md-3">
                                <input
                                    className="form-control"
                                    placeholder="Purpose"
                                    value={form.purpose}
                                    onChange={(e) =>
                                        setForm({
                                            ...form,
                                            purpose: e.target.value
                                        })
                                    }
                                    required
                                />
                            </div>

                            <div className="col-md-1">
                                <button
                                    type="submit"
                                    className="btn btn-success w-100"
                                >
                                    Save
                                </button>
                            </div>

                        </form>

                    </div>
                </div>
            )}

            <table className="table table-bordered table-hover">

                <thead className="table-light">

                    <tr>
                        <th>ID</th>
                        <th>Code</th>
                        <th>Name</th>
                        <th>Mobile</th>
                        <th>Resident</th>
                        <th>Purpose</th>
                        <th>Entry</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>

                </thead>

                <tbody>

                    {
                        visitors.map((v) => (

                            <tr key={v.visitor_id}>

                                <td>{v.visitor_id}</td>
                                <td>
                                    {v.entry_code ? (
                                        <>
                                            <strong>{v.entry_code}</strong>
                                            <button
                                                type="button"
                                                className="btn btn-link btn-sm p-0 ms-1"
                                                onClick={() =>
                                                    copyCode(v.entry_code)
                                                }
                                            >
                                                Copy
                                            </button>
                                        </>
                                    ) : (
                                        "-"
                                    )}
                                </td>
                                <td>{v.visitor_name}</td>
                                <td>{v.mobile_number}</td>
                                <td>
                                    {v.resident_name} ({v.flat_number})
                                </td>
                                <td>{v.purpose}</td>
                                <td>{v.entry_time || "-"}</td>
                                <td>{v.status}</td>

                                <td>

                                    {v.status === "Pending" && (
                                        <button
                                            className="btn btn-success btn-sm me-2"
                                            onClick={() =>
                                                approveVisitor(
                                                    v.visitor_id
                                                )
                                            }
                                        >
                                            Approve
                                        </button>
                                    )}

                                    {v.status === "Approved" && (
                                        <button
                                            className="btn btn-danger btn-sm"
                                            onClick={() =>
                                                markExit(
                                                    v.visitor_id
                                                )
                                            }
                                        >
                                            Exit
                                        </button>
                                    )}

                                </td>

                            </tr>

                        ))
                    }

                </tbody>

            </table>

        </Layout>
    );
}

export default Visitors;
