from django.contrib.contenttypes.models import ContentType
from django.db import models

CATEGORY_MODELS = []
CATEGORY_CONTENT_TYPES = None

def get_category_content_types():
    global CATEGORY_CONTENT_TYPES
    if CATEGORY_CONTENT_TYPES is None:
        CATEGORY_CONTENT_TYPES = [
            ContentType.objects.get_for_model(model) for model in CATEGORY_MODELS
        ]
    return CATEGORY_CONTENT_TYPES


def register_category(model):
    if model not in CATEGORY_MODELS:
        CATEGORY_MODELS.append(model)
        CATEGORY_MODELS.sort(key=lambda x: x._meta.verbose_name)
    return model


class BaseCategory(models.Model):
    category_name = models.CharField(
        max_length=60, 
        verbose_name='Category name'
    )
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return self.category_name
    