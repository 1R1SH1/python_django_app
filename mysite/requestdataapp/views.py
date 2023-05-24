from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from requestdataapp.forms import UserBioForm, UploadFileForm


def process_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get('a', '')
    b = request.GET.get('b', '')
    result = a + b
    context = {
        'a': a,
        'b': b,
        'result': result,
    }
    return render(request, 'requestdataapp/request-query-params.html', context=context)


def user_form(request: HttpRequest) -> HttpResponse:
    context = {
        'form': UserBioForm(),
    }
    return render(request, 'requestdataapp/user-bio-form.html', context=context)


def handle_file_upload(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST' and request.FILES.get('myfile'):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            myfile = request.FILES['myfile']
            fs = FileSystemStorage()
            if request.FILES['myfile'].size > 1000000:
                return render(request, 'requestdataapp/error-message.html')
            else:
                fs.save(myfile.name, myfile)
                print('saved file', myfile)
        return render(request, 'requestdataapp/file-upload.html')
    else:
        form = UploadFileForm()

    context = {
        'form': form,
    }
    return render(request, 'requestdataapp/file-upload.html', context=context)
