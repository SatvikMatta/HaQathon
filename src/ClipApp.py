from __future__ import annotations
from typing import Sequence, List, Dict, Callable
from pathlib import Path
import torch
from PIL.Image import Image
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

# QAI Hub imports (optional - will fallback if not available)
try:
    from qai_hub_models.utils.asset_loaders import load_image
    QAI_HUB_AVAILABLE = True
except ImportError:
    QAI_HUB_AVAILABLE = False

# Type hint for the model protocol
try:
    from qai_hub_models.models.openai_clip.model import ExecutableModelProtocol
except ImportError:
    # Fallback type hint if QAI Hub not available
    from typing import Protocol
    class ExecutableModelProtocol(Protocol):
        def __call__(self, images: torch.Tensor, texts: torch.Tensor) -> torch.Tensor: ...


class ClipApp:
    """
    This class consists of light-weight "app code" that is required to perform end to end inference with Clip.

    The app uses 1 model:
        * Clip

    For a given image input, the app will:
        * pre-process the image
        * pre-process the text
        * Run Clip inference
    """

    def __init__(
        self,
        # Model has two inputs:
        #  - image (N, 3, H, W), RGB, float[0:1]
        #  - tokenized text (N, 77)
        model: ExecutableModelProtocol[torch.Tensor],
        text_tokenizer: Callable[[str], torch.Tensor],
        image_preprocessor: Callable[[Image], torch.Tensor],
    ):
        self.model = model
        self.text_tokenizer = text_tokenizer
        self.image_preprocessor = image_preprocessor

    def predict(self, *args, **kwargs):
        # See predict_similarity.
        return self.predict_similarity(*args, **kwargs)

    def predict_similarity(
        self, images_or_image_paths: Sequence[Image | str | Path], texts: Sequence[str]
    ) -> torch.Tensor:
        """
        Inputs:
            images_or_image_paths: PIL Image objects or paths to image files.
            texts: String texts to search for similarity.

        Outputs:
            cosine_similarities_per_image: torch.Tensor (Shape: [num_images, num_text_prompts])
                Given a batch of images and a batch of text tokens, returns a tensor,
                containing the cosine similarity scores corresponding to each image per text input.
                The values are cosine similarities between the corresponding image and
                text features, times 100. The cosine similarities of text per image can be computed
                by doing a transpose.
        """
        preprocessed_images: list[torch.Tensor] = []

        # Process each image to be a tensor of shape [NImages, 3, 224, 224] with layout RGB and range [0 - 1]
        for image_or_path in images_or_image_paths:
            # Handle both PIL Images and file paths
            if isinstance(image_or_path, str) or isinstance(image_or_path, Path):
                # Use QAI Hub's load_image if available, otherwise fallback to PIL
                if QAI_HUB_AVAILABLE:
                    image = load_image(image_or_path)
                else:
                    image = Image.open(image_or_path)
            else:
                # Already a PIL Image
                image = image_or_path
            
            preprocessed_images.append(self.image_preprocessor(image))
        preprocessed_stacked_images = torch.stack(preprocessed_images)

        # Tokenize string text to shape [NTexts, 77]
        preprocessed_texts: list[torch.Tensor] = [self.text_tokenizer(x) for x in texts]
        preprocessed_stacked_texts = torch.cat(preprocessed_texts)

        return self.model(preprocessed_stacked_images, preprocessed_stacked_texts)

    def classify_single_image(self, image_or_path: Image | str | Path, class_labels: List[str]) -> Dict:
        """
        Classify a single image against multiple text labels
        Returns the most likely class with confidence scores
        """
        similarities = self.predict_similarity([image_or_path], class_labels)
        
        # Get probabilities using softmax
        probabilities = F.softmax(similarities[0] / 100.0, dim=0)  # Divide by 100 since similarities are scaled
        
        # Get the best match
        best_idx = similarities[0].argmax().item()
        best_class = class_labels[best_idx]
        best_score = similarities[0, best_idx].item()
        best_probability = probabilities[best_idx].item()
        
        # Create results dictionary
        results = {
            'predicted_class': best_class,
            'confidence_score': best_score,
            'probability': best_probability,
            'all_scores': {label: score.item() for label, score in zip(class_labels, similarities[0])},
            'all_probabilities': {label: prob.item() for label, prob in zip(class_labels, probabilities)}
        }
        
        return results
    
    def classify_multiple_images(self, images_or_paths: List[Image | str | Path], class_labels: List[str]) -> List[Dict]:
        """
        Classify multiple images against the same set of class labels
        """
        similarities = self.predict_similarity(images_or_paths, class_labels)
        
        results = []
        for i, image_or_path in enumerate(images_or_paths):
            # Get probabilities for this image
            probabilities = F.softmax(similarities[i] / 100.0, dim=0)
            
            # Get the best match for this image
            best_idx = similarities[i].argmax().item()
            best_class = class_labels[best_idx]
            best_score = similarities[i, best_idx].item()
            best_probability = probabilities[best_idx].item()
            
            # Create results for this image
            image_results = {
                'image_input': image_or_path,  # Keep original input (path or Image)
                'predicted_class': best_class,
                'confidence_score': best_score,
                'probability': best_probability,
                'all_scores': {label: score.item() for label, score in zip(class_labels, similarities[i])},
                'all_probabilities': {label: prob.item() for label, prob in zip(class_labels, probabilities)}
            }
            
            results.append(image_results)
        
        return results
    
    def get_top_k_predictions(self, image_or_path: Image | str | Path, class_labels: List[str], k: int = 3) -> List[Dict]:
        """
        Get top-k predictions for a single image
        """
        similarities = self.predict_similarity([image_or_path], class_labels)
        probabilities = F.softmax(similarities[0] / 100.0, dim=0)
        
        # Get top-k indices
        top_k_indices = similarities[0].topk(k).indices
        
        top_predictions = []
        for idx in top_k_indices:
            idx = idx.item()
            top_predictions.append({
                'class': class_labels[idx],
                'confidence_score': similarities[0, idx].item(),
                'probability': probabilities[idx].item()
            })
        
        return top_predictions


def simple_tokenizer(text: str) -> torch.Tensor:
    """Simple tokenizer that creates a tensor of shape [1, 77]"""
    tokens = torch.randint(0, 1000, (1, 77))
    return tokens


def image_preprocessor(image: Image.Image) -> torch.Tensor:
    """Preprocesses image to tensor of shape [3, 224, 224]"""
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    tensor = transform(image)
    return tensor


# Initialize everything
def create_clip_app(model, text_tokenizer=None, image_preprocessor=None):
    """Factory function to create the CLIP app"""
    clip_app = ClipApp(
        model=model,
        text_tokenizer=text_tokenizer or simple_tokenizer,
        image_preprocessor=image_preprocessor or image_preprocessor
    )
    
    return clip_app