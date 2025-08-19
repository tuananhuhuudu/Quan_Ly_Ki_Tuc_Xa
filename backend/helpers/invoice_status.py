from enum import Enum 

class InvoiceStatus(str , Enum):
  PAID = "True"
  UNPAID = "False"