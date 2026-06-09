import { useEffect, useState } from "react";
import PortalLayout from "../../components/PortalLayout/PortalLayout";
import api from "../../services/api";

function PortalNotices() {

    const [notices, setNotices] = useState([]);

    useEffect(() => {
        api.get("/portal/notices").then((res) => {
            setNotices(res.data);
        });
    }, []);

    return (
        <PortalLayout>
            <h2>Society Notices</h2>

            {notices.map((notice) => (
                <div key={notice.notice_id} className="card mb-3">
                    <div className="card-body">
                        <h4>{notice.title}</h4>
                        <small className="text-muted">
                            {notice.created_date}
                        </small>
                        <hr />
                        <p>{notice.description}</p>
                    </div>
                </div>
            ))}
        </PortalLayout>
    );
}

export default PortalNotices;
