import { useEffect, useState } from "react";
import PortalLayout from "../../components/PortalLayout/PortalLayout";
import api from "../../services/api";
import { getResidentId } from "../../utils/auth";

const emptyForm = {
    subject: "",
    description: ""
};

function PortalComplaints() {

    const [complaints, setComplaints] = useState([]);
    const [form, setForm] = useState(emptyForm);
    const [showForm, setShowForm] = useState(false);

    useEffect(() => {
        loadComplaints();
    }, []);

    const loadComplaints = async () => {
        const response = await api.get("/portal/complaints");
        setComplaints(response.data);
    };

    const submitComplaint = async (event) => {

        event.preventDefault();

        await api.post("/portal/complaints", {
            ...form,
            resident_id: getResidentId()
        });

        setForm(emptyForm);
        setShowForm(false);
        loadComplaints();
    };

    return (
        <PortalLayout>
            <div className="d-flex justify-content-between mb-3">
                <h2>My Complaints</h2>
                <button
                    className="btn btn-primary"
                    onClick={() => setShowForm(!showForm)}
                >
                    {showForm ? "Cancel" : "New Complaint"}
                </button>
            </div>

            {showForm && (
                <div className="card mb-4">
                    <div className="card-body">
                        <form onSubmit={submitComplaint}>
                            <input
                                className="form-control mb-2"
                                placeholder="Subject"
                                value={form.subject}
                                onChange={(e) =>
                                    setForm({
                                        ...form,
                                        subject: e.target.value
                                    })
                                }
                                required
                            />
                            <textarea
                                className="form-control mb-2"
                                rows="3"
                                placeholder="Description"
                                value={form.description}
                                onChange={(e) =>
                                    setForm({
                                        ...form,
                                        description: e.target.value
                                    })
                                }
                                required
                            />
                            <button
                                type="submit"
                                className="btn btn-success"
                            >
                                Submit
                            </button>
                        </form>
                    </div>
                </div>
            )}

            <table className="table table-bordered">
                <thead>
                    <tr>
                        <th>Subject</th>
                        <th>Description</th>
                        <th>Status</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    {complaints.map((c) => (
                        <tr key={c.complaint_id}>
                            <td>{c.subject}</td>
                            <td>{c.description}</td>
                            <td>{c.status}</td>
                            <td>{c.created_date}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </PortalLayout>
    );
}

export default PortalComplaints;
