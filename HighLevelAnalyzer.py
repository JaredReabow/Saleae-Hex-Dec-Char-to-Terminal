# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions
from time import *

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting


# High level analyzers must subclass the HighLevelAnalyzer class.
class Hla(HighLevelAnalyzer):
    # List of settings that a user can set for this High Level Analyzer
    Line_start_delimiter_Type = ChoicesSetting(choices=('HEX', 'DEC', 'CHAR'))
    Line_start_delimiter = StringSetting(label='Line start delimiter')
    Terminal_output_type = ChoicesSetting(choices=('HEX', 'DEC', 'HEX & DEC', 'CHAR'))
    Output_Chunk_Time = ChoicesSetting(choices=('Yes', 'No'))
    Output_Frame_Time = ChoicesSetting(choices=('Yes', 'No'))
    Output_Configuration = ChoicesSetting(choices=('Yes', 'No'))


    delimiter = ""
    lineLimit = ""

    startTime = 0;
    startFrameTime = 0
    startChunkTime = 0
    firstFrame = True

    delimiterFound = False
    delimiterProcessing = False
    customFrameTag = False

    rowStore = ""
    unknownStore = ""
    previousFrameValue = ""
    toggler = 0
    if Line_start_delimiter == "":
        delimiter = "DISABLED"
    else:
        delimiter = Line_start_delimiter

    # An optional list of types this analyzer produces, providing a way to customize the way frames are displayed in Logic 2.
    result_types = {
        'mytype': {
            'format': ' {{data.input_type}} '
        }
    }

    def __init__(self):
        '''
        Initialize HLA.

        Settings can be accessed using the same name used above.
        '''

        print("Delimiter type: "+self.Line_start_delimiter_Type, "Delimiter: "+self.delimiter, "Terminal output type: "+ self.Terminal_output_type)



    def decode(self, frame: AnalyzerFrame):
        currentFrameValueHex = frame.data['data'].hex()
        currentFrameValueDec = int(currentFrameValueHex,16)

        hours = int(str(frame.start_time).split("T")[1].split(":")[0]) * 60 * 60
        minutes = int(str(frame.start_time).split("T")[1].split(":")[1]) * 60
        seconds = float(((str(frame.start_time).split("T")[1].split(":")[2]).split("Z"))[0])

        hoursEnd = int(str(frame.end_time).split("T")[1].split(":")[0]) * 60 * 60
        minutesEnd = int(str(frame.end_time).split("T")[1].split(":")[1]) * 60
        secondsEnd = float(((str(frame.end_time).split("T")[1].split(":")[2]).split("Z"))[0])

        totalSecondsStart =  hours + minutes + seconds

        totalSecondsEnd = hoursEnd + minutesEnd + secondsEnd

        if self.firstFrame == True:
            self.startTime = totalSecondsStart
            self.startFrameTime = frame.start_time
            self.firstFrame = False


        # If the character matches the one we are searching for, output a new frame
        if self.Line_start_delimiter_Type == 'HEX':
            if currentFrameValueHex == self.delimiter:
                print("")
                self.delimiterFound = True
                startChunkTime = totalSecondsStart
        elif self.Line_start_delimiter_Type == 'DEC':
            if int(currentFrameValueDec) == int(self.delimiter):
                print("")
                self.delimiterFound = True
        elif self.Line_start_delimiter_Type == 'CHAR':
            if chr(currentFrameValueDec) == self.delimiter:
                print("")
                self.delimiterFound = True


        if self.Terminal_output_type == 'HEX':
            outputString = str(currentFrameValueHex)
        elif self.Terminal_output_type == 'DEC':
            outputString = str(currentFrameValueDec)
        elif self.Terminal_output_type == 'CHAR':
            outputString = str(chr(currentFrameValueDec))
        elif self.Terminal_output_type == 'HEX & DEC':
            outputString = (str(currentFrameValueDec)+"-"+str(currentFrameValueHex))

        if self.delimiterFound == True and self.delimiterProcessing == False:
            self.rowStore = outputString
            self.delimiterProcessing = True
            self.delimiterFound = False
        elif self.delimiterFound == False and self.delimiterProcessing == True:
            self.rowStore = self.rowStore + ","+ outputString
        elif self.delimiterFound == True and self.delimiterProcessing == True:
            print("")
            print(self.rowStore)
            self.rowStore = ""
            self.rowStore = outputString
            self.delimiterProcessing = True
            self.delimiterFound = False

            if self.Output_Chunk_Time == 'Yes':
                print(" Chunk time: " + str(totalSecondsEnd-startChunkTime))
                print(" Chunk START time: " + str(frame.start_time).split("T")[1], " Chunk END time: " + str(frame.end_time).split("T")[1])
            if self.Output_Frame_Time == 'Yes':
                print(" First frame time: " + str(self.startFrameTime).split("T")[1]," Last frame time: " + str(frame.end_time).split("T")[1])
            if self.Output_Configuration == 'Yes':
                print(" Delimiter " + self.Line_start_delimiter_Type + " Val: " + self.delimiter + ", Terminal outputting " + self.Terminal_output_type)
                print(" Total runTime: " + str(totalSecondsEnd - self.startTime))

        else:
            print(outputString )
            outputString = ""


        '''if self.deliniator == self.Line_start_delimiter:
                    return AnalyzerFrame('mytype', frame.start_time, frame.end_time, {
                        'input_type': frame.type
                 })'''

        #self.delimiterFound = False
        if self.customFrameTag == False:
            # Return the data frame itself
            return AnalyzerFrame('mytype', frame.start_time, frame.end_time, {
                'input_type': "DEC: " + str(currentFrameValueDec) + "  HEX: 0x" + currentFrameValueHex + " CHAR: " + chr(currentFrameValueDec),
            })
        else:
            # Return the data frame itself
            return AnalyzerFrame('mytype', frame.start_time, frame.end_time, {
                'input_type': "DEC: " + str(
                    currentFrameValueDec) + "  HEX: 0x" + currentFrameValueHex + " CHAR: " + chr(currentFrameValueDec),
            })

