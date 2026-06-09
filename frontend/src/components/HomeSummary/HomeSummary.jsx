import { useEffect, useState } from "react";
import api from "../../services/api";
import LoadingState from "../ui/LoadingState";

const defaultSummary = {
    current_month: "",
    current_year: new Date().getFullYear(),
    billed_this_month: 0,
    collected_this_month: 0,
    pending_amount: 0,
    open_complaints: 0,
    last_month_closing: 0,
    present_account_balance: 0
};

function HomeSummary() {

    const [summary, setSummary] = useState(defaultSummary);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadSummary();
    }, []);

    const loadSummary = async () => {

        try {
            const response = await api.get("/home/summary");
            setSummary(response.data);
        } catch {
            setSummary(defaultSummary);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <LoadingState message="Loading summary..." />;
    }

    const periodLabel = summary.current_month
        ? `${summary.current_month} ${summary.current_year}`
        : "This Month";

    const cards = [
        {
            title: "Billed This Month",
            subtitle: periodLabel,
            value: summary.billed_this_month,
            prefix: "₹",
            variant: "primary"
        },
        {
            title: "Collected",
            subtitle: periodLabel,
            value: summary.collected_this_month,
            prefix: "₹",
            variant: "success"
        },
        {
            title: "Pending",
            subtitle: "Society total",
            value: summary.pending_amount,
            prefix: "₹",
            variant: "warning"
        },
        {
            title: "Open Complaints",
            subtitle: "Needs attention",
            value: summary.open_complaints,
            prefix: "",
            variant: "danger"
        },
        {
            title: "Last Month Closing",
            subtitle: "Month end balance",
            value: summary.last_month_closing,
            prefix: "₹",
            variant: "secondary"
        },
        {
            title: "Account Balance",
            subtitle: "Current",
            value: summary.present_account_balance,
            prefix: "₹",
            variant: "info"
        }
    ];

    return (
        <div className="row g-3">
            {cards.map((card) => (
                <div className="col-md-6 col-lg-4 col-xl-2" key={card.title}>
                    <div className={`stat-card stat-card--${card.variant}`}>
                        <h6>{card.title}</h6>
                        <small className="text-muted d-block mb-2">
                            {card.subtitle}
                        </small>
                        <p className="stat-value">
                            {card.prefix}{card.value}
                        </p>
                    </div>
                </div>
            ))}
        </div>
    );
}

export default HomeSummary;
