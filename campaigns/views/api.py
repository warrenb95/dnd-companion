from django.views import View
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from ..models import SessionNote
from ..services.llm import generate_session_summary


class GenerateSessionSummaryView(View):

    def post(self, request, pk):
        session = SessionNote.objects.get(pk=pk)
        if not session.content:
            return HttpResponseRedirect(reverse("campaigns:campaign_list"))

        summary = generate_session_summary(
            session.content, chapter_title=session.encounter.chapter.title
        )
        session.summary = summary
        session.save()

        return HttpResponseRedirect(session.encounter.chapter.campaign.get_absolute_url())


def empty_fragment(request):
    return HttpResponse()