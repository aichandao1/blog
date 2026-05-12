# blog/admin.py
from .models import Auteur, Categorie, Article, Commentaire, Tag

@admin.register(Article)
class TagAdmin(admin.ModelAdmin):
    list_display        = ['nom', 'slug', 'nb_articles']
    prepopulated_fields = {'slug': ('nom',)}
    search_fields       = ['nom']

    def nb_articles(self, obj):
        return obj.articles.filter(statut='publie').count()
    nb_articles.short_description = 'Articles publiés'