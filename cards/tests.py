from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Card, Deck


class LangCardsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='password123')
        self.client.login(username='student', password='password123')
        self.deck = Deck.objects.create(
            title='Английский: A1 Базовый',
            source_language='Английский',
            target_language='Русский',
            owner=self.user,
        )
        self.card = Card.objects.create(
            deck=self.deck,
            front_text='apple',
            back_text='яблоко',
            example='I eat an apple every day.',
        )

    def test_dashboard_and_stats_render(self):
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Английский: A1 Базовый')

        stats_resp = self.client.get(reverse('stats'))
        self.assertEqual(stats_resp.status_code, 200)
        self.assertContains(stats_resp, 'Статистика прогресса')

    def test_card_crud_in_deck(self):
        resp = self.client.post(
            reverse('deck_detail', args=[self.deck.pk]),
            {
                'front_text': 'book',
                'back_text': 'книга',
                'example': 'Read a good book.',
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(self.deck.cards.count(), 2)

        new_card = Card.objects.get(front_text='book')
        edit_resp = self.client.post(
            reverse('card_edit', args=[new_card.pk]),
            {
                'front_text': 'notebook',
                'back_text': 'тетрадь',
                'example': 'Write in a notebook.',
            },
        )
        self.assertEqual(edit_resp.status_code, 302)
        new_card.refresh_from_db()
        self.assertEqual(new_card.front_text, 'notebook')

        del_resp = self.client.post(reverse('card_delete', args=[new_card.pk]))
        self.assertEqual(del_resp.status_code, 302)
        self.assertEqual(self.deck.cards.count(), 1)

    def test_study_flow_updates_progress(self):
        study_url = reverse('deck_study', args=[self.deck.pk])
        resp = self.client.get(f'{study_url}?restart=1')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'apple')
        self.assertNotContains(resp, 'яблоко')

        reveal_resp = self.client.get(f'{study_url}?reveal=1')
        self.assertEqual(reveal_resp.status_code, 200)
        self.assertContains(reveal_resp, 'яблоко')

        # 1-й ответ «Помню» -> статус «Изучается»
        post_resp = self.client.post(study_url, {'result': 'remembered'})
        self.assertEqual(post_resp.status_code, 302)

        self.card.refresh_from_db()
        self.assertEqual(self.card.review_count, 1)
        self.assertEqual(self.card.success_count, 1)
        self.assertEqual(self.card.status, Card.Status.LEARNING)
        self.assertIsNotNone(self.card.last_reviewed_at)

        # 2-й ответ «Помню» -> статус «Выучено»
        self.client.get(f'{study_url}?restart=1')
        self.client.post(study_url, {'result': 'remembered'})
        self.card.refresh_from_db()
        self.assertEqual(self.card.review_count, 2)
        self.assertEqual(self.card.success_count, 2)
        self.assertEqual(self.card.status, Card.Status.LEARNED)

        # Ответ «Не помню» -> статус снова «Изучается»
        self.client.get(f'{study_url}?restart=1')
        self.client.post(study_url, {'result': 'forgot'})
        self.card.refresh_from_db()
        self.assertEqual(self.card.review_count, 3)
        self.assertEqual(self.card.success_count, 2)
        self.assertEqual(self.card.status, Card.Status.LEARNING)
