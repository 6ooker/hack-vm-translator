#!/bin/python3

import vmparser as Parser
import vmcodewriter as CodeWriter
import sys
import os


class Translator:
    def __init__(self) -> None:
        pass
    
    def writeBootstrap(self, outfile):
        CW = CodeWriter.CodeWriter(outfile)
        CW.writeBootstrapCode()
        CW.close()
    
    def translate(self, infile, outFile):
        parser = Parser.Parser(infile)
        CW = CodeWriter.CodeWriter(outFile)
        CW.setFileName(infile)
        while (parser.hasMoreLines()):
            parser.advance()
            cmdt = parser.commandType()
            
            if not cmdt == parser.C_RETURN: arg1 = parser.arg1()
            
            if (cmdt == parser.C_ARITHMETIC):
                CW.writeArithmetic(arg1, parser.lineNumber)
            elif (cmdt == parser.C_PUSH or cmdt == parser.C_POP):
                arg2 = parser.arg2()
                CW.writePushPop(cmdt, arg1, arg2)
            elif (cmdt == parser.C_LABEL):
                CW.writeLabel(arg1)
            elif (cmdt == parser.C_GOTO):
                CW.writeGoto(arg1)
            elif (cmdt == parser.C_IF):
                CW.writeIf(arg1)
            elif (cmdt == parser.C_FUNCTION):
                arg2 = parser.arg2()
                CW.writeFunction(arg1, arg2)
            elif (cmdt == parser.C_CALL):
                arg2 = parser.arg2()
                CW.writeCall(arg1, arg2, parser.lineNumber)
            elif (cmdt == parser.C_RETURN):
                CW.writeReturn()
        CW.close()


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 vmmain.py 'file.vm' or dir")
    else:
        file_or_dir = sys.argv[1]
    
    # Determine correct output file name
    outFile = os.path.basename(file_or_dir)
    if (outFile.endswith('.vm')):
        outFile = outFile.replace('.vm', '.asm')
    else:
        outFile = outFile + '.asm'
    
    
    trans = Translator()
    
    if (os.path.isfile(file_or_dir)):
        if (not os.path.basename(file_or_dir).endswith('.vm')):
            raise Exception("Must provide single or dir containing .vm-files")

        trans.writeBootstrap(outFile)
        trans.translate(file_or_dir, outFile)
    
    elif (os.path.isdir(file_or_dir)):
        outFileInDir = os.path.join(file_or_dir, outFile)
        if (os.path.exists(outFileInDir)):
            os.remove(outFileInDir)
        trans.writeBootstrap(outFileInDir)

        for vmFile in [f for f in os.listdir(file_or_dir) if f.endswith('.vm') and not f.startswith('.')]:
            inFileInDir = os.path.join(file_or_dir, vmFile)
            trans.translate(inFileInDir, outFileInDir)
    
    
main()