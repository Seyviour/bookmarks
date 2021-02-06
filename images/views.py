from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import ImageCreateForm
from .models import Image

# Create your views here.

@login_required
def image_create(request): 
    if request.method == 'POST': 
        #form is sent
        form = ImageCreateForm(data=request.POST)
        if form.is_valid(): 
            #form data is valid
            cd = form.cleaned_data
            new_item = form.save(commit=False)

            #assign current user to item 
            new_item.user = request.user
            new_item.save()
            messages.success(request, 'Image added successfully')

            return redirect(new_item.get_absolute_url())
        
    else: 
        form = ImageCreateForm(data=request.GET)

    return render(request, 
                    'images/image/create.html', 
                    {'section': 'images',
                    'form': form})
    
def image_detail(request, id, slug): 
    image = get_object_or_404(Image, id=id, slug=slug)
    return render(request,
                'images/image/detail.html',
                {'section': 'images',
                'image': image})

