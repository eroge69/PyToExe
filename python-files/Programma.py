print('Введите требуемые для расчета параметры:скорость воздуха вдоль длины поверхности(в метрах в секунду), температуру воздуха(в градусах Цельсия),температуру поверхности(в градусах Цельсия),степень черноты поверхности, ширину поверхности(в метрах), длину поверхности(в метрах)')
AirVelocity = float(input('Введите скорость воздуха вдоль длины поверхности(в метрах в секунду)'))
AirTemperature = float(input('Введите температуру воздуха(в градусах Цельсия)'))
SurfaceTemperature = float(input('Введите температуру поверхности(в градусах Цельсия)'))
Blackness = float(input('Введите степень черноты поверхности'))
Width = float(input('Введите ширину поверхности(в метрах)'))
Length = float(input('Введите длину поверхности(в метрах)'))
print('Введите тип расчета, введя соответствующую цифру: 1-принудительная конвекция, 2-естественная конвекция, 3 - естественная нестабильная конвекция, 4 - естественная стабильная конвенкция')
TypeOfCalculation = int(input('Введите число от 1 до 4'))
DefiningTemperature = (AirTemperature+SurfaceTemperature)/2
if ((TypeOfCalculation == 1) or (TypeOfCalculation == 2)): 
    DefiningSurfaceSize = Length
else: 
    DefiningSurfaceSize = ((Width*Length)/(2*(Width+Length)))
AirDencity = 353.0885/(273.15 + DefiningTemperature)
DynamicAirViscosityCoefficient = (7.06064681472347*(10**-9)*(DefiningTemperature**3)-0.0000217418543389576*(DefiningTemperature**2)+0.0482101987326381*(DefiningTemperature)+17.1625054185128)/1000000
SpecificIsobaricHeatCapacityOfAir = 1.81359472734094*(10**-10)*(DefiningTemperature**4)-5.87507811990248*(10**-7)*(DefiningTemperature**3)+0.000578428942965047*(DefiningTemperature**2)+0.00743322055343565*(DefiningTemperature)+1005.64463836247    
CoefficientOfThermalConductivityOfAir = (9.34273884650736*(10**-10)*(DefiningTemperature**3)-2.53697754410552*(10**-6)*(DefiningTemperature**2)+0.00732841363832881*DefiningTemperature+2.41822263249161)/100
CinematicAirViscosityCoefficient = DynamicAirViscosityCoefficient/AirDencity
CoefficientOfVolumetricExpansionOfAir = 1 / (273.15 + DefiningTemperature)
Prandtl = DynamicAirViscosityCoefficient*SpecificIsobaricHeatCapacityOfAir/CoefficientOfThermalConductivityOfAir
Reinolds = AirVelocity*DefiningSurfaceSize/CinematicAirViscosityCoefficient
Grassgoff = 9.80666*CoefficientOfVolumetricExpansionOfAir*abs(SurfaceTemperature-AirTemperature)*(DefiningSurfaceSize**3)/(CinematicAirViscosityCoefficient**2)
Reley = Prandtl*Grassgoff
if TypeOfCalculation == 1:
    if Reinolds <= 500000:
        Nusselt = 0.664*(Reinolds**0.5)*(Prandtl**(1/3))
    elif Reinolds <= 30000000:
        Nusselt = 0.037*(Reinolds**(4/5))*(Prandtl**(43/100))
    else: 
        Nusselt = '???'
elif TypeOfCalculation == 2:
    if Reley <= 1000000000:
        Nusselt = 0.68+0.67*(Reley**(1/4))*(1+(0.492/Prandtl)**(9/16))**(-4/9)
    else:
        Nusselt = 0.825 + (0.387*(Reley**(1/6)))/((1+((0.492/Prandtl)**(9/16)))**(8/27))
elif TypeOfCalculation == 3:
    if (Reley >= 10000) and (Reley <= 10000000):
        Nusselt = 0.54*((Reley)**(1/4))
    elif (Reley >= 10000000) and (Reley <= 10000000000):
        Nusselt = 0.15*((Reley)**(1/3))
    else: 
        Nusselt = '???'
elif TypeOfCalculation == 4:
    if (Reley >= 100000) and (Reley <= 100000000000):
        Nusselt = 0.27*((Reley)**(1/4))
    else: 
        Nusselt = '???'
else:
    Nusselt = '???'
if isinstance(Nusselt, str):
    ConvectiveHeatTransferCoefficient = 'не может быть рассчитан'
    TotalHeatTransferCoefficient = 'не может быть рассчитан'
    SpecificHeatFlowCapacity = 'не может быть рассчитана'
    FullHeatFlowCapacity = 'не может быть рассчитана'
else:
    ConvectiveHeatTransferCoefficient = Nusselt*CoefficientOfThermalConductivityOfAir/DefiningSurfaceSize
    if SurfaceTemperature < AirTemperature:
        CoefficientOfRadiativeHeatTransfer = 0
    else:
        CoefficientOfRadiativeHeatTransfer = Blackness*0.00000005670367*((SurfaceTemperature+273.15)**4-(AirTemperature+273.15)**4)/(SurfaceTemperature-AirTemperature)
    TotalHeatTransferCoefficient = ConvectiveHeatTransferCoefficient + CoefficientOfRadiativeHeatTransfer
    SpecificHeatFlowCapacity = TotalHeatTransferCoefficient*(SurfaceTemperature-AirTemperature)
    FullHeatFlowCapacity = SpecificHeatFlowCapacity*Width*Length
print('Определяющая температура равна:', DefiningTemperature,'градусов Цельсия')
print('Определяющий размер поверхности:', DefiningSurfaceSize,'м')
print('Плотность воздуха:', AirDencity,'кг/м^3')
print('Динамический коэффициент вязкости воздуха:', DynamicAirViscosityCoefficient,'Па*с')
print('Удельная изобараная теплоемкость воздуха:', SpecificIsobaricHeatCapacityOfAir,'Дж/(кг*К)')
print('Коэффициент теплопроводности воздуха:', CoefficientOfThermalConductivityOfAir,'Вт/(м*К)')
print('Кинематический коэффициент вязкости:', CinematicAirViscosityCoefficient,'м^2/c')
print('Коэффициент объемного расширения воздуха:', CoefficientOfVolumetricExpansionOfAir,'1/К')
print('Число Прандтля:', Prandtl)
print('Число Рейнольдса:', Reinolds)
print('Число Грассгофа:', Grassgoff)
print('Число Релея:', Reley)
print('Число Нуссельта:', Nusselt)
print('Коэффициент конвективной теплоотдачи:', ConvectiveHeatTransferCoefficient,'Вт/(м^2*К)')
print('Коэффициент радиационной теплоотдачи:', CoefficientOfRadiativeHeatTransfer,'Вт/(м^2*К)')
print('Суммарный коэффициент теплоотдачи:', TotalHeatTransferCoefficient,'Вт/(м^2*К)')
print('Удельная мощность теплового потока:', SpecificHeatFlowCapacity,'Вт/м^2')
print('Полная мощность теплового потока:', FullHeatFlowCapacity,'Вт')
