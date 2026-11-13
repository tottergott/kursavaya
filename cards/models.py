from django.conf import settings
from django.db import models
from django.utils import timezone


class Deck(models.Model):
    """Языковая колода (категория карточек)."""

    title = models.CharField('Название колоды', max_length=150)
    source_language = models.CharField('Исходный язык', max_length=60, default='Английский')
    target_language = models.CharField('Изучаемый язык', max_length=60, default='Русский')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='decks',
        verbose_name='Владелец',
    )

    class Meta:
        verbose_name = 'Колода'
        verbose_name_plural = 'Колоды'
        ordering = ['-id']

    def __str__(self) -> str:
        return f'{self.title} ({self.source_language} → {self.target_language})'


class Card(models.Model):
    """Карточка со словом/фразой и встроенной статистикой прогресса изучения."""

    class Status(models.TextChoices):
        NEW = 'new', 'Новое'
        LEARNING = 'learning', 'Изучается'
        LEARNED = 'learned', 'Выучено'

    deck = models.ForeignKey(
        Deck,
        on_delete=models.CASCADE,
        related_name='cards',
        verbose_name='Колода',
    )
    front_text = models.CharField('Исходное слово / фраза', max_length=255)
    back_text = models.CharField('Перевод / толкование', max_length=255)
    example = models.TextField('Контекстный пример', blank=True)

    # Поля статистики и прогресса изучения
    review_count = models.PositiveIntegerField('Количество повторений', default=0)
    success_count = models.PositiveIntegerField('Правильных ответов', default=0)
    status = models.CharField(
        'Статус',
        max_length=16,
        choices=Status.choices,
        default=Status.NEW,
    )
    last_reviewed_at = models.DateTimeField(
        'Дата последнего повторения',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Карточка'
        verbose_name_plural = 'Карточки'
        ordering = ['id']

    def __str__(self) -> str:
        return f'{self.front_text} — {self.back_text}'

    def record_review(self, remembered: bool) -> None:
        """Фиксирует результат ответа пользователя и обновляет статус карточки."""
        self.review_count += 1
        self.last_reviewed_at = timezone.now()

        if remembered:
            self.success_count += 1
            if self.status in (self.Status.LEARNING, self.Status.LEARNED):
                self.status = self.Status.LEARNED
            else:
                self.status = self.Status.LEARNING
        else:
            self.status = self.Status.LEARNING

        self.save()
