from pydantic import BaseModel, Field
from typing import Optional

class WellData(BaseModel):
    wellhead_temp: float = Field(..., alias="Wellhead Temp. (C)")
    wellhead_press: float = Field(..., alias="Wellhead Press (psi)")
    mmcfd_gas: float = Field(..., alias="MMCFD- gas")
    bopd: float = Field(..., alias="BOPD (barrel of oil produced per day)")
    bwpd: float = Field(..., alias="BWPD (barrel of water produced per day)")
    bsw: float = Field(..., alias="BSW - basic solid and water (%)")
    co2: float = Field(..., alias="CO2 mol. (%) @ 25 C & 1 Atm.")
    gas_grav: float = Field(..., alias="Gas Grav.")
    corrosion_defect: float = Field(..., alias="CR-corrosion defect ")
    timestamp: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
