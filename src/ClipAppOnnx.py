from __future__ import annotations
from pathlib import Path
import platform, time

import os
os.environ["OPENCV_SKIP_CPU_BASELINE_CHECK"] = "1"
import cv2 as cv
import numpy as np
from PIL import ImageGrab
import onnxruntime as ort
from transformers import CLIPTokenizer


def get_model():
    onnx_path = Path(r".\openai_clip.onnx")                 # QDQ / quantised!
    assert onnx_path.exists(), f"Missing {onnx_path}"

    ort_dir  = Path(ort.__file__).parent
    qnn_dll  = ort_dir / "capi" / "QnnHtp.dll"

    sess = ort.InferenceSession(
        onnx_path,
        providers=[("QNNExecutionProvider", {"backend_path": str(qnn_dll)}),
                "CPUExecutionProvider"]
    )
    return sess

def get_tokenizer():
    return CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch16")

def encode_text(tokenizer, prompt: str) -> np.ndarray:
    """Return a (1,77) int32 tensor for CLIP."""
    ids = tokenizer(prompt,
                    padding="max_length",
                    truncation=True,
                    max_length=77,
                    return_tensors="np").input_ids
    return ids.astype(np.int32)

def preprocess_image(pil_img) -> np.ndarray:
    """PIL - (1,3,224,224) float32, NCHW, normalized."""
    img = cv.cvtColor(np.array(pil_img), cv.COLOR_RGB2BGR)
    img = cv.resize(img, (224, 224), interpolation=cv.INTER_CUBIC)
    img = img[:, :, ::-1]  # BGR→RGB
    img = img.astype(np.float32) / 255.0
    img = (img - [0.485,0.456,0.406]) / [0.229,0.224,0.225]
    chw  = np.transpose(img, (2,0,1))[None]          # (1,3,224,224)
    return chw.astype(np.float32)