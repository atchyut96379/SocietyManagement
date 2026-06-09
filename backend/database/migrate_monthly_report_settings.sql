USE SocietyManagement;
GO

IF OBJECT_ID('MonthlyReportSettings', 'U') IS NULL
BEGIN
    CREATE TABLE MonthlyReportSettings (
        ReportSettingID INT IDENTITY(1,1) PRIMARY KEY,
        ReportMonth NVARCHAR(20) NOT NULL,
        ReportYear INT NOT NULL,
        Notes NVARCHAR(MAX) NULL,
        CorpusPendingFlats NVARCHAR(MAX) NULL,
        UpdatedDate DATETIME NOT NULL DEFAULT GETDATE(),
        CONSTRAINT UQ_MonthlyReportSettings_Period
            UNIQUE (ReportMonth, ReportYear)
    );
END
GO
