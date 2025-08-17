from django.shortcuts import render , HttpResponse,get_object_or_404
from django.contrib.auth import get_user_model

from django.contrib.auth.decorators import login_required
User = get_user_model()

@login_required
def profileList(req):

    con = {
        'list': User.objects.filter(is_active=True)
    }

    return render(req, 'profile/list.html', con)


@login_required
# Create your views here.
def profileDetailView(req , username=None, *args, **kwargs):

    user = req.user
    user_grp = user.groups.all()
    # print(user.has_perm("subscription.basic") ,
    #          user.has_perm("subscription.advance"))
    if user_grp.filter(name__icontains='Basic').exists():
        return HttpResponse(f"Basic")
    else:

        # profile_usr_obj = User.objects.get(username=username)
        profile_usr_obj = get_object_or_404(User , username=username)

        is_me  = profile_usr_obj == user

        con = {
            "object" : profile_usr_obj,
            "usr": profile_usr_obj,
            "owner": is_me,
        }
        return render(req, 'profile/det.html', con)
