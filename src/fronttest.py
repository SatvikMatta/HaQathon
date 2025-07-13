from ClipAppOnnx import *
from PIL import ImageGrab
from PIL.Image import Image
from PIL import Image


# Initizalization
session = get_model()
tokenizer = get_tokenizer()

pil_shot = ImageGrab.grab()

img_name = session.get_inputs()[0].name                 # "images"
txt_name = session.get_inputs()[1].name                 # "texts"
out_name = session.get_outputs()[0].name                # "similarities"

def get_clip_inference():
    img_tensor = preprocess_image(pil_shot)
    
    labels = [
    "a web browser", "a terminal", "a YouTube video", "a game", "a cat", "a spreadsheet"
    ]

    scores = []
    for lbl in labels:
        txt_tensor = encode_text(tokenizer,lbl)
        sim = session.run([out_name],
                    {img_name: img_tensor,
                        txt_name: txt_tensor})[0]        # (1,1) ×100
        scores.append(float(sim.squeeze()))

    scores = np.array(scores)
    probs  = np.exp(scores/100 - scores.max()/100)
    probs /= probs.sum()

    best = int(scores.argmax())
    print("\n🧠  Classification result")
    print(f"   → label        : {labels[best]}")
    print(f"   → score (×100) : {scores[best]:.2f}")
    print(f"   → probability  : {probs[best]:.2%}")

    print("\n🔍  Full table")
    for lbl, sc, pb in zip(labels, scores, probs):
        print(f"   - {lbl:20s}: {sc:6.2f}   ({pb:.2%})")

get_clip_inference()