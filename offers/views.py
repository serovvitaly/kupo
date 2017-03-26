from django.shortcuts import render
from django.views import generic
from offers.models import *
from django.http import Http404, HttpResponseForbidden, HttpResponse, JsonResponse
from django.template import loader, Context
import json



def get_offers_value_objects_mini(offers_ids):
    if type(offers_ids) is not list:
        return []
    if len(offers_ids) < 1:
        return []
    offers = Offer.objects.filter(id__in=offers_ids).all()

    idx_offers = {offer.id: type('offer_dict', (object,), {**offer.__dict__, **{'images':[]}})() for offer in offers}

    offers_media = OfferMedia.objects.filter(offer_id__in=offers_ids).order_by('offer_id').all()
    for offer_media in offers_media:
        if offer_media.offer_id not in idx_offers:
            continue
        idx_offer = idx_offers[offer_media.offer_id]
        idx_offer.images.append(offer_media.url)

    return list(idx_offers.values())


def get_offer_value_object_full(offer_id):
    try:
        offer = Offer.objects.get(pk=offer_id)
    except Offer.DoesNotExist:
        return None
    offer_dict = type('offer_dict', (object,), {**offer.__dict__, **{
        'images':[],
        'items': [],
        'places': [],
        'merchant': [],
    }})
    offers_media = OfferMedia.objects.filter(offer_id__exact=offer_id).all()
    offers_items = OfferItem.objects.filter(offer_id__exact=offer_id).all()
    merchant_places = Place.objects.filter(merchant_id__exact=offer.merchant_id).all()
    merchant = Merchant.objects.get(pk=offer.merchant_id)
    offer_dict.merchant = merchant.__dict__
    for offer_media in offers_media:
        offer_dict.images.append(offer_media.url)
    for offer_item in offers_items:
        offer_dict.items.append(offer_item.__dict__)
    for offer_place in merchant_places:
        offer_place = json.loads(offer_place.data)
        offer_dict.places.append(offer_place)
    return offer_dict


class IndexView(generic.TemplateView):
    template_name = 'v1/index.html'

    def get_page(self, page_number):
        page_number = int(page_number)
        if page_number < 1:
            page_number = 1
        #posts = Offer.objects.filter(status__exact='p').all()
        posts = Offer.objects.all()
        post_template = loader.get_template('v1/post-mini.html')
        page_items_count = 30
        items_from = (page_number - 1) * page_items_count
        items_to = items_from + page_items_count
        offers_ids = []
        for offer in posts[items_from:items_to]:
            #post_content = post_template.render(Context({'item': post}))
            offers_ids.append(offer.id)
        #offers_ids = [3168,3169,3170,3171,3172,3173,3174,3175,3176,3177,3178,3179,]

        offers_val_objs = get_offers_value_objects_mini(offers_ids)
        items_content = []
        for offer_val_obj in offers_val_objs:
            context = Context({
                'offer': offer_val_obj,
                'images_range': range(1, 5),
            })
            items_content.append(post_template.render(context))
        return JsonResponse({
            'success': True,
            'page_number': page_number,
            'items': items_content,

        })

    def get_context_data(self, **kwargs):
        items_by_columns = {1: [], 2: [], 3: []}
        return {
            'items_by_columns': items_by_columns,
            'wrapper_widget': 'widget/multi-column.html',
            'item_widget': 'widget/post-mini.html',
        }



class OfferView(generic.TemplateView):
    template_name = 'v1/post.html'

    def get_context_data(self, **kwargs):
        offer_id = kwargs['post_id']
        try:
            offer = Offer.objects.get(pk=offer_id)
        except Offer.DoesNotExist:
            raise Http404("Post not found")
        allowed_statuses = ['p']
        if offer.status not in allowed_statuses:
            #raise Http404("Post not found")
            pass
        if self.request.is_ajax():
            return {
                'layout': 'v1/layout-post-ajax.html',
                'offer': get_offer_value_object_full(offer_id),
                'post_content': '',
            }
        else:
            self.template_name = 'v1/index.html'
            items_by_columns = {1: [], 2: [], 3: []}
            return {
                'items_by_columns': items_by_columns,
                'offer': offer,
                'wrapper_widget': 'widget/multi-column.html',
                'item_widget': 'widget/post-mini.html',
            }



class Version1View(generic.TemplateView):
    template_name = 'v1/index.html'

    def get_context_data(self, **kwargs):
        return {
            #'wrapper_widget': 'v1/multi-column.html',
        }


class Version2View(generic.TemplateView):
    template_name = 'v2/layout.html'
