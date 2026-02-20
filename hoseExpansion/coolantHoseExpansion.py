"""
coolantHoseExpansion.py
Keith Bozin 2026-02-18 started
The purpose of this program is to calculate the needed makeup volume for the pressure pulsing coolant cart

"""
import math # needed for pi

# Calculate lenght of hose in cm
lengthFeet = float(input("What is the length of hose in feet? "))
lengthCm = lengthFeet * 12 * 2.54
print("The length of a ", f"{lengthFeet:.3f}", " foot hose is", f"{lengthCm:.3f}", " cm \n")

# Calculate the cross sectional area hose with no pressure
diamInch = float(input("What is the diameter of hose in inches? "))
diamInitCm = diamInch * 2.54
print("The diameter in cm is: ", f"{diamInitCm:.3f}")
areaInit = ((diamInitCm)/2)**2 * math.pi
print("The area of an unpressurized hose is ", f"{areaInit:.3f}", "cm2")

# Calculate the cross sectional area of pressurized hose
diamPress = float(input("What is the expected change in diameter of hose when pressurized in cm? ")) + diamInitCm
print("The pressurized diameter in cm is: ", f"{diamPress:.3f}")
areaPress = (diamPress/2)**2 * math.pi
print("The area of a pressurized hose is ", f"{areaPress:.3f}", "cm2 \n")

# Calculate volumes of hoses and change in volume
volumeInit = lengthCm * areaInit
volumePress = lengthCm * areaPress
volumeChange = volumePress - volumeInit
print("The initial volume is ", f"{volumeInit:.3f}", "cm3 ", "The pressurized volume is ", f"{volumePress:.3f}", "cm3 ", "The change in volume is ", f"{volumeChange:.3f}", "cm3 \n")

numberHoses = int(input("How many hoses are in the test? "))
print("For ", numberHoses, " Hoses the volumes are: ")
print("The initial volume is ", f"{volumeInit * numberHoses:.3f}", "cm3 ", "The pressurized volume is ", f"{volumePress * numberHoses:.3f}", "cm3 ", "The change in volume is ", f"{volumeChange * numberHoses:.3f}", "cm3 \n")

# Calculate stroke length needed
boreInch = float(input("What is the bore diameter of the cylinder in inches "))
boreCm = boreInch * 2.54
stroke = (volumeChange * numberHoses)/(math.pi* (boreCm/2)**2)
print("The stroke length for ", numberHoses, "hoses is", f"{stroke:.3f}", "cm or", f"{stroke/2.54:.3f}", "inches")

# Calculate force needed to reach 100 PSI
forceLbf = 100 * math.pi * boreInch**2
print("The force need for a ", boreInch, "inch cylinder to reach 100 psi is ", f"{forceLbf:.3f}", " LbF or", f"{forceLbf*4.448:.3f}", "Newtons \n")


# Code from Gpt5-mini to calc change in volume of water with temperature change
"""
rho_4 = 0.9999749       # g/cm3 at 4 C (table)
rho_99 = 0.959058       # g/cm3 at 99 C (interpolated)
V1 = volumeInit            # cm3

m = rho_4 * V1
V2 = m / rho_99
dV = V2 - V1
rel = dV / V1 * 100.0
print("Change in volume with temperature change going from 4C to 99C")
print(f"V1 = {V1:.3f} cm3")
print(f"V2 = {V2:.3f} cm3")
print(f"Delta V = {dV:.3f} cm3 ({rel:.3f} %)")
"""
