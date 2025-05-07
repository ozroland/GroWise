import torch
import os
from django.conf import settings
from .model_architecture import ResNet9
from torchvision import transforms

disease_labels_hu = {
    'Apple_Apple_scab': 'Alma - Varasodás', 
    'Apple_Black_rot': 'Alma - Fekete rothadás',
    'Apple_Cedar_apple_rust': 'Alma - Cédrus-almarozsda',
    'Apple_Healthy': 'Alma - Egészséges',
    'Cherry_Healthy': 'Cseresznye - Egészséges',
    'Cherry_Powdery_mildew': 'Cseresznye - Lisztharmat',
    'Corn_Common_rust': 'Kukorica - közönséges rozsdagomba',
    'Corn_Gray_leaf_spot': 'Kukorica - Cerkospórás levélfoltosság',
    'Corn_Healthy': 'Kukorica - Egészséges',
    'Corn_Northern_leaf_blight': 'Kukorica - Északi levélfoltosság',
    'Grape_Black_rot': 'Szőlő - Feketerothadás',
    'Grape_Esca': 'Szőlő - Esca (fekete kanyaró)',
    'Grape_Healthy': 'Szőlő - Egészséges',
    'Grape_Leaf_blight': 'Szőlő - Levélfoltosság',
    'Peach_Bacterial_spot': 'Őszibarack - Baktériumos levélfoltosság',
    'Peach_Healthy': 'Őszibarack - Egészséges',
    'Pepper_Bacterial_spot': 'Paprika - Baktériumos levélfoltosság',
    'Pepper_Healthy': 'Paprika - Egészséges',
    'Potato_Early_blight': 'Burgonya alternáriás levélfoltosság',
    'Potato_Healthy': 'Burgonya - Egészséges',
    'Potato_Late_blight': 'Burgonya - Burgonyavész',
    'Strawberry_Healthy': 'Eper - Egészséges',
    'Strawberry_Leaf_scorch': 'Eper - Levélszáradás',
    'Tomato_Bacterial_spot': 'Paradicsom - Baktériumos levélfoltosság',
    'Tomato_Early_blight': 'Paradicsom - alternáriás levélfoltosság',
    'Tomato_Healthy': 'Paradicsom - Egészséges',
    'Tomato_Late_blight': 'Paradicsom - Paradicsomvész',
    'Tomato_Leaf_Mold': 'Paradicsom - Levélpenész',
    'Tomato_Septoria_leaf_spot': 'Paradicsom - Szeptóriás levélfoltosság',
    'Tomato_Spider_mites': 'Paradicsom - Takácsatkák',
    'Tomato_Target_Spot': 'Paradicsom - Célfoltosság',
    'Tomato_Tomato_Yellow_leaf_curl_virus': 'Paradicsom - Sárga levélkunkorodás vírus',
    'Tomato_Tomato_mosaic_virus': 'Paradicsom - Mozaikvírus',
}


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_path = os.path.join(settings.BASE_DIR, 'plant-disease-model.pth')

model = ResNet9(3, len(disease_labels_hu ))
model.load_state_dict(torch.load(model_path, map_location=device))
model.to(device)
model.eval()

transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
])


def to_device(data, device):
    if isinstance(data, (list,tuple)):
        return [to_device(x, device) for x in data]
    return data.to(device, non_blocking=True)
