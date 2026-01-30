from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import NewsPaper
from .forms import NewsPaperForm


@login_required
def newspaper_list(request):
    edit_id = request.GET.get("edit")
    edit_obj = get_object_or_404(NewsPaper, id=edit_id) if edit_id else None

    # POST: Add / Edit / Activate / Deactivate
    if request.method == "POST":

        # EDIT existing
        if "newspaper_id" in request.POST:
            obj = get_object_or_404(NewsPaper, id=request.POST["newspaper_id"])
            form = NewsPaperForm(request.POST, instance=obj)
        # ADD new
        else:
            obj = None
            form = NewsPaperForm(request.POST)

        if form.is_valid():
            paper = form.save(commit=False)

            if not obj:
                paper.is_active = True

            if "deactivate" in request.POST:
                paper.is_active = False
            if "activate" in request.POST:
                paper.is_active = True

            paper.save()
            return redirect("newspaper")

    else:
        form = NewsPaperForm(instance=edit_obj)

    newspapers = NewsPaper.objects.all()

    return render(
        request,
        "newspaper/add_newspaper.html",
        {
            "newspapers": newspapers,
            "form": form,
            "edit_obj": edit_obj,
        }
    )




