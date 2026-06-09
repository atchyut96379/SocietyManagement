import SidebarNav from "../ui/SidebarNav";

const GUARD_ITEMS = [
    { to: "/guard", label: "Gate Entry", end: true, icon: "🛡️" },
    { to: "/guard/log", label: "Visitor Log", icon: "📋" }
];

function GuardSidebar() {

    return (
        <aside className="app-sidebar app-sidebar--guard">
            <div className="app-sidebar-brand">
                <h3>Guard Portal</h3>
                <small>Gate & Visitor Control</small>
            </div>
            <SidebarNav items={GUARD_ITEMS} />
        </aside>
    );
}

export default GuardSidebar;
