#!/usr/bin/env python3


import re

class Parser:
    C_ARITHMETIC = 0
    C_PUSH = 1
    C_POP = 2
    C_LABEL = 3
    C_GOTO = 4
    C_IF = 5
    C_FUNCTION = 6
    C_RETURN = 7
    C_CALL = 8
    
    def __init__(self, filename) -> None:
        file = open(filename, 'r')
        self._lines = file.read()
        self._commands = self._commands_list(self._lines.split('\n'))
        self.current_command = ''
        self._init_command_info()
        self.lineNumber = 0
    
    def _init_command_info(self):
        self._cmd_type = -1
        self._segment = ''
        self._arg1 = ''
        self._arg2 = -1
    
    def __str__(self) -> str:
        pass
    
    def hasMoreLines(self):
        return self._commands != []
    
    def advance(self):
        self.lineNumber += 1
        self._init_command_info()
        self.current_command = self._commands.pop(0)
        
        self._cmd_type = self.getCommandType(self.current_command)
        
        if (self._cmd_type != Parser.C_RETURN):
            self._arg1 = self.getArg1(self.current_command)
        if (self._cmd_type is Parser.C_PUSH or \
            self._cmd_type is Parser.C_POP or \
            self._cmd_type is Parser.C_FUNCTION or \
            self._cmd_type is Parser.C_CALL):
            self._arg2 = self.getArg2(self.current_command)
    
    def _commands_list(self, lines):
        return [c for c in [self._single_command(l) for l in lines] if c != '']
    
    def _single_command(self, line):
        return self._remove_comments(line)
    
    _comment = re.compile('//.*$')
    def _remove_comments(self, line):
        return self._comment.sub('', line).strip()
    
    _pop_re = re.compile('^pop\s*')
    _push_re = re.compile('^push\s*')
    _add = '^add$'
    _sub = '^sub$'
    _neg = '^neg$'
    _eq = '^eq$'
    _gt = '^gt$'
    _lt = '^lt$'
    _and = '^and$'
    _or = '^or$'
    _not = '^not$'
    _arithmetic_re = re.compile(_add +'|'+ _sub +'|'+ _neg +'|'+ _eq +'|'+ _lt +'|'+ _gt +'|'+ _and +'|'+ _or +'|'+ _not)
    _label_re = re.compile('^label(?= )')
    _goto_re = re.compile('goto(?= )')
    _if_re = re.compile('if-goto(?= )')
    _func_re = re.compile('function(?= )')
    _call_re = re.compile('call(?= )')
    _return_re = re.compile('return$')
    def getCommandType(self, command):
        
        if (self._pop_re.match(command)):
            return Parser.C_POP
        elif (self._push_re.match(command)):
            return Parser.C_PUSH
        elif (self._arithmetic_re.match(command)):
            return Parser.C_ARITHMETIC
        elif (self._label_re.match(command)):
            return Parser.C_LABEL
        elif (self._goto_re.match(command)):
            return Parser.C_GOTO
        elif (self._if_re.match(command)):
            return Parser.C_IF
        elif (self._func_re.match(command)):
            return Parser.C_FUNCTION
        elif (self._call_re.match(command)):
            return Parser.C_CALL
        elif (self._return_re.match(command)):
            return Parser.C_RETURN

    _arg1_re = re.compile('(?<= ).*(?= )')
    _labelname_re = re.compile('(?<=label ).+$')
    _gotoname_re = re.compile('(?<=goto ).+$')
    _ifname_re = re.compile('(?<=if-goto ).+$')
    def getArg1(self, command):
        if (self._cmd_type is Parser.C_ARITHMETIC):
            return command
        elif (self._cmd_type is Parser.C_LABEL):
            temp = self._labelname_re.search(command)
            return temp.group()
        elif (self._cmd_type is Parser.C_GOTO):
            temp = self._gotoname_re.search(command)
            return temp.group()
        elif (self._cmd_type is Parser.C_IF):
            temp = self._ifname_re.search(command)
            return temp.group()
        else:
            temp = self._arg1_re.search(command)
            return temp.group()
    
    _arg2_re = re.compile('(?<= )\d*$')
    def getArg2(self, command):
        temp = self._arg2_re.search(command)
        return int(temp.group())

    def commandType(self):
        return self._cmd_type
    
    def arg1(self):
        return self._arg1
    
    def arg2(self):
        return self._arg2
