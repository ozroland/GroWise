from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from apps.authentication.tokens import generate_token
import os
from django.contrib.messages import get_messages
import tempfile
from unittest.mock import patch

User = get_user_model()

class HomeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('home')
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='StrongPassword123!',
            is_active=True
        )

    def test_home_redirects_authenticated_user(self):
        self.client.login(email='testuser@example.com', password='StrongPassword123!')
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recognition', kwargs={'image_type': 'disease'}))

    def test_home_renders_for_anonymous_user(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')


class SignupViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')
        self.test_user_data = {
            'email': 'test@example.com',
            'fname': 'Test',
            'lname': 'User',
            'pass1': 'StrongPassword123!',
            'pass2': 'StrongPassword123!'
        }
        
    def test_signup_page_loads(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        
    def test_successful_signup(self):
        response = self.client.post(self.signup_url, self.test_user_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        self.assertEqual(len(mail.outbox), 1)
        
    def test_signup_with_existing_email(self):
        User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='StrongPassword123!'
        )
        
        response = self.client.post(self.signup_url, self.test_user_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.filter(email='test@example.com').count(), 1)
        
    def test_signup_with_mismatched_passwords(self):
        data = self.test_user_data.copy()
        data['pass2'] = 'DifferentPassword123!'
        
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(email='test@example.com').exists())
        
    def test_signup_with_weak_password(self):
        data = self.test_user_data.copy()
        data['pass1'] = data['pass2'] = '123456'
        
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(email='test@example.com').exists())

    @patch('apps.authentication.views.User.objects.create_user')
    @patch('apps.authentication.views.logger.error')
    def test_signup_with_exception_handling(self, mock_logger, mock_create_user):
        mock_create_user.side_effect = Exception("DB hiba")
        
        response = self.client.post(self.signup_url, self.test_user_data)
        
        self.assertEqual(response.status_code, 302)
        
        mock_logger.assert_called_once()
        log_message = mock_logger.call_args[0][0]
        self.assertIn("Regisztrációs hiba", log_message)
        self.assertIn(self.test_user_data['email'], log_message)
        self.assertIn("DB hiba", log_message)
        
        messages = list(get_messages(response.wsgi_request))
        error_message = next(
            (m for m in messages if "Valami hiba történt a regisztráció során" in str(m)),
            None
        )
        
        self.assertIsNotNone(error_message, "A hibaüzenet nem jelent meg a messages rendszerben")
        self.assertEqual(error_message.level_tag, 'error')
        
        self.assertEqual(User.objects.count(), 0)


class ActivateViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='inactive@example.com',
            email='inactive@example.com',
            password='StrongPassword123!',
            is_active=False
        )
        
    def test_successful_activation(self):
        token = generate_token.make_token(self.user)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        activation_url = reverse('activate', kwargs={'uidb64': uidb64, 'token': token})
        
        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, 302)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        
    def test_invalid_activation_link(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        activation_url = reverse('activate', kwargs={'uidb64': uidb64, 'token': 'invalid-token'})
        
        self.client.get(activation_url)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_activation_with_invalid_uid_raises_exception(self):
        invalid_uidb64 = '!!!invalid!!!'
        token = generate_token.make_token(self.user)

        activation_url = reverse('activate', kwargs={'uidb64': invalid_uidb64, 'token': token})
        response = self.client.get(activation_url)

        self.assertRedirects(response, reverse('login'))
        messages_list = list(response.wsgi_request._messages)
        self.assertTrue(any("Érvénytelen aktiválási link" in str(msg) for msg in messages_list))


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='StrongPassword123!',
            is_active=True
        )
        
    def test_login_page_loads(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        
    def test_successful_login(self):
        data = {
            'email': 'test@example.com',
            'pass1': 'StrongPassword123!'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        
    def test_login_with_incorrect_credentials(self):
        data = {
            'email': 'test@example.com',
            'pass1': 'WrongPassword123!'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
    def test_login_with_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        
        data = {
            'email': 'test@example.com',
            'pass1': 'StrongPassword123!'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_view_redirects_authenticated_user(self):
        self.client.login(username='test@example.com', password='StrongPassword123!')
        response = self.client.get(self.login_url)
        self.assertRedirects(response, reverse('recognition', kwargs={'image_type': 'disease'}))


class SignoutViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signout_url = reverse('signout')
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='StrongPassword123!',
            is_active=True
        )
        
    def test_successful_signout(self):
        self.client.login(username='test@example.com', password='StrongPassword123!')
        
        response = self.client.get(self.signout_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.profile_url = reverse('profile')
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='StrongPassword123!',
            first_name='Test',
            last_name='User',
            is_active=True
        )
        
    def test_profile_redirects_if_not_logged_in(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
        
    def test_profile_loads_if_logged_in(self):
        self.client.login(username='test@example.com', password='StrongPassword123!')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], self.user)


class ChangePasswordViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.change_password_url = reverse('change_password')
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='StrongPassword123!',
            is_active=True
        )
        
    def test_change_password_redirects_if_not_logged_in(self):
        response = self.client.get(self.change_password_url)
        self.assertEqual(response.status_code, 302)
        
    def test_successful_password_change(self):
        self.client.login(username='test@example.com', password='StrongPassword123!')
        
        data = {
            'old_password': 'StrongPassword123!',
            'new_password1': 'NewStrongPassword456!',
            'new_password2': 'NewStrongPassword456!'
        }
        
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, 302)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewStrongPassword456!'))

    def test_change_password_get_renders_form_for_logged_in_user(self):
        self.client.login(username='test@example.com', password='StrongPassword123!')
        response = self.client.get(self.change_password_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/profile.html')
        self.assertIn('form', response.context)

    def test_change_password_invalid_data_shows_errors(self):
        self.client.login(username='test@example.com', password='StrongPassword123!')

        data = {
            'old_password': 'WrongOldPassword!',
            'new_password1': 'NewStrongPassword456!',
            'new_password2': 'DoesNotMatch456!'
        }

        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/profile.html')

        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(form.errors)

class DownloadTermsPdfViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.terms_url = reverse('download_terms_pdf')
        self.temp_dir = tempfile.TemporaryDirectory()
        self.pdf_path = os.path.join(self.temp_dir.name, "terms_and_conditions.pdf")

        with open(self.pdf_path, "wb") as f:
            f.write(b"%PDF-1.4 dummy pdf content")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_terms_pdf_download(self):
        response = self.client.get(self.terms_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        content = b"".join(response.streaming_content)
        self.assertIn(b"%PDF", content)

        self.assertEqual(
            response.get('Content-Disposition'),
            'attachment; filename="ASZF_GroWise.pdf"'
        )

class CustomPasswordResetCompleteViewTest(TestCase):
    def setUp(self):
        self.client = self.client_class()
        self.reset_complete_url = reverse('password_reset_complete')
    
    def test_password_reset_complete_view(self):
        response = self.client.get(self.reset_complete_url)
        
        self.assertEqual(response.status_code, 302)
        
        storage = get_messages(response.wsgi_request)
        message = list(storage)[0]
        self.assertEqual(message.message, "A jelszavad sikeresen megváltozott! Most már bejelentkezhetsz.")
        
        self.assertRedirects(response, reverse('login'))


class CustomPasswordResetDoneViewTest(TestCase):
    def setUp(self):
        self.client = self.client_class()
        self.reset_done_url = reverse('password_reset_done')
    
    def test_password_reset_done_view(self):
        response = self.client.get(self.reset_done_url)
        
        self.assertEqual(response.status_code, 302)
        
        storage = get_messages(response.wsgi_request)
        message = list(storage)[0]
        self.assertEqual(message.message, "Elküldtük az email címedre a jelszó-visszaállítási linket!")
        
        self.assertRedirects(response, reverse('login'))
