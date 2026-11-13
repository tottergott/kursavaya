import sqlite3
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from cards.models import Card, Deck


class Command(BaseCommand):
    help = 'Создает суперпользователя admin, тестового пользователя demo, колоды и 12 карточек.'

    def handle(self, *args, **options):
        admin_user, admin_created = User.objects.get_or_create(
            username='admin',
            defaults={'is_staff': True, 'is_superuser': True, 'email': 'admin@example.com'},
        )
        if admin_created or not admin_user.is_superuser:
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.set_password('admin12345')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Создан суперпользователь admin (пароль: admin12345)'))

        user, created = User.objects.get_or_create(username='demo')
        if created:
            user.set_password('demo12345')
            user.email = 'demo@example.com'
            user.save()
            self.stdout.write(self.style.SUCCESS('Создан пользователь demo (пароль: demo12345)'))

        Deck.objects.filter(owner=user).delete()

        now = timezone.now()

        deck_a1 = Deck.objects.create(
            title='Английский: A1 Базовый',
            source_language='Английский',
            target_language='Русский',
            owner=user,
        )
        a1_words = [
            ('accomplish', 'выполнять, достигать', 'She worked hard to accomplish her goal.', 'learned', 3, 3),
            ('reliable', 'надежный', 'We need a reliable source of information.', 'learned', 2, 2),
            ('essential', 'необходимый, существенный', 'Water is essential for all living things.', 'learning', 2, 1),
            ('opportunity', 'возможность', 'This project is a great opportunity to learn.', 'learning', 1, 0),
            ('maintain', 'поддерживать, сохранять', 'It is important to maintain a clear schedule.', 'new', 0, 0),
            ('fluent', 'беглый, свободный (о речи)', 'He became fluent in Spanish after two years.', 'new', 0, 0),
            ('knowledge', 'знание, познания', 'Reading books expands your knowledge.', 'learned', 2, 2),
            ('improve', 'улучшать, совершенствовать', 'Daily practice will improve your vocabulary.', 'learning', 1, 1),
        ]
        for front, back, example, status, reviews, successes in a1_words:
            Card.objects.create(
                deck=deck_a1,
                front_text=front,
                back_text=back,
                example=example,
                status=status,
                review_count=reviews,
                success_count=successes,
                last_reviewed_at=now if reviews > 0 else None,
            )

        deck_it = Deck.objects.create(
            title='Английский: B1 Разработка и ИТ',
            source_language='Английский',
            target_language='Русский',
            owner=user,
        )
        it_words = [
            ('deployment', 'развертывание', 'The deployment to production completed without errors.', 'learned', 2, 2),
            ('query', 'запрос (к базе данных)', 'This SQL query returns all active users.', 'learning', 1, 1),
            ('constraint', 'ограничение', 'Database constraints protect data integrity.', 'new', 0, 0),
            ('authentication', 'аутентификация, проверка подлинности', 'Standard Django authentication handles user sessions.', 'new', 0, 0),
        ]
        for front, back, example, status, reviews, successes in it_words:
            Card.objects.create(
                deck=deck_it,
                front_text=front,
                back_text=back,
                example=example,
                status=status,
                review_count=reviews,
                success_count=successes,
                last_reviewed_at=now if reviews > 0 else None,
            )

        db_path = settings.DATABASES['default']['NAME']
        conn = sqlite3.connect(db_path)
        conn.execute('VACUUM')
        conn.close()

        self.stdout.write(
            self.style.SUCCESS(
                f'Готово: суперпользователь admin восстановлен, карточек в базе: {Card.objects.count()}.'
            )
        )
