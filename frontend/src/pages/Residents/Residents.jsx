import { useEffect, useState } from "react";
import Layout from "../../components/Layout/Layout";
import PageHeader from "../../components/ui/PageHeader";
import api from "../../services/api";

const emptyForm = {
    flat_id: "",
    full_name: "",
    phone_number: "",
    email: "",
    resident_type: "Owner",
    committee_role: "None",
    role: ""
};

const SYSTEM_ROLES = ["Admin", "Secretary", "Security"];

function roleLabel(resident) {
    if (resident.role && SYSTEM_ROLES.includes(resident.role)) {
        return resident.role;
    }
    if (
        resident.login_role &&
        SYSTEM_ROLES.includes(resident.login_role)
    ) {
        return resident.login_role;
    }
    if (resident.role) {
        return resident.role;
    }
    if (
        resident.committee_role &&
        resident.committee_role !== "None"
    ) {
        return resident.committee_role;
    }
    if (resident.login_role) {
        return resident.login_role;
    }
    return "Resident";
}

function formatApiError(err, fallback) {
    const data = err.response?.data;
    if (data?.message) return data.message;
    if (data?.detail) {
        if (Array.isArray(data.detail)) {
            return data.detail.map((d) => d.msg).join(". ");
        }
        return String(data.detail);
    }
    return fallback;
}

