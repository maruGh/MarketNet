from django.contrib import admin

from tags.models import TaggedItem, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']
    search_fields = ['label']


@admin.register(TaggedItem)
class TaggedItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'tag', 'content_type', 'object_id', 'content_object']
