const STATUS_MAP = {
    Pending: "warning",
    Approved: "success",
    Completed: "secondary",
    Open: "danger",
    Resolved: "success",
    Paid: "success",
    Unpaid: "warning",
    Active: "success",
    "Pending Setup": "warning"
};

function StatusBadge({ status }) {

    const variant = STATUS_MAP[status] || "light";
    const textClass = variant === "warning" ? "text-dark" : "";

    return (
        <span className={`badge bg-${variant} ${textClass}`}>
            {status}
        </span>
    );
}

export default StatusBadge;
