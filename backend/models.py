from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import re

ALL_GROUPS_LABEL = 'Все'
DEFAULT_CONTACT_GROUP = 'Общие'
CONTACT_GROUPS = [
    DEFAULT_CONTACT_GROUP,
    'Друзья',
    'Работа',
    'Семья',
    'Сервис',
    'Соседи',
    'Другое',
]

@dataclass
class Contact:
    id: Optional[int]
    last_name: str
    first_name: str
    middle_name: Optional[str]
    phone_number: str
    note: Optional[str]
    contact_group: str
    is_favorite: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)

    @property
    def formatted_phone(self) -> str:
        digits = re.sub(r'\D', '', self.phone_number)

        if len(digits) == 11:
            return f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
        return self.phone_number

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            last_name=data['last_name'],
            first_name=data['first_name'],
            middle_name=data.get('middle_name'),
            phone_number=data['phone_number'],
            note=data.get('note'),
            contact_group=data.get('contact_group', DEFAULT_CONTACT_GROUP),
            is_favorite=data.get('is_favorite', False),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

class ContactRepository:
    def __init__(self, db):
        self.db = db

    def get_all(self, group: Optional[str] = None, search: Optional[str] = None) -> List[Contact]:
        query = "SELECT * FROM contacts WHERE 1=1"
        params = []

        if group and group != ALL_GROUPS_LABEL:
            query += " AND contact_group = %s"
            params.append(group)

        if search:
            query += """ AND (
                last_name ILIKE %s OR 
                first_name ILIKE %s OR 
                phone_number ILIKE %s OR 
                note ILIKE %s
            )"""
            search_pattern = f'%{search}%'
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern])

        query += " ORDER BY is_favorite DESC, last_name, first_name"

        results = self.db.execute_query(query, params, fetch_all=True)
        return [Contact.from_dict(row) for row in results]

    def get_by_id(self, contact_id: int) -> Optional[Contact]:
        query = "SELECT * FROM contacts WHERE id = %s"
        result = self.db.execute_query(query, (contact_id,), fetch_one=True)
        return Contact.from_dict(result) if result else None

    def create(self, contact: Contact) -> int:
        query = """
            INSERT INTO contacts
            (last_name, first_name, middle_name, phone_number, note, contact_group, is_favorite)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        params = (
            contact.last_name, contact.first_name, contact.middle_name,
            contact.phone_number, contact.note, contact.contact_group,
            contact.is_favorite
        )
        result = self.db.execute_query(query, params, fetch_one=True)
        return result['id']

    def update(self, contact_id: int, contact: Contact) -> bool:
        query = """
            UPDATE contacts SET
                last_name = %s, first_name = %s, middle_name = %s,
                phone_number = %s, note = %s, contact_group = %s,
                is_favorite = %s
            WHERE id = %s
        """
        params = (
            contact.last_name, contact.first_name, contact.middle_name,
            contact.phone_number, contact.note, contact.contact_group,
            contact.is_favorite, contact_id
        )
        self.db.execute_query(query, params)
        return True

    def delete(self, contact_id: int) -> bool:
        query = "DELETE FROM contacts WHERE id = %s"
        self.db.execute_query(query, (contact_id,))
        return True

    def get_groups(self) -> List[str]:
        query = "SELECT DISTINCT contact_group FROM contacts ORDER BY contact_group"
        results = self.db.execute_query(query, fetch_all=True)
        existing_groups = [row['contact_group'] for row in results]
        ordered_groups = list(CONTACT_GROUPS)

        for group in existing_groups:
            if group not in ordered_groups:
                ordered_groups.append(group)

        return [ALL_GROUPS_LABEL] + ordered_groups

    def toggle_favorite(self, contact_id: int) -> bool:
        query = "UPDATE contacts SET is_favorite = NOT is_favorite WHERE id = %s"
        updated_rows = self.db.execute_query(query, (contact_id,), return_rowcount=True)
        return updated_rows > 0
