from django.test import TestCase
from django.urls import reverse
from taxi.models import Manufacturer, Car, Driver
from django.contrib.auth import get_user_model


class ManufacturerListViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )
        self.client.force_login(self.user)
        Manufacturer.objects.create(name="BMW", country="Germany")
        Manufacturer.objects.create(name="Toyota", country="Japan")

    def test_manufacturer_filter_by_name(self):
        response = self.client.get(reverse("taxi:manufacturer-list"),
                                   {"name": "BM"})
        self.assertContains(response, "BMW")
        self.assertNotContains(response, "Toyota")


class CarListViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )
        self.client.force_login(self.user)
        manufacturer = Manufacturer.objects.create(
            name="BMW", country="Germany"
        )
        Car.objects.create(model="X5", manufacturer=manufacturer)
        Car.objects.create(model="Corolla", manufacturer=manufacturer)

    def test_car_filter_by_model(self):
        response = self.client.get(reverse("taxi:car-list"), {"model": "X"})
        self.assertContains(response, "X5")
        self.assertNotContains(response, "Corolla")


class DriverListViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="admin", password="testpass"
        )
        self.client.force_login(self.user)
        get_user_model().objects.create_user(
            username="john", password="123", license_number="1111"
        )
        get_user_model().objects.create_user(
            username="alex", password="123", license_number="2222"
        )

    def test_driver_filter_by_username(self):
        response = self.client.get(reverse(
            "taxi:driver-list"), {"username": "jo"}
        )
        self.assertContains(response, "john")
        self.assertNotContains(response, "alex")


class ToggleAssignToCarTest(TestCase):
    def setUp(self):
        self.driver = get_user_model().objects.create_user(
            username="driver1", password="testpass", license_number="123456"
        )
        self.client.force_login(self.driver)
        self.manufacturer = Manufacturer.objects.create(
            name="BMW", country="Germany"
        )
        self.car = Car.objects.create(
            model="X5", manufacturer=self.manufacturer
        )

    def test_toggle_assign_adds_car(self):
        self.client.post(reverse(
            "taxi:toggle-car-assign", args=[self.car.id])
        )
        self.assertIn(self.car, self.driver.cars.all())

    def test_toggle_assign_removes_car(self):
        self.driver.cars.add(self.car)
        self.client.post(reverse("taxi:toggle-car-assign", args=[self.car.id]))
        self.assertNotIn(self.car, self.driver.cars.all())
