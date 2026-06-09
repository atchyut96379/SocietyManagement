USE SocietyManagement;
GO

IF COL_LENGTH('Expenses', 'ProofImagePath') IS NULL
BEGIN
    ALTER TABLE Expenses ADD ProofImagePath NVARCHAR(500) NULL;
END
GO
