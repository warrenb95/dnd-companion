"""
Custom S3 storage backend for campaign media files.

Provides user and campaign-specific folder organization:
/user-{user_id}/campaigns/{campaign_id}/filename.ext
"""

import logging
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

logger = logging.getLogger(__name__)


class CampaignMediaStorage(S3Boto3Storage):
    """
    Custom S3 storage for campaign media files with organized folder structure.
    
    Files are stored in the pattern:
    user-{user_id}/campaigns/{campaign_id}/filename.ext
    """
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    region_name = settings.AWS_S3_REGION_NAME
    default_acl = None  # Disable ACL to avoid AccessControlListNotSupported error
    file_overwrite = False
    custom_domain = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info(f"CampaignMediaStorage initialized - Bucket: {self.bucket_name}, Region: {self.region_name}")
    
    def _save(self, name, content):
        """Override _save to add logging for S3 uploads."""
        try:
            logger.info(f"Starting S3 upload - File: {name}, Size: {content.size} bytes")
            result = super()._save(name, content)
            logger.info(f"S3 upload successful - File saved as: {result}")
            return result
        except Exception as e:
            logger.error(f"S3 upload failed - File: {name}, Error: {str(e)}")
            raise


def get_encounter_image_path(instance, filename):
    """
    Generate the upload path for encounter images.
    
    Args:
        instance: The Encounter model instance
        filename: The original filename
        
    Returns:
        String path in format: user-{user_id}/campaigns/{campaign_id}/filename
    """
    import os
    from django.utils.text import get_valid_filename
    
    try:
        # Get user ID from the encounter's campaign owner
        if hasattr(instance, 'chapter') and hasattr(instance.chapter, 'campaign'):
            user_id = instance.chapter.campaign.owner.id
            campaign_id = instance.chapter.campaign.id
            
            # Ensure we have valid IDs
            if user_id and campaign_id:
                # Sanitize filename
                clean_filename = get_valid_filename(filename)
                
                # Create organized path structure
                path = f"user-{user_id}/campaigns/{campaign_id}/{clean_filename}"
                
                logger.info(f"Generated upload path - User: {user_id}, Campaign: {campaign_id}, "
                           f"Original filename: {filename}, Clean filename: {clean_filename}, "
                           f"Final path: {path}")
                
                return path
        
        # If we can't get proper IDs, fall back to simple filename
        logger.warning(f"Could not generate organized path for {filename}, using simple filename")
        return get_valid_filename(filename)
        
    except Exception as e:
        logger.error(f"Error generating upload path - Instance: {instance}, "
                    f"Filename: {filename}, Error: {str(e)}")
        # Fallback to simple filename
        return get_valid_filename(filename)