"""
Utility functions for 360 Emlak Platform
"""
import os
import uuid
import hashlib
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
import bleach


def generate_id() -> str:
    """Generate unique ID"""
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """Generate short unique ID"""
    return uuid.uuid4().hex[:length]


def hash_password(password: str) -> str:
    """
    Hash password using SHA-256
    Note: In production, use bcrypt or similar
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_file(file, upload_folder: str, subfolder: str = '') -> str:
    """
    Save uploaded file and return filename
    
    Args:
        file: Werkzeug FileStorage object
        upload_folder: Base upload folder path
        subfolder: Optional subfolder
    
    Returns:
        str: Saved filename
    """
    if not file:
        return ''
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    unique_filename = f"{generate_short_id()}_{int(datetime.now().timestamp())}.{extension}"
    
    # Create full path
    if subfolder:
        save_folder = os.path.join(upload_folder, subfolder)
    else:
        save_folder = upload_folder
    
    os.makedirs(save_folder, exist_ok=True)
    
    file_path = os.path.join(save_folder, unique_filename)
    file.save(file_path)
    
    return unique_filename


def fix_image_orientation(image_path: str) -> bool:
    """
    Fix image orientation based on EXIF data
    
    Args:
        image_path: Path to image file
    
    Returns:
        bool: True if orientation was fixed
    """
    try:
        from PIL import ImageOps
        
        with Image.open(image_path) as img:
            # Check if image has EXIF data
            if hasattr(img, '_getexif') and img._getexif() is not None:
                # Apply EXIF orientation
                img = ImageOps.exif_transpose(img)
                img.save(image_path, quality=95, optimize=True)
                return True
    except Exception as e:
        print(f"Error fixing image orientation: {e}")
    
    return False


def resize_image(image_path: str, max_width: int = 1920, max_height: int = 1080, quality: int = 85):
    """
    Resize image while maintaining aspect ratio
    
    Args:
        image_path: Path to image file
        max_width: Maximum width
        max_height: Maximum height
        quality: JPEG quality (1-100)
    """
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Calculate new dimensions
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save with optimization
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
    except Exception as e:
        print(f"Error resizing image: {e}")


def create_thumbnail(source_path: str, thumbnail_path: str, size: tuple = (400, 300), quality: int = 85) -> bool:
    """
    Create thumbnail from image
    
    Args:
        source_path: Path to source image
        thumbnail_path: Path to save thumbnail
        size: Thumbnail size (width, height)
        quality: JPEG quality (1-100)
    
    Returns:
        bool: True if successful
    """
    try:
        with Image.open(source_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            img.save(thumbnail_path, 'JPEG', quality=quality, optimize=True)
            return True
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return False


def process_360_image(image_path: str, max_dimension: int = 8192) -> dict:
    """
    Process 360 panoramic image with EXIF fix and size validation
    
    Args:
        image_path: Path to image file
        max_dimension: Maximum width or height (default 8192px)
    
    Returns:
        dict: Processing result with width, height, and success status
    """
    result = {
        'success': False,
        'width': 0,
        'height': 0,
        'size_bytes': 0,
        'fixed_orientation': False,
        'resized': False
    }
    
    try:
        # Fix orientation first
        result['fixed_orientation'] = fix_image_orientation(image_path)
        
        with Image.open(image_path) as img:
            original_width, original_height = img.size
            result['width'] = original_width
            result['height'] = original_height
            
            # Check if resize needed
            if original_width > max_dimension or original_height > max_dimension:
                # Calculate new dimensions
                if original_width > original_height:
                    new_width = max_dimension
                    new_height = int(original_height * (max_dimension / original_width))
                else:
                    new_height = max_dimension
                    new_width = int(original_width * (max_dimension / original_height))
                
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Resize
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                img.save(image_path, 'JPEG', quality=90, optimize=True)
                
                result['width'] = new_width
                result['height'] = new_height
                result['resized'] = True
        
        # Get file size
        result['size_bytes'] = os.path.getsize(image_path)
        result['success'] = True
        
    except Exception as e:
        print(f"Error processing 360 image: {e}")
        result['error'] = str(e)
    
    return result


def sanitize_html(html_content: str, allowed_tags: list = None) -> str:
    """
    Sanitize HTML content
    
    Args:
        html_content: HTML string to sanitize
        allowed_tags: List of allowed HTML tags
    
    Returns:
        str: Sanitized HTML
    """
    if allowed_tags is None:
        allowed_tags = [
            'a', 'abbr', 'b', 'blockquote', 'br', 'code', 'div', 'em', 'h1', 'h2', 'h3',
            'h4', 'h5', 'h6', 'i', 'img', 'li', 'ol', 'p', 'pre', 'span', 'strong', 'ul',
            'table', 'tbody', 'td', 'th', 'thead', 'tr'
        ]
    
    allowed_attrs = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'width', 'height'],
        'div': ['class'],
        'span': ['class'],
        'p': ['class'],
        'h1': ['class'],
        'h2': ['class'],
        'h3': ['class'],
        'h4': ['class'],
        'h5': ['class'],
        'h6': ['class']
    }
    
    return bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attrs, strip=True)


def format_price(price: int) -> str:
    """Format price with thousand separators"""
    return f"{price:,}".replace(',', '.')


def format_date(date_string: str, format: str = '%d.%m.%Y') -> str:
    """
    Format ISO date string
    
    Args:
        date_string: ISO format date string
        format: Output format
    
    Returns:
        str: Formatted date
    """
    try:
        date_obj = datetime.fromisoformat(date_string)
        return date_obj.strftime(format)
    except:
        return date_string


def slugify(text: str) -> str:
    """
    Create URL-friendly slug from text
    
    Args:
        text: Input text
    
    Returns:
        str: Slugified text
    """
    # Turkish character mapping
    char_map = {
        'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c',
        'İ': 'i', 'Ğ': 'g', 'Ü': 'u', 'Ş': 's', 'Ö': 'o', 'Ç': 'c'
    }
    
    # Replace Turkish characters
    for turkish, english in char_map.items():
        text = text.replace(turkish, english)
    
    # Convert to lowercase and replace spaces with hyphens
    text = text.lower()
    text = ''.join(c if c.isalnum() or c in '-_' else '-' for c in text)
    
    # Remove consecutive hyphens
    while '--' in text:
        text = text.replace('--', '-')
    
    return text.strip('-')


def truncate_text(text: str, length: int = 100, suffix: str = '...') -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Input text
        length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        str: Truncated text
    """
    if len(text) <= length:
        return text
    
    return text[:length].rsplit(' ', 1)[0] + suffix


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Basic Turkish phone number validation"""
    import re
    # Remove spaces and common separators
    phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Turkish phone pattern: +90 or 0 followed by 10 digits
    pattern = r'^(\+90|0)?[1-9][0-9]{9}$'
    return bool(re.match(pattern, phone))
