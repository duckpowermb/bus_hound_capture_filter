# -*- coding: utf-8 -*-
import re
import sys
import io

verbose = 0
def v_p(x):
	global verbose
	if verbose:
		print('[Dbg]%s'%x)

Headersep = '\r\n\r\n'

class CONV_STATUS:
	HEAD = 0
	BODY = 1
	CONTENT_START = 2
	CONTENT_CONTINUE = 3

class Parse_Result:
	def __init__(self):
		self.device = None
		self.parse = None
		self.data = None

		self.new_line = None

class Parse_Rule:
	def __init__(self,name,before_run,verf_reg,handler):
		self.name = name
		self.before_run = before_run
		self.verf_reg = verf_reg
		self.handler = handler
	def execute(self,line_content):
		global v_p
		v_p('[Rule %s]:'%self.name)
		v_p('Handling:%s'%line_content)
		if self.before_run is not None:
			line_content = self.before_run(line_content)
			v_p('After-BeforeRun:%s'%line_content)
		matchObj = re.match(self.verf_reg,line_content)
		if matchObj:
			match_str = matchObj.group()
			v_p('matched:%s'%match_str)
			if self.handler is not None:
				retobj = self.handler(match_str)
				if retobj is not None:
					v_p('result:')
					v_p('device:%s'%retobj.device)
					v_p('parse:%s'%retobj.parse)
					v_p('data:%s'%retobj.data)
				return retobj
		else:
			v_p('No match')
		return None

def make_space_standard(line_content):
	line = line_content.strip()
	out = ''
	spc_cnt = 0
	for i in range(len(line)):
		if line[i] == ' ':
			spc_cnt +=1
		else:
			spc_cnt = 0
		if spc_cnt < 2:
			out += line[i]
	return out

def start_content_handler(content):
    str_arr = content.split(' ')
    if len(str_arr) > 2:
        ret = Parse_Result()
        ret.device = str_arr[0]
        ret.parse = str_arr[1]
        ret.data = ' '.join(str_arr[2:])
        return ret
	return None

def continue_content_handler(content):
    str_arr = content.split(' ')
    if len(str_arr) > 1:
        ret = Parse_Result()
        ret.data = ' '.join(str_arr)
        return ret #Parse_Result
	return None

bus_hound_line_parsers = [
	Parse_Rule(
		name = 'Line_start',
		before_run = make_space_standard,
		verf_reg = '^[0-9]{1,4} [A-Z]{2,3} ([0-9a-z]{2} )+',
		handler = start_content_handler
	),
	Parse_Rule(
		name = 'Line_continue',
		before_run = make_space_standard,
		verf_reg = '^([0-9a-z]{2} )+',
		handler = continue_content_handler
	),
]

def line_parse(line):
    if line == '\r\n':
        ret = Parse_Result()
        ret.new_line = True
        return ret

    for rule in bus_hound_line_parsers:
        ret = rule.execute(line)
        if ret:
            return ret

    return  None

def main():
    global verbose
    input_file = None
    #sys.argv.append('-v')
    #sys.argv.append('rx.txt')

    if len(sys.argv) > 3 or len(sys.argv) < 2:
        print('take 1 or 2 arguments')
        return
    
    if len(sys.argv) == 2:
        if sys.argv[1] == '-v':
            verbose = 1
            #err-status
        else:
            input_file = sys.argv[1]
        
    if len(sys.argv) == 3:
        if sys.argv[1] == '-v':
            verbose = 1
            input_file = sys.argv[2]
        if sys.argv[2] == '-v':
            verbose = 1
            input_file = sys.argv[1]

    v_p('Handling File %s'%input_file)
    
    if input_file is None:
        print('No input file')

    old_status = CONV_STATUS.HEAD
    status = CONV_STATUS.HEAD
    new_line_num = 0
    data_cat = ''

    file_opened = False

    with open(input_file, 'r') as f:
        file_opened = True
        for line in f.readlines():
            result = line_parse(line)
            if result is None:
                if status > CONV_STATUS.HEAD:
                    status = CONV_STATUS.BODY
            else:
                if result.new_line:
                    new_line_num += 1
                    if new_line_num == 2 and status == CONV_STATUS.HEAD:
                        status = CONV_STATUS.BODY
                elif result.device is not None:
                    status = CONV_STATUS.CONTENT_START
                elif result.data is not None:
                    status = CONV_STATUS.CONTENT_CONTINUE

            if status == CONV_STATUS.HEAD:
                pass
            if status == CONV_STATUS.BODY:
                pass
            if status == CONV_STATUS.CONTENT_START:
                if len(data_cat) > 1:
                    print("DATA:%s"%data_cat)
                data_cat = ''
                data_cat += result.data + ''
                print("\nBLOCK:device:%s:parse:%s"%(result.device,result.parse))
            if status == CONV_STATUS.CONTENT_CONTINUE:
                data_cat += result.data + ''
            
            if old_status != status:
                old_status = status
                v_p('Status:%s'%status)


        if len(data_cat) > 1:
            print("DATA:%s"%data_cat)
    
    if not file_opened:
        print('Open %s failed'%input_file)

if __name__ == "__main__":
    main()
