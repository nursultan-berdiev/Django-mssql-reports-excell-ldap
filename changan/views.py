from django.http import HttpResponse
from datetime import datetime
from django.shortcuts import render
import pyodbc
from . import commands
from xlsxwriter.workbook import Workbook
from . import excel
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return render(request, 'changan/index.html')
                else:
                    return HttpResponse('Disabled account')
            else:
                message = 'Неверный логин или пароль'
                return render(request, 'changan/login.html', {'form': form, 'message': message})
    else:
        form = LoginForm()
    context = {
        'form': form,
    }

    return render(request, 'changan/login.html', context)


cnxn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=10.10.1.2;'
    'DATABASE=Database;'
    'UID=dbadm;PWD=********')
cursor = cnxn.cursor()


def str_date(date):
    return date.strftime("%Y%m%d")


def index(request):

    return render(request, 'changan/index.html')


def payments(request):
    date_beg = request.GET.get('date_beg')
    date_end = request.GET.get('date_end')
    if date_beg is None:
        date_beg = '19000101'
    if date_end is None:
        date_end = '19000101'

    cursor.execute(commands.payment(date_beg, date_end))
    row = cursor.fetchall()
    title = 'Погашения по кредитам за период'
    context = {
        'row': row,
        'title': title,
        'date_beg': date_beg,
        'date_end': date_end
    }

    request.session['date_beg'] = date_beg
    request.session['date_end'] = date_end

    return render(request, 'changan/payments.html', context)


def excel_payments(request):
    date_beg = request.session['date_beg']
    date_end = request.session['date_end']
    if date_beg is None:
        date_beg = datetime.now()
    if date_end is None:
        date_end = datetime.now()

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = "attachment; filename=Payments{}.xlsx".format(date_end)
    context = {
        'in_memory': True,
        'remove_timezone': True
    }

    book = Workbook(response, context)
    columns = 5
    sheet = book.add_worksheet('Погашения по кредитам')
    for i in range(columns):
        sheet.set_column(i, i, 18)

    col = 0
    row = 0
    sheet.write(0, col, 'Дата', excel.style_format(book))
    sheet.write(row, col + 1, 'Погашение, сом', excel.style_format(book))
    sheet.write(row, col + 2, 'Погашение, доллар', excel.style_format(book))
    sheet.write(row, col + 3, 'Проценты, сом', excel.style_format(book))
    sheet.write(row, col + 4, 'Проценты, доллар', excel.style_format(book))

    row = 1
    col = 0

    cursor.execute(commands.payment(date_beg, date_end))
    sql_row = cursor.fetchall()

    for a in sql_row:
        sheet.write(row, col, a.Date, excel.date_format(book))
        sheet.write(row, col + 1, a.Pay417, excel.money_format(book))
        sheet.write(row, col + 2, a.Pay840, excel.money_format(book))
        sheet.write(row, col + 3, a.Proc417, excel.money_format(book))
        sheet.write(row, col + 4, a.Proc840, excel.money_format(book))
        row = row + 1
    book.close()

    return response


def overdue_view(request):
    date_beg = request.GET.get('date_beg')
    date_end = request.GET.get('date_end')
    if date_beg is None:
        date_beg = '19000101'
    if date_end is None:
        date_end = '19000101'

    cursor.execute(commands.overdue(date_beg, date_end))
    overdue_row = cursor.fetchall()
    title = 'Просрочки за период'
    paginator = Paginator(overdue_row, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'overdue_row': page_obj,
        'date_beg': date_beg,
        'date_end': date_end
    }

    request.session['date_beg'] = date_beg
    request.session['date_end'] = date_end

    return render(request, 'changan/overdue.html', context)


