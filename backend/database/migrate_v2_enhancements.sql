USE SocietyManagement;
GO

IF OBJECT_ID('Flats', 'U') IS NULL
BEGIN
    CREATE TABLE Flats (
        FlatID INT IDENTITY(1,1) PRIMARY KEY,
        FlatNumber NVARCHAR(20) NOT NULL UNIQUE,
        FloorNumber INT NOT NULL,
        TowerName NVARCHAR(50) NOT NULL DEFAULT 'Tower A',
        IsOccupied BIT NOT NULL DEFAULT 0,
        ResidentID INT NULL
    );
END
GO

IF COL_LENGTH('Users', 'MustChangePassword') IS NULL
BEGIN
    ALTER TABLE Users
    ADD MustChangePassword BIT NOT NULL DEFAULT 1;
END
GO

IF COL_LENGTH('Users', 'ProfileCompleted') IS NULL
BEGIN
    ALTER TABLE Users
    ADD ProfileCompleted BIT NOT NULL DEFAULT 0;
END
GO

IF EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'UQ_Users_Email' AND object_id = OBJECT_ID('Users')
)
BEGIN
    ALTER TABLE Users DROP CONSTRAINT UQ_Users_Email;
END
GO

IF EXISTS (
    SELECT 1 FROM sys.key_constraints
    WHERE name LIKE '%Email%' AND parent_object_id = OBJECT_ID('Users')
)
BEGIN
    DECLARE @sql NVARCHAR(MAX);
    SELECT @sql = 'ALTER TABLE Users DROP CONSTRAINT ' + name
    FROM sys.key_constraints
    WHERE parent_object_id = OBJECT_ID('Users')
      AND type = 'UQ'
      AND name IN (
          SELECT name FROM sys.indexes
          WHERE object_id = OBJECT_ID('Users')
            AND is_unique = 1
            AND COL_NAME(object_id, (
                SELECT MIN(column_id) FROM sys.index_columns
                WHERE object_id = sys.indexes.object_id
                  AND index_id = sys.indexes.index_id
            )) = 'Email'
      );
    IF @sql IS NOT NULL EXEC sp_executesql @sql;
END
GO

ALTER TABLE Users ALTER COLUMN Email NVARCHAR(100) NULL;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'UQ_Users_PhoneNumber' AND object_id = OBJECT_ID('Users')
)
BEGIN
    CREATE UNIQUE INDEX UQ_Users_PhoneNumber
    ON Users (PhoneNumber)
    WHERE PhoneNumber IS NOT NULL;
END
GO

IF COL_LENGTH('Residents', 'FlatID') IS NULL
BEGIN
    ALTER TABLE Residents ADD FlatID INT NULL;
END
GO

IF COL_LENGTH('Residents', 'ResidentType') IS NULL
BEGIN
    ALTER TABLE Residents
    ADD ResidentType NVARCHAR(20) NOT NULL DEFAULT 'Owner';
END
GO

IF COL_LENGTH('Residents', 'OwnerName') IS NULL
BEGIN
    ALTER TABLE Residents ADD OwnerName NVARCHAR(100) NULL;
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

IF OBJECT_ID('Vehicles', 'U') IS NULL
BEGIN
    CREATE TABLE Vehicles (
        VehicleID INT IDENTITY(1,1) PRIMARY KEY,
        ResidentID INT NOT NULL UNIQUE,
        CarNumber NVARCHAR(20) NULL,
        BikeNumber NVARCHAR(20) NULL,
        UpdatedDate DATETIME NOT NULL DEFAULT GETDATE(),
        CONSTRAINT FK_Vehicles_Residents FOREIGN KEY (ResidentID) REFERENCES Residents(ResidentID)
    );
END
GO

IF COL_LENGTH('PaymentTransactions', 'PaymentSource') IS NULL
BEGIN
    ALTER TABLE PaymentTransactions
    ADD PaymentSource NVARCHAR(20) NOT NULL DEFAULT 'Manual';
END
GO

IF COL_LENGTH('PaymentTransactions', 'ProofImagePath') IS NULL
BEGIN
    ALTER TABLE PaymentTransactions ADD ProofImagePath NVARCHAR(500) NULL;
END
GO

IF COL_LENGTH('PaymentTransactions', 'ReceiptNumber') IS NULL
BEGIN
    ALTER TABLE PaymentTransactions ADD ReceiptNumber NVARCHAR(50) NULL;
END
GO

IF COL_LENGTH('PaymentTransactions', 'GatewayOrderId') IS NULL
BEGIN
    ALTER TABLE PaymentTransactions ADD GatewayOrderId NVARCHAR(100) NULL;
END
GO

IF COL_LENGTH('PaymentTransactions', 'GatewayPaymentId') IS NULL
BEGIN
    ALTER TABLE PaymentTransactions ADD GatewayPaymentId NVARCHAR(100) NULL;
END
GO

IF COL_LENGTH('PaymentTransactions', 'IsImmutable') IS NULL
BEGIN
    ALTER TABLE PaymentTransactions
    ADD IsImmutable BIT NOT NULL DEFAULT 1;
END
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'UQ_Residents_CommitteeRole' AND object_id = OBJECT_ID('Residents')
)
BEGIN
    CREATE UNIQUE INDEX UQ_Residents_CommitteeRole
    ON Residents (CommitteeRole)
    WHERE CommitteeRole IS NOT NULL AND CommitteeRole <> 'None';
END
GO
