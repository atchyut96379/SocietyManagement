import { Navigate, useLocation } from "react-router-dom";
import {
    getHomeRoute,
    getRoleId,
    getSetupPath,
    hasValidSession,
    logout,
    needsSetupProfile
} from "../../utils/auth";

function ProtectedRoute({ children, allowedRoles = [1] }) {

    const location = useLocation();

    if (!hasValidSession()) {
        logout();
        return <Navigate to="/" replace />;
    }

    const roleId = getRoleId();

    if (!allowedRoles.includes(roleId)) {
        const home = getHomeRoute();

        if (home === "/") {
            logout();
            return <Navigate to="/" replace />;
        }

        return <Navigate to={home} replace />;
    }

    if (needsSetupProfile()) {
        const setupPath = getSetupPath();

        if (location.pathname !== setupPath) {
            return <Navigate to={setupPath} replace />;
        }
    }

    return children;
}

export default ProtectedRoute;
