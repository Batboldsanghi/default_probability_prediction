from typing import Any, Optional
from pydantic import BaseModel, validator
import config

class Auth(BaseModel):
    username: str
    password: str  

class Req1(BaseModel):
    uuid: str
    account_worst_status_0_3m: Optional[int] = None
    age: int
    max_paid_inv_0_12m: float
    max_paid_inv_0_24m: float
    num_arch_dc_0_12m: int
    num_arch_rem_0_12m: int
    num_unpaid_bills: int
    status_last_archived_0_24m: int
    sum_capital_paid_account_0_12m: float
    sum_paid_inv_0_12m: float
    merchant_group: str 
    merchant_category: str

    @validator('account_worst_status_0_3m')
    def validator_field1(cls, v):        
        if(v not in range(0,100)):
            raise ValueError('needs to be between (0,100)')
        return v

    @validator('age')
    def validator_range_20_100(cls, v):
        if(v not in range(20,100)):
            raise ValueError('needs to be between (20,100)')
        return v

    @validator('max_paid_inv_0_12m','max_paid_inv_0_24m','sum_capital_paid_account_0_12m','sum_paid_inv_0_12m')
    def validator_range_0_1000000(cls, v):
        if(v not in range(0,1000000)):
            raise ValueError('needs to be between (0,1000000)')
        return v

    @validator('num_arch_dc_0_12m','num_arch_rem_0_12m','status_last_archived_0_24m')
    def validator_range_0_100(cls, v):
        if(v not in range(0,100)):
            raise ValueError('needs to be between (0,100)')
        return v

    @validator('num_unpaid_bills')
    def validator_range_0_1000(cls, v):
        if(v not in range(0,1000)):
            raise ValueError('needs to be between (0,1000)')
        return v

    @validator('merchant_group')
    def validator_merchant_group(cls, v):
        
        if(v not in config.merchant_group):
            raise ValueError('unknown merchant group. please enter again')
        return v

    @validator('merchant_category')
    def validator_merchant_category(cls, v):
        
        if(v not in config.merchant_category):
            raise ValueError('unknown merchant category. please enter again')
        return v
    