from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.plant.models import Disease, Plant

User = get_user_model()

class PlantViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="Teszt felhasználó", 
            email="testuser@example.com", 
            password="testpassword123"
        )

        self.disease = Disease.objects.create(
            common_name="Tomato_Leaf_mold",
            common_name_hu="Paradicsom levélpenész",
            pathogen="Passalora fulva",
            type="Gombás",
            identification="Sárga foltok a felső oldalon, penészes bevonat az alsón",
            solutions="Szellőztetés, fungicidek (pl. klorotalonil)",
            host="Paradicsom",
            image="images/disease_images/Tomato_Leaf_mold.jpg"
        )

        self.plant = Plant.objects.create(
            botanical_name="Solanum lycopersicum",
            common_name="Paradicsom",
            family="Solanaceae",
            genus="Solanum",
            species="lycopersicum",
            uses="Friss fogyasztás, szószok, konzerv, levesek, ketchup.",
            distribution="Világszerte termesztik, különösen meleg éghajlaton.",
            image="images/plant_images/paradicsom.jpg"
        )

    def test_disease_list_authenticated(self):
        self.client.login(email="testuser@example.com", password="testpassword123")
        response = self.client.get(reverse('disease_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plant/disease_list.html')
        self.assertIn(self.disease, response.context['disease'])

    def test_disease_detail_authenticated(self):
        self.client.login(email="testuser@example.com", password="testpassword123")
        response = self.client.get(reverse('disease_detail', kwargs={'disease_id': self.disease.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plant/disease_detail.html')
        self.assertEqual(response.context['disease'], self.disease)

    def test_plant_list_authenticated(self):
        self.client.login(email="testuser@example.com", password="testpassword123")
        response = self.client.get(reverse('plant_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plant/plant_list.html')
        self.assertIn(self.plant, response.context['plant'])

    def test_plant_detail_authenticated(self):
        self.client.login(email="testuser@example.com", password="testpassword123")
        response = self.client.get(reverse('plant_detail', kwargs={'plant_id': self.plant.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plant/plant_detail.html')
        self.assertEqual(response.context['plant'], self.plant)

    def test_views_redirect_when_not_logged_in(self):
        urls = [
            reverse('disease_list'),
            reverse('disease_detail', kwargs={'disease_id': self.disease.id}),
            reverse('plant_list'),
            reverse('plant_detail', kwargs={'plant_id': self.plant.id}),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"{settings.LOGIN_URL}?next={url}")
