import { useEffect, useState } from "react";
import PortalLayout from "../../components/PortalLayout/PortalLayout";
import PageHeader from "../../components/ui/PageHeader";
import EntryCodeBanner from "../../components/ui/EntryCodeBanner";
import api from "../../services/api";

const emptyForm = {
    visitor_name: "",
    mobile_number: "",
    purpose: ""
};

function PortalVisitors() {

    const [visitors, setVisitors] = useState([]);
    const [form, setForm] = useState(emptyForm);
    const [showForm, setShowForm] = useState(false);
    const [lastCode, setLastCode] = useState(null);

    useEffect(() => {
        loadVisitors();
    }, []);

    const loadVisitors = async () => {

        try {

            const response = await api.get("/visitor/my");
            setVisitors(response.data);

        } catch (err) {

            alert(
                err.response?.data?.detail ||
                err.response?.data?.message ||
                "Unable to load your visitors"
            );
        }
    };

    const registerVisitor = async (event) => {

        event.preventDefault();

        try {

            const response = await api.post("/visitor/my", form);

            setLastCode({
                code: response.data.entry_code,
                validUntil: response.data.valid_until,
                visitorName: form.visitor_name
            });

            setForm(emptyForm);
            setShowForm(false);
            loadVisitors();

        } catch (err) {

            alert(
                err.response?.data?.detail ||
                err.response?.data?.message ||
                "Unable to register visitor"
            );
        }
    };

    const copyCode = (code) => {
        navigator.clipboard.writeText(code);
        alert(
            `Entry code ${code} copied.\n\n` +
            "Share this with security at the gate."
        );
    };

    return (
        <PortalLayout>
            <PageHeader
                title="My Visitors"
                subtitle="Register visitors and share the entry code with security"
            >
                <button
                    type="button"
                    className="btn btn-primary"
                    onClick={() => setShowForm(!showForm)}
                >
                    {showForm ? "Cancel" : "Register Visitor"}
                </button>
            </PageHeader>

            {lastCode && (
                <EntryCodeBanner
                    code={lastCode.code}
                    validUntil={lastCode.validUntil}
                    visitorName={lastCode.visitorName}
                    onCopy={copyCode}
                />
            )}

            {showForm && (
                <div className="card mb-4">
                    <div className="card-body">
                        <form
                            className="row g-3"
                            onSubmit={registerVisitor}
                        >
                            <div className="col-md-4">
                                <input
                                    className="form-control"
                                    placeholder="Visitor Name *"
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

                            <div className="col-md-3">
                                <input
                                    className="form-control"
                                    placeholder="Visitor Mobile *"
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

                            <div className="col-md-4">
                                <input
                                    className="form-control"
                                    placeholder="Purpose *"
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
                        <th>Code</th>
                        <th>Name</th>
                        <th>Mobile</th>
                        <th>Purpose</th>
                        <th>Status</th>
                        <th>Valid Until</th>
                    </tr>
                </thead>

                <tbody>
                    {visitors.map((v) => (
                        <tr key={v.visitor_id}>
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
                            <td>{v.purpose}</td>
                            <td>{v.status}</td>
                            <td>{v.valid_until || "-"}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </PortalLayout>
    );
}

export default PortalVisitors;
