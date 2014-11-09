from django.conf import settings
from django.conf.urls import include, url
from django.core import urlresolvers
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Permission

from wagtail.wagtailcore import hooks
from wagtail.wagtailadmin.menu import MenuItem

from wagtailcategories import urls
from wagtailcategories.permissions import user_can_edit_categories
from wagtailcategories.models import get_category_content_types


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^categories/', include(urls)),
    ]


class CategoriesMenuItem(MenuItem):
    def is_shown(self, request):
        return user_can_edit_categories(request.user)


@hooks.register('register_admin_menu_item')
def register_snippets_menu_item():
    return CategoriesMenuItem(_('Categories'),
                              urlresolvers.reverse('wagtailcategories_index'),
                              classnames='icon icon-doc-empty',
                              order=500)


@hooks.register('register_permissions')
def register_permissions():
    category_content_types = get_category_content_types()
    category_permissions = Permission.objects.filter(content_type__in=category_content_types)
    return category_permissions
