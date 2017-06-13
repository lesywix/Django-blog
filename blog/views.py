import logging
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
import markdown
from django.utils.text import slugify
from django.views.generic import ListView, DetailView
from django.views.generic import TemplateView
from markdown.extensions.toc import TocExtension

from blog.models import Post, Category, Nav, Tag
from comments.forms import CommentFrom
from django.conf import settings

# logger
logger = logging.getLogger(__name__)


class BaseMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super(BaseMixin, self).get_context_data(**kwargs)
        try:
            # 网站标题等内容
            context['website_title'] = settings.WEBSITE_TITLE
            context['website_welcome'] = settings.WEBSITE_WELCOME
            # 热门文章
            context['hot_article_list'] = \
                Post.objects.order_by("-views")[0:10]
            # 导航条
            context['nav_list'] = Nav.objects.all()
            # 最新评论
            # context['latest_comment_list'] = \
            #     Comment.objects.order_by("-create_time")[0:10]
            # 友情链接
            # context['links'] = Link.objects.order_by('create_time').all()
            # colors = ['primary', 'success', 'info', 'warning', 'danger']
            # for index, link in enumerate(context['links']):
            #     link.color = colors[index % len(colors)]
            # 用户未读消息数
            # user = self.request.user
            # if user.is_authenticated():
            #     context['notification_count'] = \
            #         user.to_user_notification_set.filter(is_read=0).count()
        except Exception as e:
            logger.error(u'[BaseMixin]加载基本信息出错')

        return context


class IndexView(BaseMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10


class PostDetailView(BaseMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        response = super(PostDetailView, self).get(request, *args, **kwargs)
        self.object.increase_views()
        return response

    def get_object(self, queryset=None):
        post = super(PostDetailView, self).get_object(queryset=None)
        md = markdown.Markdown(extensions=[
                                          'markdown.extensions.extra',
                                          'markdown.extensions.codehilite',
                                          'markdown.extensions.toc',
                                          TocExtension(slugify=slugify),
                                      ])
        post.body = md.convert(post.body)
        post.toc = md.toc
        return post

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        form = CommentFrom()
        comment_list = self.object.comment_set.all()
        context.update({
            'form': form,
            'comment_list': comment_list
        })
        return context


class ArchivesView(BaseMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchivesView, self).get_queryset().filter(created_time__year=year, created_time__month=month)


class CategoryView(BaseMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        # cate = self.kwargs.get('category')
        cate = get_object_or_404(Category, name=self.kwargs.get('category'))
        return super(CategoryView, self).get_queryset().filter(category=cate)


# def search(request):
#     q = request.GET.get('q')
#     error_msg = ''
#     if not q:
#         error_msg = "请输入关键词"
#         return render(request, 'blog/index.html', {'error_msg': error_msg})
#     post_list = Post.objects.filter(title__icontains=q)
#     return render(request, 'blog/index.html', {'error_msg': error_msg,
#                                                  'post_list': post_list})

class TagView(BaseMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        t = get_object_or_404(Tag, name=self.kwargs.get('tag'))
        return super(TagView, self).get_queryset().filter(tags=t)


class AboutView(BaseMixin, TemplateView):
    template_name = 'blog/about.html'
