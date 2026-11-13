from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BootstrapAuthenticationForm, CardForm, DeckForm, RegisterForm
from .models import Card, Deck


class UserLoginView(LoginView):
    """Страница входа пользователя."""

    template_name = 'registration/login.html'
    authentication_form = BootstrapAuthenticationForm
    redirect_authenticated_user = True


def register_view(request: HttpRequest) -> HttpResponse:
    """Регистрация нового пользователя."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно. Добро пожаловать!')
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


def _build_user_summary(user) -> dict:
    """Собирает общую сводку по всем колодам и карточкам пользователя."""
    decks = list(Deck.objects.filter(owner=user).prefetch_related('cards'))

    total_cards = 0
    learned_cards = 0
    learning_cards = 0
    new_cards = 0
    total_reviews = 0
    total_success = 0
    last_activity = None

    deck_rows = []
    for deck in decks:
        cards = list(deck.cards.all())
        deck_total = len(cards)
        deck_learned = sum(1 for c in cards if c.status == Card.Status.LEARNED)
        deck_learning = sum(1 for c in cards if c.status == Card.Status.LEARNING)
        deck_new = max(0, deck_total - deck_learned - deck_learning)

        deck_reviews = sum(c.review_count for c in cards)
        deck_success = sum(c.success_count for c in cards)
        reviewed_dates = [c.last_reviewed_at for c in cards if c.last_reviewed_at]
        deck_last_reviewed = max(reviewed_dates) if reviewed_dates else None

        if deck_last_reviewed and (last_activity is None or deck_last_reviewed > last_activity):
            last_activity = deck_last_reviewed

        total_cards += deck_total
        learned_cards += deck_learned
        learning_cards += deck_learning
        new_cards += deck_new
        total_reviews += deck_reviews
        total_success += deck_success

        mastery_percent = round((deck_learned / deck_total) * 100) if deck_total else 0
        learning_percent = round((deck_learning / deck_total) * 100) if deck_total else 0
        accuracy_percent = round((deck_success / deck_reviews) * 100) if deck_reviews else 0

        deck_rows.append(
            {
                'deck': deck,
                'total_cards': deck_total,
                'learned_cards': deck_learned,
                'learning_cards': deck_learning,
                'new_cards': deck_new,
                'mastery_percent': mastery_percent,
                'learning_percent': learning_percent,
                'review_count': deck_reviews,
                'accuracy_percent': accuracy_percent,
                'last_reviewed_at': deck_last_reviewed,
            }
        )

    overall_accuracy = round((total_success / total_reviews) * 100) if total_reviews else 0
    overall_mastery = round((learned_cards / total_cards) * 100) if total_cards else 0

    return {
        'deck_rows': deck_rows,
        'total_decks': len(decks),
        'total_cards': total_cards,
        'learned_cards': learned_cards,
        'learning_cards': learning_cards,
        'new_cards': new_cards,
        'total_reviews': total_reviews,
        'total_success': total_success,
        'overall_accuracy': overall_accuracy,
        'overall_mastery': overall_mastery,
        'last_activity': last_activity,
    }


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """Главная панель (дашборд) со списком колод и краткой сводкой."""
    summary = _build_user_summary(request.user)
    return render(request, 'cards/dashboard.html', summary)


@login_required
def create_demo_deck_view(request: HttpRequest) -> HttpResponse:
    """Создает демонстрационную колоду с базовыми словами для быстрого старта."""
    if request.method == 'POST':
        deck = Deck.objects.create(
            title='Английский: A1 Базовый',
            source_language='Английский',
            target_language='Русский',
            owner=request.user,
        )
        sample_cards = [
            ('accomplish', 'выполнять, достигать', 'She worked hard to accomplish her goal.'),
            ('reliable', 'надежный', 'We need a reliable source of information.'),
            ('essential', 'необходимый, существенный', 'Water is essential for all living things.'),
            ('opportunity', 'возможность', 'This project is a great opportunity to learn.'),
            ('maintain', 'поддерживать, сохранять', 'It is important to maintain a clear schedule.'),
            ('fluent', 'беглый, свободный (о речи)', 'He became fluent in Spanish after two years.'),
            ('knowledge', 'знание, познания', 'Reading books expands your knowledge.'),
            ('improve', 'улучшать, совершенствовать', 'Daily practice will improve your vocabulary.'),
        ]
        for front, back, example in sample_cards:
            Card.objects.create(
                deck=deck,
                front_text=front,
                back_text=back,
                example=example,
            )
        messages.success(request, f'Демо-колода «{deck.title}» создана ({len(sample_cards)} карточек).')
        return redirect('deck_detail', pk=deck.pk)
    return redirect('dashboard')


@login_required
def deck_create_view(request: HttpRequest) -> HttpResponse:
    """Создание новой языковой колоды."""
    if request.method == 'POST':
        form = DeckForm(request.POST)
        if form.is_valid():
            deck = form.save(commit=False)
            deck.owner = request.user
            deck.save()
            messages.success(request, f'Колода «{deck.title}» успешно создана.')
            return redirect('deck_detail', pk=deck.pk)
    else:
        form = DeckForm()

    return render(
        request,
        'cards/deck_form.html',
        {'form': form, 'page_title': 'Новая колода', 'submit_label': 'Создать колоду'},
    )


@login_required
def deck_edit_view(request: HttpRequest, pk: int) -> HttpResponse:
    """Редактирование параметров колоды."""
    deck = get_object_or_404(Deck, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = DeckForm(request.POST, instance=deck)
        if form.is_valid():
            form.save()
            messages.success(request, 'Параметры колоды обновлены.')
            return redirect('deck_detail', pk=deck.pk)
    else:
        form = DeckForm(instance=deck)

    return render(
        request,
        'cards/deck_form.html',
        {
            'form': form,
            'deck': deck,
            'page_title': f'Редактирование колоды: {deck.title}',
            'submit_label': 'Сохранить изменения',
        },
    )


@login_required
def deck_delete_view(request: HttpRequest, pk: int) -> HttpResponse:
    """Удаление колоды вместе с её карточками."""
    deck = get_object_or_404(Deck, pk=pk, owner=request.user)
    if request.method == 'POST':
        title = deck.title
        deck.delete()
        messages.success(request, f'Колода «{title}» удалена.')
        return redirect('dashboard')

    return render(request, 'cards/deck_confirm_delete.html', {'deck': deck})


@login_required
def deck_detail_view(request: HttpRequest, pk: int) -> HttpResponse:
    """Просмотр карточек колоды в таблице и форма быстрого добавления новой карточки."""
    deck = get_object_or_404(Deck, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.deck = deck
            card.save()
            messages.success(request, f'Карточка «{card.front_text}» добавлена.')
            return redirect('deck_detail', pk=deck.pk)
    else:
        form = CardForm()

    cards = list(deck.cards.all())
    card_rows = [
        {
            'index': index,
            'card': card,
            'status_code': card.status,
            'status_label': card.get_status_display(),
            'review_count': card.review_count,
            'success_count': card.success_count,
            'last_reviewed_at': card.last_reviewed_at,
        }
        for index, card in enumerate(cards, start=1)
    ]

    return render(
        request,
        'cards/deck_detail.html',
        {
            'deck': deck,
            'card_rows': card_rows,
            'form': form,
        },
    )


@login_required
def card_edit_view(request: HttpRequest, pk: int) -> HttpResponse:
    """Редактирование карточки."""
    card = get_object_or_404(Card, pk=pk, deck__owner=request.user)
    if request.method == 'POST':
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            messages.success(request, f'Карточка «{card.front_text}» обновлена.')
            return redirect('deck_detail', pk=card.deck.pk)
    else:
        form = CardForm(instance=card)

    return render(
        request,
        'cards/card_form.html',
        {'form': form, 'card': card, 'deck': card.deck},
    )


@login_required
def card_delete_view(request: HttpRequest, pk: int) -> HttpResponse:
    """Удаление карточки."""
    card = get_object_or_404(Card, pk=pk, deck__owner=request.user)
    deck = card.deck
    if request.method == 'POST':
        front_text = card.front_text
        card.delete()
        messages.success(request, f'Карточка «{front_text}» удалена.')
        return redirect('deck_detail', pk=deck.pk)

    return render(
        request,
        'cards/card_confirm_delete.html',
        {'card': card, 'deck': deck},
    )


def _init_study_session(request: HttpRequest, deck: Deck) -> list[int]:
    """Формирует очередь карточек для тренировки (сначала невыученные, затем выученные)."""
    cards = list(deck.cards.all())
    priority_order = {
        Card.Status.LEARNING: 0,
        Card.Status.NEW: 1,
        Card.Status.LEARNED: 2,
    }
    sorted_cards = sorted(cards, key=lambda c: (priority_order.get(c.status, 1), c.id))

    queue = [c.id for c in sorted_cards]
    request.session[f'study_queue_{deck.pk}'] = queue
    request.session[f'study_total_{deck.pk}'] = len(queue)
    request.session[f'study_stats_{deck.pk}'] = {'remembered': 0, 'forgot': 0}
    request.session.modified = True
    return queue


@login_required
def deck_study_view(request: HttpRequest, pk: int) -> HttpResponse:
    """Режим тренировки: поочередный показ карточек, открытие ответа и оценка."""
    deck = get_object_or_404(Deck, pk=pk, owner=request.user)
    total_deck_cards = deck.cards.count()

    if total_deck_cards == 0:
        messages.warning(request, 'В этой колоде пока нет карточек. Добавьте хотя бы одну карточку.')
        return redirect('deck_detail', pk=deck.pk)

    queue_key = f'study_queue_{deck.pk}'
    total_key = f'study_total_{deck.pk}'
    stats_key = f'study_stats_{deck.pk}'

    if request.GET.get('restart') == '1' or queue_key not in request.session:
        queue = _init_study_session(request, deck)
    else:
        existing_ids = set(deck.cards.values_list('id', flat=True))
        queue = [cid for cid in request.session.get(queue_key, []) if cid in existing_ids]
        request.session[queue_key] = queue

    if not queue:
        session_stats = request.session.get(stats_key, {'remembered': 0, 'forgot': 0})
        return render(
            request,
            'cards/study_complete.html',
            {
                'deck': deck,
                'session_stats': session_stats,
                'total_reviewed': session_stats.get('remembered', 0) + session_stats.get('forgot', 0),
            },
        )

    current_card_id = queue[0]
    card = get_object_or_404(Card, pk=current_card_id, deck=deck)

    if request.method == 'POST':
        result = request.POST.get('result')
        if result in ('remembered', 'forgot'):
            remembered = result == 'remembered'
            card.record_review(remembered=remembered)

            queue.pop(0)
            request.session[queue_key] = queue

            session_stats = request.session.get(stats_key, {'remembered': 0, 'forgot': 0})
            if remembered:
                session_stats['remembered'] = session_stats.get('remembered', 0) + 1
            else:
                session_stats['forgot'] = session_stats.get('forgot', 0) + 1
            request.session[stats_key] = session_stats
            request.session.modified = True

            return redirect('deck_study', pk=deck.pk)

    total_in_session = max(request.session.get(total_key, len(queue)), len(queue))
    current_position = total_in_session - len(queue) + 1
    reveal = request.GET.get('reveal') == '1'

    return render(
        request,
        'cards/study.html',
        {
            'deck': deck,
            'card': card,
            'progress': card,
            'reveal': reveal,
            'current_position': current_position,
            'total_in_session': total_in_session,
            'remaining_count': len(queue),
        },
    )


@login_required
def stats_view(request: HttpRequest) -> HttpResponse:
    """Сводная страница статистики изучения по всем колодам."""
    summary = _build_user_summary(request.user)
    return render(request, 'cards/stats.html', summary)
