from pydantic import BaseModel
from datetime import datetime
class ContractExtendRequest(BaseModel):
    new_end_date: datetime