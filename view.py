__author__ = 'dmytro'

from django.http import HttpResponse
from django.db import connection
from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import redirect

import forms
import action
from MySQLConnection import MySQL

def homePage(request):
    return render(request, "base.html", { }, context_instance = RequestContext(request))

def showSales(request):
    cursor = connection.cursor()
    cursor.execute("select * from SALES;")
    row = cursor.fetchone()
    print row

    return HttpResponse("See the response")

def AddSales(request):
    if 'POST' == request.method:
        print "Information from POST:"
        print request.POST['promotion_name']
        print request.POST['price']
        print request.POST['customer']
        print request.POST['product']

        bd = MySQL()
        cursor = bd.getCursor()
        # cursor = action.db.cursor() # for execute sql command
        #cursor.execute( "SET foreign_key_checks = 0;" )

        cursor.execute( "SET foreign_key_checks = 0;" )

        # add new promotion
        query = "INSERT INTO PROMOTION values( 0, \"{0}\", {1} ); ".format( \
            request.POST['promotion_name'], request.POST['price'] )
        print query
        cursor.execute( query )
        # action.db.commit()

        # get last promotion id
        query = "SELECT MAX(idPROMOTION) FROM PROMOTION;"
        print query
        cursor.execute( query )
        res = cursor.fetchall()
        promotion_id = res[0][0]

        # insert new sales
        query = "INSERT INTO SALES values( 0, {0}, {1}, {2}, CURDATE()  ); ".format( \
            request.POST['product'], promotion_id, request.POST['customer'] )
        print query
        cursor.execute( query )
        #action.db.commit()

        cursor.close()
        bd.close()
        return render(request, "commit.html", context_instance = RequestContext(request))
    else:
        product_choiser = action.getProductList()
        customer_choiser = action.getCustomerList()

        formset = forms.AddSallesForm( myChoiseCustomer = customer_choiser, myChoiseProduct = product_choiser )

    return render(request, "AddSales.html", {
        'formset' : formset,
        'title' : "Add new sale"
        }, context_instance = RequestContext(request))

def searchView(request):
    return render(request, "searchLink.html", context_instance = RequestContext(request))

def about(request):
    return render(request, "about.html", context_instance = RequestContext(request))

def searchProduct(request):
    if 'POST' == request.method:
        print "text: " + request.POST['text_names']
        cursor = action.db.cursor() # for execute sql command

        list_name = ""
        for name in request.POST['text_names'].split(','):
            list_name += " \"{0}\",".format( name.replace(" ", "") )
        list_name = list_name[:-1]

        query = "SELECT * FROM PRODUCT WHERE  name IN ({0});".format( list_name )
        print query

        cursor.execute(query)

        content = u""
        # make list of customer variants
        for row in cursor.fetchall() :
            content += u"{0} {1} {2} <hr> \t".format(row[1], row[2], row[3])

        print content

        #cursor.close()
        return render(request, "resultView.html", {
            'table' : content,
            }, context_instance = RequestContext(request))
    else:
        formset = forms.SearchProductForm()

    return render(request, "AddSales.html", {
        'formset' : formset,
        'title' : "Search product"
        }, context_instance = RequestContext(request))

def searchPromotion(request):
    if 'POST' == request.method:
        print "min: " + request.POST['min_value']
        print "max: " + request.POST['max_value']
        cursor = action.db.cursor() # for execute sql command

        query = "SELECT * FROM PROMOTION WHERE price BETWEEN {0} AND {1};".format( request.POST['min_value'], request.POST['max_value'] )
        print query
        cursor.execute(query)

        content = u""
        # make list of customer variants
        for row in cursor.fetchall() :
            content += u"{0} {1} <hr> \t".format(row[1], row[2])

        print content

        #cursor.close()
        return render(request, "resultView.html", {
            'table' : content,
        }, context_instance = RequestContext(request))
    else:
        formset = forms.SearchPromotionForm()

    return render(request, "AddSales.html", {
        'formset' : formset,
        'title' : "Search promotion"
        }, context_instance = RequestContext(request))

