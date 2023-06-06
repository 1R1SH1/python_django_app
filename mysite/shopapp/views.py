from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from timeit import default_timer
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import ProductForm, OrderForm, GroupForm
from .models import Product, Order


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context = {
            'time_running': default_timer(),
            'products': products,
        }
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            'form': GroupForm(),
            'groups': Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request:HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = 'shopapp/products-details.html'
    model = Product
    context_object_name = 'product'
    queryset = (
        Product.objects.select_related('created_by')
    )
    # def get(self, request: HttpRequest, pk: int) -> HttpResponse:
    #     product = get_object_or_404(Product, pk=pk)
    #     context = {
    #         'product': product,
    #     }
    #     return render(request, 'shopapp/products-details.html', context=context)


class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    # model = Product
    context_object_name = 'products'
    queryset = (
        Product.objects.select_related('created_by')
    )

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["products"] = Product.objects.all()
    #     return context


class ProductCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    # def test_func(self):
    #     return self.request.user.is_superuser
    permission_required = 'shopapp.add_product'

    model = Product
    fields = 'name', 'price', 'description', 'discount'
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super(ProductCreateView, self).form_valid(form)


class ProductUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    permission_required = 'shopapp.change_product'

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        if self.request.user.pk == self.get_object().created_by.pk:
            return True
        else:
            return False

    model = Product
    fields = 'name', 'price', 'description', 'discount'
    template_name_suffix = '_update_form'

    # def get_success_url(self):
    #     return reverse(
    #         'shopapp:products_details',
    #         kwargs={'pk': self.object.pk},
    #     )


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


# def create_product(request: HttpRequest) -> HttpResponse:
#     if request.method == 'POST':
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             Product.objects.create(**form.cleaned_data)
#             form.save()
#             url = render(request, 'shopapp/products-list.html')
#             return redirect(url)
#     else:
#         form = ProductForm()
#     context = {
#         'form': form,
#     }
#     return render(request, 'shopapp/create-product.html', context=context)


# def orders_list(request: HttpRequest):
#     context = {
#         'orders': Order.objects.select_related('user').prefetch_related('products').all(),
#     }
#     return render(request, 'shopapp/order_list.html', context=context)


class OrderListView(LoginRequiredMixin, ListView):
    context_object_name = 'orders'
    queryset = (
        Order.objects.select_related('user').prefetch_related('products').filter(archived=False)
    )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'shopapp.view_order'
    queryset = (
        Order.objects.select_related('user').prefetch_related('products')
    )


class OrderCreateView(CreateView):
    model = Order
    fields = 'delivery_address', 'promocods', 'user', 'products'
    success_url = reverse_lazy('shopapp:order_list')


# def create_order(request: HttpRequest) -> HttpResponse:
#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             form.save()
#             url = render(request, 'shopapp/order_list.html')
#             return redirect(url)
#     else:
#         form = OrderForm()
#     context = {
#         'form': form,
#     }
#     return render(request, 'shopapp/create-order.html', context=context)


class OrderUpdateView(UpdateView):
    model = Order
    fields = 'delivery_address', 'promocods', 'user', 'products'
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse(
            'shopapp:order_detail',
            kwargs={'pk': self.object.pk},
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy('shopapp:order_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)
