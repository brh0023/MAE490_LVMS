# MAE-490/492 LIFTOFF Team 3
# Main data processing script
# Created by: Bradley Henderson, bradley.henderson@uah.edu
# Date: 7/29/2017
#   Last updated: 11/16/2017


import numpy as np
import matplotlib.pyplot as plt
plt.close("all")


#The following line needs to be changed based on the saving style, the headers
#  must be in order as determined by the Arduino data saving

colHeaders = ['time_millis','atmoPressureA','atmoPressureB', \
              'intPressure','intTemp','ax','ay','az', \
              'mx','my','mz','gx','gy','gz']


# VARIABLES ARE FOR TESTING, REMOVE LATER
#filename = 'demo_day_flight1.txt' #filename for testing
fig_dpi = 600

#Ask for file name to process
filename = input('What is the data file to process? : ')   #ask user for data file to process
print('The filename being processed is:',filename)#print what filename was input

#ask user for figure dpi value
#fig_dpi = int(input('What dpi would you like the figures to be? (whole number): '))
#get the flight data from the file, skip first 4 rows (start-up data)
flightData = np.loadtxt(fname=filename, delimiter=',',skiprows=4) 


#function to retrieve data based on what column header is requested
def getData(colHeaders,data_array,variable_interest): 
    j = 0
    i = 0
    for i in range(len(colHeaders)):           #loops over entire 'colHeaders' list
        if colHeaders[i] == variable_interest: #finds column index for req. data
                j = i                          #hold the index value
    dataRequested = data_array[:,j]            #column of data
    return dataRequested                       #return the requested data

#function to take derivitive
def getDerivitive(data_array):
    dataDerivitive = np.zeros((len(data_array)-1,1))
    i = 0
    for i in range(len(data_array)-1):             #loops over entire dataArray
        dataDerivitive[i] = data_array[i+1] - data_array[i] #difference
    return dataDerivitive                         #return the differenced data

#function to exponentially smooth any data set
def smoothData(data_array):
    smoothedData = np.zeros((len(data_array),1))
    i = 1
    for i in range(len(data_array)-1):             #loops over entire dataArray
        smoothedData[i] = (0.7*data_array[i]) + (0.3*data_array[i-1]) #EXP smooth
    smoothedData[len(data_array)-1] = data_array[len(data_array)-1]
    smoothedData[0] = data_array[0]
    return smoothedData                         #return the differenced data

######## Importing data section ########

#get time (in ms)
if 'time_millis' in colHeaders:
    time_ms = getData(colHeaders,flightData,'time')
    time_seconds = time_ms/1000.0
    time_offset = time_seconds[1]
    time_seconds = time_seconds - time_offset
#get time in seconds if not in milliseconds
elif 'time_seconds' in colHeaders:
    time_seconds = getData(colHeaders,flightData,'time')
    
#get atmosheric pressures
if 'atmoPressureA' in colHeaders:
    PressureA = getData(colHeaders,flightData,'atmoPressureA')
    OutputA = (PressureA/9.0)*(3.3/1023.0)
    atmoPressureA = (1000*(((OutputA/3.3)+0.095)/0.009))
    PressureB = getData(colHeaders,flightData,'atmoPressureB')
    OutputB = (PressureB/9.0)*(3.3/1023.0)
    atmoPressureB = (1000*(((OutputB/3.3)+0.095)/0.009))
    #section below for smoothing pressure/altitude data
    atmoPressureA = smoothData(atmoPressureA)
    atmoPressureB = smoothData(atmoPressureB)
      
#get altitudes
if 'atmoPressureA' in colHeaders:
    pressureMillibarA = atmoPressureA/100.0;                              #converts kPa to mBar
    altA = (1-(pow((pressureMillibarA/1013.25),0.190284)))*145366.45  #calculates altitude in feet
    initial_altA = np.average(altA[1:40])
    altA = altA - initial_altA
    pressureMillibarB = atmoPressureB/100.0;                              #converts kPa to mBar
    altB = (1-(pow((pressureMillibarB/1013.25),0.190284)))*145366.45  #calculates altitude in feet  
    initial_altB = np.average(altB[1:40])
    altB = altB - initial_altB
    maxAltA = np.amax(altA)
    maxAltB = np.amax(altB)
    print('Max Alt. A is:',maxAltA,'feet') #print max altA
    print('Max Alt. B is:',maxAltB,'feet') #print max altB
    
#get internal pressure
if 'intPressure' in colHeaders:
    intPressure_hundredths = getData(colHeaders,flightData,'intPressure')
    intPressure = intPressure_hundredths/100
    
