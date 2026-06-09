import { NavLink } from "react-router-dom";

function SidebarNav({ items }) {

    return (
        <nav className="app-sidebar-nav">
            {items.map((item) => (
                <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.end}
                    className={({ isActive }) =>
                        `nav-link${isActive ? " active" : ""}`
                    }
                >
                    {item.icon && `${item.icon} `}
                    {item.label}
                </NavLink>
            ))}
        </nav>
    );
}

export default SidebarNav;
