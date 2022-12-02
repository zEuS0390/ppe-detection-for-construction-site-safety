DROP DATABASE IF EXISTS ppedb;

-- Create the table if it does not exist
CREATE DATABASE ppedb;

USE ppedb;

-- SFTP Data (Detection and Recognition) Table
CREATE TABLE SFTPData (
	sftpdata_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	path_to_directory VARCHAR(255) NOT NULL
);

-- Person Information Table
CREATE TABLE Person (
	person_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    profile_image LONGTEXT NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    middle_name VARCHAR(255),
    last_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL
);

-- YOLOR Detection Class Name Table
CREATE TABLE PPEClass (
	ppeclass_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
	ppeclass_name VARCHAR(255)
);

-- Violation Details Table
CREATE TABLE ViolationDetails (
	violationdetails_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    violationdetails_image LONGTEXT NOT NULL,
    violationdetails_timestamp DATETIME NOT NULL
);

-- Violator Table
CREATE TABLE Violator(
	violator_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    person_id INT NOT NULL,
    violationdetails_id INT NOT NULL,
    FOREIGN KEY (person_id) REFERENCES Person(person_id) ON DELETE CASCADE,
    FOREIGN KEY (violationdetails_id) REFERENCES ViolationDetails(violationdetails_id) ON DELETE CASCADE
);

-- Detected Class Table
CREATE TABLE DetectedPPEClass (
	detectedppeclass_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    ppeclass_id INT NOT NULL,
    violator_id INT NOT NULL,
    FOREIGN KEY (ppeclass_id) REFERENCES PPEClass(ppeclass_id) ON DELETE CASCADE,
    FOREIGN KEY (violator_id) REFERENCES Violator(violator_id) ON DELETE CASCADE
);