#get internal temp.
if 'intTemp' in colHeaders:
    #thermistor coefficients and resistances
    Rref     = 10000
    R1_therm = 10000    #R1 value for voltage divider at thermistor
    a1 = 0.003354016
    b1 = 0.0002569850
    c1 = 0.000002620131
    D1 = 0.00000006383091
    Vs_therm = 3.30
    intTempV = (getData(colHeaders,flightData,'intTemp'))/1000.0
    R = R1_therm/((Vs_therm/intTempV)-1)
    intTempK = 1.0/(a1 + (b1*np.log(R/Rref))+ \
               (c1*np.power((np.log(R/Rref)),2)) + \
               (D1*np.power((np.log(R/Rref)),3)))
    intTempC = intTempK - 273.15
    intTempF = (intTempC*1.8) + 32.0
    
#get accelerations (milli-g)
if 'ax' in colHeaders:
    ax = getData(colHeaders,flightData,'ax')
    ay = getData(colHeaders,flightData,'ay')
    az = getData(colHeaders,flightData,'az')
#get gyro rates (degrees/sec)
if 'roll' in colHeaders:
    roll  = getData(colHeaders,flightData,'roll')
    pitch = getData(colHeaders,flightData,'pitch')
    yaw   = getData(colHeaders,flightData,'yaw')
#get magnetometer data (milli-gauss)
if 'mx' in colHeaders:
    mx = getData(colHeaders,flightData,'mx')
    my = getData(colHeaders,flightData,'my')
    mz = getData(colHeaders,flightData,'mz')
    
#get gyro rates (Degrees/sec)
if 'gx' in colHeaders:
    gx = getData(colHeaders,flightData,'gx')
    gy = getData(colHeaders,flightData,'gy')
    gz = getData(colHeaders,flightData,'gz')


######## Flight data characteristics section ########

#Sampling Frequency over time
samplingFreq = 1.0/getDerivitive(time_seconds)

# max altitude?

# vertical velocity
vertVelocityA = getDerivitive(altA)/getDerivitive(time_seconds)
vertVelocityB = getDerivitive(altB)/getDerivitive(time_seconds)
# max velocity?

# vertical acceleration
vertAccelA = (getDerivitive(vertVelocityA)/getDerivitive(time_seconds[1:len(time_seconds)]))/32.2
vertAccelB = (getDerivitive(vertVelocityB)/getDerivitive(time_seconds[1:len(time_seconds)]))/32.2
# coast time?

# drag?

# #thrust?



