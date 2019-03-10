from aiohttp import web
import json
import psycopg2


def make_connection():
    return psycopg2.connect(dbname='avito_test',
                            user='',
                            password='',
                            host='localhost')


def add_company(name):
    db = make_connection()
    cursor = db.cursor()

    cursor.execute("INSERT INTO company (name) VALUES ('{}');".format(str(name)))
    db.commit()

    cursor.close()
    db.close()


def add_join_employee(employee_name, company_name=None):
    name = str(employee_name)
    db = make_connection()
    cursor = db.cursor()

    if not company_name:  # Просто создаём сотрудника
        cursor.execute("INSERT INTO employee (name) VALUES ('{}');".format(name))
        db.commit()
    else:  # Привязываем к компании
        cursor.execute("SELECT id FROM company WHERE name = '{}';".format(str(company_name)))
        company_id = int(cursor.fetchall()[0][0])

        cursor.execute("SELECT * FROM employee WHERE name = '{}';".format(name))

        if cursor.fetchall():  # Если такой сотрудник существует
            cursor.execute("UPDATE employee SET company_id = {} WHERE name = '{}';".format(company_id, employee_name))
        else:  # Если не существует сотрудника
            cursor.execute("INSERT INTO employee (name, company_id) VALUES ('{}', {});".format(name, company_id))
        db.commit()

    cursor.close()
    db.close()


def add_product(title):
    db = make_connection()
    cursor = db.cursor()

    cursor.execute("INSERT INTO product (title) VALUES ('{}');".format(str(title)))
    db.commit()

    cursor.close()
    db.close()


def choose_responsible_employee(title, employee_name):
    db = make_connection()
    cursor = db.cursor()

    cursor.execute("SELECT id FROM employee WHERE name = '{}';".format(str(employee_name)))
    employee_id = int(cursor.fetchall()[0][0])

    cursor.execute("UPDATE product SET employee_id = {} WHERE title = '{}';".format(employee_id, str(title)))
    db.commit()

    cursor.close()
    db.close()


async def add_company_post(request):
    try:
        company_name = str(request.query['name'])
        add_company(company_name)
        response_obj = {'status': 'success', 'message': 'company was added: ' + company_name}
        return web.Response(text=json.dumps(response_obj), status=200)

    except Exception as e:
        response_obj = {'status': 'failure', 'message': str(e)}
        return web.Response(text=json.dumps(response_obj), status=500)


async def add_join_employee_post(request):
    try:  # В параметрах запроса ищем имя сотрудника
        employee_name = str(request.query['employee_name'])
        company_name = None
        message_part_company = ''

        try:  # В параметрах запроса ищем название компании
            company_name = str(request.query['company_name'])
            message_part_company = company_name
        except Exception:  # Название компании не нашли
            message_part_company = 'does not indicate'
        finally:
            add_join_employee(employee_name, company_name)
            response_obj = {'status': 'success', 'message': 'employee was added: {}; to a company: {}'.format(employee_name, message_part_company)}
            return web.Response(text=json.dumps(response_obj), status=200)

    except Exception as e:  # Имя сотрудника не нашли
        response_obj = {'status': 'failure', 'message': str(e)}
        return web.Response(text=json.dumps(response_obj), status=500)


async def add_product_post(request):
    try:
        title = str(request.query['title'])
        add_product(title)
        response_obj = {'status': 'success', 'message': 'product was added: ' + title}
        return web.Response(text=json.dumps(response_obj), status=200)

    except Exception as e:
        response_obj = {'status': 'failure', 'message': str(e)}
        return web.Response(text=json.dumps(response_obj), status=500)


async def choose_responsible_employee_post(request):
    try:
        title = str(request.query['title'])
        employee_name = str(request.query['employee_name'])
        choose_responsible_employee(title, employee_name)
        response_obj = {'status': 'success', 'message': 'responsible employee for {}: {}'.format(title, employee_name)}
        return web.Response(text=json.dumps(response_obj), status=200)

    except Exception as e:
        response_obj = {'status': 'failure', 'message': str(e)}
        return web.Response(text=json.dumps(response_obj), status=500)


app = web.Application()

app.router.add_post('/add_company', add_company_post)
app.router.add_post('/add_join_employee', add_join_employee_post)
app.router.add_post('/add_product', add_product_post)
app.router.add_post('/choose_responsible_employee', choose_responsible_employee_post)

web.run_app(app, host='127.0.0.1', port='8000')
