def jazzmin_pagination_context_processor(request):
    """
    Context processor to fix Jazzmin pagination issues.
    """
    return {
        'jazzmin_paginator_fix': True,
    }
