from django import template
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag(takes_context=True)
def jazzmin_pagination(context):
    """
    Custom pagination tag that works with Jazzmin admin theme.
    Handles both standard Django pagination and Django REST framework pagination.
    """
    request = context.get('request')
    page_obj = context.get('page_obj')
    paginator = context.get('paginator')
    
    if not page_obj and 'page' in context:
        page_obj = context['page']
    
    if not paginator and 'paginator' in context:
        paginator = context['paginator']
    
    # Handle Django REST Framework pagination
    if not page_obj and 'page' in context and hasattr(context['page'], 'paginator'):
        page_obj = context['page']
        paginator = page_obj.paginator
    
    if not (page_obj and paginator):
        return ''
    
    page_number = page_obj.number
    total_pages = paginator.num_pages
    
    # Calculate page range (show 2 pages before and after current page)
    page_range = []
    for i in range(max(1, page_number - 2), min(page_number + 3, total_pages + 1)):
        page_range.append(i)
    
    # Add ellipsis if needed
    if page_range and page_range[0] > 1:
        page_range.insert(0, 1)
        if page_range[1] > 2:
            page_range[1] = '.'
    
    if page_range and page_range[-1] < total_pages:
        page_range.append(total_pages)
        if page_range[-2] < total_pages - 1:
            page_range[-2] = '.'
    
    # Prepare context for the template
    pagination_context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'page_num': page_number,
        'pages': total_pages,
        'page_range': page_range,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else 1,
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else total_pages,
        'show_first': page_number > 3,
        'show_last': page_number < total_pages - 2,
        'getvars': '',
    }
    
    # Add request GET parameters
    if request and hasattr(request, 'GET'):
        get_vars = request.GET.copy()
        if 'page' in get_vars:
            del get_vars['page']
        if get_vars:
            pagination_context['getvars'] = '&' + get_vars.urlencode()
    
    return mark_safe(render_to_string('jazzmin/pagination_simple.html', pagination_context, request=request))
