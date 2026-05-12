from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import math


class Auteur(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='auteur',
        verbose_name='Utilisateur',
    )
    bio = models.TextField(blank=True, verbose_name='Biographie')
    photo = models.ImageField(upload_to='auteurs/', blank=True, null=True, verbose_name='Photo de profil')
    site_web = models.URLField(blank=True, verbose_name='Site web')
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Auteur'
        verbose_name_plural = 'Auteurs'
        ordering = ['user__last_name']

    def __str__(self):
        return f'{self.user.get_full_name()} (@{self.user.username})'

    def get_absolute_url(self):
        return reverse('blog:auteur_detail', kwargs={'pk': self.pk})

    @property
    def nom_complet(self):
        return self.user.get_full_name() or self.user.username

    @property
    def nb_articles(self):
        return self.articles.filter(statut='publie').count()


class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name='Nom')
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, verbose_name='Description')
    couleur = models.CharField(max_length=7, default='#3B82F6', verbose_name='Couleur (hex)')
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categorie'
        verbose_name_plural = 'Categories'
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('blog:categorie_detail', kwargs={'slug': self.slug})

    @property
    def nb_articles(self):
        return self.articles.filter(statut='publie').count()


class Tag(models.Model):
    nom = models.CharField(max_length=50, unique=True, verbose_name='Tag')
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['nom']

    def __str__(self):
        return f'#{self.nom}'

    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'slug': self.slug})


class Article(models.Model):
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('publie',    'Publie'),
        ('archive',   'Archive'),
    ]

    titre = models.CharField(max_length=200, verbose_name='Titre')
    slug = models.SlugField(max_length=200, unique=True)
    auteur = models.ForeignKey(
        Auteur,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles',
        verbose_name='Auteur',
    )
    categories = models.ManyToManyField(
        Categorie,
        blank=True,
        related_name='articles',
        verbose_name='Categories',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='articles',
        verbose_name='Tags',
    )
    contenu = models.TextField(verbose_name='Contenu')
    extrait = models.TextField(blank=True, max_length=500, verbose_name='Extrait')
    image_couverture = models.ImageField(upload_to='articles/', blank=True, null=True, verbose_name='Image de couverture')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon', verbose_name='Statut')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    date_publication = models.DateTimeField(null=True, blank=True)
    nb_vues = models.PositiveIntegerField(default=0, verbose_name='Nombre de vues')
    temps_lecture = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-date_publication', '-date_creation']

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('blog:article_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.temps_lecture = math.ceil(len(self.contenu.split()) / 200)
        super().save(*args, **kwargs)

    @property
    def nb_commentaires(self):
        return self.commentaires.filter(approuve=True).count()

    def incrementer_vues(self):
        self.nb_vues += 1
        self.save(update_fields=['nb_vues'])


class Commentaire(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='commentaires',
        verbose_name='Article',
    )
    auteur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='commentaires',
        verbose_name='Auteur',
    )
    contenu = models.TextField(verbose_name='Commentaire', max_length=2000)
    approuve = models.BooleanField(default=False, verbose_name='Approuve')
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'
        ordering = ['date_creation']

    def __str__(self):
        auteur_nom = self.auteur.username if self.auteur else 'Utilisateur supprime'
        return f'Commentaire de {auteur_nom} sur "{self.article.titre[:40]}"'


class Like(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('article', 'user')