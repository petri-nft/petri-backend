import requests
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class CardGenerationService:
    """Service for calling the card generation microservice."""
    
    @staticmethod
    def generate_nft_card(tree_id: int, species: str, latitude: float, longitude: float, health_score: float):
        """
        Call the card generation service to generate NFT card image and metadata.
        
        Args:
            tree_id: ID of the tree
            species: Species of the tree
            latitude: Latitude of tree location
            longitude: Longitude of tree location
            health_score: Current health score
            
        Returns:
            dict with image_uri and metadata_uri
        """
        try:
            payload = {
                "tree_id": tree_id,
                "species": species,
                "latitude": latitude,
                "longitude": longitude,
                "health_score": health_score,
            }
            
            response = requests.post(
                f"{settings.CARD_GENERATION_SERVICE_URL}/api/generate",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                "image_uri": result.get("image_uri"),
                "metadata_uri": result.get("metadata_uri"),
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Card generation service error: {str(e)}")
            # Return mock data for hackathon
            return {
                "image_uri": f"https://placehold.co/400?text=Tree+{tree_id}",
                "metadata_uri": f"ipfs://QmMockMetadata{tree_id}",
            }


class HealthScoringService:
    """Service for calling the health scoring microservice."""
    
    @staticmethod
    def calculate_health_score(tree_id: int, weeks_since_planting: int, species: str, region: str = "temperate"):
        """
        Call the health scoring service to calculate current health score.
        
        Args:
            tree_id: ID of the tree
            weeks_since_planting: Weeks since tree was planted
            species: Species of the tree
            region: Region/climate zone
            
        Returns:
            dict with health_score and estimated_value
        """
        try:
            payload = {
                "tree_id": tree_id,
                "weeks_since_planting": weeks_since_planting,
                "species": species,
                "region": region,
            }
            
            response = requests.post(
                f"{settings.HEALTH_SCORING_SERVICE_URL}/api/calculate",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                "health_score": result.get("health_score", 100.0),
                "token_value": result.get("token_value", 100.0),
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Health scoring service error: {str(e)}")
            # Return default values for hackathon
            return {
                "health_score": 100.0,
                "token_value": 100.0,
            }
    
    @staticmethod
    def simulate_risk_event(tree_id: int, event_type: str = "drought"):
        """
        Simulate a risk event that affects health score.
        
        Args:
            tree_id: ID of the tree
            event_type: Type of event (drought, pest, disease, recovery)
            
        Returns:
            dict with new health_score and impact
        """
        try:
            payload = {
                "tree_id": tree_id,
                "event_type": event_type,
            }
            
            response = requests.post(
                f"{settings.HEALTH_SCORING_SERVICE_URL}/api/simulate-event",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                "health_score": result.get("health_score"),
                "impact": result.get("impact"),
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Health simulation service error: {str(e)}")
            return {
                "health_score": 100.0,
                "impact": 0.0,
            }
