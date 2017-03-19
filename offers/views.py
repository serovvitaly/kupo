from django.shortcuts import render
from django.views import generic
from offers.models import *
from django.http import Http404, HttpResponseForbidden, HttpResponse, JsonResponse
from django.template import loader, Context




class IndexView(generic.TemplateView):
    template_name = 'v1/index.html'

    def get_page(self, page_number):
        page_number = int(page_number)
        if page_number < 1:
            page_number = 1
        #posts = Offer.objects.filter(status__exact='p').all()
        posts = Offer.objects.all()
        post_template = loader.get_template('v1/post-mini.html')
        items_by_columns = []
        column_index = 1
        page_items_count = 30
        items_from = (page_number - 1) * page_items_count
        items_to = items_from + page_items_count
        for post in posts[items_from:items_to]:
            post_content = post_template.render(Context({'item': post}))
            items_by_columns.append(post_content)
            if column_index > 2:
                column_index = 0
            column_index += 1
        return JsonResponse({
            'success': True,
            'page_number': page_number,
            'items': items_by_columns,
        })

    def get_context_data(self, **kwargs):
        posts = Offer.objects.filter(status__exact='p').all()
        items_by_columns = {1: [], 2: [], 3: []}
        column_index = 1
        for post in posts[0:30]:
            #items_by_columns[column_index].append(post)
            if column_index > 2:
                column_index = 0
            column_index += 1
        return {
            'items_by_columns': items_by_columns,
            'wrapper_widget': 'widget/multi-column.html',
            'item_widget': 'widget/post-mini.html',
        }



class PostView(generic.TemplateView):
    template_name = 'v1/post.html'

    def get_context_data(self, **kwargs):
        try:
            self.post = Offer.objects.get(pk=kwargs['post_id'])
        except Offer.DoesNotExist:
            raise Http404("Post not found")
        is_editor = self.request.user.has_perm('blog.change_post')
        allowed_statuses = ['p']
        if self.request.user.has_perm('blog.change_post', self.post) is False and self.post.status not in allowed_statuses:
            raise Http404("Post not found")
        post_content = self.post.content
        if self.request.is_ajax():
            return {
                'layout': 'layout-post-ajax.html',
                'item': self.post,
                'post_content': post_content,
                'posts': Offer.objects.filter(is_active__exact=True),
                'is_editor': is_editor,
                'sub_posts': Offer.objects.all()[0:6],
            }
        else:
            self.template_name = 'v1/index.html'
            items_by_columns = {1: [], 2: [], 3: []}
            return {
                'items_by_columns': items_by_columns,
                'item': self.post,
                'wrapper_widget': 'widget/multi-column.html',
                'item_widget': 'widget/post-mini.html',
                'is_editor': is_editor,
            }



class Version1View(generic.TemplateView):
    template_name = 'v1/index.html'

    def get_context_data(self, **kwargs):
        return {
            #'wrapper_widget': 'v1/multi-column.html',
        }


class Version2View(generic.TemplateView):
    template_name = 'v2/layout.html'
