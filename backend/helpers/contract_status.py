from enum import Enum 

class ContractStatus(str , Enum):
  ACTIVE = "active"
  INACTIVE = "inactive"
  
  