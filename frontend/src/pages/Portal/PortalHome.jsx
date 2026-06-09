import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import PortalLayout from "../../components/PortalLayout/PortalLayout";
import api from "../../services/api";
import LoadingState from "../../components/ui/LoadingState";

function PortalHome() {

    const [profile, setProfile] = useState(null);

    useEffect(() => {
        loadProfile();
    }, []);

    const loadProfile = async () => {
        try {
            const response = await api.get("/portal/profile");
            setProfile(response.data);
        } catch {
            setProfile(null);
        }
    };

    if (!profile) {
        return (
            <PortalLayout>
                <LoadingState message="Loading your profile..." />
            </PortalLayout>
        );
    }

    return (
        <PortalLayout>
            <div className="app-card card mb-4">
                <div className="card-body p-4">
                    <h2 className="mb-1">Welcome, {profile.full_name}</h2>
                    <p className="text-muted mb-0">
                        {profile.tower_name} · Flat {profile.flat_number}
                        {profile.committee_role &&
                        profile.committee_role !== "None"
                            ? ` · ${profile.committee_role}`
                            : ""}
                    </p>
                </div>
            </div>

            <div className="row g-3">
                <div className="col-md-6 col-lg-3">
                    <div className="stat-card stat-card--primary">
                        <h6>My Flat</h6>
                        <p className="stat-value">{profile.flat_number}</p>
                    </div>
                </div>
                <div className="col-md-6 col-lg-3">
                    <div className="stat-card stat-card--success">
                        <h6>Quick Link</h6>
                        <p className="stat-value" style={{ fontSize: "1rem" }}>
                            <Link to="/portal/dues" className="text-decoration-none">
                                Pay Dues →
                            </Link>
                        </p>
                    </div>
                </div>
                <div className="col-md-6 col-lg-3">
                    <div className="stat-card stat-card--warning">
                        <h6>Visitors</h6>
                        <p className="stat-value" style={{ fontSize: "1rem" }}>
                            <Link
                                to="/portal/visitors"
                                className="text-decoration-none"
                            >
                                Register →
                            </Link>
                        </p>
                    </div>
                </div>
                <div className="col-md-6 col-lg-3">
                    <div className="stat-card stat-card--primary">
                        <h6>Monthly Reports</h6>
                        <p className="stat-value" style={{ fontSize: "1rem" }}>
                            <Link
                                to="/portal/reports"
                                className="text-decoration-none"
                            >
                                View & Download →
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </PortalLayout>
    );
}

export default PortalHome;
