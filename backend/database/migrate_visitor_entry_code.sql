USE SocietyManagement;
GO

IF COL_LENGTH('Visitors', 'EntryCode') IS NULL
BEGIN
    ALTER TABLE Visitors ADD EntryCode NVARCHAR(8) NULL;
END
GO

IF COL_LENGTH('Visitors', 'ValidUntil') IS NULL
BEGIN
    ALTER TABLE Visitors ADD ValidUntil DATETIME NULL;
END
GO
