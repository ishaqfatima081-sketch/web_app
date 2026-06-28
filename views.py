from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from .models import Product, Category, Brand


def product_list(request):
    """Display list of all products with search and filter"""
    products = Product.objects.filter(is_available=True).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Filter by category
    category_id = request.GET.get('category', '')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Filter by brand
    brand_id = request.GET.get('brand', '')
    if brand_id:
        products = products.filter(brand_id=brand_id)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all categories and brands for filter dropdowns
    categories = Category.objects.all()
    brands = Brand.objects.filter(active=True)
    
    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'search_query': search_query,
        'categories': categories,
        'brands': brands,
        'selected_category': category_id,
        'selected_brand': brand_id,
    }
    
    return render(request, 'products/product_list.html', context)


def product_detail(request, pk):
    """Display product detail page"""
    product = get_object_or_404(Product, pk=pk, is_available=True)
    
    # Get related products from same category
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(pk=pk)[:4]
    
    # Get approved reviews
    reviews = product.reviews.filter(is_approved=True).order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': reviews.count(),
    }
    
    return render(request, 'products/product_detail.html', context)


def low_stock_products(request):
    """Display products with low stock"""
    products = Product.objects.filter(
        is_available=True,
        stock_quantity__lt=10
    ).order_by('stock_quantity')
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filters
    categories = Category.objects.all()
    brands = Brand.objects.filter(active=True)
    
    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'title': 'Low Stock Products',
        'categories': categories,
        'brands': brands,
    }
    
    return render(request, 'products/product_list.html', context)


def featured_products(request):
    """Display featured products"""
    products = Product.objects.filter(
        is_featured=True,
        is_available=True
    ).order_by('-created_at')
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filters
    categories = Category.objects.all()
    brands = Brand.objects.filter(active=True)
    
    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'title': 'Featured Products',
        'categories': categories,
        'brands': brands,
    }
    
    return render(request, 'products/product_list.html', context)
