"""
File validation functions for campaign media uploads.

Provides validation for:
- File size (5MB limit)
- Image dimensions (6000x6000px limit)
- File types (JPG, PNG, WEBP only)
- MIME type checking
"""

import os
from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions


def validate_image_file_size(file):
    """
    Validate that uploaded file is under 5MB.
    
    Args:
        file: Django UploadedFile object
        
    Raises:
        ValidationError: If file exceeds 5MB limit
    """
    max_size_mb = 5
    max_size_bytes = max_size_mb * 1024 * 1024  # 5MB in bytes
    
    if file.size > max_size_bytes:
        raise ValidationError(
            f'File size ({file.size / (1024*1024):.1f}MB) exceeds maximum allowed size of {max_size_mb}MB.'
        )


def validate_image_dimensions(file):
    """
    Validate that image dimensions don't exceed 6000x6000 pixels.
    
    Args:
        file: Django UploadedFile object
        
    Raises:
        ValidationError: If image dimensions exceed limits
    """
    max_width = 6000
    max_height = 6000
    
    try:
        width, height = get_image_dimensions(file)
        if width is None or height is None:
            raise ValidationError('Unable to determine image dimensions. Please ensure the file is a valid image.')
            
        if width > max_width or height > max_height:
            raise ValidationError(
                f'Image dimensions ({width}x{height}px) exceed maximum allowed size of {max_width}x{max_height}px.'
            )
    except Exception as e:
        raise ValidationError(f'Error validating image dimensions: {str(e)}')


def validate_image_file_type(file):
    """
    Validate that uploaded file is a supported image type.
    
    Allowed types: JPG, JPEG, PNG, WEBP
    
    Args:
        file: Django UploadedFile object
        
    Raises:
        ValidationError: If file type is not supported
    """
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    allowed_content_types = [
        'image/jpeg',
        'image/png', 
        'image/webp'
    ]
    
    # Check file extension
    file_extension = os.path.splitext(file.name)[1].lower()
    if file_extension not in allowed_extensions:
        raise ValidationError(
            f'File type "{file_extension}" is not supported. '
            f'Allowed types: {", ".join(allowed_extensions)}'
        )
    
    # Check MIME type for additional security
    if hasattr(file, 'content_type') and file.content_type:
        if file.content_type not in allowed_content_types:
            raise ValidationError(
                f'File MIME type "{file.content_type}" is not supported. '
                f'Please upload a valid image file.'
            )


def validate_encounter_image(file):
    """
    Combined validator for encounter images.
    
    Validates file size, dimensions, and type.
    
    Args:
        file: Django UploadedFile object
        
    Raises:
        ValidationError: If any validation fails
    """
    validate_image_file_type(file)
    validate_image_file_size(file)
    validate_image_dimensions(file)