from rest_framework import serializers
from .models import Article, Commentaire


class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = '__all__'


class CommentaireSerializer(serializers.ModelSerializer):

    class Meta:
        model = Commentaire
        fields = '__all__'