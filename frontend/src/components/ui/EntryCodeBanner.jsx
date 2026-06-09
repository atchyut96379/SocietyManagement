function EntryCodeBanner({ code, validUntil, visitorName, onCopy }) {

    if (!code) {
        return null;
    }

    return (
        <div className="entry-code-banner mb-4">
            <strong>Visitor registered!</strong>
            <p className="mb-2 mt-1 text-muted">
                Share this code with security at the gate:
            </p>
            <div className="d-flex flex-wrap align-items-center gap-3">
                <span className="entry-code-value">{code}</span>
                <button
                    type="button"
                    className="btn btn-outline-success btn-sm"
                    onClick={() => onCopy(code)}
                >
                    Copy Code
                </button>
            </div>
            {validUntil && visitorName && (
                <small className="text-muted d-block mt-2">
                    Valid until {validUntil} for {visitorName}
                </small>
            )}
        </div>
    );
}

export default EntryCodeBanner;
