-- Создание таблицы контактов
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_favorite BOOLEAN DEFAULT FALSE,
    contact_group VARCHAR(50) DEFAULT 'Общие'
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
('Крючков', 'Евгений', 'Святославович', '+7 (999) 123-22-97', 'Одногруппник', 'Друзья'),
('Ефимов', 'Арсений', 'Максимович', '+7 (999) 439-11-66', 'Одноклассник', 'Друзья'),
('Филатова', 'Амина', 'Максимовна', '+7 (999) 999-99-99', 'Коллега', 'Работа'),
('Крылов', 'Михаил', 'Миронович', '+7 (999) 456-78-90', 'Сосед', 'Соседи'),
('Виноградова', 'Анастасия', 'Данииловна', '+7 (999) 167-09-01', 'Мастер маникюра', 'Сервис');

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
