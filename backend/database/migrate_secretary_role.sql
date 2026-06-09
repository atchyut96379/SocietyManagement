USE SocietyManagement;
GO

IF NOT EXISTS (SELECT 1 FROM Roles WHERE RoleName = N'Secretary')
BEGIN
    INSERT INTO Roles (RoleName) VALUES (N'Secretary');
END
GO

IF COL_LENGTH('PaymentTransactions', 'RecordedBy') IS NULL
BEGIN
    ALTER TABLE PaymentTransactions
    ADD RecordedBy INT NULL;

    ALTER TABLE PaymentTransactions
    ADD CONSTRAINT FK_Payments_Users
        FOREIGN KEY (RecordedBy) REFERENCES Users(UserID);
END
GO
