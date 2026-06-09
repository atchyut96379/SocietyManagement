import { useEffect, useState } from "react";
import Layout from "../../components/Layout/Layout";
import api from "../../services/api";

const emptyForm = {
    title: "",
    description: ""
};

function Notices() {

    const [notices, setNotices] = useState([]);
    const [form, setForm] = useState(emptyForm);
    const [showForm, setShowForm] = useState(false);

    useEffect(() => {
        loadNotices();
    }, []);

    const loadNotices = async () => {

        try {

            const response =
                await api.get("/notice");

            setNotices(response.data);

        } catch {

            alert(
                "Unable to load notices"
            );
        }
    };

    const addNotice = async (event) => {

        event.preventDefault();

        try {

            await api.post("/notice", form);
            setForm(emptyForm);
            setShowForm(false);
            loadNotices();

        } catch {

            alert("Unable to post notice");
        }
    };

    const removeNotice = async (id) => {

        if (!window.confirm("Delete this notice?")) {
            return;
        }

        try {

            await api.delete(`/notice/${id}`);
            loadNotices();

        } catch {

            alert("Unable to delete notice");
        }
    };

    return (

        <Layout>

            <div className="d-flex justify-content-between align-items-center mb-3">
                <h2>Notice Board</h2>

                <button
                    className="btn btn-primary"
                    onClick={() => setShowForm(!showForm)}
                >
                    {showForm ? "Cancel" : "Post Notice"}
                </button>
            </div>

            {showForm && (

                <div className="card mb-4">
                    <div className="card-body">

                        <form onSubmit={addNotice}>

                            <div className="mb-3">
                                <input
                                    className="form-control"
                                    placeholder="Title"
                                    value={form.title}
                                    onChange={(e) =>
                                        setForm({
                                            ...form,
                                            title: e.target.value
                                        })
                                    }
                                    required
                                />
                            </div>

                            <div className="mb-3">
                                <textarea
                                    className="form-control"
                                    rows="4"
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

                            <button
                                type="submit"
                                className="btn btn-success"
                            >
                                Publish
                            </button>

                        </form>

                    </div>
                </div>
            )}

            {
                notices.map((notice) => (

                    <div
                        key={notice.notice_id}
                        className="card mb-3"
                    >

                        <div className="card-body">

                            <div className="d-flex justify-content-between">
                                <h4>{notice.title}</h4>
                                <button
                                    className="btn btn-danger btn-sm"
                                    onClick={() =>
                                        removeNotice(
                                            notice.notice_id
                                        )
                                    }
                                >
                                    Delete
                                </button>
                            </div>

                            <small className="text-muted">
                                {notice.created_date}
                            </small>

                            <hr />

                            <p>{notice.description}</p>

                        </div>

                    </div>

                ))
            }

        </Layout>
    );
}

export default Notices;
