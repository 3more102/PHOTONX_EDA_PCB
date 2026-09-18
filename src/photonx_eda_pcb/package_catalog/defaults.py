from .model import PackageEntry
def common_packages():
    return [PackageEntry("R_0603","chip_resistor",2,0.8,1.6,.8,"smd"),PackageEntry("C_0603","chip_capacitor",2,0.8,1.6,.8,"smd"),PackageEntry("SOT-23","sot",3,.95,2.9,1.3,"smd"),PackageEntry("SOIC-8","soic",8,1.27,4.9,3.9,"smd"),PackageEntry("DIP-8","dip",8,2.54,10.2,7.6,"tht")]
