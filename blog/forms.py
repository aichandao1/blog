# blog/forms.py

from django import forms
from .models import Article, Categorie, Auteur, Commentaire, Tag


class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = '__all__'


class CategorieForm(forms.ModelForm):

    class Meta:
        model = Categorie
        fields = '__all__'


class AuteurForm(forms.ModelForm):

    class Meta:
        model = Auteur
        fields = '__all__'


class CommentaireForm(forms.ModelForm):

    class Meta:
        model = Commentaire
        fields = '__all__'


class TagForm(forms.ModelForm):

    class Meta:
        model = Tag
        fields = '__all__'