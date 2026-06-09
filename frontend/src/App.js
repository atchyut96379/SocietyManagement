import {
    BrowserRouter,
    Routes,
    Route
} from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute/ProtectedRoute";
import Login from "./pages/Login/Login";
import Dashboard from "./pages/Dashboard/Dashboard";
import Residents from "./pages/Residents/Residents";
import Visitors from "./pages/Visitors/Visitors";
import Complaints from "./pages/Complaints/Complaints";
import Finance from "./pages/Finance/Finance";
import Notices from "./pages/Notices/Notices";
import PortalHome from "./pages/Portal/PortalHome";
import PortalNotices from "./pages/Portal/PortalNotices";
import PortalComplaints from "./pages/Portal/PortalComplaints";
import PortalDues from "./pages/Portal/PortalDues";
import PortalReports from "./pages/Portal/PortalReports";
import PortalVisitors from "./pages/Portal/PortalVisitors";
import PortalProfileSetup from "./pages/Portal/PortalProfileSetup";
import FirstLoginSetup from "./pages/Setup/FirstLoginSetup";
import MyDuesPage from "./pages/MyDues/MyDuesPage";
import GuardGate from "./pages/Guard/GuardGate";
import GuardVisitorLog from "./pages/Guard/GuardVisitorLog";
import GuardSetup from "./pages/Guard/GuardSetup";
import {
    MANAGEMENT_ROLES,
    RESIDENT_ROLE,
    SECRETARY_ROLE,
    SECURITY_ROLE
} from "./utils/auth";

function App() {

    return (
        <BrowserRouter>

            <Routes>
                <Route path="/" element={<Login />} />

                <Route
                    path="/setup-profile"
                    element={
                        <ProtectedRoute allowedRoles={[SECRETARY_ROLE]}>
                            <FirstLoginSetup />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/dashboard"
                    element={
                        <ProtectedRoute allowedRoles={MANAGEMENT_ROLES}>
                            <Dashboard />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/residents"
                    element={
                        <ProtectedRoute allowedRoles={[SECRETARY_ROLE]}>
                            <Residents />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/visitors"
                    element={
                        <ProtectedRoute allowedRoles={[SECRETARY_ROLE]}>
                            <Visitors />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/guard/setup"
                    element={
                        <ProtectedRoute allowedRoles={[SECURITY_ROLE]}>
                            <GuardSetup />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/guard"
                    element={
                        <ProtectedRoute allowedRoles={[SECURITY_ROLE]}>
                            <GuardGate />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/guard/log"
                    element={
                        <ProtectedRoute allowedRoles={[SECURITY_ROLE]}>
                            <GuardVisitorLog />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/complaints"
                    element={
                        <ProtectedRoute allowedRoles={[SECRETARY_ROLE]}>
                            <Complaints />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/finance"
                    element={
                        <ProtectedRoute allowedRoles={[SECRETARY_ROLE]}>
                            <Finance />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/notices"
                    element={
                        <ProtectedRoute allowedRoles={[SECRETARY_ROLE]}>
                            <Notices />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/my-dues"
                    element={
                        <ProtectedRoute allowedRoles={[SECRETARY_ROLE]}>
                            <MyDuesPage />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/portal/setup"
                    element={
                        <ProtectedRoute allowedRoles={[RESIDENT_ROLE]}>
                            <PortalProfileSetup />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/portal"
                    element={
                        <ProtectedRoute allowedRoles={[RESIDENT_ROLE]}>
                            <PortalHome />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/portal/notices"
                    element={
                        <ProtectedRoute allowedRoles={[RESIDENT_ROLE]}>
                            <PortalNotices />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/portal/complaints"
                    element={
                        <ProtectedRoute allowedRoles={[RESIDENT_ROLE]}>
                            <PortalComplaints />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/portal/visitors"
                    element={
                        <ProtectedRoute allowedRoles={[RESIDENT_ROLE]}>
                            <PortalVisitors />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/portal/dues"
                    element={
                        <ProtectedRoute allowedRoles={[RESIDENT_ROLE]}>
                            <PortalDues />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/portal/reports"
                    element={
                        <ProtectedRoute allowedRoles={[RESIDENT_ROLE]}>
                            <PortalReports />
                        </ProtectedRoute>
                    }
                />
            </Routes>

        </BrowserRouter>
    );
}

export default App;
