import markdown
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.six import python_2_unicode_compatible
from django.urls import reverse


@python_2_unicode_compatible
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'名称')
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    def get_absolute_url(self):
        return reverse('blog:category', args=(self.name,))

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Tag(models.Model):
    name = models.CharField(max_length=100)
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    def get_absolute_url(self):
        return reverse('blog:tag', args=(self.name,))

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Post(models.Model):
    title = models.CharField(max_length=70)
    en_title = models.CharField(max_length=100, verbose_name=u'英文标题')
    body = models.TextField()
    created_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    modified_time = models.DateTimeField()
    excerpt = models.CharField(max_length=45, blank=True, null=True,
                               help_text="可选，如若为空将摘取正文的前54个字符")
    category = models.ForeignKey(Category)
    tags = models.ManyToManyField(Tag, blank=True)
    author = models.ForeignKey(User)
    # img = models.CharField(max_length=200, default='/static/img/article/default.jpg')
    img = models.ImageField(u'文章图片', upload_to='img/%Y')
    views = models.PositiveIntegerField(default=0)
    is_top = models.BooleanField(default=False, verbose_name=u'置顶')

    class Meta:
        ordering = ['-created_time', 'title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])


class Nav(models.Model):
    name = models.CharField(max_length=40, verbose_name=u'导航条内容')
    url = models.CharField(max_length=200, blank=True, null=True,
                           verbose_name=u'指向地址')
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = verbose_name = u"导航条"
        ordering = ['-create_time']
        # app_label = string_with_title('blog', u"博客管理")

    def __str__(self):
        return self.name
