function PageHeader({ title, subtitle, children }) {

    return (
        <div className="d-flex flex-wrap justify-content-between align-items-start gap-3 app-page-header">
            <div>
                <h2>{title}</h2>
                {subtitle && <p>{subtitle}</p>}
            </div>
            {children && (
                <div className="d-flex flex-wrap gap-2">{children}</div>
            )}
        </div>
    );
}

export default PageHeader;