def searchCustomer(request):
    if 'POST' == request.method:
        print "min: " + request.POST['city']
        cursor = action.db.cursor() # for execute sql command

        if "man" in request.POST:
            man = True
        else:
            man = False

        query = "SELECT * FROM CUSTOMER WHERE adress = \"{0}\" and man = {1};".format( request.POST['city'], man )
        print query
        cursor.execute(query)

        content = u""
        # make list of customer variants
        for row in cursor.fetchall() :
            content += u"{0} {1} <hr> \n".format(row[1], row[2])

        print content

        #cursor.close()
        return render(request, "resultView.html", {
        'content' : content,
        }, context_instance = RequestContext(request))
    else:
        formset = forms.SearchCustomerForm()

    return render(request, "AddSales.html", {
        'formset' : formset,
        'title' : "Search customer"
        }, context_instance = RequestContext(request))

def fullTextSearch( request ):
    if 'POST' == request.method:
        cursor = action.db.cursor() # for execute sql command

        prefix = "+"
        if '1' == request.POST['fullSearch']:
            prefix = "-"

        print request.POST['fullSearch']
        request.POST['name']
        query = "SELECT * FROM PRODUCT WHERE MATCH (Description) AGAINST ({0}\"{1}\" in boolean mode);"\
            .format( prefix, request.POST['name'] )
        print query
        print request.POST['name']
        cursor.execute(query)

        content = u""
        # make list of customer variants
        for row in cursor.fetchall() :
            content += u"{0} {1} <hr>\t".format(row[1], row[2])

        print content

        #cursor.close()
        return render(request, "resultView.html", {
        'table' : content,
        }, context_instance = RequestContext(request))
    else:
        formset = forms.FullTextSearchForm()

    return render(request, "AddSales.html", {
        'formset' : formset,
        'title' : "Full text search"
        }, context_instance = RequestContext(request))

def getView( request ):
    cursor = action.db.cursor() # for execute sql command
    query = "SELECT * FROM SALES;"

    # execute command
    cursor.execute(query)
    table = "<table style=\"width:100%\">\n"

    # make list of customer variants
    for row in cursor.fetchall() :
        table += "\t<tr>\n\t\t<td>{0}</td>\n\t\t<td>{1}</td>\n\t\t<td>{2}</td>\
        \n\t\t<td>{3}</td>\n\t\t<td><a href=\"/updateSale?id={0}\">Update</a></td>\
        \n\t\t<td> <a href=\"/delSale?id={0}\">Delete</a> </td>\n\t</tr>\n".\
            format(row[0], row[1], row[2], row[3] )
    table += "</table>"

    return render(request, "resultView.html", {
        'table' : table,
        }, context_instance = RequestContext(request))

def delSales( request ):
    """
    Get get query with parameters fro delete

    :param request:
    :return:
    """

    if 'GET' == request.method:
        cursor = action.db.cursor() # for execute sql command

        query = "DELETE FROM SALES WHERE idSALES = {0};".format(request.GET['id'])
        print query
        print "Id: ", request.GET['id']

        # execute command
        cursor.execute(query)
        return redirect( getView )
        # return HttpResponse("nice")

sales_id = 0
def updateSales( request ):
    global sales_id
    print "start"

    if 'POST' == request.method:
        print "POST"
        cursor = action.db.cursor() # for execute sql command
        query = "UPDATE SALES SET PRODUCT_idPRODUCT = {0},\
         PROMOTION_idPROMOTION = {1}, CUSTOMER_idCUSTOMER = {2} WHERE idSALES = {3};"\
            .format(request.POST['product'], request.POST['promotion'], request.POST['customer'], sales_id)

        print query
        cursor.execute(query)
        action.db.commit()

        #return HttpResponse("nice")
        return redirect( getView )
    else:
        promotion_choiser = action.getPromotionList()
        product_choiser = action.getProductList()
        customer_choiser = action.getCustomerList()
        sales_id = request.GET['id']

        query = "SELECT * FROM SALES WHERE idSALES = {0};".format(request.GET['id'])
        cursor = action.db.cursor() # for execute sql command
        cursor.execute(query)
        row = cursor.fetchall()[0]

        init = {
            "product" : row[1],
            "customer" : row[3],
            "promotion" : row[2],
        }

        formset = forms.UpdateSalesForm( myChoiseCustomer = customer_choiser,\
                                         myChoiseProduct = product_choiser,\
                                         myChoisePromotion = promotion_choiser,\
                                         init = init)

        return render(request, "AddSales.html", {
            'formset' : formset,
            'title' : "Update sale"
            }, context_instance = RequestContext(request))

