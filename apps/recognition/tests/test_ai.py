import os
import re
from django.test import TestCase
from PIL import Image as PILImage
import torch
from apps.core.model_loader import model, device, transform, disease_labels_hu, to_device

class DiseaseModelTestCase(TestCase):
    def setUp(self):
        self.test_image_dir = 'static/images/test'

        self.label_mapping = {
            "AppleScab": "Apple_Apple_scab",
            "AppleCedarRust": "Apple_Cedar_apple_rust",
            "CornCommonRust": "Corn_Common_rust",
            "PotatoEarlyBlight": "Potato_Early_blight",
            "PotatoHealthy": "Potato_Healthy",
            "TomatoEarlyBlight": "Tomato_Early_blight",
            "TomatoHealthy": "Tomato_Healthy",
            "TomatoYellowCurlVirus": "Tomato_Tomato_Yellow_leaf_curl_virus",
        }

    def extract_key_from_filename(self, filename):
        return re.sub(r'\d+', '', filename.split('.')[0])

    def test_model_predictions_against_expected_labels(self):
        failures = []

        for filename in os.listdir(self.test_image_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                file_path = os.path.join(self.test_image_dir, filename)
                key = self.extract_key_from_filename(filename)

                if key not in self.label_mapping:
                    continue

                expected_label_key = self.label_mapping[key]
                expected_label = disease_labels_hu.get(expected_label_key)

                img = PILImage.open(file_path).convert('RGB')
                img_tensor = transform(img)
                xb = to_device(img_tensor.unsqueeze(0), device)

                with torch.no_grad():
                    outputs = model(xb)
                    _, predicted = torch.max(outputs, dim=1)
                    predicted_class = predicted[0].item()

                label_keys = list(disease_labels_hu.keys())
                predicted_label_key = label_keys[predicted_class]
                predicted_label = disease_labels_hu[predicted_label_key]

                self.assertTrue(
                    expected_label and predicted_label, 
                    f"{filename}: Elvárt és kapott címke is hiányzik."
                )

                self.assertTrue(
                    expected_label.lower() in predicted_label.lower(),
                    f"{filename}: elvárt '{expected_label}', de kapott '{predicted_label}'"
                )

        if failures:
            self.fail("Néhány kép felismerése nem megfelelő:\n" + "\n".join(failures))
