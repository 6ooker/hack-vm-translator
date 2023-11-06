#!/bin/python3

class CodeWriter:
    SP_inc = '// SP++\n@SP\nM=M+1\n'
    SP_dec = '// SP--\n@SP\nM=M-1\n'
    segment_alias = {'local': 'LCL', 'argument': 'ARG',
                     'this': 'THIS', 'that': 'THAT'}
    
    def __init__(self, outputFile) -> None:
#        self.outf = open(self._outfile(infile), 'a')
#        self.filename = infile.split("/")[-1].replace('.vm', '')
        self.filename = ''
        self.outf = open(outputFile, 'a')
        #self.writeBootstrapCode()
    
#    def _outfile(self, infile):
#        if (infile.endswith('.vm')):
#            return infile.replace('.vm', '.asm')
#        else:
#            return infile + '.asm'
    
    def setFileName (self, fileName):
        self.filename = fileName.split("/")[-1].replace('.vm','')
    
    def writeBootstrapCode(self):
        self.outf.write(self._bootstrapCode())
        self.writeCall("Sys.init", 0, 1)
    
    def writeArithmetic(self, command, lineNumber):
        _command_string = f'\n// {command}\n'
        
        if (command == 'add'): _command_string += self._binaryOpp('D+M')
        elif (command == 'sub'): _command_string += self._binaryOpp('M-D')
        elif (command == 'neg'): _command_string += self._unaryOpp('-M')
        elif (command == 'eq'): _command_string += self._compareOpp('JEQ', lineNumber)
        elif (command == 'gt'): _command_string += self._compareOpp('JGT', lineNumber)
        elif (command == 'lt'): _command_string += self._compareOpp('JLT', lineNumber)
        elif (command == 'and'): _command_string += self._binaryOpp('D&M')
        elif (command == 'or'): _command_string += self._binaryOpp('D|M')
        elif (command == 'not'): _command_string += self._unaryOpp('!M')
        
        self.outf.write(_command_string)
    
    def _binaryOpp(self, comp):
        _command_string = CodeWriter.SP_dec
        _command_string += \
f'''
A=M
D=M
'''
        _command_string += CodeWriter.SP_dec
        _command_string += \
f'''
A=M
M={comp}        // compute {comp}
'''
        _command_string += CodeWriter.SP_inc
        
        return _command_string
    
    def _unaryOpp(self, comp):
        _command_string = CodeWriter.SP_dec
        _command_string += \
f'''
A=M
M={comp}        // compute {comp}
'''
        _command_string += CodeWriter.SP_inc
        
        return _command_string
    
    def _compareOpp(self, jump, lineNumber):
        _command_string = CodeWriter.SP_dec
        _command_string += \
f'''
A=M
D=M
'''
        _command_string += CodeWriter.SP_dec
        _command_string += \
f'''
A=M
D=M-D
@EQ_{lineNumber}        // jump to EQ
D;{jump}
@SP
A=M
M=0
@NE_{lineNumber}        // jump to NE
0;JMP
(EQ_{lineNumber})
    @SP
    A=M
    M=-1
(NE_{lineNumber})
'''
        _command_string += CodeWriter.SP_inc
        
        return _command_string
    
    def writePushPop(self, command, segment, index):
        
        _command_string = ''
        if (command == 1):                                   # C_PUSH
            _command_string += self._pushString(segment, index)
        elif (command == 2):
            _command_string += self._popString(segment, index)
        else:
            print('Error at writePushPop()')
        
        self.outf.write(_command_string)

    def _pushString(self, segment, index):
        _command_string = ''

        if (segment == 'constant'):
            _command_string += \
f'''
// push constant {index}
@{index}
D=A
@SP
A=M
M=D
'''
            _command_string += CodeWriter.SP_inc
            
        elif (segment == 'static'):
            _command_string += \
f'''
// push static {index}
@{self.filename}.{index}
D=M
@SP
A=M
M=D
'''
            _command_string += CodeWriter.SP_inc
            
        elif (segment == 'temp'):
            _command_string += \
f'''
// push temp {index}
@5
D=A
@{index}
A=D+A
D=M
@SP
A=M
M=D
'''
            _command_string += CodeWriter.SP_inc
            
        elif (segment == 'pointer'):
            if (index == 0):
                _command_string += \
f'''
// push pointer 0
@THIS
D=M
@SP
A=M
M=D
'''
                _command_string += CodeWriter.SP_inc
            elif (index == 1):
                _command_string += \
f'''
// push pointer 1
@THAT
D=M
@SP
A=M
M=D
'''
                _command_string += CodeWriter.SP_inc
            else:
                print("Error: pointer can only be 0/1")

        else:
            _command_string += \
