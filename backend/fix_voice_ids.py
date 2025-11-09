#!/usr/bin/env python
"""
Fix invalid voice IDs in the database.
Maps old voice IDs to valid ones that work with current ElevenLabs API.
"""

from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.models import TreePersonality
from app.services.ai_service import TTSService

# Mapping of old (invalid) voice IDs to new (valid) ones
VOICE_ID_MAPPING = {
    "2EiwWnXFnvU5JabPnXlx": TTSService.AVAILABLE_VOICES["Ember"]["voice_id"],  # Clyde -> Ember
    "JZ8chara1Hjw9IUgr9eb": TTSService.AVAILABLE_VOICES["Rachel"]["voice_id"],  # Grace -> Rachel
    "SAz9YHcvj6GT2YYXdXnW": TTSService.AVAILABLE_VOICES["Bella"]["voice_id"],   # River -> Bella
}

def fix_voice_ids():
    """Fix all invalid voice IDs in the database."""
    db = SessionLocal()
    
    try:
        # Find all personalities with invalid voice IDs
        personalities = db.query(TreePersonality).all()
        
        updated_count = 0
        for personality in personalities:
            if personality.voice_id in VOICE_ID_MAPPING:
                old_voice_id = personality.voice_id
                new_voice_id = VOICE_ID_MAPPING[old_voice_id]
                
                personality.voice_id = new_voice_id
                db.add(personality)
                updated_count += 1
                
                print(f"✓ Tree {personality.tree_id} ({personality.name}): "
                      f"{old_voice_id[:10]}... → {new_voice_id[:10]}...")
        
        db.commit()
        print(f"\n✓ Updated {updated_count} personalities")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Fixing invalid voice IDs in database...\n")
    fix_voice_ids()
