CREATE TYPE contact_group_enum AS ENUM (
    'Общие',
    'Друзья',
    'Работа',
    'Семья',
    'Сервис',
    'Соседи',
    'Другое'
);

CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    phone_number VARCHAR(16) NOT NULL UNIQUE CHECK (phone_number ~ '^\+[1-9][0-9]{1,14}$'), -- just E.164 re check
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_favorite BOOLEAN DEFAULT FALSE,
    contact_group contact_group_enum NOT NULL DEFAULT 'Общие'
);

CREATE INDEX idx_contacts_last_name ON contacts(last_name);
CREATE INDEX idx_contacts_phone ON contacts(phone_number);
CREATE INDEX idx_contacts_group ON contacts(contact_group);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_contacts_updated_at
    BEFORE UPDATE ON contacts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

INSERT INTO contacts (last_name, first_name, middle_name, phone_number, note, contact_group) VALUES
    ('Крючков', 'Евгений', 'Святославович', '+79991232297', 'Одногруппник', 'Друзья'),
    ('Ефимов', 'Арсений', 'Максимович', '+79994391166', 'Одноклассник', 'Друзья'),
    ('Филатова', 'Амина', 'Максимовна', '+79999999999', 'Коллега', 'Работа'),
    ('Крылов', 'Михаил', 'Миронович', '+79994567890', 'Сосед', 'Соседи'),
    ('Виноградова', 'Анастасия', 'Данииловна', '+79991670901', 'Мастер маникюра', 'Сервис'),
    ('Smith', 'Olivia', NULL, '+12025550147', 'Контакт из США', 'Работа'),
    ('Dubois', 'Claire', NULL, '+33142278186', 'Контакт из Франции', 'Другое'),
    ('Silva', 'Mateus', NULL, '+5511912345678', 'Контакт из Бразилии', 'Работа'),
    ('月', '夜神', NULL, '+81312345678', 'Контакт из Японии', 'Другое'),
    ('Bjornsdottir', 'Eva', NULL, '+3545885522', 'Контакт из Исландии', 'Сервис');

CREATE VIEW vw_contacts_summary AS
SELECT 
    id,
    CONCAT(last_name, ' ', first_name, COALESCE(' ' || middle_name, '')) as full_name,
    phone_number,
    CASE 
        WHEN LENGTH(note) > 30 THEN CONCAT(LEFT(note, 30), '...')
        ELSE note
    END as note_short,
    contact_group,
    is_favorite,
    created_at
FROM contacts;
