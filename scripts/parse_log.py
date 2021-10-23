#!/usr/bin/python3

import argparse, re, statistics, json
import constants

"""
Class to represent a test environment reference values
"""
class Reference:
    def __init__(self, temperature, humidity):
        self.temperature = float(temperature)
        self.humidity = float(humidity)

"""
Class to represent any sensor type
"""
class Sensor:
    def __init__(self, name, values=None):
        self.name = name
        if values is None:
            self.values = []
        else:
            self.values = values

    def add_value(self, value):
        self.values.append(float(value))

"""
Class to represent a thermometer
"""
class Thermometer(Sensor):
    LABEL = "Thermometer"
    LOG_LABEL = "thermometer"
    THERM_RANGE = 0.5

    THERM_ULTRA_PRECISE = { 'label': 'ultra precise', 'deviation': 3.0 }
    THERM_VERY_PRECISE = { 'label': 'very precise', 'deviation': 5.0 }
    THERM_PRECISE = { 'label': 'precise' }

    def evaluate(self, reference):
        ref_min = reference.temperature - self.THERM_RANGE
        ref_max = reference.temperature + self.THERM_RANGE
        mean = sum(self.values)/len(self.values)

        if mean > ref_min and mean < ref_max:
            std_dev = statistics.stdev(self.values)
            if std_dev < self.THERM_ULTRA_PRECISE['deviation']:
                print("{} {} has standard deviation {} and is '{}'.".format(self.LABEL, self.name, std_dev, self.THERM_ULTRA_PRECISE['label']))
                return self.THERM_ULTRA_PRECISE['label']
            elif std_dev < self.THERM_VERY_PRECISE['deviation']:
                print("{} {} has standard deviation {} and is '{}'.".format(self.LABEL, self.name, std_dev, self.THERM_VERY_PRECISE['label']))
                return self.THERM_VERY_PRECISE['label']

        print("{} {} is '{}'.".format(self.LABEL, self.name, self.THERM_PRECISE['label']))
        return self.THERM_PRECISE['label']

"""
Class to represent a humidity sensor
"""
class HumiditySensor(Sensor):
    LABEL = "Humidity sensor"
    LOG_LABEL = "humidity"
    HUMIDITY_RANGE = 0.01

    def evaluate(self, reference):
        one_percent = reference.humidity * self.HUMIDITY_RANGE
        ref_min = reference.humidity - one_percent
        ref_max = reference.humidity + one_percent
        deviations = 0

        for value in self.values:
            if value < ref_min or value > ref_max:
                deviations += 1
        
        if deviations > 0:
            print("{} {} has {} deviatations. Will be discarded.".format(self.LABEL, self.name, deviations))
            return "discard"
        else:
            print("{} {} has {} deviatations. Will be kept.".format(self.LABEL, self.name, deviations))
            return "keep"


"""
Class to represent a carbon monoxide detector (TBD)
"""
class CODetector:
    pass

"""
Class to represent a noise level detector (TBD)
"""
class NoiseLevelDetector:
    pass

"""
Return output file passed as an argument or default value if no argument received
"""
def get_output_file(output):
    return args.output or constants.DEFAULT_OUTPUT

"""
Function will parse a log file, evaluate quality of a sensors and write their classification into the output file
"""
def parse(log, output):
    print("File {} will be parsed and exported to {}".format(log, output))
    data = {}

    with open(log, "r") as logfile:
        line = logfile.readline().split()
        reference = Reference(line[1], line[2])
        print("Test room reference values:")
        print("     temperature:    {} degrees".format(reference.temperature))
        print("     humidity:       {} %".format(reference.humidity))
        print()
        
        line = logfile.readline().split()
        while line:
            if line[0] == Thermometer.LOG_LABEL:
                sensor = Thermometer(line[1])
                print("{} {} registered.".format(Thermometer.LABEL, sensor.name))
            elif line[0] == HumiditySensor.LOG_LABEL:
                sensor = HumiditySensor(line[1])
                print("{} {} registered.".format(HumiditySensor.LABEL, sensor.name))
            else:
                sensor.add_value(line[1])
            
            line = logfile.readline().split()
            if line:
                regexp = re.compile(constants.SENSORS_REGEX)
                if regexp.match(line[0]):
                    cq = sensor.evaluate(reference)
                    data[sensor.name] = cq
                    print()

        # evaluate last sensor
        cq = sensor.evaluate(reference)
        data[sensor.name] = cq
        print()

    with open(output, "w") as outputfile:
        json.dump(data, outputfile)


""" Local usage:
python3 ./parse_log.py ../logs/example.log
python3 ./parse_log.py ../logs/example.log --export output.log
"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read the log file, parse its content and save the results in a file.')
    parser.add_argument('function', help='parse')
    parser.add_argument('log', help='path to the log file to parse')
    parser.add_argument('-o', '--output', help='output file to export (default: {})'.format(constants.DEFAULT_OUTPUT), default=constants.DEFAULT_OUTPUT)
    args = parser.parse_args()

    output_file = get_output_file(args.output)

    if args.function == "parse":
        globals()[args.function](args.log, output_file)
