from PIL import Image
import torch
from PIL import ImageGrab
from ClipApp import ClipApp, create_clip_app, simple_tokenizer, image_preprocessor
import Backend
from Backend import get_json_screenshot, screenshot

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
    screen = Backend.screenshot()
    clip_result = model.classify_single_image(screen, class_labels)
    clip_class = clip_result['predicted_class']
    print(clip_class)

    result = get_json_screenshot(screenshot=screen, clip_input=clip_class)
    print(result['classification'])


if __name__ == "__main__":
    main()