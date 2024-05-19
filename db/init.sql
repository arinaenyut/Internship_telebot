CREATE TABLE IF NOT EXISTS email_addresses (
	ID SERIAL PRIMARY KEY,
	email VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS phone_numbers (
	ID SERIAL PRIMARY KEY,
	number VARCHAR(100) NOT NULL
);

INSERT INTO email_addresses (email) VALUES
	('arina@arina.ru'),
	('test@test.com');

INSERT INTO phone_numbers (number) VALUES
	('+7-123-456-78-90'),
	('81112223344');

CREATE USER ${DB_REPL_USER} REPLICATION ENCRYPTED PASSWORD '${DB_REPL_PASSWORD}';
SELECT pg_create_physical_replication_slot('replication_slot');
