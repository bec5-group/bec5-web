from .utils import return_jsonp, auth_jsonp, auth_logger

@return_jsonp
@auth_jsonp
def get_logs(request):
    max_count = 1000
    GET = request.GET
    logs = auth_logger.get_records(GET.get('from'), GET.get('to'),
                                   max_count + 1)
    if len(logs) > max_count:
        return {
            'logs': logs[:max_count],
            'is_all': False
        }
    return {
        'logs': logs,
        'is_all': True
    }
