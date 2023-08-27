from decimal import Decimal
from rest_framework import serializers
from .models import Collection, Product, Review


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']
        read_only_fields = ['products_count']
    products_count = serializers.IntegerField(read_only=True)

    # products_count = SerializerMethodField(method_name='get_count_product')

    # def get_count_product(self, collection: Collection):
    #     return collection.products.count()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'unit_price',
                  'slug', 'inventory', 'price_with_tax', 'last_update', 'collection']
        read_only_fields = ['price_with_tax', 'last_update']

    collection = serializers.HyperlinkedRelatedField(
        queryset=Collection.objects.all(),
        view_name='collections-detail'
        # read_only=True
    )

    price_with_tax = serializers.SerializerMethodField(method_name='get_tax')

    def get_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'name', 'description', 'date']
        read_only_fields = ['product']

    def create(self, validated_data):
        return Review.objects.create(product_id=self.context['product_id'], **validated_data)
