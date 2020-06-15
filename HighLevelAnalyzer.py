# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting


# High level analyzers must subclass the HighLevelAnalyzer class.
class Hla(HighLevelAnalyzer):
    # List of settings that a user can set for this High Level Analyzer
    Line_start_delimiter_Type = ChoicesSetting(choices=('HEX', 'DEC', 'CHAR'))
    Line_start_delimiter = StringSetting(label='Line start delimiter')
    Terminal_output_type = ChoicesSetting(choices=('HEX', 'DEC', 'HEX & DEC', 'CHAR'))

    delimiter = ""
    lineLimit = ""

    delimiterFound = False
    delimiterProcessing = False
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


        # If the character matches the one we are searching for, output a new frame
        if self.Line_start_delimiter_Type == 'HEX':
            if currentFrameValueHex == self.delimiter:
                print("")
                self.delimiterFound = True
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

            self.rowStore = outputString
            self.delimiterProcessing = True
            self.delimiterFound = False
            print("Delimiter " + self.Line_start_delimiter_Type + " Val: " + self.delimiter + ", Terminal outputting " + self.Terminal_output_type)
            print("")

        else:
            print(outputString)



        '''if self.deliniator == self.Line_start_delimiter:
                    return AnalyzerFrame('mytype', frame.start_time, frame.end_time, {
                        'input_type': frame.type
                 })'''

        #self.delimiterFound = False
        # Return the data frame itself
        return AnalyzerFrame('mytype', frame.start_time, frame.end_time, {
            'input_type': "DEC: " + str(currentFrameValueDec) + "  HEX: 0x" + currentFrameValueHex + " CHAR: " + chr(currentFrameValueDec),
        })
