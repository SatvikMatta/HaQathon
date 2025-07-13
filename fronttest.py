from PIL import Image
import torch
from PIL import ImageGrab
from ClipApp import ClipApp, create_clip_app, simple_tokenizer, image_preprocessor

def create_qai_hub_clip() -> ClipApp:
    """Create ClipApp using QAI Hub OpenAI CLIP model"""
    from qai_hub_models.models.openai_clip.model import OpenAIClip
    clip_model = OpenAIClip.from_pretrained()
    app = ClipApp(
        model=clip_model,
        text_tokenizer=clip_model.text_tokenizer,
        image_preprocessor=clip_model.image_preprocessor
    )
    
    return app

def main():
    model  = create_qai_hub_clip()
    class_labels = [
        "code",
        "games",
        "video"
    ]
    screenshot = ImageGrab.grab()
    print(model.classify_single_image(screenshot, class_labels))

if __name__ == "__main__":
    main()