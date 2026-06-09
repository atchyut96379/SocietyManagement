USE SocietyManagement;
GO

IF COL_LENGTH('Users', 'ResidentID') IS NULL
BEGIN
    ALTER TABLE Users
    ADD ResidentID INT NULL;

    ALTER TABLE Users
    ADD CONSTRAINT FK_Users_Residents
        FOREIGN KEY (ResidentID) REFERENCES Residents(ResidentID);
END
GO
