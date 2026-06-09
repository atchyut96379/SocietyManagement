import { useEffect, useState } from "react";
import GuardLayout from "../../components/GuardLayout/GuardLayout";
import PageHeader from "../../components/ui/PageHeader";
import LoadingState from "../../components/ui/LoadingState";
import EmptyState from "../../components/ui/EmptyState";
import StatusBadge from "../../components/ui/StatusBadge";
import api from "../../services/api";

function GuardVisitorLog() {

    const [visitors, setVisitors] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState("all");

    useEffect(() => {
        loadVisitors();
    }, []);

    const loadVisitors = async () => {

        setLoading(true);

        try {

            const response = await api.get("/visitor");
            setVisitors(response.data);

        } catch {

            alert("Unable to load visitor log");

        } finally {
            setLoading(false);
        }
    };

    const markExit = async (id) => {

        if (!window.confirm("Record visitor exit?")) {
            return;
        }

        await api.post(`/visitor/${id}/exit`);
        loadVisitors();
    };

    const filtered = visitors.filter((v) => {
        if (filter === "active") {
            return v.status === "Pending" || v.status === "Approved";
        }
        return true;
    });

    return (
        <GuardLayout>
            <PageHeader
                title="Visitor Log"
                subtitle="Full history with entry and exit times"
            >
                <select
                    className="form-select form-select-sm"
                    style={{ width: "140px" }}
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                >
                    <option value="all">All Visitors</option>
                    <option value="active">Active Only</option>
                </select>
                <button
                    type="button"
                    className="btn btn-outline-primary btn-sm"
                    onClick={loadVisitors}
                >
                    Refresh
                </button>
            </PageHeader>

            {loading ? (
                <LoadingState />
            ) : (
                <div className="table-app table-responsive">
                <table className="table table-hover align-middle">
                    <thead>
                        <tr>
                            <th>Code</th>
                            <th>Visitor</th>
                            <th>Mobile</th>
                            <th>Flat</th>
                            <th>Resident</th>
                            <th>Purpose</th>
                            <th>Status</th>
                            <th>Entry Time</th>
                            <th>Exit Time</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filtered.length === 0 && (
                            <tr>
                                <td colSpan={10}>
                                    <EmptyState message="No visitors found" />
                                </td>
                            </tr>
                        )}

                        {filtered.map((v) => (
                            <tr key={v.visitor_id}>
                                <td>
                                    <strong>{v.entry_code || "-"}</strong>
                                </td>
                                <td>{v.visitor_name}</td>
                                <td>{v.mobile_number}</td>
                                <td>{v.flat_number}</td>
                                <td>{v.resident_name}</td>
                                <td>{v.purpose}</td>
                                <td>
                                    <StatusBadge status={v.status} />
                                </td>
                                <td>{v.entry_time || "-"}</td>
                                <td>{v.exit_time || "-"}</td>
                                <td>
                                    {v.status === "Approved" && (
                                        <button
                                            className="btn btn-danger btn-sm"
                                            onClick={() =>
                                                markExit(v.visitor_id)
                                            }
                                        >
                                            Record Exit
                                        </button>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                </div>
            )}
        </GuardLayout>
    );
}

export default GuardVisitorLog;