f'''
// push {segment} {index}
@{index}
D=A
@{CodeWriter.segment_alias[segment]}
A=M+D
D=M
@SP
A=M
M=D
'''
            _command_string += CodeWriter.SP_inc

        return _command_string
    
    def _popString(self, segment, index):
        _command_string = ''
        
        if (segment == 'static'):
            _command_string += \
f'''
// pop static {index}
@SP
M=M-1
A=M
D=M
@{self.filename}.{index}
M=D
'''
        
        elif (segment == 'temp'):
            _command_string += \
f'''
// pop temp {index}
@5
D=A
@{index}
D=D+A
@R13        // temp. store address in R13
M=D
'''
            _command_string += CodeWriter.SP_dec
            _command_string += \
f'''A=M
D=M
@R13        // get target address back from R13
A=M
M=D
'''
        
        elif (segment == 'pointer'):
            if (index == 0):
                _command_string += CodeWriter.SP_dec
                _command_string += \
f'''
// pop pointer 0
A=M
D=M
@THIS
M=D
'''
            elif (index == 1):
                _command_string += CodeWriter.SP_dec
                _command_string += \
f'''
// pop pointer 1
A=M
D=M
@THAT
M=D
'''
            else:
                print("Error: pointer can only be 0/1")
        
        else:
            _command_string += \
f'''
// pop {segment} {index}
@{index}
D=A
@{CodeWriter.segment_alias[segment]}
D=D+M
@R13        // temp. store address in R13
M=D
'''
            _command_string += CodeWriter.SP_dec
            _command_string += \
f'''
A=M
D=M
@R13        // get target address back from R13
A=M
M=D
'''
        
        return _command_string
    
    def writeLabel(self, label):
        _command_string = \
f'''
// label {label}
({label})
'''
        self.outf.write(_command_string)
    
    def writeGoto(self, label):
        _command_string = \
f'''
// goto {label}
@{label}
0;JMP
'''
        self.outf.write(_command_string)
    
    def writeIf (self, label):
        _command_string = \
f'''
// if-goto {label}
@SP
M=M-1
A=M
D=M
@{label}
D;JNE
'''
        self.outf.write(_command_string)
    
    def writeFunction (self, funcName, nVars):
        push_0 = \
"""
@SP
A=M
M=0
@SP
M=M+1       // push 0
""" * nVars

        _command_string = \
f'''
// function {funcName} {nVars}
({funcName})
{push_0}
'''

        self.outf.write(_command_string)
    
    def writeCall (self, funcName, nArgs, lineNumber):
        # save return address
        # save callers segment pointers
        # reposition ARG + LCL for callee
        # goto callees code
        
        _command_string = \
f'''
// call {funcName} {nArgs}

// push return-address
@{funcName}$ret.{lineNumber}
D=A
@SP
A=M
M=D
@SP
M=M+1       // SP ++
// push LCL
@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1       // SP ++
// push ARG
@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1       // SP ++
// push THIS
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1       // SP ++
// push THAT
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1       // SP ++
// reposition ARG (SP-5-nArgs)
@SP
D=M
@{nArgs}
D=D-A
@5
D=D-A
@ARG
M=D
// reposition LCL (LCL = SP)
@SP
D=M
@LCL
M=D
// goto {funcName}
@{funcName}
0;JMP
// return-address label
({funcName}$ret.{lineNumber})
'''
        self.outf.write(_command_string)
    
    def writeReturn (self):
        # replace args pushed by caller w/ val returned by callee
        # recycle memory used by callee
        # reinstate callers segment pointers
        # jump to return address
        
        _command_string = \
f'''
// return
@LCL
D=M
@endFrame
M=D         // get addr at frames end
@5
D=D-A
A=D
D=M
@retAddr
M=D         // get return address
@SP
M=M-1
A=M
D=M
@ARG
A=M
M=D         // puts return val for caller
@ARG
D=M+1
@SP
M=D         // reposition SP
@endFrame
D=M-1
A=D
D=M
@THAT
M=D         // restore THAT
@2
D=A
@endFrame
D=M-D
A=D
D=M
@THIS
M=D         // restore THIS
@3
D=A
@endFrame
D=M-D
A=D
D=M
@ARG
M=D         // restores ARG
@4
D=A
@endFrame
D=M-D
A=D
D=M
@LCL
M=D         // restores LCL
@retAddr
A=M
0;JMP       // jump to return address
'''
        self.outf.write(_command_string)
    
    def _bootstrapCode(self):
        _command_string = \
f'''
// bootstrap code
@256
D=A
@SP
M=D
'''
        return _command_string
    
    def close(self):
        self.outf.close()
