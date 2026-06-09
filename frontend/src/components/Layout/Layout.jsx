import Sidebar from "../Sidebar/Sidebar";
import Navbar from "../Navbar/Navbar";

function Layout({ children }) {

    return (
        <div className="app-shell">
            <Navbar />

            <div className="app-body">
                <Sidebar />

                <main className="app-main">
                    {children}
                </main>
            </div>
        </div>
    );
}

export default Layout;
