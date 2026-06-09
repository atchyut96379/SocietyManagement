import Layout from "../../components/Layout/Layout";
import MyDues from "../../components/MyDues/MyDues";

function MyDuesPage() {

    return (
        <Layout>
            <h2>My Dues</h2>
            <p className="text-muted">
                Update your profile with flat number, then pay bills via Razorpay.
            </p>
            <MyDues />
        </Layout>
    );
}

export default MyDuesPage;
