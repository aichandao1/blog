from django import forms
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from .models import Article, Categorie, Auteur, Commentaire, Tag

# ── Validation image ───────────────────────────────────────────
def validate_image(file):
    if file:
        if file.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
            raise ValidationError("Seules les images JPG et PNG sont autorisées.")


# ── Formulaire Article ─────────────────────────────────────────
class ArticleForm(forms.ModelForm):
    image_couverture = forms.ImageField(
        required=False,
        validators=[validate_image]
    )

    class Meta:
        model = Article
        fields = ['titre', 'categories', 'tags', 'contenu',
                  'extrait', 'image_couverture', 'statut']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de l article',
            }),
            'categories': forms.CheckboxSelectMultiple(),
            'tags': forms.CheckboxSelectMultiple(),
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'rows': 15}),
            'extrait': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.titre)
        if commit:
            instance.save()
            self.save_m2m()
        return instance


# ── Formulaire Categorie ───────────────────────────────────────
class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'description', 'couleur']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'couleur': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.nom)
        if commit:
            instance.save()
        return instance


# ── Formulaire Auteur ──────────────────────────────────────────
class AuteurForm(forms.ModelForm):
    class Meta:
        model = Auteur
        fields = ['bio', 'photo', 'site_web']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'site_web': forms.URLInput(attrs={'class': 'form-control'}),
        }


# ── Formulaire Commentaire ─────────────────────────────────────
class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Votre commentaire...',
            })
        }
        labels = {'contenu': 'Votre commentaire'}


# ── Formulaire Tag ─────────────────────────────────────────────
class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: astuce',
            }),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.nom)
        if commit:
            instance.save()
        return instance