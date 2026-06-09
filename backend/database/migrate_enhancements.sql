USE SocietyManagement;
GO

-- Flats master table (auto-generated units per tower/floor)
IF OBJECT_ID('Flats', 'U') IS NULL
BEGIN
    CREATE TABLE Flats (
        FlatID INT IDENTITY(1,1) PRIMARY KEY,
        TowerName NVARCHAR(50) NOT NULL,
        FlatNumber NVARCHAR(20) NOT NULL,
        FloorNumber INT NOT NULL,
        IsOccupied BIT NOT NULL DEFAULT 0,
        CONSTRAINT UQ_Flats_Tower_Flat UNIQUE (TowerName, FlatNumber)
    );
END
GO

-- Users: mobile login, optional email, first-login flag
IF COL_LENGTH('Users', 'FirstLoginCompleted') IS NULL
BEGIN
    ALTER TABLE Users
    ADD FirstLoginCompleted BIT NOT NULL DEFAULT 0;
END
GO

-- Make email optional (drop unique if needed and re-add as nullable unique)
IF EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'UQ__Users__A9D2D4A7' AND object_id = OBJECT_ID('Users')
)
BEGIN
    -- index name may vary; alter column nullable instead
    ALTER TABLE Users ALTER COLUMN Email NVARCHAR(100) NULL;
END
ELSE IF COL_LENGTH('Users', 'Email') IS NOT NULL
BEGIN
    ALTER TABLE Users ALTER COLUMN Email NVARCHAR(100) NULL;
END
GO

-- Residents: owner name (tenants), vehicles, profile flag, flat link
IF COL_LENGTH('Residents', 'OwnerName') IS NULL
BEGIN
    ALTER TABLE Residents ADD OwnerName NVARCHAR(100) NULL;
END
GO

IF COL_LENGTH('Residents', 'VehicleDetails') IS NULL
BEGIN
    ALTER TABLE Residents ADD VehicleDetails NVARCHAR(MAX) NULL;
END
GO

IF COL_LENGTH('Residents', 'ProfileCompleted') IS NULL
BEGIN
    ALTER TABLE Residents ADD ProfileCompleted BIT NOT NULL DEFAULT 0;
END
GO

IF COL_LENGTH('Residents', 'FlatID') IS NULL
BEGIN
    ALTER TABLE Residents ADD FlatID INT NULL;
END
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Residents_Flats'
)
BEGIN
    ALTER TABLE Residents
    ADD CONSTRAINT FK_Residents_Flats
        FOREIGN KEY (FlatID) REFERENCES Flats(FlatID);
END
GO

-- Payments: immutable audit fields, cash proof, gateway, receipt
IF COL_LENGTH('PaymentTransactions', 'PaymentSource') IS NULL
BEGIN
    ALTER TABLE PaymentTransactions ADD PaymentSource NVARCHAR(20) NOT NULL DEFAULT 'Manual';
END
GO

IF COL_LENGTH('PaymentTransactions', 'PaymentProofPath') IS NULL
BEGIN
    ALTER TABLE PaymentTransactions ADD PaymentProofPath NVARCHAR(500) NULL;
END
GO

IF COL_LENGTH('PaymentTransactions', 'GatewayTransactionId') IS NULL
BEGIN
    ALTER TABLE PaymentTransactions ADD GatewayTransactionId NVARCHAR(100) NULL;
END
GO

IF COL_LENGTH('PaymentTransactions', 'ReceiptNumber') IS NULL
BEGIN
    ALTER TABLE PaymentTransactions ADD ReceiptNumber NVARCHAR(50) NULL;
END
GO

IF COL_LENGTH('PaymentTransactions', 'IsImmutable') IS NULL
BEGIN
    ALTER TABLE PaymentTransactions ADD IsImmutable BIT NOT NULL DEFAULT 1;
END
GO

-- Unique phone per user (login username)
IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'UQ_Users_PhoneNumber' AND object_id = OBJECT_ID('Users')
)
BEGIN
    CREATE UNIQUE INDEX UQ_Users_PhoneNumber ON Users(PhoneNumber)
    WHERE PhoneNumber IS NOT NULL;
END
GO
