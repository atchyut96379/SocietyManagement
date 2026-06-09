IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'SocietyManagement')
BEGIN
    CREATE DATABASE SocietyManagement;
END
GO

USE SocietyManagement;
GO

IF OBJECT_ID('Roles', 'U') IS NULL
BEGIN
    CREATE TABLE Roles (
        RoleID INT IDENTITY(1,1) PRIMARY KEY,
        RoleName NVARCHAR(50) NOT NULL
    );

    INSERT INTO Roles (RoleName) VALUES ('Admin'), ('Resident'), ('Security'), ('Secretary');
END
GO

IF OBJECT_ID('Users', 'U') IS NULL
BEGIN
    CREATE TABLE Users (
        UserID INT IDENTITY(1,1) PRIMARY KEY,
        FullName NVARCHAR(100) NOT NULL,
        Email NVARCHAR(100) NOT NULL UNIQUE,
        PasswordHash NVARCHAR(255) NOT NULL,
        PhoneNumber NVARCHAR(20) NULL,
        RoleID INT NOT NULL DEFAULT 1,
        ResidentID INT NULL,
        CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
        CONSTRAINT FK_Users_Roles FOREIGN KEY (RoleID) REFERENCES Roles(RoleID)
    );
END
GO

IF COL_LENGTH('Users', 'ResidentID') IS NULL
BEGIN
    ALTER TABLE Users
    ADD ResidentID INT NULL;
END
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.foreign_keys
    WHERE name = 'FK_Users_Residents'
)
BEGIN
    ALTER TABLE Users
    ADD CONSTRAINT FK_Users_Residents
        FOREIGN KEY (ResidentID) REFERENCES Residents(ResidentID);
END
GO

IF OBJECT_ID('Residents', 'U') IS NULL
BEGIN
    CREATE TABLE Residents (
        ResidentID INT IDENTITY(1,1) PRIMARY KEY,
        FullName NVARCHAR(100) NOT NULL,
        FlatNumber NVARCHAR(20) NOT NULL,
        PhoneNumber NVARCHAR(20) NOT NULL,
        Email NVARCHAR(100) NULL,
        TowerName NVARCHAR(50) NOT NULL,
        IsOwner BIT NOT NULL DEFAULT 1,
        CommitteeRole NVARCHAR(50) NULL,
        CreatedDate DATETIME NOT NULL DEFAULT GETDATE()
    );
END
GO

IF OBJECT_ID('Visitors', 'U') IS NULL
BEGIN
    CREATE TABLE Visitors (
        VisitorID INT IDENTITY(1,1) PRIMARY KEY,
        VisitorName NVARCHAR(100) NOT NULL,
        MobileNumber NVARCHAR(20) NOT NULL,
        ResidentID INT NOT NULL,
        Purpose NVARCHAR(255) NOT NULL,
        EntryTime DATETIME NOT NULL DEFAULT GETDATE(),
        ExitTime DATETIME NULL,
        Status NVARCHAR(20) NOT NULL DEFAULT 'Pending',
        CONSTRAINT FK_Visitors_Residents FOREIGN KEY (ResidentID) REFERENCES Residents(ResidentID)
    );
END
GO

IF OBJECT_ID('Complaints', 'U') IS NULL
BEGIN
    CREATE TABLE Complaints (
        ComplaintID INT IDENTITY(1,1) PRIMARY KEY,
        ResidentID INT NOT NULL,
        Subject NVARCHAR(150) NOT NULL,
        Description NVARCHAR(MAX) NOT NULL,
        Status NVARCHAR(20) NOT NULL DEFAULT 'Open',
        CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
        UpdatedDate DATETIME NULL,
        CONSTRAINT FK_Complaints_Residents FOREIGN KEY (ResidentID) REFERENCES Residents(ResidentID)
    );
END
GO

IF OBJECT_ID('Notices', 'U') IS NULL
BEGIN
    CREATE TABLE Notices (
        NoticeID INT IDENTITY(1,1) PRIMARY KEY,
        Title NVARCHAR(150) NOT NULL,
        Description NVARCHAR(MAX) NOT NULL,
        CreatedBy INT NOT NULL,
        CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
        CONSTRAINT FK_Notices_Users FOREIGN KEY (CreatedBy) REFERENCES Users(UserID)
    );
END
GO

IF OBJECT_ID('MaintenanceInvoices', 'U') IS NULL
BEGIN
    CREATE TABLE MaintenanceInvoices (
        InvoiceID INT IDENTITY(1,1) PRIMARY KEY,
        ResidentID INT NOT NULL,
        InvoiceMonth NVARCHAR(20) NOT NULL,
        InvoiceYear INT NOT NULL,
        Amount DECIMAL(12,2) NOT NULL,
        DueDate DATE NOT NULL,
        Status NVARCHAR(20) NOT NULL DEFAULT 'Pending',
        CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
        CONSTRAINT FK_Invoices_Residents FOREIGN KEY (ResidentID) REFERENCES Residents(ResidentID)
    );
END
GO

IF OBJECT_ID('PaymentTransactions', 'U') IS NULL
BEGIN
    CREATE TABLE PaymentTransactions (
        PaymentID INT IDENTITY(1,1) PRIMARY KEY,
        InvoiceID INT NOT NULL,
        AmountPaid DECIMAL(12,2) NOT NULL,
        PaymentMode NVARCHAR(50) NOT NULL,
        TransactionReference NVARCHAR(100) NOT NULL,
        PaymentDate DATETIME NOT NULL DEFAULT GETDATE(),
        CONSTRAINT FK_Payments_Invoices FOREIGN KEY (InvoiceID) REFERENCES MaintenanceInvoices(InvoiceID)
    );
END
GO

IF OBJECT_ID('Expenses', 'U') IS NULL
BEGIN
    CREATE TABLE Expenses (
        ExpenseID INT IDENTITY(1,1) PRIMARY KEY,
        ExpenseType NVARCHAR(100) NOT NULL,
        Amount DECIMAL(12,2) NOT NULL,
        Description NVARCHAR(255) NOT NULL,
        ExpenseDate DATE NOT NULL,
        CreatedDate DATETIME NOT NULL DEFAULT GETDATE()
    );
END
GO
