from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.contrib.messages import get_messages
from unittest.mock import patch


class ContactViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.contact_url = reverse('contact')
        self.valid_form_data = {
            'name': 'Teszt Felhasználó',
            'email': 'teszt@example.com',
            'message': 'Ez egy teszt üzenet a kapcsolatfelvételi űrlapról.'
        }

    def test_contact_page_loads_with_get_request(self):
        response = self.client.get(self.contact_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_contact_form_submits_successfully(self):
        response = self.client.post(self.contact_url, self.valid_form_data)
        
        self.assertRedirects(response, reverse('home'))
        
        self.assertEqual(len(mail.outbox), 1)
        
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.subject, 'Kapcsolatfelvétel a weboldalról')
        self.assertIn('Teszt Felhasználó', sent_email.body)
        self.assertIn('teszt@example.com', sent_email.body)
        self.assertIn('Ez egy teszt üzenet', sent_email.body)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Az üzenetet sikeresen elküldtük!')

    @patch("apps.core.views.send_mail", return_value=0)
    def test_contact_form_fails_to_send_email(self, mock_send_mail):
        response = self.client.post(self.contact_url, self.valid_form_data)

        self.assertRedirects(response, reverse('home'))
        self.assertEqual(len(mail.outbox), 0)

        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Hiba történt az üzenet küldésekor.")

    @patch("apps.core.views.send_mail", side_effect=Exception("SMTP error"))
    def test_contact_form_raises_exception_during_send(self, mock_send_mail):
        response = self.client.post(self.contact_url, self.valid_form_data)

        self.assertRedirects(response, reverse('home'))

        self.assertEqual(len(mail.outbox), 0)

        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Hiba történt az üzenet küldésekor.")


class InfoPagesViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_leaf_disease_info_page_loads(self):
        url = reverse('leaf_disease_info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/leaf_disease_info.html')
        
    def test_plant_identifier_info_page_loads(self):
        url = reverse('plant_identifier_info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/plant_identifier_info.html')
        
    def test_plant_database_info_page_loads(self):
        url = reverse('plant_database_info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/plant_database_info.html')
