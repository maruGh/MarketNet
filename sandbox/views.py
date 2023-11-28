from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import mail_admins, EmailMessage, send_mail, send_mass_mail, BadHeaderError
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, F, Count, Max, Avg, Sum, Value, Func, ExpressionWrapper, DecimalField
from django.db.transaction import atomic
from django.template.loader import render_to_string

from tags.models import TaggedItem
from .models import *
from .tasks import send_email_to_all_user
from likes.models import Like


def back_task(request):
    send_email_to_all_user.delay(request.user.username, context={
        'name': request.user.username})
    return HttpResponse('<h1>Background task [sending email to all user]</br> is running with out affecting this main app </h1>')


def hello(request):
    try:
        # send_mail(subject='subject1', message='replay me when u are available',
        #           from_email=None,
        #           recipient_list=['marudemamu833@gmail.com', 'recipient1@gmail.com'])

        # send_mass_mail([['subject...', 'message....', None, [
        #                'recipient1@gmail.com', 'recipient2@gmail.com']]])

        # mail_admins('admin_subject', 'plain text message',
        #             html_message='<h1>HTML admin message</h1>')

        html_message = render_to_string(
            'email/welcome.html', {'name': 'Mistrawit'})

        message = EmailMessage('subj', None, None, [
                               'mesifkr926@gmail.com', 'marugithub@gmail.com'])
        message.content_subtype = 'html'
        message.body = html_message
        message.attach_file('media/store/images/20230621_060448_0.jpg')
        message.send()

        # message = EmailMessage('email/welcome.tpl', {'name': 'Maru'})
        # message.send()

    except Exception as e:
        print(e)
    return HttpResponse('<h1>Hello</h1>')


def index(request):
    # p = Product.objects.filter(pk=0).first()
    # p = Product.objects.filter(unit_price__gt=20)[:5]
    # p = Product.objects.filter(title__icontains='coffee')
    # p = Product.objects.filter(title__istartswith='coffee')
    # p = Product.objects.filter(last_update__year__gt=2020)
    # p = Customer.objects.filter(email__icontains='.com')
    # p = Collection.objects.filter(featured_product__isnull=True)
    # p = OrderItem.objects.filter(product__collection__id=3)

    # AND
    # p = Product.objects.filter(inventory__lt=10).filter(unit_price__lt=20) # or filter(inventory__lt=10,unit_price__lt=20)

    # Or
    # p = Product.objects.filter(Q(inventory__lt=10) | ~Q(unit_price__lt=20))
    # p = Product.objects.filter(collection_id=F('inventory'))
    # p = Product.objects.earliest('title') or order_by
    # p = Product.objects.all()[998:1002]
    # p = Product.objects.values(
    #     'id', 'title', 'collection__title').filter(pk__gt=900)
    # Product that have been ordered
    # p = OrderItem.objects.values('product__title').filter(
    #     product_id__isnull=False).order_by('product__title')
    # p = Product.objects.filter(order_items__isnull=False).values(
    #     'title').order_by('title').distinct()

    # p = Product.objects.select_related('collection').values_list(
    #     'id', 'title', 'collection__title')

    # p = Order.objects.select_related('customer').prefetch_related(
    #     'order_items__product').order_by('-placed_at').all()[:5]

    # p = Product.objects.aggregate(Count('id'), Avg('unit_price'))
    # How many units of product 1 have we sold?
    # p = OrderItem.objects.select_related('product').filter(
    #     product_id=1, order__payment_status='C').aggregate(Sum('quantity'))
    # How many orders has customer 1 placed?
    # p = Customer.objects.prefetch_related(
    #     'orders').filter(pk=1).aggregate(Count('orders'))

    # p = Product.objects.annotate(n=F('id')+Value(2))
    # p = Customer.objects.annotate(full_name=Func(F('first_name'), Value(
    #     ' '), ('last_name'), function='CONCAT')).values('id', 'email', 'full_name')

    # p = Product.objects.annotate(discount=ExpressionWrapper(
    #     F('unit_price')*0.9, output_field=DecimalField()))

    # p = TaggedItem.objects.select_related('tag').filter(
    #     tag_id=1, content_type=ContentType.objects.get_for_model(Product), object_id=1)

    # p = Product.objects.all()
    # list(p)
    # list(p)
    # p[0]

    # p = Collection.objects.filter(pk=2).update(featured_product=2)
    # with atomic():
    #     order = Order.objects.create(customer_id=1)
    #     OrderItem.objects.create(
    #         order=order, product_id=1, unit_price=20.0000, quantity=500)

    # print(p)

    return HttpResponse('<html> <title>Title</title> <body> <h1>Maru</h1> </body></html>')
    return render(request, 'store/index.html', {'name': list(p)})
