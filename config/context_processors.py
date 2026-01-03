def jazzmin_pagination_context_processor(request):
    """
    Context processor to handle pagination settings and fix common issues.
    """
    context = {
        'jazzmin_paginator_fix': True,
        'pagination_required': False,  # Will be overridden in views
        'page_range': [],
        'page_num': 1,
        'pages': 1,
        'has_previous': False,
        'has_next': False,
        'show_first': False,
        'show_last': False,
        'previous_page_number': 1,
        'next_page_number': 1,
        'getvars': '',
    }
    
    # Add pagination parameters from request
    if hasattr(request, 'GET') and 'p' in request.GET:
        try:
            context['page_num'] = max(1, int(request.GET.get('p', 1)))
        except (ValueError, TypeError):
            context['page_num'] = 1
    
    # Preserve other GET parameters
    if hasattr(request, 'GET'):
        get_vars = request.GET.copy()
        if 'p' in get_vars:
            del get_vars['p']
        if get_vars:
            context['getvars'] = '&' + get_vars.urlencode()
    
    return context
