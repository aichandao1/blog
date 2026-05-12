from django.urls import path
from . import views
from .views import (
    ArticleListView,
    ArticleDetailView,
    ArticleCreateView,
    ArticleUpdateView,
    ArticleDeleteView,
    ArticleListCreateAPIView,
    ArticleDetailAPIView,
    CommentaireListCreateAPIView,
    CommentaireDetailAPIView
)



app_name = 'blog'

urlpatterns = [

    # ── Accueil ─────────────────────────
    path('', views.accueil, name='accueil'),

    # ── Articles (CLASS BASED VIEWS) ────
    path('articles/', ArticleListView.as_view(), name='article_liste'),

    path('articles/creer/', ArticleCreateView.as_view(), name='article_creer'),

    path('articles/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),

    path('articles/<slug:slug>/modifier/', ArticleUpdateView.as_view(), name='article_modifier'),

    path('articles/<slug:slug>/supprimer/', ArticleDeleteView.as_view(), name='article_supprimer'),

    # ── Categories ───────────────────────
    path('categories/', views.liste_categories, name='categorie_liste'),

    path('categories/creer/', views.creer_categorie, name='categorie_creer'),

    path('categories/<slug:slug>/', views.detail_categorie, name='categorie_detail'),

    path('categories/<slug:slug>/modifier/', views.modifier_categorie, name='categorie_modifier'),

    # ── Auteurs ──────────────────────────
    path('auteurs/', views.liste_auteurs, name='auteur_liste'),

    path('auteurs/<int:pk>/', views.detail_auteur, name='auteur_detail'),

    path('mon-profil/modifier/', views.modifier_profil, name='auteur_modifier'),

    # ── Commentaires ─────────────────────
    path('articles/<slug:slug>/commenter/', views.ajouter_commentaire, name='commentaire_ajouter'),

    path('commentaires/<int:pk>/supprimer/', views.supprimer_commentaire, name='commentaire_supprimer'),

    # ── Autres ───────────────────────────
    path('articles/<slug:slug>/like/', views.liker_article, name='article_like'),

    path('recherche/', views.recherche_globale, name='recherche'),

     # =========================
     # API ARTICLES
     # =========================
     path('auteurs/', views.liste_auteurs, name='auteur_liste'),

path('auteurs/<int:pk>/', views.detail_auteur, name='auteur_detail'),

path('mon-profil/modifier/', views.modifier_profil, name='auteur_modifier'),

# ── Commentaires ─────────────────────
path('articles/<slug:slug>/commenter/',
     views.ajouter_commentaire,
     name='commentaire_ajouter'),

path('commentaires/<int:pk>/supprimer/',
     views.supprimer_commentaire,
     name='commentaire_supprimer'),

# ── Autres ───────────────────────────
path('articles/<slug:slug>/like/',
     views.liker_article,
     name='article_like'),

path('recherche/',
     views.recherche_globale,
     name='recherche'),

# ── API ARTICLES ────────────────────
path('api/articles/',
     ArticleListCreateAPIView.as_view(),
     name='api_articles'),

path('api/articles/<slug:slug>/',
     ArticleDetailAPIView.as_view(),
     name='api_article_detail'),

# ── API COMMENTAIRES ────────────────
path('api/commentaires/',
     CommentaireListCreateAPIView.as_view(),
     name='api_commentaires'),

path('api/commentaires/<int:pk>/',
     CommentaireDetailAPIView.as_view(),
     name='api_commentaire_detail'),

     path('tags/', views.liste_tags, name='tag_liste'),
     path('tags/<slug:slug>/', views.detail_tag, name='tag_detail'),
     path('categories/creer/', views.creer_categorie, name='categorie_creer'),
]
