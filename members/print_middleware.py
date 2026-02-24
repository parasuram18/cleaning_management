

def MonitoringMiddleware(get_response):
    def middleware(request):

        response = get_response(request)

        print(request.path)

        return response
    
    return middleware