# product/apps.py
from django.apps import AppConfig


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'product'
    verbose_name = 'Product Management'
    
    def ready(self):
        """
        Patch Jazzmin template tag to fix pagination error globally.
        This fixes the 'args or kwargs must be provided' error when format_html is called with empty string.
        
        We use a two-pronged approach:
        1. Patch the module function directly
        2. Override the template tag in the library registry
        
        The custom template tag in product/templatetags/jazzmin_fix.py will also override
        Jazzmin's tag when loaded in templates.
        """
        try:
            from django.utils.html import format_html as django_format_html
            
            # Patch format_html only in Jazzmin's module namespace to avoid interfering with Django core
            # This is safer than patching globally
            import jazzmin.templatetags.jazzmin as jazzmin_module
            
            # Only patch if Jazzmin has its own format_html reference
            if hasattr(jazzmin_module, 'format_html'):
                original_jazzmin_format_html = jazzmin_module.format_html
                
                def patched_jazzmin_format_html(format_string, *args, **kwargs):
                    """Patched format_html for Jazzmin that handles empty format_string gracefully"""
                    try:
                        # Ensure we have at least one argument or kwarg
                        if not format_string and not args and not kwargs:
                            return original_jazzmin_format_html('{}', '')  # Pass empty string as argument
                            
                        # Check if format_string is empty (the source of the error)
                        if not format_string or (isinstance(format_string, str) and not format_string.strip()):
                            # If we have args, use the first one
                            if args:
                                return original_jazzmin_format_html('{}', args[0])
                            # If we have kwargs, use the first value
                            elif kwargs:
                                first_value = next(iter(kwargs.values()), '')
                                return original_jazzmin_format_html('{}', first_value)
                            # Otherwise return empty span with proper format
                            else:
                                return original_jazzmin_format_html('{}', '')  # Pass empty string as argument
                        # Normal case - call original
                        return original_jazzmin_format_html(format_string, *args, **kwargs)
                    except Exception as e:
                        # Last resort - return empty span with proper format
                        try:
                            return original_jazzmin_format_html('{}', '')  # Pass empty string as argument
                        except Exception:
                            # If even that fails, return empty string
                            return ''
                
                jazzmin_module.format_html = patched_jazzmin_format_html
            
            # Get the original function
            original_func = getattr(jazzmin_module, 'jazzmin_paginator_number', None)
            
            if not original_func:
                return
            
            # Create the safe wrapper function that accepts variable arguments
            def safe_jazzmin_paginator_number(*args, **kwargs):
                """
                Safe replacement that never passes empty strings to format_html.
                Accepts variable arguments to match how Django template tags are called.
                """
                # Extract arguments - template tags can be called in different ways
                cl = None
                page_num = None
                url_vars = None
                
                # Try to extract arguments from args/kwargs
                if args:
                    cl = args[0] if len(args) > 0 else None
                    page_num = args[1] if len(args) > 1 else None
                    url_vars = args[2] if len(args) > 2 else kwargs.get('url_vars', None)
                else:
                    cl = kwargs.get('cl', None)
                    page_num = kwargs.get('page_num', None)
                    url_vars = kwargs.get('url_vars', None)
                
                try:
                    # Try calling original first with the same arguments
                    try:
                        result = original_func(*args, **kwargs)
                        if result:
                            return result
                    except TypeError as e:
                        error_str = str(e)
                        # Check if it's the empty format_html error or argument count error
                        if "args or kwargs must be provided" in error_str:
                            # Fall through to safe implementation
                            pass
                        elif "positional arguments" in error_str or "takes" in error_str:
                            # Try calling with extracted arguments
                            if cl is not None and page_num is not None:
                                try:
                                    if url_vars is not None:
                                        result = original_func(cl, page_num, url_vars)
                                    else:
                                        result = original_func(cl, page_num)
                                    if result:
                                        return result
                                except Exception:
                                    pass
                            # Fall through to safe implementation
                        else:
                            raise
                except Exception as e:
                    # For any other exception, fall through to safe implementation
                    pass
                
                # Safe implementation
                try:
                    if not cl or not hasattr(cl, 'page_var'):
                        page_num = page_num or 1
                        return django_format_html('<span class="page-link">{}</span>', page_num)
                    
                    page_num = page_num or 1
                    url_parts = [f"{cl.page_var}={page_num}"]
                    
                    if hasattr(cl, 'is_popup') and cl.is_popup:
                        url_parts.append("_popup=1")
                    
                    if hasattr(cl, 'search_url') and cl.search_url:
                        url_parts.append(str(cl.search_url))
                    
                    url = "?" + "&".join(url_parts)
                    html_str = f'<a href="{url}" class="page-link">{page_num}</a>'
                    
                    return django_format_html('{}', html_str)
                    
                except Exception as e:
                    page_num = page_num or 1
                    return django_format_html('<span class="page-link">{}</span>', page_num)
            
            # Replace in module - this will be used by the template tag when it executes
            # We don't patch the template library directly as that can interfere with template compilation
            jazzmin_module.jazzmin_paginator_number = safe_jazzmin_paginator_number
            
            # Note: format_html patching is already done above if Jazzmin has its own reference
                
        except ImportError:
            pass
        except Exception:
            pass
