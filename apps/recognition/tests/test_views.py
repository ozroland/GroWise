from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
import torch
from apps.recognition.models import Image, Result
from io import BytesIO
from PIL import Image as PILImage
from django.contrib.messages import get_messages

User = get_user_model()

class RecognitionViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="Teszt felhasználó", email="test@example.com", password="testpass123")
        self.client.login(email="test@example.com", password="testpass123")
        self.dummy_image = self._create_test_image_file()
        self.image_instance = Image.objects.create(
            user=self.user,
            image=self.dummy_image,
            image_type='disease'
        )

    def _create_test_image_file(self):
        image = PILImage.new('RGB', (100, 100))
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        return SimpleUploadedFile("test.jpg", buffer.read(), content_type="image/jpeg")

    def test_recognition_get_view(self):
        response = self.client.get(reverse('recognition', kwargs={'image_type': 'disease'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recognition/disease_recognition.html')

    def test_recognition_post_view_upload_image(self):
        with open(self.image_instance.image.path, 'rb') as img:
            response = self.client.post(reverse('recognition', kwargs={'image_type': 'disease'}), {
                'images': [img]
            }, format='multipart')
        self.assertEqual(response.status_code, 302)

    def test_recognition_exception_handling(self):
        with patch('logging.Logger.error') as mock_logger, \
            patch('django.contrib.messages.error') as mock_messages, \
            patch('django.db.models.Model.save', side_effect=Exception("Test error")):
            
            with open(self.image_instance.image.path, 'rb') as img:
                response = self.client.post(reverse('recognition', kwargs={'image_type': 'disease'}), {
                    'images': [img]
                }, format='multipart')
            
            mock_logger.assert_called_once()
            self.assertIn("Hiba történt a képek feltöltése közben: Test error", 
                        mock_logger.call_args[0][0])
            
            mock_messages.assert_called_once_with(
                response.wsgi_request, 
                "Hiba történt a képek feltöltése közben!"
            )
            
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse('recognition', kwargs={'image_type': 'disease'}))
            
            self.assertEqual(Image.objects.filter(user=self.user).count(), 1)


class EvaluateDiseaseViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="Teszt felhasználó", email="test@example.com", password="testpass123")
        self.client.login(email="test@example.com", password="testpass123")
        self.dummy_image = self._create_test_image_file()
        self.image_instance = Image.objects.create(
            user=self.user,
            image=self.dummy_image,
            image_type='disease'
        )
    
    def _create_test_image_file(self):
        image = PILImage.new('RGB', (100, 100))
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        return SimpleUploadedFile("test.jpg", buffer.read(), content_type="image/jpeg")
    
    @patch('apps.recognition.views.model')
    @patch('apps.recognition.views.transform')
    @patch('apps.recognition.views.to_device')
    def test_evaluate_disease(self, mock_to_device, mock_transform, mock_model):
        mock_tensor = MagicMock()
        mock_tensor.unsqueeze.return_value = mock_tensor
        mock_transform.return_value = mock_tensor
        mock_output = torch.tensor([[0.1]*9 + [0.9]])
        mock_model.return_value = mock_output
        mock_to_device.return_value = mock_tensor

        response = self.client.post(reverse('evaluate_disease'), {
            'selected_images': [self.image_instance.id]
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Result.objects.filter(image=self.image_instance).count(), 1)

    def test_evaluate_disease_get_request_redirects(self):
        response = self.client.get(reverse('evaluate_disease'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recognition', kwargs={'image_type': 'disease'}))

    def test_evaluate_disease_post_without_selected_images(self):
        response = self.client.post(reverse('evaluate_disease'), data={'selected_images': []})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recognition', kwargs={'image_type': 'disease'}))

    def test_evaluate_disease_skips_already_processed_images(self):
        self.image_instance.image_status = 'Feldolgozva'
        self.image_instance.save()

        response = self.client.post(reverse('evaluate_disease'), {
            'selected_images': [self.image_instance.id]
        })

        self.assertEqual(Result.objects.filter(image=self.image_instance).count(), 0)
        self.assertEqual(response.status_code, 302)

    @patch('apps.recognition.views.torch.no_grad')
    @patch('apps.recognition.views.PILImage.open')
    def test_disease_recognition_exception_handling(self, mock_pil_open, mock_no_grad):

        disease_image = Image.objects.create(
            user=self.user,
            image=self._create_test_image_file(),
            image_type='disease'
        )
        
        mock_pil_open.side_effect = Exception("Képfeldolgozási hiba")
        
        disease_url = reverse('evaluate_disease')
        
        with patch('apps.recognition.views.logger.error') as mock_logger:
            response = self.client.post(disease_url, {'selected_images': [disease_image.id]})
            
            mock_logger.assert_called_once()
            
            log_message = mock_logger.call_args[0][0]
            self.assertIn("Hiba történt a betegség felismerés közben", log_message)
            self.assertIn("Képfeldolgozási hiba", log_message)
        
        self.assertRedirects(response, reverse('recognition', kwargs={'image_type': 'disease'}))
        
        messages = list(response.wsgi_request._messages)
        error_message = next(
            (m for m in messages if "Hiba történt a betegség felismerés közben" in str(m)),
            None
        )
        
        self.assertIsNotNone(error_message, "A hibaüzenet nem jelent meg a messages rendszerben")
        self.assertEqual(error_message.level_tag, 'error')
        disease_image.refresh_from_db()
        self.assertNotEqual(disease_image.image_status, 'Feldolgozva')
        self.assertEqual(Result.objects.filter(image=disease_image).count(), 0)


class DeleteImagesViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="Teszt felhasználó", email="test@example.com", password="testpass123"
        )
        self.client.login(email="test@example.com", password="testpass123")
        self.image = Image.objects.create(
            user=self.user,
            image=self._create_test_image_file(),
            image_type='disease',
            image_status='Feldolgozva'
        )
        self.result = Result.objects.create(
            user=self.user,
            image=self.image,
            detected_disease="Teszt",
            disease_confidence_level=95
        )

    def _create_test_image_file(self):
        image = PILImage.new('RGB', (100, 100))
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        return SimpleUploadedFile("test.jpg", buffer.read(), content_type="image/jpeg")

    def test_delete_images(self):
        response = self.client.post(reverse('delete_images'), {
            'selected_images': [self.image.id],
            'image_type': 'disease'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Image.objects.filter(id=self.image.id).exists())
        self.assertFalse(Result.objects.filter(image=self.image).exists())

    def test_delete_images_with_no_selection(self):
        response = self.client.post(reverse('delete_images'), {
            'selected_images': [],
            'image_type': 'disease'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Image.objects.filter(id=self.image.id).exists())

    def test_delete_images_get_request_redirects(self):
        response = self.client.get(reverse('delete_images'), {'image_type': 'disease'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recognition', kwargs={'image_type': 'disease'}))

    @patch("django.core.files.storage.default_storage.exists", return_value=False)
    def test_delete_image_file_does_not_exist(self, mock_exists):
        response = self.client.post(reverse('delete_images'), {
            'selected_images': [self.image.id],
            'image_type': 'disease'
        })
        self.assertEqual(response.status_code, 302)
        mock_exists.assert_called_once()
        self.assertFalse(Image.objects.filter(id=self.image.id).exists())

    @patch("django.core.files.storage.default_storage.exists", return_value=True)
    def test_delete_image_with_file(self, mock_exists):
        self.image.image = 'user_uploads/test_image.jpg'
        self.image.save()

        response = self.client.post(reverse('delete_images'), {
            'selected_images': [self.image.id],
            'image_type': 'disease'
        })
        mock_exists.assert_called_once_with(self.image.image.path)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Image.objects.filter(id=self.image.id).exists())

    def test_delete_image_without_file(self):
        self.image.image = None
        self.image.save()

        response = self.client.post(reverse('delete_images'), {
            'selected_images': [self.image.id],
            'image_type': 'disease'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Image.objects.filter(id=self.image.id).exists())

    @patch('django.db.models.QuerySet.delete')
    @patch('apps.recognition.views.logger.error')
    def test_delete_images_exception_handling(self, mock_logger, mock_delete):
        mock_delete.side_effect = Exception("Törlési hiba")
        
        delete_url = reverse('delete_images')
        response = self.client.post(delete_url, {
            'selected_images': [self.image.id],
            'image_type': 'disease'
        })
        
        self.assertRedirects(response, reverse('recognition', kwargs={'image_type': 'disease'}))
        
        mock_logger.assert_called_once()
        expected_log_message = "Hiba történt a képek törlése közben: Törlési hiba"
        self.assertEqual(mock_logger.call_args[0][0], expected_log_message)
        
        messages = list(response.wsgi_request._messages)
        
        error_message = next(
            (m for m in messages if "Hiba történt a képek törlése közben" in str(m)),
            None
        )
        
        self.assertIsNotNone(error_message, "A hibaüzenet nem jelent meg a messages rendszerben")
        self.assertEqual(error_message.level_tag, 'error', "A hibaüzenet nem 'error' típusú")
        self.assertEqual(str(error_message), "Hiba történt a képek törlése közben!")


class EvaluatePlantViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="Teszt felhasználó", email="test@example.com", password="StrongPassword123!")
        self.client.login(email='test@example.com', password='StrongPassword123!')
        
        self.image = Image.objects.create(
            user=self.user,
            image=SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg"),
            image_type='plant',
            image_status='Feldolgozásra vár'
        )
        self.url = reverse('evaluate_plant')

    @patch('apps.recognition.views.requests.post')
    def test_successful_evaluation_creates_result(self, mock_post):
        mock_response_data = {
            "results": [
                {
                    "species": {
                        "commonNames": ["Tomato"]
                    },
                    "score": 0.87
                }
            ]
        }
        mock_post.return_value.json.return_value = mock_response_data

        response = self.client.post(self.url, data={'selected_images': [str(self.image.id)]})
        self.assertRedirects(response, reverse('recognition', kwargs={'image_type': 'plant'}))

        self.image.refresh_from_db()
        self.assertEqual(self.image.image_status, 'Feldolgozva')

        result = Result.objects.filter(image=self.image).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.detected_plant, 'Tomato')
        self.assertEqual(result.plant_confidence_level, 87.0)

    def test_post_without_selected_images_redirects(self):
        response = self.client.post(self.url, data={})
        self.assertRedirects(response, reverse('recognition', kwargs={'image_type': 'plant'}))

    def test_get_request_redirects(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('recognition', kwargs={'image_type': 'plant'}))

    @patch('apps.recognition.views.requests.post')
    def test_api_returns_no_results(self, mock_post):
        mock_post.return_value.json.return_value = {"results": []}
        response = self.client.post(self.url, data={'selected_images': [str(self.image.id)]})
        self.assertRedirects(response, reverse('recognition', kwargs={'image_type': 'plant'}))

        self.image.refresh_from_db()
        self.assertEqual(self.image.image_status, 'Feldolgozásra vár')
        self.assertFalse(Result.objects.exists())

    @patch('apps.recognition.views.requests.post')
    @patch('apps.recognition.views.logger.error')
    def test_evaluate_plant_api_failure(self, mock_logger, mock_post):
        mock_post.side_effect = Exception("API hiba")
        
        response = self.client.post(self.url, {'selected_images': [self.image.id]})
        
        self.assertRedirects(response, reverse('recognition', kwargs={'image_type': 'plant'}))
        
        mock_logger.assert_called_once()
        self.assertIn("API hiba", mock_logger.call_args[0][0])
        
        messages = list(response.wsgi_request._messages)
        error_message = next((m for m in messages if "Hiba történt a növény felismerés közben" in str(m)), None)
        
        self.assertIsNotNone(error_message, "A hibaüzenet nem jelent meg a messages rendszerben")