######## Plotting section ########
if 'time_millis' or 'time_seconds' in colHeaders:
    if 'atmoPressureA' in colHeaders:
    #atmospheric pressure plot(s)
        fig_pressure = plt.figure(1)
        plt.title('Atmospheric Pressure vs. Time') # title        
        plt.ylabel('Pressure [Pa]')
        plt.xlabel('Time [s]')
        plt.plot(time_seconds,atmoPressureA, 'rs-', label='Sensor A')
        plt.plot(time_seconds,atmoPressureB, 'bo-', label='Sensor B')
        fig_pressure.tight_layout()
        plt.legend()
        plt.savefig('pressurePlot.png', dpi=fig_dpi)
        plt.show()
        
    if 'atmoPressureA' in colHeaders:
    #altitude plot(s)
        fig_altitude = plt.figure(2)
        plt.title('Altitude vs. Time') # title        
        plt.ylabel('Altitude [ft]')
        plt.xlabel('Time [s]')
        plt.plot(time_seconds,altA,'rs-', label='Sensor A')
        plt.plot(time_seconds,altB,'bo-', label='Sensor B')
        fig_pressure.tight_layout()
        plt.legend()
        plt.savefig('altitudePlot.png', dpi=fig_dpi, bbox_inches='tight')
        plt.show()
           
    if 'intPressure' in colHeaders:
    #internal pressure plot(s)
        fig_intPressure = plt.figure(3)
        plt.title('Internal Pressure vs. Time') # title
        plt.ylabel('Pressure [PSI]')
        plt.xlabel('Time [s]')
        plt.plot(time_seconds,intPressure)
        fig_intPressure.tight_layout()
        plt.savefig('internalPressurePlot.png', dpi=fig_dpi, bbox_inches='tight')  
        plt.show()
                 
    if 'intTemp' in colHeaders:
    #internal temperature plot(s)
        fig_intTemp = plt.figure(4)
        plt.title('Internal Temperature vs. Time') # title
        plt.ylabel('Temperature [F]')
        plt.xlabel('Time [s]')
        plt.plot(time_seconds,intTempF)
        fig_intTemp.tight_layout()
        plt.savefig('internalTempPlot.png', dpi=fig_dpi, bbox_inches='tight')
        plt.show()
           
    if 'ax' in colHeaders:        
    #acceleration plot(s)
        fig_accel = plt.figure(5)
        plt.title('Acceleration vs. Time') # title
        plt.ylabel('Acceleration [milli-g]')
        plt.xlabel('Time [s]')
        plt.plot(time_seconds, ax, label='a-X')
        plt.plot(time_seconds, ay, label='a-Y')
        plt.plot(time_seconds, az, label='a-Z')        
        fig_accel.tight_layout()
        plt.legend()
        plt.savefig('accerlerationPlot.png', dpi=fig_dpi, bbox_inches='tight')
        plt.show()
           
    if 'roll' in colHeaders:
    #angular rates plot(s)
        fig_rates = plt.figure(6)
        plt.title('AHRS vs. Time') # title
        plt.ylabel('Heading [deg]')
        plt.xlabel('Time [s]')
        plt.plot(time_seconds, roll, label='Roll')
        plt.plot(time_seconds, pitch, label='Pitch')
        plt.plot(time_seconds, yaw, label='Yaw')
        fig_accel.tight_layout()
        plt.legend()
        plt.savefig('AHRSplot.png', dpi=fig_dpi, bbox_inches='tight')
        plt.show()
           
    if 'mx' in colHeaders:
    #magnetometer plot(s)
        fig_mag = plt.figure(7)
        plt.title('Magnetic Field vs. Time') # title
        plt.ylabel('Magnetic Field [mGauss]')
        plt.xlabel('Time [s]')
        plt.plot(time_seconds, mx, label='m-X')
        plt.plot(time_seconds, my, label='m-Y')
        plt.plot(time_seconds, mz, label='m-Z')
        fig_mag.tight_layout()
        plt.legend()
        plt.savefig('magneticFieldPlot.png', dpi=fig_dpi, bbox_inches='tight')
        plt.show()
               
    if 'gx' in colHeaders:
    #angular rates plot(s)
        fig_rates = plt.figure(8)
        plt.title('Angular Rates vs. Time') # title
        plt.ylabel('Angular Rate [deg/s]')
        plt.xlabel('Time [s]')
        plt.plot(time_seconds, gx, label='g-X')
        plt.plot(time_seconds, gy, label='g-Y')
        plt.plot(time_seconds, gz, label='g-Z')
        fig_accel.tight_layout()
        plt.legend()
        plt.savefig('angularRatesPlot.png', dpi=fig_dpi, bbox_inches='tight')
        plt.show()
        
    
####### Extra Graphs #######
    if 'vertVelocityA' and 'vertVelocityB' in globals():
    # vertitcal veloctiy plot
        fig_vertVelocity = plt.figure(9)
        plt.title('Vertical Velocity vs. Time') # title        
        plt.ylabel('Velocity [ft/s]')
        plt.xlabel('Time [s]')
        plt.plot(time_seconds[1:len(time_seconds)], vertVelocityA, 'rs-', label='Pressure Sensor A')
        plt.plot(time_seconds[1:len(time_seconds)], vertVelocityB, 'bo-', label='Pressure Sensor B')
        fig_vertVelocity.tight_layout()
        plt.legend()
        plt.savefig('verticalVelocityPlot.png', dpi=fig_dpi)
        plt.show()
                
        
    if 'vertAccelA' and 'vertAccelB' in globals():
    # vertical acceleration plot
        fig_vertAccel = plt.figure(10)
        plt.title('Vertical Acceleration vs. Time') # title        
        plt.ylabel('Acceleration [g]')
        plt.xlabel('Time [s]')
        plt.plot(time_seconds[2:len(time_seconds)], vertAccelA, 'rs-', label='Pressure Sensor A')
        plt.plot(time_seconds[2:len(time_seconds)], vertAccelB, 'bo-', label='Pressure Sensor B')
        fig_vertAccel.tight_layout()
        plt.legend()
        plt.savefig('verticalAccelPlot.png', dpi=fig_dpi)
        plt.show()
             
        
    if 'time_millis' and 'samplingFreq' in globals():
        #Sampling frequency plot
        fig_samplingFreq = plt.figure(11)
        plt.title('Sampling Frequency vs. Time') # title        
        plt.ylabel('Sampling Frequency [Hz]')
        plt.xlabel('Time [s]')
        plt.plot(time_seconds[1:len(time_seconds)],samplingFreq, '-')
        fig_samplingFreq.tight_layout()
        plt.savefig('samplingFreqPlot.png', dpi=fig_dpi)
        plt.show()
        
        
        
        
        
        
        
