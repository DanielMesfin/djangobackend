"""
Custom template tag to override Jazzmin's problematic paginator_number tag.
This template tag library must be loaded AFTER jazzmin to override it.
"""
from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def jazzmin_paginator_number(*args, **kwargs):
    """
    Safe replacement for Jazzmin's jazzmin_paginator_number tag.
    This prevents the 'args or kwargs must be provided' error when format_html receives an empty string.
    Accepts variable arguments to match how Django template tags are called.
    """
    # Extract arguments - handle both positional and keyword arguments
    cl = None
    page_num = None
    url_vars = None
    
    if args:
        cl = args[0] if len(args) > 0 else None
        page_num = args[1] if len(args) > 1 else None
        url_vars = args[2] if len(args) > 2 else kwargs.get('url_vars', None)
    else:
        cl = kwargs.get('cl', None)
        page_num = kwargs.get('page_num', None)
        url_vars = kwargs.get('url_vars', None)
    
    try:
        # Validate inputs
        if not cl or not hasattr(cl, 'page_var'):
            page_num = page_num or 1
            return format_html('<span class="page-link">{}</span>', page_num)
        
        # Build URL parameters safely
        page_num = page_num or 1
        url_parts = [f"{cl.page_var}={page_num}"]
        
        if hasattr(cl, 'is_popup') and cl.is_popup:
            url_parts.append("_popup=1")
        
        if hasattr(cl, 'search_url') and cl.search_url:
            url_parts.append(str(cl.search_url))
        
        # Construct URL - always non-empty
        url = "?" + "&".join(url_parts)
        
        # Build HTML string - always non-empty
        html_str = f'<a href="{url}" class="page-link">{page_num}</a>'
        
        # Use format_html with proper arguments (format string + content)
        return format_html('{}', html_str)
        
    except Exception:
        # Fallback - return a minimal safe span
        try:
            page_num = page_num or 1
            if cl and hasattr(cl, 'page_var'):
                url = f"?{cl.page_var}={page_num}"
                html_str = f'<a href="{url}" class="page-link">{page_num}</a>'
                return format_html('{}', html_str)
        except Exception:
            pass
        
        # Absolute last resort
        page_num = page_num or 1
        return format_html('<span class="page-link">{}</span>', page_num)

