import { useEffect, useState } from "react";
import Layout from "../../components/Layout/Layout";
import api from "../../services/api";

const emptyForm = {
    resident_id: "",
    subject: "",
    description: ""
};

function Complaints() {

    const [complaints, setComplaints] = useState([]);
    const [residents, setResidents] = useState([]);
    const [form, setForm] = useState(emptyForm);
    const [showForm, setShowForm] = useState(false);

    useEffect(() => {
        loadComplaints();
        loadResidents();
    }, []);

    const loadComplaints = async () => {

        try {

            const response =
                await api.get("/complaint");

            setComplaints(response.data);

        } catch {

            alert(
                "Unable to load complaints"
            );
        }
    };

    const loadResidents = async () => {

        try {

            const response =
                await api.get("/resident");

            setResidents(response.data);

        } catch {
            // optional
        }
    };

    const addComplaint = async (event) => {

        event.preventDefault();

        try {

            await api.post("/complaint", {
                ...form,
                resident_id: Number(form.resident_id)
            });

            setForm(emptyForm);
            setShowForm(false);
            loadComplaints();

        } catch {

            alert("Unable to submit complaint");
        }
    };

    const resolveComplaint = async (id) => {

        try {

            await api.put(
                `/complaint/${id}/Resolved`
            );

            loadComplaints();

        } catch {

            alert(
                "Unable to update complaint"
            );
        }
    };

    return (

        <Layout>

            <div className="d-flex justify-content-between align-items-center mb-3">
                <h2>Complaints</h2>

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

                        <form onSubmit={addComplaint}>

                            <div className="row g-3">

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
                                </div>

                                <div className="col-md-4">
                                    <input
                                        className="form-control"
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
                                </div>

                                <div className="col-md-2">
                                    <button
                                        type="submit"
                                        className="btn btn-success w-100"
                                    >
                                        Submit
                                    </button>
                                </div>

                            </div>

                        </form>

                    </div>
                </div>
            )}

            <table className="table table-bordered table-hover">

                <thead className="table-light">

                    <tr>
                        <th>ID</th>
                        <th>Resident</th>
                        <th>Subject</th>
                        <th>Description</th>
                        <th>Status</th>
                        <th>Date</th>
                        <th>Action</th>
                    </tr>

                </thead>

                <tbody>

                    {
                        complaints.map((c) => (

                            <tr key={c.complaint_id}>

                                <td>{c.complaint_id}</td>
                                <td>
                                    {c.resident_name} ({c.flat_number})
                                </td>
                                <td>{c.subject}</td>
                                <td>{c.description}</td>
                                <td>{c.status}</td>
                                <td>{c.created_date}</td>

                                <td>

                                    {c.status !== "Resolved" &&

                                        <button
                                            className="btn btn-success btn-sm"
                                            onClick={() =>
                                                resolveComplaint(
                                                    c.complaint_id
                                                )
                                            }
                                        >
                                            Resolve
                                        </button>
                                    }

                                </td>

                            </tr>

                        ))
                    }

                </tbody>

            </table>

        </Layout>
    );
}

export default Complaints;
