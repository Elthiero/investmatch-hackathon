import json
import argparse
from database import engine, SessionLocal, Base
from models import ForensicTool 

def init_db():
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def load_from_json(file_path: str):
    print(f"Reading data from {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tools_data = json.load(f)
    except Exception as e:
        print(f"File Error: {e}")
        return

    db = SessionLocal()
    try:
        inserted_count = 0
        for item in tools_data:
            existing = db.query(ForensicTool).filter(ForensicTool.name == item['name']).first()
            if existing:
                continue

            new_tool = ForensicTool(
                name=item.get('name', '').strip(),
                vendor=item.get('vendor', 'Unknown'),
                url=item.get('url', '#'),
                capability_tags=item.get('capability_tags', []),
                jurisdictional_legality=item.get('jurisdictional_legality', 'Unknown'),
                evidentiary_admissibility=item.get('evidentiary_admissibility', 'Unknown'),
                cost_and_licensing=item.get('cost_and_licensing', 'Unknown'),
                access_restrictions=item.get('access_restrictions', 'Public'),
                skill_level=item.get('skill_level', 'Beginner').lower(),
                platform_and_integration=item.get('platform_and_integration', 'Unknown'),
                region=item.get('region', 'Unknown'),
                investigation_type=item.get('investigation_type', 'Unknown'),
                last_verified=item.get('last_verified', 'Unknown'),
                documentation_and_support=item.get('documentation_and_support', 'Unknown'),
                additional_metadata=item.get('additional_metadata', {})
            )
            db.add(new_tool)
            inserted_count += 1
            
        db.commit()
        print(f"Success! Bulk inserted {inserted_count} new tools.")
    except Exception as e:
        db.rollback()
        print(f"DB Error: {e}")
    finally:
        db.close()

def list_tools():
    db = SessionLocal()
    try:
        tools = db.query(ForensicTool).all()
        print(f"\n--- Forensic Tools in Database ({len(tools)} total) ---")
        for tool in tools:
            print(f"- {tool.name} (Vendor: {tool.vendor})")
    finally:
        db.close()

def clear_db():
    confirm = input("Are you sure you want to delete ALL tools? (y/N): ")
    if confirm.lower() == 'y':
        db = SessionLocal()
        try:
            db.query(ForensicTool).delete()
            db.commit()
            print("Database cleared.")
        except Exception as e:
            db.rollback()
            print(f"Error: {e}")
        finally:
            db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--load", type=str, metavar="FILE.json")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--clear", action="store_true")
    args = parser.parse_args()

    if args.init: init_db()
    elif args.load: load_from_json(args.load)
    elif args.list: list_tools()
    elif args.clear: clear_db()
    else: parser.print_help()