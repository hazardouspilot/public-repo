DROP TABLE Attempts;

DROP TABLE Routes;

DROP TABLE Results;

DROP TABLE PrivacyPrefs;

DROP TABLE Modes;

DROP TABLE Type_table;

DROP TABLE Locations;

DROP TABLE Access_table;

DROP TABLE Climbers;

DROP TABLE Gyms;

DROP TABLE Companys;

DROP TABLE Grades;

-- Create Grade table
CREATE TABLE Grades (
    GradingSystem VARCHAR(50),
    Grade VARCHAR(50),
    PRIMARY KEY (GradingSystem, Grade)
);

-- Create Company table
CREATE TABLE Companys (
    CompanyName VARCHAR(50) PRIMARY KEY,
    BoulderGradeSystem VARCHAR(50),
    SportGradeSystem VARCHAR(50),
    PrimaryCountry VARCHAR(50),
    FOREIGN KEY (BoulderGradeSystem) REFERENCES Grades (GradingSystem),
    FOREIGN KEY (SportGradeSystem) REFERENCES Grades (GradingSystem)
);

-- Create Gym table
CREATE TABLE Gyms (
    CompanyName VARCHAR(50),
    Suburb VARCHAR(50),
    City VARCHAR(50),
    Country VARCHAR(50),
    PRIMARY KEY (CompanyName, Suburb),
    FOREIGN KEY (CompanyName) REFERENCES Companys (CompanyName)
);

-- Create Climber table
CREATE TABLE Climbers (
    Username VARCHAR(50) PRIMARY KEY,
    Pass VARCHAR(500),
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    PrivacyPref VARCHAR(50) DEFAULT 'Alias',
    Access VARCHAR(50),
    Email VARCHAR(50),
    Photo BLOB,
    FB VARCHAR(50),
    Insta VARCHAR(50),
    YT VARCHAR(50),
    X VARCHAR(50)
);

-- Create Access table
CREATE TABLE Access_table ( Access VARCHAR(50) PRIMARY KEY );

-- Create Location table
CREATE TABLE Locations (
    CompanyName VARCHAR(50),
    Suburb VARCHAR(50),
    Location VARCHAR(50),
    PRIMARY KEY (CompanyName, Suburb, Location),
    FOREIGN KEY (CompanyName, Suburb) REFERENCES Gyms (CompanyName, Suburb)
);

-- Create Type table
CREATE TABLE Type_table ( Type_column VARCHAR(50) PRIMARY KEY );

-- Create Mode table
CREATE TABLE Modes ( Mode_column VARCHAR(50) PRIMARY KEY );

-- Create PrivacyPref table
CREATE TABLE PrivacyPrefs (
    PrivacyPref VARCHAR(50) PRIMARY KEY
);

-- Create Result table
CREATE TABLE Results ( Result VARCHAR(50) PRIMARY KEY );

-- Create Route table
CREATE TABLE Routes (
    RID INTEGER AUTO_INCREMENT PRIMARY KEY,
    CompanyName VARCHAR(50),
    Suburb VARCHAR(50),
    Location VARCHAR(50),
    GradingSystem VARCHAR(50),
    Grade VARCHAR(50),
    Type_column VARCHAR(50),
    Colour VARCHAR(50),
    Existing INTEGER,
    FOREIGN KEY (CompanyName, Suburb) REFERENCES Gyms (CompanyName, Suburb),
    FOREIGN KEY (GradingSystem, Grade) REFERENCES Grades (GradingSystem, Grade),
    FOREIGN KEY (CompanyName, Suburb, Location) REFERENCES Locations (CompanyName, Suburb, Location),
    FOREIGN KEY (Type_column) REFERENCES Type_table (Type_column)
);

-- Create Attempt table
CREATE TABLE Attempts (
    Username VARCHAR(50),
    RID INTEGER,
    Mode_column VARCHAR(50),
    AttemptNo INTEGER,
    Date_column DATE,
    Time_column TIME,
    Result VARCHAR(50),
    Rating INT DEFAULT 0,
    Notes VARCHAR(500),
    Video BLOB,
    PRIMARY KEY (
        Username,
        RID,
        Mode_column,
        AttemptNo
    ),
    FOREIGN KEY (Username) REFERENCES Climbers (Username),
    FOREIGN KEY (RID) REFERENCES Routes (RID),
    FOREIGN KEY (Mode_column) REFERENCES Modes (Mode_column)
);