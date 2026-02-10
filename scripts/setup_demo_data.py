"""
Sample Data Generator for 360EV
Creates demo properties with placeholder images for development
"""
import json
import os
import shutil
from datetime import datetime
import uuid

def setup_sample_data():
    """Create sample properties and copy placeholder images"""
    
    # Sample property data
    sample_properties = [
        {
            "id": "demo-property-1",
            "user_id": "demo-user-1", 
            "title": "Denizli Yenişehir 2+1 Satılık Daire",
            "description": "Merkezi konumda, deniz manzaralı, modern 2+1 daire. Asansörlü binada, otopark dahil.",
            "category": "residential",
            "listing_type": "sale",
            "price": 480000,
            "city": "Denizli",
            "district": "Yenişehir", 
            "address": "Yenişehir Mahallesi, Atatürk Caddesi No:45",
            "area": 95,
            "rooms": "2+1",
            "floor": "3",
            "building_age": 5,
            "status": "active",
            "views": 147,
            "images": [
                {
                    "filename": "demo_photo_1.jpg",
                    "thumbnail": "demo_thumb_1.jpg", 
                    "order": 0
                },
                {
                    "filename": "demo_photo_2.jpg",
                    "thumbnail": "demo_thumb_2.jpg",
                    "order": 1
                }
            ],
            "tour": {
                "scenes": [
                    {
                        "id": "demo-scene-1",
                        "name": "Oturma Odası",
                        "filename": "demo_360_living.jpg",
                        "thumbnail": "demo_360_living_thumb.jpg",
                        "width": 4096,
                        "height": 2048,
                        "size": 1024000,
                        "hotspots": [],
                        "created_at": datetime.now().isoformat()
                    },
                    {
                        "id": "demo-scene-2", 
                        "name": "Mutfak",
                        "filename": "demo_360_kitchen.jpg",
                        "thumbnail": "demo_360_kitchen_thumb.jpg",
                        "width": 4096,
                        "height": 2048,
                        "size": 987000,
                        "hotspots": [],
                        "created_at": datetime.now().isoformat()
                    }
                ],
                "hotspots": []
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    # Sample user data
    sample_users = [
        {
            "id": "demo-user-1",
            "email": "ahmet.demo@360ev.com",
            "name": "Ahmet Yılmaz",
            "phone": "+90 532 123 45 67", 
            "role": "user",
            "password_hash": "demo_hash",
            "is_active": True,
            "email_verified": True,
            "bio": "Denizli bölgesinde 10 yıllık emlak deneyimi",
            "profession": "Emlak Danışmanı",
            "city": "Denizli",
            "photo_url": "/static/images/demo_avatar.jpg",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    return {
        "users": sample_users,
        "properties": sample_properties,
        "categories": [
            {"id": "residential", "name": "Konut"},
            {"id": "commercial", "name": "Ticari"},
            {"id": "land", "name": "Arsa"}
        ],
        "cities": ["Denizli", "İstanbul", "Ankara", "İzmir", "Antalya"]
    }

if __name__ == "__main__":
    data = setup_sample_data()
    
    # Save to data.json
    with open("../data/sample_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("✅ Demo veriler oluşturuldu: data/sample_data.json")
    print("📁 Placeholder resimler için static/images/placeholders/ klasörüne sample resimler ekleyin")