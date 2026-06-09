function LoadingState({ message = "Loading..." }) {

    return (
        <div className="text-center py-5">
            <div
                className="spinner-border text-primary mb-3"
                role="status"
            >
                <span className="visually-hidden">Loading</span>
            </div>
            <p className="text-muted mb-0">{message}</p>
        </div>
    );
}

export default LoadingState;
