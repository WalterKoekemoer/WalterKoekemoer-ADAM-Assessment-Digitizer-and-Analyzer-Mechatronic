DROP TABLE IF EXISTS lecturer;
DROP TABLE IF EXISTS gathering;
DROP TABLE IF EXISTS participant;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS test;
DROP TABLE IF EXISTS sections;

DROP TABLE IF EXISTS assessor;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS validator;

CREATE TABLE lecturer (
  id INTEGER PRIMARY KEY,
  username VARCHAR(22) NOT NULL,
  password VARCHAR(22) NOT NULL
);

CREATE TABLE gathering (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  lecturer_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title VARCHAR(22) NOT NULL,
  test_date DATE NOT NULL,
  test_module VARCHAR(22) NOT NULL,
  test_total DECIMAL(3,3) NOT NULL,
  completed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (lecturer_id) REFERENCES lecturer (id)
);

CREATE TABLE participant (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  assessor_id INTEGER NOT NULL,
  gathering_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  section_description VARCHAR(18) NOT NULL,
  section_total DECIMAL(3,3) NOT NULL,
  FOREIGN KEY (gathering_id) REFERENCES gathering (id)
);

CREATE TABLE messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  gathering_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  info TEXT NOT NULL,
  FOREIGN KEY (gathering_id) REFERENCES gathering (id)
);

CREATE TABLE test (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  gathering_id INTEGER NOT NULL,
  n1 CHAR NOT NULL,                     --firs number of student number
  n2 CHAR NOT NULL,
  n3 CHAR NOT NULL,
  n4 CHAR NOT NULL,
  n5 CHAR NOT NULL,
  n6 CHAR NOT NULL,
  n7 CHAR NOT NULL,
  n8 CHAR NOT NULL,                     --last number of student number
  FOREIGN KEY (gathering_id) REFERENCES gathering (id)
);

CREATE TABLE sections (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  test_id INTEGER NOT NULL,
  sections_mark DECIMAL(3,3) NOT NULL,
  FOREIGN KEY (test_id) REFERENCES test (id)
);

CREATE TABLE assessor (
  id INTEGER PRIMARY KEY,
  username VARCHAR(22) NOT NULL,          
  FOS VARCHAR(42) NOT NULL,                   --field of study
  T CHAR,                                     --period of study in years (None if M)
  M BOOLEAN NOT NULL,                         --masters?
  sts BOOLEAN NOT NULL DEFAULT 1,             --status: avalable?
  completions INT NOT NULL DEFAULT 0,         --how many time did this person assist?             
  password VARCHAR(22) NOT NULL
);


CREATE TABLE student (
  id INTEGER PRIMARY KEY,
  password VARCHAR(22) NOT NULL
);

CREATE TABLE validator (
  id INTEGER PRIMARY KEY,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  password VARCHAR(22) NOT NULL
);