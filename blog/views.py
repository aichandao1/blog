# blog/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

from rest_framework import generics

from .models import (
    Article,
    Categorie,
    Auteur,
    Commentaire,
    Like,
    Tag
)

from .forms import (
    ArticleForm,
    CategorieForm,
    AuteurForm,
    CommentaireForm,
    TagForm
)

from .serializers import (
    ArticleSerializer,
    CommentaireSerializer
)


# =========================
# ACCUEIL
# =========================

def accueil(request):
    articles_recents = Article.objects.all()[:6]
    categories = Categorie.objects.all()[:8]

    return render(request, 'blog/accueil.html', {
        'articles_recents': articles_recents,
        'categories': categories,
    })


# =========================
# ARTICLES
# =========================

class ArticleListView(ListView):
    model = Article
    template_name = 'blog/articles/liste.html'
    context_object_name = 'articles'


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/articles/detail.html'
    context_object_name = 'article'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


class ArticleCreateView(CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/articles/formulaire.html'
    success_url = reverse_lazy('blog:article_liste')


class ArticleUpdateView(UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/articles/formulaire.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


class ArticleDeleteView(DeleteView):
    model = Article
    template_name = 'blog/articles/confirmer_suppression.html'
    success_url = reverse_lazy('blog:article_liste')


# =========================
# CATEGORIES
# =========================

def liste_categories(request):
    categories = Categorie.objects.all()

    return render(request, 'blog/categories/liste.html', {
        'categories': categories
    })


def detail_categorie(request, slug):
    categorie = get_object_or_404(Categorie, slug=slug)

    return render(request, 'blog/categories/detail.html', {
        'categorie': categorie
    })


# =========================
# AUTEURS
# =========================

def liste_auteurs(request):
    auteurs = Auteur.objects.all()

    return render(request, 'blog/auteurs/liste.html', {
        'auteurs': auteurs
    })


def detail_auteur(request, pk):
    auteur = get_object_or_404(Auteur, pk=pk)

    return render(request, 'blog/auteurs/detail.html', {
        'auteur': auteur
    })


@login_required
def modifier_profil(request):

    auteur, created = Auteur.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':
        form = AuteurForm(
            request.POST,
            request.FILES,
            instance=auteur
        )

        if form.is_valid():
            form.save()
            return redirect('blog:auteur_detail', pk=auteur.pk)

    else:
        form = AuteurForm(instance=auteur)

    return render(request, 'blog/auteurs/formulaire.html', {
        'form': form
    })


# =========================
# COMMENTAIRES
# =========================

@login_required
def ajouter_commentaire(request, slug):

    article = get_object_or_404(Article, slug=slug)

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

    if request.user == commentaire.auteur:

        if request.method == 'POST':
            slug = commentaire.article.slug
            commentaire.delete()

            return redirect(
                'blog:article_detail',
                slug=slug
            )

    return redirect('blog:accueil')


# =========================
# LIKES
# =========================

@login_required
def liker_article(request, slug):

    article = get_object_or_404(Article, slug=slug)

    like = Like.objects.filter(
        article=article,
        user=request.user
    )

    if like.exists():
        like.delete()

    else:
        Like.objects.create(
            article=article,
            user=request.user
        )

    return redirect('blog:article_detail', slug=slug)


# =========================
# RECHERCHE
# =========================

def recherche_globale(request):

    query = request.GET.get('q', '')

    articles = Article.objects.filter(
        Q(titre__icontains=query) |
        Q(contenu__icontains=query)
    )

    auteurs = Auteur.objects.filter(
        Q(user__username__icontains=query)
    )

    return render(request, 'blog/recherche.html', {
        'query': query,
        'articles': articles,
        'auteurs': auteurs
    })


# =========================
# TAGS
# =========================

def liste_tags(request):

    tags = Tag.objects.all()

    return render(request, 'blog/tags/liste.html', {
        'tags': tags
    })


def detail_tag(request, slug):

    tag = get_object_or_404(Tag, slug=slug)

    return render(request, 'blog/tags/detail.html', {
        'tag': tag
    })


# =========================
# API ARTICLES
# =========================

class ArticleListCreateAPIView(
    generics.ListCreateAPIView
):

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


class ArticleDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = 'slug'


# =========================
# API COMMENTAIRES
# =========================

class CommentaireListCreateAPIView(
    generics.ListCreateAPIView
):

    queryset = Commentaire.objects.all()
    serializer_class = CommentaireSerializer


class CommentaireDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = Commentaire.objects.all()
    serializer_class = CommentaireSerializer

    
    # =========================
# CATEGORIES CRUD
# =========================

@login_required
def creer_categorie(request):

    if request.method == 'POST':

        form = CategorieForm(request.POST)

        if form.is_valid():
            categorie = form.save()

            return redirect(
                'blog:categorie_detail',
                slug=categorie.slug
            )

    else:
        form = CategorieForm()

    return render(
        request,
        'blog/categories/formulaire.html',
        {
            'form': form
        }
    )


@login_required
def modifier_categorie(request, slug):

    categorie = get_object_or_404(
        Categorie,
        slug=slug
    )

    if request.method == 'POST':

        form = CategorieForm(
            request.POST,
            instance=categorie
        )

        if form.is_valid():

            form.save()

            return redirect(
                'blog:categorie_detail',
                slug=categorie.slug
            )

    else:
        form = CategorieForm(
            instance=categorie
        )

    return render(
        request,
        'blog/categories/formulaire.html',
        {
            'form': form
        }
    )