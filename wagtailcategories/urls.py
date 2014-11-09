from django.conf.urls import url

from wagtailcategories import views

urlpatterns = [
    url(r'^$', views.index, name='wagtailcategories_index'),
    url(r'^(\w+)/(\w+)/$', views.list, name='wagtailcategories_list'),
    url(r'^(\w+)/(\w+)/new/$', views.create, name='wagtailcategories_create'),
    url(r'^(\w+)/(\w+)/(\d+)/$', views.edit, name='wagtailcategories_edit'),
    url(r'^(\w+)/(\w+)/(\d+)/delete/$', views.delete, name='wagtailcategories_delete'),
]