def excel_overdues(request):
    date_beg = request.session['date_beg']
    date_end = request.session['date_end']
    if date_beg is None:
        date_beg = datetime.now()
    if date_end is None:
        date_end = datetime.now()

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = "attachment; filename=Overdues{}.xlsx".format(date_end)
    context = {
        'in_memory': True,
        'remove_timezone': True
    }

    book = Workbook(response, context)
    columns = 14
    sheet = book.add_worksheet('Погашения по кредитам')
    for i in range(columns):
        sheet.set_column(i, i, 18)

    col = 0
    row = 0
    sheet.write(0, col, 'Номер ID', excel.style_format(book))
    sheet.write(row, col + 1, 'Клиент', excel.style_format(book))
    sheet.write(row, col + 2, 'Дата рождения', excel.style_format(book))
    sheet.write(row, col + 3, 'Паспорт', excel.style_format(book))
    sheet.write(row, col + 4, 'ИНН', excel.style_format(book))
    sheet.write(row, col + 5, 'Начало просрочки', excel.style_format(book))
    sheet.write(row, col + 6, 'Конец просрочки', excel.style_format(book))
    sheet.write(row, col + 7, 'Дни просрочки', excel.style_format(book))
    sheet.write(row, col + 8, 'Просрочка осн. сумма', excel.style_format(book))
    sheet.write(row, col + 9, 'Кредитный специалист', excel.style_format(book))
    sheet.write(row, col + 10, 'Продукт', excel.style_format(book))
    sheet.write(row, col + 11, 'Номер счета', excel.style_format(book))
    sheet.write(row, col + 12, 'Остаток в номинале', excel.style_format(book))
    sheet.write(row, col + 13, 'Остаток в нац. валюте', excel.style_format(book))

    row = 1
    col = 0

    cursor.execute(commands.overdue(date_beg, date_end))
    sql_row = cursor.fetchall()

    for a in sql_row:
        sheet.write(row, col, a.number, excel.number_format(book))
        sheet.write(row, col + 1, a.ClientName, excel.style_format(book))
        sheet.write(row, col + 2, a.birth_date, excel.date_format(book))
        sheet.write(row, col + 3, a.passport, excel.style_format(book))
        sheet.write(row, col + 4, a.inn, excel.number_format(book))
        sheet.write(row, col + 5, a.start_overdue, excel.date_format(book))
        sheet.write(row, col + 6, a.end_overdue, excel.date_format(book))
        sheet.write(row, col + 7, a.overdue_days, excel.number_format(book))
        sheet.write(row, col + 8, a.main_overdue_summ, excel.money_format(book))
        sheet.write(row, col + 9, a.user, excel.style_format(book))
        sheet.write(row, col + 10, a.product, excel.style_format(book))
        sheet.write(row, col + 11, a.account_no, excel.number_format(book))
        sheet.write(row, col + 12, a.current_balance, excel.money_format(book))
        sheet.write(row, col + 13, a.current_nat_balance, excel.money_format(book))
        row = row + 1
    book.close()

    return response


def payments_purpose(request):
    date_beg = request.GET.get('date_beg')
    date_end = request.GET.get('date_end')
    if date_beg is None:
        date_beg = '19000101'
    if date_end is None:
        date_end = '19000101'

    cursor.execute(commands.payment_purpose(date_beg, date_end))
    row = cursor.fetchall()
    title = 'Погашения по кредитам за период по целям'
    context = {
        'row': row,
        'title': title,
        'date_beg': date_beg,
        'date_end': date_end
    }

    request.session['date_beg'] = date_beg
    request.session['date_end'] = date_end

    return render(request, 'changan/payments_purpose.html', context)


def excel_payments_purpose(request):
    date_beg = request.session['date_beg']
    date_end = request.session['date_end']
    if date_beg is None:
        date_beg = datetime.now()
    if date_end is None:
        date_end = datetime.now()

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = "attachment; filename=Payments_purpose{}.xlsx".format(date_end)
    context = {
        'in_memory': True,
        'remove_timezone': True
    }

    book = Workbook(response, context)
    columns = 5
    sheet = book.add_worksheet('Погашения {}-{}'.format(date_beg, date_end))
    for i in range(columns):
        sheet.set_column(i, i, 18)

    col = 0
    row = 0
    sheet.write(0, col, 'Цель', excel.style_format(book))
    sheet.write(row, col + 1, 'Погашение, сом', excel.style_format(book))
    sheet.write(row, col + 2, 'Погашение, доллар', excel.style_format(book))
    sheet.write(row, col + 3, 'Проценты, сом', excel.style_format(book))
    sheet.write(row, col + 4, 'Проценты, доллар', excel.style_format(book))

    row = 1
    col = 0

    cursor.execute(commands.payment_purpose(date_beg, date_end))
    sql_row = cursor.fetchall()

    for a in sql_row:
        sheet.write(row, col, a.Purpose, excel.style_format(book))
        sheet.write(row, col + 1, a.Pay417, excel.money_format(book))
        sheet.write(row, col + 2, a.Pay840, excel.money_format(book))
        sheet.write(row, col + 3, a.Proc417, excel.money_format(book))
        sheet.write(row, col + 4, a.Proc840, excel.money_format(book))
        row = row + 1
    book.close()

    return response


