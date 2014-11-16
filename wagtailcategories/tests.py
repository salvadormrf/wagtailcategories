from django.test import TestCase
from django.core.urlresolvers import reverse
from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.tests.utils import WagtailTestUtils

from wagtailcategories.models import register_category, CATEGORY_MODELS
from wagtailcategories.views import get_category_edit_handler

from wagtailcategories.models import BaseCategory, register_category

@register_category
class TestCategory(BaseCategory):
    some_field = models.CharField(max_length=100)
    
    class Meta:
        verbose_name='Test Category'
        verbose_name_plural='Test Categories'
        

class TestCategoryIndexView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def get(self, params={}):
        return self.client.get(reverse('wagtailcategories_index'), params)

    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailcategories/index.html')

    def test_displays_category(self):
        self.assertContains(self.get(), "Test Category")


class TestCategoryListView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()
    
    def get(self, params={}):
        return self.client.get(
            reverse('wagtailcategories_list', args=('wagtailcategories', 'testcategory')),
            params
        )
    
    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailcategories/type_index.html')
    
    def test_displays_add_button(self):
        self.assertContains(self.get(), "Add Test Category")


class TestCategoryCreateView(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()

    def get(self, params={}):
        return self.client.get(
            reverse('wagtailcategories_create', args=('wagtailcategories', 'testcategory')), 
            params)
    
    def post(self, post_data={}):
        return self.client.post(
            reverse('wagtailcategories_create', args=('wagtailcategories', 'testcategory')), 
            post_data)
    
    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailcategories/create.html')
    
    def test_create_invalid(self):
        response = self.post(post_data={'foo': 'bar'})
        self.assertContains(response, "The category could not be created due to errors.")
        self.assertContains(response, "This field is required.")
    
    def test_create(self):
        response = self.post(post_data={'category_name': 'test_category', 'some_field': 'hello'})
        self.assertRedirects(response, reverse('wagtailcategories_list', args=('wagtailcategories', 'testcategory')))
        
        categories = TestCategory.objects.filter(category_name='test_category')
        self.assertEqual(categories.count(), 1)


class TestCategoryEditView(TestCase, WagtailTestUtils):
    
    def setUp(self):
        self.test_category = TestCategory()
        self.test_category.category_name = 'test_category'
        self.test_category.some_field = 'hello'
        self.test_category.save()
        
        self.login()

    def get(self, params={}):
        return self.client.get(
            reverse('wagtailcategories_edit', args=('wagtailcategories', 'testcategory', self.test_category.id)), 
            params
        )
    
    def post(self, post_data={}):
        return self.client.post(
            reverse('wagtailcategories_edit', args=('wagtailcategories', 'testcategory', self.test_category.id)), 
            post_data
        )
        
    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wagtailcategories/edit.html')
    
    def test_non_existant_model(self):
        response = self.client.get(
            reverse('wagtailcategories_edit', args=('wagtailcategories', 'foo', self.test_category.id))
        )
        self.assertEqual(response.status_code, 404)

    def test_nonexistant_id(self):
        response = self.client.get(
            reverse('wagtailcategories_edit', args=('wagtailcategories', 'testcategory', 999999))
        )
        self.assertEqual(response.status_code, 404)
    
    def test_edit_invalid(self):
        response = self.post(post_data={'foo': 'bar'})
        self.assertContains(response, "The category could not be saved due to errors.")
        self.assertContains(response, "This field is required.")
        
    def test_edit(self):
        response = self.post(post_data={'category_name': 'test_category', 'some_field': 'hello'})
        self.assertRedirects(response, reverse('wagtailcategories_list', args=('wagtailcategories', 'testcategory')))
        
        categories = TestCategory.objects.filter(category_name='test_category')
        self.assertEqual(categories.count(), 1)
        self.assertEqual(categories.first().some_field, 'hello')
        

class TestCategoryDelete(TestCase, WagtailTestUtils):
    
    def setUp(self):
        self.test_category = TestCategory()
        self.test_category.category_name = 'test_category'
        self.test_category.some_field = 'hello'
        self.test_category.save()
        
        self.login()

    def test_delete_get(self):
        response = self.client.get(
            reverse('wagtailcategories_delete', args=('wagtailcategories', 'testcategory', self.test_category.id))
        )
        self.assertEqual(response.status_code, 200)
        
    def test_delete_post(self):
        post_data = {'foo': 'bar'}
        response = self.client.post(
            reverse('wagtailcategories_delete', args=('wagtailcategories', 'testcategory', self.test_category.id)), 
            post_data
        )
        self.assertRedirects(response, reverse('wagtailcategories_list', args=('wagtailcategories', 'testcategory')))
        self.assertEqual(TestCategory.objects.filter(category_name='test_category').count(), 0)


class TestCategoryRegistering(TestCase):
    
    def test_register_function(self):
        class RegisterFunction(models.Model):
            pass
        register_category(RegisterFunction)
        
        self.assertIn(RegisterFunction, CATEGORY_MODELS)
    
    def test_register_decorator(self):
        @register_category
        class RegisterDecorator(models.Model):
            pass
        # Misbehaving decorators often return None
        self.assertIsNotNone(RegisterDecorator)
        self.assertIn(RegisterDecorator, CATEGORY_MODELS)
        
