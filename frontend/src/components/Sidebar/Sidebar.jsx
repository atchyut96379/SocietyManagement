import SidebarNav from "../ui/SidebarNav";
import { isAdmin, isManagement } from "../../utils/auth";

function Sidebar() {

    const items = [];

    if (isAdmin() || isManagement()) {
        items.push({
            to: "/dashboard",
            label: isAdmin() ? "Admin Panel" : "Home",
            end: true,
            icon: "🏠"
        });
    }

    if (isManagement()) {
        items.push(
            { to: "/residents", label: "Residents", icon: "👥" },
            { to: "/visitors", label: "Visitors", icon: "🚶" },
            { to: "/complaints", label: "Complaints", icon: "📋" },
            { to: "/finance", label: "Finance", icon: "💰" },
            { to: "/notices", label: "Notices", icon: "📢" },
            { to: "/my-dues", label: "My Dues", icon: "🧾" }
        );
    }

    return (
        <aside className="app-sidebar app-sidebar--management">
            <div className="app-sidebar-brand">
                <h3>Society App</h3>
                <small>Management Console</small>
            </div>
            <SidebarNav items={items} />
        </aside>
    );
}

export default Sidebar;
