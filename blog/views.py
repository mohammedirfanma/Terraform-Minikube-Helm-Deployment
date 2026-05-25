from django.shortcuts import render
from django.http import HttpResponse

def home_page(request):
    return HttpResponse("""
        <h1>Step 35: 100 Days of Security - Success!</h1>
        <p>Zero-Trust 3-Tier Architecture is Live.</p>
        <ul>
            <li>Non-Root User: Active</li>
            <li>Calico Network Policies: Enforced</li>
            <li>Resource Quotas: Enabled</li>
        </ul>
    """)

# Create your views here.
from django.http import JsonResponse
from .models import Article, Comment

# Create an article (quick test endpoint)
def create_article(request):
    article = Article.objects.create(
        title="Test Title",
        body="This is a test article"
    )
    return JsonResponse({"message": "Article created", "id": article.id})


# List all articles
def list_articles(request):
    articles = Article.objects.all().values()
    return JsonResponse(list(articles), safe=False)


# Add a comment to an article
def add_comment(request, article_id):
    article = Article.objects.get(id=article_id)
    comment = Comment.objects.create(
        article=article,
        text="Test comment"
    )
    return JsonResponse({"message": "Comment added", "id": comment.id})


# Get comments for an article
def get_comments(request, article_id):
    comments = Comment.objects.filter(article_id=article_id).values()
    return JsonResponse(list(comments), safe=False)

def home_page(request):
    return HttpResponse("""
        <h1>Welcome to the Secured Kubernetes</h1>
        <p>Zero-Trust 3-Tier Architecture is Live.</p>
        <ul>
            <li>Non-Root User: Active</li>
            <li>Calico Network Policies: Enforced</li>
            <li>Resource Quotas: Enabled</li>
        </ul>
    """)