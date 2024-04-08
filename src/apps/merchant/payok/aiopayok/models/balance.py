from pydantic import BaseModel


class Balance(BaseModel):
    '''Payok API balance model'''

    balance: float
    ref_balance: float
