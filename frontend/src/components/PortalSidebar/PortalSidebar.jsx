import SidebarNav from "../ui/SidebarNav";

const PORTAL_ITEMS = [
    { to: "/portal", label: "Home", end: true, icon: "🏠" },
    { to: "/portal/notices", label: "Notices", icon: "📢" },
    { to: "/portal/complaints", label: "My Complaints", icon: "📋" },
    { to: "/portal/visitors", label: "My Visitors", icon: "🚶" },
    { to: "/portal/dues", label: "My Dues", icon: "🧾" },
    { to: "/portal/reports", label: "Monthly Reports", icon: "📊" }
];

function PortalSidebar() {

    return (
        <aside className="app-sidebar app-sidebar--resident">
            <div className="app-sidebar-brand">
                <h3>My Flat</h3>
                <small>Resident Portal</small>
            </div>
            <SidebarNav items={PORTAL_ITEMS} />
        </aside>
    );
}

export default PortalSidebar;
