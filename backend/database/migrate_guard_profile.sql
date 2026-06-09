USE SocietyManagement;
GO

IF COL_LENGTH('Users', 'IdentityCardType') IS NULL
BEGIN
    ALTER TABLE Users ADD IdentityCardType NVARCHAR(20) NULL;
END
GO

IF COL_LENGTH('Users', 'IdentityCardNumber') IS NULL
BEGIN
    ALTER TABLE Users ADD IdentityCardNumber NVARCHAR(50) NULL;
END
GO
