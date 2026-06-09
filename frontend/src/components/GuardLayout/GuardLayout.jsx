import GuardSidebar from "../GuardSidebar/GuardSidebar";
import Navbar from "../Navbar/Navbar";

function GuardLayout({ children }) {

    return (
        <div className="app-shell">
            <Navbar />

            <div className="app-body">
                <GuardSidebar />

                <main className="app-main">
                    {children}
                </main>
            </div>
        </div>
    );
}

export default GuardLayout;