function Residents() {

    const [residents, setResidents] = useState([]);
    const [availableFlats, setAvailableFlats] = useState([]);
    const [committeeRoles, setCommitteeRoles] = useState([
        { value: "None", label: "Resident" }
    ]);
    const [form, setForm] = useState(emptyForm);
    const [showForm, setShowForm] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [search, setSearch] = useState("");

    useEffect(() => {
        loadResidents();
        loadAvailableFlats();
    }, []);

    const loadResidents = async () => {

        try {

            const response = await api.get("/resident");
            setResidents(response.data);

        } catch {

            alert("Unable to load residents");
        }
    };

    const loadAvailableFlats = async () => {

        try {

            const response = await api.get("/flat/available");
            setAvailableFlats(response.data);

        } catch {
            setAvailableFlats([]);
        }
    };

    const loadCommitteeRoles = async (residentId = null) => {

        try {

            const params = residentId
                ? { editing_resident_id: residentId }
                : {};

            const response = await api.get(
                "/resident/available-committee-roles",
                { params }
            );

            setCommitteeRoles(response.data);

            const available = response.data.map((r) => r.value);
            if (!available.includes(form.committee_role)) {
                setForm((prev) => ({
                    ...prev,
                    committee_role: "None"
                }));
            }

        } catch {
            setCommitteeRoles([{ value: "None", label: "Resident" }]);
        }
    };

    const handleChange = (field, value) => {
        setForm({ ...form, [field]: value });
    };

    const resetForm = () => {
        setForm(emptyForm);
        setEditingId(null);
        setShowForm(false);
    };

    const startEdit = (resident) => {
        setForm({
            flat_id: resident.flat_id || "",
            full_name: resident.full_name,
            phone_number: resident.phone_number,
            email: resident.email || "",
            resident_type: resident.resident_type ||
                (resident.is_owner ? "Owner" : "Tenant"),
            committee_role: resident.committee_role || "None",
            role: roleLabel(resident)
        });
        setEditingId(resident.resident_id);
        setShowForm(true);
        loadCommitteeRoles(resident.resident_id);
    };

    const openAddForm = () => {
        setEditingId(null);
        setForm(emptyForm);
        setShowForm(true);
        loadCommitteeRoles();
        loadAvailableFlats();
    };

    const buildPayload = () => {
        const payload = {
            full_name: form.full_name.trim(),
            phone_number: form.phone_number.trim(),
            resident_type: form.resident_type,
            committee_role: form.committee_role
        };

        if (form.email?.trim()) {
            payload.email = form.email.trim();
        }

        if (!editingId) {
            payload.flat_id = Number(form.flat_id);
        }

        return payload;
    };

    const saveResident = async (event) => {

        event.preventDefault();

        try {

            if (editingId) {
                const response = await api.put(
                    `/resident/${editingId}`,
                    buildPayload()
                );

                if (response.data.success === false) {
                    alert(response.data.message);
                    return;
                }
            } else {
                const response = await api.post(
                    "/resident",
                    buildPayload()
                );

                if (response.data.success === false) {
                    alert(response.data.message);
                    return;
                }

                if (response.data.password) {
                    alert(
                        "Resident and login created!\n\n" +
                        `Mobile: ${response.data.phone_number}\n` +
                        `Password: ${response.data.password}\n\n` +
                        "Share these with the resident."
                    );
                }
            }

            resetForm();
            loadResidents();
            loadAvailableFlats();
            loadCommitteeRoles();

        } catch (err) {

            alert(
                formatApiError(
                    err,
                    editingId
                        ? "Unable to update resident"
                        : "Unable to add resident"
                )
            );
        }
    };

    const removeResident = async (id) => {

        if (!window.confirm("Delete this resident?")) {
            return;
        }

        try {

            await api.delete(`/resident/${id}`);
            loadResidents();
            loadAvailableFlats();

        } catch {

            alert("Unable to delete resident");
        }
    };

    const filtered = residents.filter((r) => {

        const term = search.toLowerCase();

        return (
            r.full_name.toLowerCase().includes(term) ||
            (r.flat_number || "").toLowerCase().includes(term) ||
            (r.email || "").toLowerCase().includes(term) ||
            roleLabel(r).toLowerCase().includes(term)
        );
    });

    const isSystemRole = (role) => SYSTEM_ROLES.includes(role);

    return (

        <Layout>

            <PageHeader
                title="Residents"
                subtitle="Manage flat owners, tenants, and committee roles"
            >
                <button
                    className="btn btn-primary"
                    onClick={() => {
                        if (showForm) {
                            resetForm();
                        } else {
                            openAddForm();
                        }
                    }}
                >
                    {showForm ? "Cancel" : "Add Resident"}
                </button>
            </PageHeader>

            <input
                className="form-control mb-3 app-card"
                style={{ border: "none", padding: "0.75rem 1rem" }}
                placeholder="Search by name, flat, email, or role"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
            />

            {showForm && (

                <div className="form-section-card card mb-4">
                    <div className="card-header">
                        {editingId ? "Edit Resident" : "Add Resident + Login"}
                    </div>
                    <div className="card-body">

                        <form
                            className="row g-3"
                            onSubmit={saveResident}
                        >

                            <div className="col-md-3">
                                <input
                                    className="form-control"
                                    placeholder="Full Name *"
                                    value={form.full_name}
                                    onChange={(e) =>
                                        handleChange(
                                            "full_name",
                                            e.target.value
                                        )
                                    }
                                    required
                                />
                            </div>

                            {!editingId && (
                                <div className="col-md-2">
                                    <select
                                        className="form-select"
                                        value={form.flat_id}
                                        onChange={(e) =>
                                            handleChange(
                                                "flat_id",
                                                e.target.value
                                            )
                                        }
                                        required
                                    >
                                        <option value="">
                                            Select Flat *
                                        </option>
                                        {availableFlats.map((flat) => (
                                            <option
                                                key={flat.flat_id}
                                                value={flat.flat_id}
                                            >
                                                {flat.flat_number}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            )}

                            <div className="col-md-2">
                                <input
                                    type="tel"
                                    className="form-control"
                                    placeholder="Mobile *"
                                    value={form.phone_number}
                                    onChange={(e) =>
                                        handleChange(
                                            "phone_number",
                                            e.target.value
                                        )
                                    }
                                    required
                                />
                            </div>

                            <div className="col-md-2">
                                <input
                                    type="text"
                                    className="form-control"
                                    placeholder="Email (optional)"
                                    value={form.email}
                                    onChange={(e) =>
                                        handleChange(
                                            "email",
                                            e.target.value
                                        )
                                    }
                                />
                            </div>

                            <div className="col-md-2">
                                <select
                                    className="form-select"
                                    value={form.resident_type}
                                    onChange={(e) =>
                                        handleChange(
                                            "resident_type",
                                            e.target.value
                                        )
                                    }
                                >
                                    <option value="Owner">Owner</option>
                                    <option value="Tenant">Tenant</option>
                                </select>
                            </div>

                            {editingId && isSystemRole(form.role) ? (
                                <div className="col-md-2">
                                    <input
                                        className="form-control"
                                        value={form.role}
                                        readOnly
                                        title="System role (Admin creates Secretary; cannot change here)"
                                    />
                                    <small className="text-muted">Role</small>
                                </div>
                            ) : (
                                <div className="col-md-2">
                                    <select
                                        className="form-select"
                                        value={form.committee_role}
                                        onChange={(e) =>
                                            handleChange(
                                                "committee_role",
                                                e.target.value
                                            )
                                        }
                                    >
                                        {committeeRoles.map((role) => (
                                            <option
                                                key={role.value}
                                                value={role.value}
                                            >
                                                {role.label}
                                            </option>
                                        ))}
                                    </select>
                                    <small className="text-muted">Role</small>
                                </div>
                            )}

                            <div className="col-md-1">
                                <button
                                    type="submit"
                                    className="btn btn-success w-100"
                                >
                                    {editingId ? "Update" : "Save"}
                                </button>
                            </div>

                        </form>

                        {!editingId && (
                            <small className="text-muted d-block mt-2">
                                Login is auto-created. Password uses flat number
                                (e.g. MyGa119) or committee role code.
                                Secretary is created by Admin only — not listed here.
                                Assigned committee roles disappear from this list.
                            </small>
                        )}

                    </div>
                </div>
            )}

            <div className="table-app table-responsive">
            <table className="table table-hover align-middle">

                <thead>

                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Flat</th>
                        <th>Mobile</th>
                        <th>Email</th>
                        <th>Type</th>
                        <th>Role</th>
                        <th>Actions</th>
                    </tr>

                </thead>

                <tbody>

                    {
                        filtered.map((r) => (

                            <tr key={r.resident_id}>

                                <td>{r.resident_id}</td>
                                <td>{r.full_name}</td>
                                <td>{r.flat_number}</td>
                                <td>{r.phone_number}</td>
                                <td>{r.email || "-"}</td>
                                <td>
                                    {r.resident_type ||
                                        (r.is_owner ? "Owner" : "Tenant")}
                                </td>
                                <td>{roleLabel(r)}</td>
                                <td>
                                    <button
                                        className="btn btn-warning btn-sm me-2"
                                        onClick={() => startEdit(r)}
                                    >
                                        Edit
                                    </button>
                                    <button
                                        className="btn btn-danger btn-sm"
                                        onClick={() =>
                                            removeResident(
                                                r.resident_id
                                            )
                                        }
                                    >
                                        Delete
                                    </button>
                                </td>

                            </tr>

                        ))
                    }

                </tbody>

            </table>
            </div>

        </Layout>
    );
}

export default Residents;
