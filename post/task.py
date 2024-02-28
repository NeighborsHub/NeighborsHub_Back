from NeighborsHub.celery import app as celery_app
from NeighborsHub.openai_manager import GetPostCategory


@celery_app.task
def celery_get_category_post(post_id: int) -> None:
    from post.models import Category, Post

    categories = [category.title for category in Category.objects.all()]
    post = Post.objects.get(id=post_id)
    category_title = GetPostCategory(categories, post.body).run()
    post.category.add(Category.objects.get(title=category_title))
    return
