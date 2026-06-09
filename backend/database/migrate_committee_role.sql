USE SocietyManagement;
GO

IF COL_LENGTH('Residents', 'CommitteeRole') IS NULL
BEGIN
    ALTER TABLE Residents
    ADD CommitteeRole NVARCHAR(50) NULL;
END
GO
