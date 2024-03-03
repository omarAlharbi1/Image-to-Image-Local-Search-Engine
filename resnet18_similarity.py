import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms, models
import numpy as np
from PIL import Image


def compare_images(image_path1, image_path2):
    device='cuda' if torch.cuda.is_available() else 'cpu'
    # Load pre-trained ResNet model
    model = models.resnet18(weights='ResNet18_Weights.DEFAULT')
    model = nn.Sequential(*list(model.children())[:-1]).to(device)  # Move model to GPU if available
    model.eval()

    # Preprocess input image
    def preprocess_image(image_path):
        image = Image.open(image_path).convert('RGB')
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        input_tensor = transform(image).unsqueeze(0).to(device)  # Move input tensor to GPU if available
        return input_tensor

    # Load two sample images
    input_tensor1 = preprocess_image(image_path1)
    input_tensor2 = preprocess_image(image_path2)

    # Forward pass to extract features
    with torch.no_grad():
        features1 = model(input_tensor1)
        features2 = model(input_tensor2)

    # Flatten and normalize the features
    features1 = features1.squeeze().cpu().numpy()  # Move back to CPU for numpy operations
    features2 = features2.squeeze().cpu().numpy()
    features1 /= np.linalg.norm(features1)
    features2 /= np.linalg.norm(features2)

    # Compute cosine similarity
    similarity = np.dot(features1, features2)
    
    return similarity