from django.contrib import admin
from .models import Card, Deck


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ('title', 'source_language', 'target_language', 'owner')
    list_filter = ('source_language', 'target_language', 'owner')
    search_fields = ('title', 'source_language', 'target_language')


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = (
        'front_text',
        'back_text',
        'deck',
        'status',
        'review_count',
        'success_count',
        'last_reviewed_at',
    )
    list_filter = ('status', 'deck')
    search_fields = ('front_text', 'back_text', 'example')
