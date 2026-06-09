import PortalSidebar from "../PortalSidebar/PortalSidebar";
import Navbar from "../Navbar/Navbar";

function PortalLayout({ children }) {

    return (
        <div className="app-shell">
            <Navbar />

            <div className="app-body">
                <PortalSidebar />

                <main className="app-main">
                    {children}
                </main>
            </div>
        </div>
    );
}

export default PortalLayout;
