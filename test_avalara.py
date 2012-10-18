from base import Document, Line, Address
from api import API
from avalara import AvalaraException
import settings_local
import datetime


def get_api():
    return API(settings_local.AVALARA_ACCOUNT_NUMBER, settings_local.AVALARA_LICENSE_KEY, settings_local.AVALARA_COMPANY_CODE, live=False)

def test_gettax():
    api = get_api()
    # A Lat/Long from Avalara's documentation
    lat = 47.627935 
    lng = -122.51702
    line = Line(Amount=10.00)
    doc = Document()
    doc.add_line(line)
    tax = api.get_tax(lat, lng, doc)
    assert tax.is_success() == True
    assert tax.Tax > 0


# when dealing with line items going to different addresses, i.e. a drop-ship situation
# don't use the basic add_from/add_to_address helpers just manually match your own 
# Origin and Destination codes for the addresses and line items
def test_multiple_address_fail():
    doc = Document.new_sales_order(DocCode='1001', DocDate=datetime.date.today(), CustomerCode='email@email.com')
    from_address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    to_address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    doc.add_from_address(from_address)
    doc.add_to_address(to_address)
    try:
        doc.add_from_address(from_address)
    except AvalaraException:
        assert True
    else:
        assert False
    try:
        doc.add_to_address(from_address)
    except AvalaraException:
        assert True
    else:
        assert False


def test_posttax():
    api = get_api()
    # CustomerCode is just a unique identifier for a customer, often times, an email address or user id
    doc = Document.new_sales_order(DocCode='1001', DocDate=datetime.date.today(), CustomerCode='email@email.com')
    from_address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    to_address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    doc.add_from_address(from_address)
    doc.add_to_address(to_address)
    line = Line(Amount=10.00)
    doc.add_line(line)
    tax = api.post_tax(doc)
    assert tax.is_success() == True
    assert tax.Tax > 0