import gradio as gr
import torch
import json
from PIL import Image
from torchvision import transforms

with open("classes.json") as f:
    classes = json.load(f)

model = torch.load("best_model.pth", map_location="cpu")
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], 
                        [0.229, 0.224, 0.225])
])

def predict(image):
    tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.softmax(outputs, dim=1)
        conf, idx = torch.max(probs, 1)
    return {
        "disease": classes[str(idx.item())],
        "confidence": round(conf.item(), 4)
    }

gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil"),
    outputs=gr.JSON(),
    title="Plant Disease Detection"
).launch()
