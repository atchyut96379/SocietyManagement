USE SocietyManagement;
GO

IF COL_LENGTH('PaymentTransactions', 'CreditAccount') IS NULL
BEGIN
    ALTER TABLE PaymentTransactions
        ADD CreditAccount NVARCHAR(20) NOT NULL
            CONSTRAINT DF_Payments_CreditAccount DEFAULT 'Maintenance';
END
GO

IF COL_LENGTH('Expenses', 'PaidFromAccount') IS NULL
BEGIN
    ALTER TABLE Expenses
        ADD PaidFromAccount NVARCHAR(20) NOT NULL
            CONSTRAINT DF_Expenses_PaidFromAccount DEFAULT 'Maintenance';
END
GO

IF OBJECT_ID('AccountTransfers', 'U') IS NULL
BEGIN
    CREATE TABLE AccountTransfers (
        TransferID INT IDENTITY(1,1) PRIMARY KEY,
        FromAccount NVARCHAR(20) NOT NULL,
        ToAccount NVARCHAR(20) NOT NULL,
        Amount DECIMAL(12,2) NOT NULL,
        Description NVARCHAR(255) NOT NULL,
        TransferDate DATE NOT NULL,
        CreatedDate DATETIME NOT NULL DEFAULT GETDATE()
    );
END
GO
