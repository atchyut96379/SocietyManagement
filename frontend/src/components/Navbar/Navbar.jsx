import { useState } from "react";
import api from "../../services/api";
import {
    getUserName,
    logout,
    getRoleLabel,
    isAdmin,
    isSecretary,
    isSecurity,
    isResident
} from "../../utils/auth";

function getPortalTitle() {
    if (isAdmin()) return "Admin Console";
    if (isSecretary()) return "Society Management";
    if (isSecurity()) return "Guard Station";
    if (isResident()) return "Resident Portal";
    return "Society Management";
}

function Navbar() {

    const [showPasswordForm, setShowPasswordForm] = useState(false);
    const [passwordForm, setPasswordForm] = useState({
        current_password: "",
        new_password: ""
    });
    const [message, setMessage] = useState("");

    const handleLogout = () => {
        logout();
        window.location.href = "/";
    };

    const changePassword = async (event) => {

        event.preventDefault();
        setMessage("");

        try {

            const response = await api.post(
                "/change-password",
                passwordForm
            );

            setMessage(response.data.message);

            if (response.data.success) {
                setPasswordForm({
                    current_password: "",
                    new_password: ""
                });
                setShowPasswordForm(false);
            }

        } catch {

            setMessage("Unable to change password");
        }
    };

    return (
        <header className="app-navbar">
            <div className="d-flex justify-content-between align-items-center">
                <div>
                    <h1 className="app-navbar-title">{getPortalTitle()}</h1>
                    <div className="app-navbar-subtitle">
                        {getUserName()} · {getRoleLabel()}
                    </div>
                </div>

                <div className="d-flex gap-2">
                    <button
                        type="button"
                        className="btn btn-outline-secondary btn-sm"
                        onClick={() =>
                            setShowPasswordForm(!showPasswordForm)
                        }
                    >
                        {showPasswordForm ? "Cancel" : "Password"}
                    </button>

                    <button
                        type="button"
                        className="btn btn-danger btn-sm"
                        onClick={handleLogout}
                    >
                        Logout
                    </button>
                </div>
            </div>

            {showPasswordForm && (
                <form
                    className="row g-2 mt-3 pt-3 border-top"
                    onSubmit={changePassword}
                >
                    <div className="col-md-4">
                        <input
                            type="password"
                            className="form-control form-control-sm"
                            placeholder="Current password"
                            value={passwordForm.current_password}
                            onChange={(e) =>
                                setPasswordForm({
                                    ...passwordForm,
                                    current_password: e.target.value
                                })
                            }
                            required
                        />
                    </div>

                    <div className="col-md-4">
                        <input
                            type="password"
                            className="form-control form-control-sm"
                            placeholder="New password"
                            value={passwordForm.new_password}
                            onChange={(e) =>
                                setPasswordForm({
                                    ...passwordForm,
                                    new_password: e.target.value
                                })
                            }
                            required
                        />
                    </div>

                    <div className="col-md-2">
                        <button
                            type="submit"
                            className="btn btn-primary btn-sm w-100"
                        >
                            Update
                        </button>
                    </div>

                    {message && (
                        <div className="col-12">
                            <small className="text-muted">{message}</small>
                        </div>
                    )}
                </form>
            )}
        </header>
    );
}

export default Navbar;
