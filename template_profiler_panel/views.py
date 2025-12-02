try:
    from django.utils.translation import gettext as _
except ImportError:  # pragma: no cover - Django < 3.0
    from django.utils.translation import ugettext as _

from django.http import HttpResponseBadRequest, JsonResponse

from debug_toolbar._compat import login_not_required
from debug_toolbar.decorators import render_with_toolbar_language, require_show_toolbar
from debug_toolbar.toolbar import DebugToolbar


@login_not_required
@require_show_toolbar
@render_with_toolbar_language
def template_export(request):
    """Return a structured JSON export of the template profiler stats."""
    from template_profiler_panel.panels.template import TemplateProfilerPanel

    request_id = request.GET.get("request_id")
    if not request_id:
        return HttpResponseBadRequest(
            _("The 'request_id' query parameter is required.")
        )

    toolbar = DebugToolbar.fetch(request_id, TemplateProfilerPanel.panel_id)
    if toolbar is None:
        content = _(
            "Data for this panel isn't available anymore. "
            "Please reload the page and retry."
        )
        return HttpResponseBadRequest(content)

    panel = toolbar.get_panel_by_id(TemplateProfilerPanel.panel_id)
    payload = panel.get_export_data()

    response = JsonResponse(payload, json_dumps_params={"indent": 2})
    response["Content-Disposition"] = (
        f'attachment; filename="djdt-templates-{request_id}.json"'
    )
    return response
