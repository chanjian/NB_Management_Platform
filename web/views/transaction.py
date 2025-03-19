from django.db.models import Q
from django.shortcuts import render
from web import models
from utils.pager import Pagination
from utils.time_filter import filter_by_date_range

def my_transaction_list(request):
    """我的交易记录"""

    keyword = request.GET.get('keyword','').strip()
    con = Q()
    if keyword:
        con.connector = 'OR'
        con.children.append(('order_oid__contains',keyword))

    queryset = models.TransactionRecord.objects.filter(customer_id=request.nb_user.id,active=1).order_by('-id')
    pager = Pagination(request,queryset)

    # 调用封装好的函数进行日期过滤
    queryset, start_date, end_date, pager = filter_by_date_range(request, queryset)

    context = {
        'pager':pager,
        'keyword':keyword,
    }
    print(start_date,end_date,queryset)
    # return render(request,'my_transaction_list.html',context)
    return render(request, 'my_transaction_list.html', locals())
