from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from .models import Article, Categorie, Auteur, Commentaire
from .forms import ArticleForm, CategorieForm, AuteurForm, CommentaireForm


# ── Accueil ───────────────────────────────────────────────────
def accueil(request):
    articles_recents = Article.objects.filter(statut='publie').select_related('auteur__user')[:6]
    categories = Categorie.objects.all()[:8]

    return render(request, 'blog/accueil.html', {
        'articles_recents': articles_recents,
        'categories': categories,
    })


# ── Liste des articles ────────────────────────────────────────
def liste_articles(request):
    articles = Article.objects.filter(statut='publie').select_related('auteur__user')

    q = request.GET.get('q', '')
    if q:
        articles = articles.filter(
            Q(titre__icontains=q) |
            Q(contenu__icontains=q) |
            Q(auteur__user__username__icontains=q)
        )

    categorie_slug = request.GET.get('categorie', '')
    if categorie_slug:
        articles = articles.filter(categories__slug=categorie_slug)

    paginator = Paginator(articles, 9)
    page = request.GET.get('page', 1)
    articles_page = paginator.get_page(page)

    return render(request, 'blog/articles/liste.html', {
        'articles': articles_page,
        'categories': Categorie.objects.all(),
        'q': q,
        'cat_active': categorie_slug,
    })


# ── Détail article ────────────────────────────────────────────
def detail_article(request, slug):
    article = get_object_or_404(Article, slug=slug, statut='publie')
    article.incrementer_vues()

    commentaires = article.commentaires.filter(approuve=True).select_related('auteur')
    form_commentaire = CommentaireForm()

    return render(request, 'blog/articles/detail.html', {
        'article': article,
        'commentaires': commentaires,
        'form': form_commentaire,
        'articles_lies': Article.objects.filter(
            statut='publie',
            categories__in=article.categories.all()
        ).exclude(pk=article.pk).distinct()[:3],
    })


# ── Créer un article ──────────────────────────────────────────
@login_required
def creer_article(request):
    try:
        auteur = request.user.auteur
    except Auteur.DoesNotExist:
        messages.error(request, "Vous devez avoir un profil auteur.")
        return redirect('blog:accueil')

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.auteur = auteur

            if article.statut == 'publie' and not article.date_publication:
                article.date_publication = timezone.now()

            article.save()
            form.save_m2m()

            messages.success(request, "Article créé avec succès !")
            return redirect('blog:article_detail', slug=article.slug)
    else:
        form = ArticleForm()

    return render(request, 'blog/articles/formulaire.html', {
        'form': form,
        'titre': 'Nouvel article',
        'bouton': 'Publier',
    })


# ── Modifier un article ───────────────────────────────────────
@login_required
def modifier_article(request, slug):
    article = get_object_or_404(Article, slug=slug)

    if article.auteur.user != request.user and not request.user.is_staff:
        messages.error(request, "Non autorisé.")
        return redirect('blog:article_detail', slug=slug)

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save()
            messages.success(request, "Article modifié !")
            return redirect('blog:article_detail', slug=article.slug)
    else:
        form = ArticleForm(instance=article)

    return render(request, 'blog/articles/formulaire.html', {
        'form': form,
        'article': article,
        'titre': f'Modifier : {article.titre}',
        'bouton': 'Enregistrer',
    })


# ── Supprimer un article ──────────────────────────────────────
@login_required
def supprimer_article(request, slug):
    article = get_object_or_404(Article, slug=slug)

    if article.auteur.user != request.user and not request.user.is_staff:
        messages.error(request, "Non autorisé.")
        return redirect('blog:article_detail', slug=slug)

    if request.method == 'POST':
        article.delete()
        messages.success(request, "Article supprimé.")
        return redirect('blog:article_liste')

    return render(request, 'blog/articles/confirmer_suppression.html', {'article': article})


# ── Catégories ────────────────────────────────────────────────
def liste_categories(request):
    categories = Categorie.objects.all()
    return render(request, 'blog/categories/liste.html', {'categories': categories})


def detail_categorie(request, slug):
    categorie = get_object_or_404(Categorie, slug=slug)
    articles = categorie.articles.filter(statut='publie')

    return render(request, 'blog/categories/detail.html', {
        'categorie': categorie,
        'articles': articles,
    })


@login_required
def creer_categorie(request):
    if not request.user.is_staff:
        return redirect('blog:categorie_liste')

    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            cat = form.save()
            return redirect('blog:categorie_detail', slug=cat.slug)
    else:
        form = CategorieForm()

    return render(request, 'blog/categories/formulaire.html', {
        'form': form,
        'titre': 'Nouvelle catégorie',
    })

@login_required
def modifier_categorie(request, slug):
    categorie = get_object_or_404(Categorie, slug=slug)
    if not request.user.is_staff:
        return redirect('blog:categorie_liste')

    if request.method == 'POST':
        form = CategorieForm(request.POST, instance=categorie)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categorie modifiee !')
            return redirect('blog:categorie_detail', slug=categorie.slug)
    else:
        form = CategorieForm(instance=categorie)

    return render(request, 'blog/categories/formulaire.html', {
        'form': form, 'titre': f'Modifier : {categorie.nom}',
    })

# ── Auteurs ───────────────────────────────────────────────────
def liste_auteurs(request):
    auteurs = Auteur.objects.select_related('user').all()
    return render(request, 'blog/auteurs/liste.html', {'auteurs': auteurs})


def detail_auteur(request, pk):
    auteur = get_object_or_404(Auteur, pk=pk)
    articles = auteur.articles.filter(statut='publie')

    return render(request, 'blog/auteurs/detail.html', {
        'auteur': auteur,
        'articles': articles,
    })


@login_required
def modifier_profil(request):
    auteur, _ = Auteur.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = AuteurForm(request.POST, request.FILES, instance=auteur)
        if form.is_valid():
            form.save()
            return redirect('blog:auteur_detail', pk=auteur.pk)
    else:
        form = AuteurForm(instance=auteur)

    return render(request, 'blog/auteurs/formulaire.html', {'form': form})


# ── Commentaires ──────────────────────────────────────────────
@login_required
def ajouter_commentaire(request, slug):
    article = get_object_or_404(Article, slug=slug, statut='publie')

    if request.method == 'POST':
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.article = article
            commentaire.auteur = request.user
            commentaire.save()

    return redirect('blog:article_detail', slug=slug)


@login_required
def supprimer_commentaire(request, pk):
    commentaire = get_object_or_404(Commentaire, pk=pk)

    if request.user == commentaire.auteur or request.user.is_staff:
        if request.method == 'POST':
            slug = commentaire.article.slug
            commentaire.delete()
            return redirect('blog:article_detail', slug=slug)

    return redirect('blog:accueil')

class ArticleDeleteView(DeleteView):
    model = Article
    template_name = 'blog/article_confirm_delete.html'
    success_url = reverse_lazy('liste_articles')


    def liste_articles(request):

    tri = request.GET.get('tri')

    articles = Article.objects.all()

    if tri == 'date':
        articles = articles.order_by('-date_creation')

    elif tri == 'titre':
        articles = articles.order_by('titre')

    elif tri == 'popularite':
        articles = articles.order_by('-vues')

    return render(request, 'blog/liste.html', {
        'articles': articles
    })



