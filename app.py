import json
import os
import sys

from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from django.core.wsgi import get_wsgi_application
from django.utils.crypto import get_random_string

from django_distill import distill_path
from markdownx.utils import markdownify

settings.configure(
    DEBUG=(os.environ.get("DEBUG", "") == "1"),
    ALLOWED_HOSTS=["*"],
    ROOT_URLCONF=__name__,  # Make this module the urlconf
    SECRET_KEY=get_random_string(50),
    STATIC_URL='/static/',
    DISTILL_PUBLISH='dist',
    STATIC_ROOT=os.path.join('.', 'static'),
    INSTALLED_APPS = ['django_distill',],
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ['templates'],
        },
    ]
)


g_titles = None


def load_books():
    global g_titles
    with open('books/titles.json') as json_file:
        g_titles = json.load(json_file)


def index(request):
    return render(request, 'index.html', {'books': g_titles})


def page_view(request, book, page):
    with open(f'books/{book}/pages.json') as json_file:
        pages = json.load(json_file)

    with open(f'books/{book}/{page}.md', 'r') as file:
        body = markdownify(file.read())

    context = {'pages': pages, 'body': body, 'book': book, 'book_title': g_titles[book]['title']}
    return render(request, 'page.html', context)


def distll_func():
    for book in next(os.walk('books'))[1]:
        with open(f'books/{book}/pages.json') as json_file:
            pages = json.load(json_file)
            for page in pages:
                yield {'book': book, 'page': page}


urlpatterns = [
    distill_path('', index, name='index', distill_func=lambda *args: None, distill_file='index.html'),
    distill_path("read/<slug:book>/<slug:page>", page_view, name='page', distill_func=distll_func),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

app = get_wsgi_application()

if __name__ == "__main__":
    load_books()
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
