def cart_alerts(request):
    """
    Context processor to handle cart alerts and clear them after display
    """
    show_cart_alert = None
    
    # Get the alert from session if it exists
    if 'show_cart_alert' in request.session:
        show_cart_alert = request.session['show_cart_alert']
        # Clear the alert from session so it doesn't show again on refresh
        del request.session['show_cart_alert']
        request.session.modified = True
    
    return {
        'show_cart_alert': show_cart_alert
    }
