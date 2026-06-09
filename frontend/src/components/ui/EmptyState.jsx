function EmptyState({ message = "No records found" }) {

    return (
        <div className="text-center py-4 text-muted">
            <div style={{ fontSize: "2rem", opacity: 0.4 }}>📋</div>
            <p className="mb-0 mt-2">{message}</p>
        </div>
    );
}

export default EmptyState;
