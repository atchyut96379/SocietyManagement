import { useEffect, useState } from "react";
import api from "../../services/api";
import SidebarNav from "../ui/SidebarNav";
import {
    getRoleLabel,
    isResident,
    setCommitteeRole
} from "../../utils/auth";

const PORTAL_ITEMS = [
    { to: "/portal", label: "Home", end: true, icon: "🏠" },
    { to: "/portal/notices", label: "Notices", icon: "📢" },
    { to: "/portal/complaints", label: "My Complaints", icon: "📋" },
    { to: "/portal/visitors", label: "My Visitors", icon: "🚶" },
    { to: "/portal/dues", label: "My Dues", icon: "🧾" },
    { to: "/portal/reports", label: "Monthly Reports", icon: "📊" }
];

function PortalSidebar() {

    const [portalLabel, setPortalLabel] = useState("Resident Portal");

    useEffect(() => {
        if (!isResident()) {
            return;
        }

        api.get("/portal/profile")
            .then((response) => {
                setCommitteeRole(response.data?.committee_role);
                const role = getRoleLabel();
                setPortalLabel(
                    role === "Resident"
                        ? "Resident Portal"
                        : `${role} · Portal`
                );
            })
            .catch(() => {
                setPortalLabel("Resident Portal");
            });
    }, []);

    return (
        <aside className="app-sidebar app-sidebar--resident">
            <div className="app-sidebar-brand">
                <h3>My Flat</h3>
                <small>{portalLabel}</small>
            </div>
            <SidebarNav items={PORTAL_ITEMS} />
        </aside>
    );
}

export default PortalSidebar;
