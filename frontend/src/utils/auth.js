export const ADMIN_ROLE = 1;
export const RESIDENT_ROLE = 2;
export const SECURITY_ROLE = 3;
export const SECRETARY_ROLE = 4;

export const MANAGEMENT_ROLES = [
    ADMIN_ROLE,
    SECRETARY_ROLE
];

export const SECRETARY_ROLES = [SECRETARY_ROLE];

export function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("role_id");
    localStorage.removeItem("resident_id");
    localStorage.removeItem("user_name");
    localStorage.removeItem("must_change_password");
    localStorage.removeItem("profile_completed");
}

function decodeTokenPayload() {
    const token = localStorage.getItem("token");

    if (!token) {
        return null;
    }

    try {
        const payload = token.split(".")[1];
        return JSON.parse(atob(payload));
    } catch {
        return null;
    }
}

export function syncSessionFromToken() {
    const token = localStorage.getItem("token");

    if (!token) {
        return false;
    }

    const payload = decodeTokenPayload();

    if (!payload?.role_id) {
        logout();
        return false;
    }

    localStorage.setItem("role_id", String(payload.role_id));

    if (payload.resident_id) {
        localStorage.setItem(
            "resident_id",
            String(payload.resident_id)
        );
    }

    if (payload.phone_number && !localStorage.getItem("user_name")) {
        localStorage.setItem("user_name", payload.phone_number);
    } else if (payload.email && !localStorage.getItem("user_name")) {
        localStorage.setItem("user_name", payload.email);
    }

    return true;
}

export function getRoleId() {
    syncSessionFromToken();
    return Number(localStorage.getItem("role_id") || 0);
}

export function getResidentId() {
    syncSessionFromToken();
    return Number(localStorage.getItem("resident_id") || 0);
}

export function isAdmin() {
    return getRoleId() === ADMIN_ROLE;
}

export function isSecretary() {
    return getRoleId() === SECRETARY_ROLE;
}

export function isManagement() {
    return getRoleId() === SECRETARY_ROLE;
}

export function isResident() {
    return getRoleId() === RESIDENT_ROLE;
}

export function isSecurity() {
    return getRoleId() === SECURITY_ROLE;
}

export function getRoleLabel() {
    if (isAdmin()) return "Admin";
    if (isSecretary()) return "Secretary";
    if (isSecurity()) return "Guard";
    if (isResident()) return "Resident";
    return "User";
}

export function getHomeRoute() {
    if (isSecurity()) {
        return "/guard";
    }

    if (isResident()) {
        return "/portal";
    }

    if (isAdmin() || isSecretary()) {
        return "/dashboard";
    }

    return "/";
}

export function getUserName() {
    return localStorage.getItem("user_name") || "User";
}

export function hasValidSession() {
    return syncSessionFromToken() && getRoleId() > 0;
}

export function getSetupPath() {
    if (isResident()) {
        return "/portal/setup";
    }
    if (isSecurity()) {
        return "/guard/setup";
    }
    return "/setup-profile";
}

export function needsSetupProfile() {
    if (isAdmin()) {
        return false;
    }

    if (
        isSecretary() &&
        localStorage.getItem("must_change_password") === "1"
    ) {
        return true;
    }

    if (
        isResident() &&
        localStorage.getItem("profile_completed") === "0"
    ) {
        return true;
    }

    if (
        isResident() &&
        localStorage.getItem("must_change_password") === "1"
    ) {
        return true;
    }

    if (
        isSecurity() &&
        (
            localStorage.getItem("profile_completed") === "0" ||
            localStorage.getItem("must_change_password") === "1"
        )
    ) {
        return true;
    }

    return false;
}

export function canModifyPayments() {
    return isAdmin();
}
