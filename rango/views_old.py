__author__ = 'admin'


def search(request):
    context = RequestContext(request)
    category_list = get_5_categories()
    context_dict = {'categories': category_list}
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # run Bing function to get results list
            result_list = run_query(query)
    context_dict['result_list'] = result_list
    return render_to_response('rango/search.html', {'result_list': result_list}, context)