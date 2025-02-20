from starlette.responses import JSONResponse

from parable import templates

async def dashboard(request):
    template = 'dashboard.html'
    context = {'request': request}
    return templates.TemplateResponse(template, context)