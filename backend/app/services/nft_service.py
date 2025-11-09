import os
import json
import logging
from PIL import Image, ImageDraw, ImageFont, ImageOps
from datetime import datetime

logger = logging.getLogger(__name__)


class NFTGenerationService:
    """Service for generating NFT images and metadata."""
    
    # Static file paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    IMAGES_DIR = os.path.join(STATIC_DIR, 'images')
    METADATA_DIR = os.path.join(STATIC_DIR, 'metadata')
    
    # Image generation constants
    BOX_SIZE = (400, 400)
    BOX_POSITION = (100, 180)
    
    def __init__(self):
        """Initialize and ensure directories exist."""
        os.makedirs(self.IMAGES_DIR, exist_ok=True)
        os.makedirs(self.METADATA_DIR, exist_ok=True)
        logger.info(f"NFT Service initialized. Static dir: {self.STATIC_DIR}")
    
    @staticmethod
    def _load_template():
        """Load the template image."""
        template_path = os.path.join(
            NFTGenerationService.BASE_DIR,
            'template.png'
        )
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template image not found: {template_path}")
        return Image.open(template_path).convert("RGBA")
    
    @staticmethod
    def _get_font(font_size=48):
        """Load font for text overlay."""
        font_path = os.path.join(
            NFTGenerationService.BASE_DIR,
            'arial.ttf'
        )
        try:
            return ImageFont.truetype(font_path, font_size)
        except IOError:
            logger.warning(f"Font not found: {font_path}. Using default font.")
            return ImageFont.load_default()
    
    @classmethod
    def generate_nft_image(cls, user_image_file, tree_id: str) -> str:
        """
        Generate NFT image by pasting user image onto template.
        
        Args:
            user_image_file: File-like object containing the user's image
            tree_id: Unique identifier for the tree
            
        Returns:
            Path to the generated NFT image
        """
        try:
            # Load template
            nft_image = cls._load_template()
            
            # Read file content if it's a SpooledTemporaryFile
            if hasattr(user_image_file, 'read'):
                file_content = user_image_file.read()
                from io import BytesIO
                user_image = Image.open(BytesIO(file_content)).convert("RGBA")
            else:
                # Load and prepare user image
                user_image = Image.open(user_image_file).convert("RGBA")
            
            # Resize user image to fit box (1:1 square)
            user_image_fitted = ImageOps.fit(
                user_image,
                cls.BOX_SIZE,
                centering=(0.5, 0.5)
            )
            
            # Paste user image onto template
            nft_image.paste(user_image_fitted, cls.BOX_POSITION, user_image_fitted)
            
            # Save final NFT image
            output_image_path = os.path.join(cls.IMAGES_DIR, f"{tree_id}.png")
            nft_image.convert("RGB").save(output_image_path)
            
            logger.info(f"Generated NFT image for tree {tree_id}: {output_image_path}")
            return output_image_path
            
        except Exception as e:
            logger.error(f"Error generating NFT image for tree {tree_id}: {e}")
            raise
    
    @classmethod
    def generate_metadata(
        cls,
        tree_id: str,
        species: str,
        health_score: float,
        planting_date: datetime,
        base_url: str,
        description: str = None
    ) -> str:
        """
        Generate NFT metadata JSON file.
        
        Args:
            tree_id: Unique identifier for the tree
            species: Tree species
            health_score: Current health score of the tree
            planting_date: Date when tree was planted
            base_url: Base URL for image and metadata URLs
            description: Optional description of the tree
            
        Returns:
            Path to the generated metadata file
        """
        try:
            base_url = base_url.rstrip('/')
            image_url = f"{base_url}/static/images/{tree_id}.png"
            
            metadata = {
                "name": f"Petri TreeToken #{tree_id}",
                "description": description or f"A living digital asset for a {species}.",
                "image": image_url,
                "attributes": [
                    {"trait_type": "Health Score", "value": str(health_score)},
                    {"trait_type": "Species", "value": species},
                    {"trait_type": "Planted", "value": planting_date.isoformat()},
                    {"trait_type": "Generated", "value": datetime.utcnow().isoformat()}
                ]
            }
            
            metadata_path = os.path.join(cls.METADATA_DIR, f"{tree_id}.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Generated metadata for tree {tree_id}: {metadata_path}")
            return metadata_path
            
        except Exception as e:
            logger.error(f"Error generating metadata for tree {tree_id}: {e}")
            raise
    
    @classmethod
    def get_image_url(cls, tree_id: str, base_url: str) -> str:
        """Get the URL for a generated NFT image."""
        base_url = base_url.rstrip('/')
        return f"{base_url}/static/images/{tree_id}.png"
    
    @classmethod
    def get_metadata_url(cls, tree_id: str, base_url: str) -> str:
        """Get the URL for generated metadata."""
        base_url = base_url.rstrip('/')
        return f"{base_url}/static/metadata/{tree_id}.json"