def verifications(request):
    client_name = request.GET.get('client_name')
    date_beg = request.GET.get('date_beg')
    date_end = request.GET.get('date_end')
    verificated = request.GET.get('verificated')
    risk = request.GET.get('risk')

    if date_beg is None or date_beg == '':
        date_beg = '2010-01-01'
    if date_end is None or date_end == '':
        date_end = '2025-12-31'
    if client_name is None:
        client_name = ''
    if verificated is None:
        verificated = ''
    if risk is None:
        risk = '1,2,3'

    cursor.execute(commands.verification(client_name, date_beg, date_end, verificated, risk))
    row = cursor.fetchall()
    paginator = Paginator(row, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Верификации'
    context = {
        'row': page_obj,
        'title': title,
        'date_beg': date_beg,
        'date_end': date_end,
        'client_name': client_name,
        'verificated': verificated,
        'risk': risk
    }

    request.session['date_beg'] = date_beg
    request.session['date_end'] = date_end
    request.session['client_name'] = client_name
    request.session['verificated'] = verificated
    request.session['risk'] = risk

    return render(request, 'changan/verifications.html', context)


def excel_verifications(request):
    client_name = request.session['client_name']
    date_beg = request.session['date_beg']
    date_end = request.session['date_end']
    verificated = request.session['verificated']
    risk = request.session['risk']
    if date_beg is None:
        date_beg = '20100101'
    if date_end is None:
        date_end = datetime.now()

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = "attachment; filename=Verifications.xlsx"
    context = {
        'in_memory': True,
        'remove_timezone': True
    }

    book = Workbook(response, context)
    columns = 7
    sheet = book.add_worksheet('Верификации по клиентам')
    for i in range(columns):
        sheet.set_column(i, i, 18)

    col = 0
    row = 0
    sheet.write(0, col, 'ID Клиента', excel.style_format(book))
    sheet.write(row, col + 1, 'Клиент', excel.style_format(book))
    sheet.write(row, col + 2, 'Дата верификации', excel.style_format(book))
    sheet.write(row, col + 3, 'Инспектор', excel.style_format(book))
    sheet.write(row, col + 4, 'Верификатор', excel.style_format(book))
    sheet.write(row, col + 5, 'Уровень риска', excel.style_format(book))
    sheet.write(row, col + 6, 'Верифицирован', excel.style_format(book))

    row = 1
    col = 0

    cursor.execute(commands.verification(client_name, date_beg, date_end, verificated, risk))
    sql_row = cursor.fetchall()

    for a in sql_row:
        sheet.write(row, col, a.CustomerID, excel.number_format(book))
        sheet.write(row, col + 1, a.ClientName, excel.style_format(book))
        sheet.write(row, col + 2, a.VerificationDate, excel.date_format(book))
        sheet.write(row, col + 3, a.Inspector, excel.style_format(book))
        sheet.write(row, col + 4, a.Verificator, excel.style_format(book))
        sheet.write(row, col + 5, a.Risk, excel.style_format(book))
        sheet.write(row, col + 6, a.Verificated, excel.style_format(book))
        row = row + 1
    book.close()

    return response


def linked_customers(request):
    client_name = request.GET.get('client_name')
    date_beg = request.GET.get('date_beg')
    date_end = request.GET.get('date_end')
    verificated = request.GET.get('verificated')

    if date_beg is None or date_beg == '':
        date_beg = '2010-01-01'
    if date_end is None or date_end == '':
        date_end = '2025-12-31'
    if client_name is None:
        client_name = ''
    if verificated is None:
        verificated = ''

    cursor.execute(commands.verification(client_name, date_beg, date_end, verificated))
    row = cursor.fetchall()
    paginator = Paginator(row, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Верификации'
    context = {
        'row': page_obj,
        'title': title,
        'date_beg': date_beg,
        'date_end': date_end,
        'client_name': client_name,
        'verificated': verificated
    }

    request.session['date_beg'] = date_beg
    request.session['date_end'] = date_end
    request.session['client_name'] = client_name
    request.session['verificated'] = verificated

    return render(request, 'changan/verifications.html', context)


def excel_linked_customers(request):
    client_name = request.session['client_name']
    date_beg = request.session['date_beg']
    date_end = request.session['date_end']
    verificated = request.session['verificated']
    if date_beg is None:
        date_beg = '20100101'
    if date_end is None:
        date_end = datetime.now()

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = "attachment; filename=Verifications.xlsx"
    context = {
        'in_memory': True,
        'remove_timezone': True
    }

    book = Workbook(response, context)
    columns = 7
    sheet = book.add_worksheet('Верификации по клиентам')
    for i in range(columns):
        sheet.set_column(i, i, 18)

    col = 0
    row = 0
    sheet.write(0, col, 'ID Клиента', excel.style_format(book))
    sheet.write(row, col + 1, 'Клиент', excel.style_format(book))
    sheet.write(row, col + 2, 'Дата верификации', excel.style_format(book))
    sheet.write(row, col + 3, 'Инспектор', excel.style_format(book))
    sheet.write(row, col + 4, 'Верификатор', excel.style_format(book))
    sheet.write(row, col + 5, 'Уровень риска', excel.style_format(book))
    sheet.write(row, col + 6, 'Верифицирован', excel.style_format(book))

    row = 1
    col = 0

    cursor.execute(commands.verification(client_name, date_beg, date_end, verificated))
    sql_row = cursor.fetchall()

    for a in sql_row:
        sheet.write(row, col, a.CustomerID, excel.number_format(book))
        sheet.write(row, col + 1, a.ClientName, excel.style_format(book))
        sheet.write(row, col + 2, a.VerificationDate, excel.date_format(book))
        sheet.write(row, col + 3, a.Inspector, excel.style_format(book))
        sheet.write(row, col + 4, a.Verificator, excel.style_format(book))
        sheet.write(row, col + 5, a.Risk, excel.style_format(book))
        sheet.write(row, col + 6, a.Verificated, excel.style_format(book))
        row = row + 1
    book.close()

    return response