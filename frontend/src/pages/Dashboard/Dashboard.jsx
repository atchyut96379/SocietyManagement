import Layout from "../../components/Layout/Layout";
import HomeSummary from "../../components/HomeSummary/HomeSummary";
import SecretarySetup from "../../components/SecretarySetup/SecretarySetup";
import PageHeader from "../../components/ui/PageHeader";
import { isAdmin, isSecretary } from "../../utils/auth";

function Dashboard() {

    return (
        <Layout>
            <PageHeader
                title={isAdmin() ? "Admin Panel" : "Dashboard"}
                subtitle={
                    isAdmin()
                        ? "Create and manage the secretary account"
                        : "Society overview and quick stats"
                }
            />

            <SecretarySetup />

            {isAdmin() && (
                <div className="alert alert-secondary app-card mb-4">
                    Admin can only manage the secretary account.
                    Log in as secretary for daily operations.
                </div>
            )}

            {isSecretary() && (
                <div className="alert alert-info app-card mb-4">
                    You are logged in as <strong>Secretary</strong>.
                    Payment records are permanent for transparency.
                </div>
            )}

            <div className="mt-2">
                <HomeSummary />
            </div>
        </Layout>
    );
}

export default Dashboard;
