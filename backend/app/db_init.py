from app.db import engine, Base
from app.models import train

print("🛠️ Création des tables manquantes...")
Base.metadata.create_all(bind=engine)
print("✅ Tables créées avec succès.")
