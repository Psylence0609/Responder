from notion_client import Client
from config import NOTION_KEY, PAGE_ID


class NotionDB:
    def __init__(self, database_title="New Database"):
        self.notion = Client(auth=NOTION_KEY)
        self.parent_page_id = PAGE_ID
        self.database_title = database_title
        self.database_id = self.get_or_create_database()
    
    def get_or_create_database(self):
        # Check if database already exists in the parent page
        children = self.notion.blocks.children.list(self.parent_page_id)['results']

        for child in children:
            if child['object'] == 'block' and child['type'] == 'child_database':
                if child['child_database']['title'] == self.database_title:
                    return child['id']

        # If not found, create a new database
        properties = {
            'Name': {'title': {}},
            'Description': {'rich_text': {}},
            'Date': {'date': {}},
        }

        database = self.notion.databases.create(
            parent={'type': 'page_id', 'page_id': self.parent_page_id},
            title=[{'type': 'text', 'text': {'content': self.database_title}}],
            properties=properties
        )
        return database['id']
    
    def add_entry(self, name, description, date):
        new_page_properties = {
            'Name': {
                'title': [
                    {
                        'text': {
                            'content': name
                        }
                    }
                ]
            },
            'Description': {
                'rich_text': [
                    {
                        'text': {
                            'content': description
                        }
                    }
                ]
            },
            'Date': {
                'date': {
                    'start': date
                }
            }
        }

        self.notion.pages.create(
            parent={'database_id': self.database_id},
            properties=new_page_properties
        )

if __name__ == "__main__":
    db = NotionDB(database_title="My Task Table")
    db.add_entry(name="Sample Entry", description="This is a sample description.", date="2025-03-29")