from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.encoding import force_text
from django.utils.text import capfirst
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from wagtail.wagtailadmin.edit_handlers import ObjectList, extract_panel_definitions_from_model_class

from wagtailcategories.models import get_category_content_types
from wagtailcategories.permissions import user_can_edit_category_type


# == Helper functions ==


def get_category_type_name(content_type):
    """ e.g. given the 'advert' content type, return ('Advert', 'Adverts') """
    opts = content_type.model_class()._meta
    return (
        force_text(opts.verbose_name),
        force_text(opts.verbose_name_plural)
    )


def get_category_type_description(content_type):
    """ return the meta description of the class associated with the given content type """
    opts = content_type.model_class()._meta
    try:
        return force_text(opts.description)
    except:
        return ''


def get_content_type_from_url_params(app_name, model_name):
    """
    retrieve a content type from an app_name / model_name combo.
    Throw Http404 if not a valid category type
    """
    try:
        content_type = ContentType.objects.get_by_natural_key(app_name, model_name)
    except ContentType.DoesNotExist:
        raise Http404
    if content_type not in get_category_content_types():
        # don't allow people to hack the URL to edit content types that aren't registered as categories
        raise Http404

    return content_type


CATEGORY_EDIT_HANDLERS = {}


def get_category_edit_handler(model):
    if model not in CATEGORY_EDIT_HANDLERS:
        panels = extract_panel_definitions_from_model_class(model, ['site'])
        edit_handler = ObjectList(panels)

        CATEGORY_EDIT_HANDLERS[model] = edit_handler

    return CATEGORY_EDIT_HANDLERS[model]


# == Views ==


@permission_required('wagtailadmin.access_admin')
def index(request):
    category_types = [
        (
            get_category_type_name(content_type)[0],
            get_category_type_description(content_type),
            content_type
        )
        for content_type in get_category_content_types()
        if user_can_edit_category_type(request.user, content_type)
    ]
    return render(request, 'wagtailcategories/index.html', {
        'category_types': category_types,
    })


@permission_required('wagtailadmin.access_admin')  # further permissions are enforced within the view
def list(request, content_type_app_name, content_type_model_name):
    content_type = get_content_type_from_url_params(content_type_app_name, content_type_model_name)
    if not user_can_edit_category_type(request.user, content_type):
        raise PermissionDenied
    
    model = content_type.model_class()
    category_type_name, category_type_name_plural = get_category_type_name(content_type)

    items = model.objects.all()

    return render(request, 'wagtailcategories/type_index.html', {
        'content_type': content_type,
        'category_type_name': category_type_name,
        'category_type_name_plural': category_type_name_plural,
        'items': items,
    })


@permission_required('wagtailadmin.access_admin')  # further permissions are enforced within the view
def create(request, content_type_app_name, content_type_model_name):
    content_type = get_content_type_from_url_params(content_type_app_name, content_type_model_name)
    if not user_can_edit_category_type(request.user, content_type):
        raise PermissionDenied

    model = content_type.model_class()
    category_type_name = get_category_type_name(content_type)[0]

    instance = model() #instance = model.for_site(request.site)
    edit_handler_class = get_category_edit_handler(model)
    form_class = edit_handler_class.get_form_class(model)

    if request.POST:
        form = form_class(request.POST, request.FILES, instance=instance)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                _("{category_type} '{instance}' created.").format(
                    category_type=capfirst(get_category_type_name(content_type)[0]),
                    instance=instance
                )
            )
            return redirect('wagtailcategories_list', content_type.app_label, content_type.model)
        else:
            messages.error(request, _("The category could not be created due to errors."))
            edit_handler = edit_handler_class(instance=instance, form=form)
    else:
        form = form_class(instance=instance)
        edit_handler = edit_handler_class(instance=instance, form=form)

    return render(request, 'wagtailcategories/create.html', {
        'content_type': content_type,
        'category_type_name': category_type_name,
        'edit_handler': edit_handler,
    })


@permission_required('wagtailadmin.access_admin')  # further permissions are enforced within the view
def edit(request, content_type_app_name, content_type_model_name, id):
    content_type = get_content_type_from_url_params(content_type_app_name, content_type_model_name)
    if not user_can_edit_category_type(request.user, content_type):
        raise PermissionDenied

    model = content_type.model_class()
    category_type_name = get_category_type_name(content_type)[0]

    instance = get_object_or_404(model, id=id)
    edit_handler_class = get_category_edit_handler(model)
    form_class = edit_handler_class.get_form_class(model)

    if request.POST:
        form = form_class(request.POST, request.FILES, instance=instance)

        if form.is_valid():
            form.save()
            
            messages.success(
                request,
                _("{category_type} '{instance}' updated.").format(
                    category_type=capfirst(category_type_name),
                    instance=instance
                )
            )
            return redirect('wagtailcategories_list', content_type.app_label, content_type.model)
        else:
            messages.error(request, _("The category could not be saved due to errors."))
            edit_handler = edit_handler_class(instance=instance, form=form)
    else:
        form = form_class(instance=instance)
        edit_handler = edit_handler_class(instance=instance, form=form)

    return render(request, 'wagtailcategories/edit.html', {
        'content_type': content_type,
        'category_type_name': category_type_name,
        'instance': instance,
        'edit_handler': edit_handler
    })


@permission_required('wagtailadmin.access_admin')  # further permissions are enforced within the view
def delete(request, content_type_app_name, content_type_model_name, id):
    content_type = get_content_type_from_url_params(content_type_app_name, content_type_model_name)
    if not user_can_edit_category_type(request.user, content_type):
        raise PermissionDenied

    model = content_type.model_class()
    category_type_name = get_category_type_name(content_type)[0]

    instance = get_object_or_404(model, id=id)

    if request.POST:
        instance.delete()
        messages.success(
            request,
            _("{category_type} '{instance}' deleted.").format(
                category_type=capfirst(category_type_name),
                instance=instance
            )
        )
        return redirect('wagtailcategories_list', content_type.app_label, content_type.model)

    return render(request, 'wagtailcategories/confirm_delete.html', {
        'content_type': content_type,
        'category_type_name': category_type_name,
        'instance': instance,
    })

