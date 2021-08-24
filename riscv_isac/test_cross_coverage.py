class temp():
    def __init__(self,instr_name, rd, rs1, rs2):
        self.instr_name = instr_name
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2

class cross():

    def __init__(self,label,coverpoint):

        self.label = label
        self.coverpoint = coverpoint
        self.result = 0

        ## Extract relevant information from coverpt
        self.data = self.coverpoint.split('::')
        self.ops = [i for i in self.data[0][1:-1].split(':')]
        self.assign_lst = [i for i in self.data[1][1:-1].split(':')]
        self.cond_lst = [i for i in self.data[2][1:-1].split(':')]
    
    def process(self, queue, window_size):

        '''
        Check whether the coverpoint is a hit or not and update the metric
        '''
        if(len(self.ops)>window_size or len(self.ops)>len(queue)):
            return

        for index in range(len(self.ops)):
            instr = queue[index]
            instr_name = instr.instr_name
            rd = int(instr.rd)
            rs1 = int(instr.rs1)
            rs2 = int(instr.rs2)
            if(self.ops[index] != '?'):
                check_lst = [i for i in self.ops[index][1:-1].split(', ')]
                if (instr_name not in check_lst):
                    break
            if(self.assign_lst[index] != '?'):
                exec(self.assign_lst[index])
            if (self.cond_lst[index] != '?'):
                if(eval(self.cond_lst[index])):
                    if(index==len(self.ops)-1):
                        self.result = self.result + 1
                else:
                    break
    
    def get_metric(self):
        return self.result

def cross_coverage(obj_dict, window_size, end=0):
    '''
    Computes cross coverage for the current queue of instructions

    Arguments:
    cross_cgf: CGF containing coverpoint nodes with their frequency of hits
    window_size: maximum window length of instructions to check
    end : end = 1 implies we have to evaluate the ending corner case

    Type:
    cross_cgf: dictionary
    window_size: int
    end: int

    '''
    global cross_cover_queue
    ## RAW, WAW, WAR
    if(end):
        while(len(cross_cover_queue)>1):
            instr_name = cross_cover_queue[0].instr_name
            for label,coverpt in obj_dict.keys():
                if(label==instr_name):
                    ## evaluate that coverpt
                    obj_dict[(label,coverpt)].process(cross_cover_queue, window_size)
            cross_cover_queue.pop(0) 
    else:  
        instr_name = cross_cover_queue[0].instr_name
        for label,coverpt in obj_dict.keys():
            if(label==instr_name):
                ## evaluate that coverpt
                obj_dict[(label,coverpt)].process(cross_cover_queue, window_size)
        cross_cover_queue.pop(0) 


def compute(cgf,window_size):

    obj_dict = {} ## (label,coverpoint): object
    for cov_labels,value in cgf.items():
        if cov_labels != 'datasets':
            if 'opcode' in value and 'cross_comb' in value and len(value['cross_comb'])!=0:
                for coverpt in value['cross_comb'].keys():
                    if(isinstance(coverpt,str)):
                        new_obj = cross(cov_labels,coverpt)
                        obj_dict[(cov_labels,coverpt)] = new_obj
    ## raw, waw, war
    global cross_cover_queue
    cross_cover_queue = []
    i1 = temp("addi",1,2,3)
    i2 = temp("slti",2,3,1) ## war(1), raw(1)
    i3 = temp("andi",1,2,3) ## waw (1)-consume, raw(2), war(2)
    i4 = temp("sub",7,8,9)  ## nothing
    i5 = temp("addi",10,11,13)
    i6 = temp("andi",11,13,10) ## war(1), raw(1)

    lst = [i1,i2,i3,i4,i5,i6]

    for instrObj_temp in lst:
        cross_cover_queue.append(instrObj_temp)
        if(len(cross_cover_queue)>=window_size):
            cross_coverage(obj_dict, window_size,0)
    ## end pts
    cross_coverage(obj_dict, window_size,1)

    for label,coverpt in obj_dict.keys():
        metric = obj_dict[(label,coverpt)].get_metric()
        if(metric!=0):
            cgf[label]['cross_comb'][coverpt] = metric

cgf = {
  "slti": {
    "config": [
      "check ISA:=regex(.*E.*) ;def RVTEST_E = True"
    ], 
    "opcode": {
      "slti": 0
    },
    "cross_comb": {
        '[(addi, andi, sub, add, slti):(addi, andi, sub, add, slti)]::[a=rd:?]::[?:rs1==a or rs2==a]':0,
        '[(addi, andi, sub, add, slti):(addi, andi, sub, add, slti)]::[a=rs1 ; b=rs2:?]::[?:rd==a or rd==b]':0
    }
  }, 
  "add": {
    "config": [
      "check ISA:=regex(.*E.*) ;def RVTEST_E = True"
    ], 
    "opcode": {
      "add": 0
    },
    "cross_comb": {
        '[(addi, andi, sub, add, slti):(addi, andi, sub, add, slti)]::[a=rs1 ; b=rs2:?]::[?:rd==a or rd==b]':0
    }
  }, 
  "andi": {
    "config": [
      "check ISA:=regex(.*E.*) ;def RVTEST_E = True"
    ], 
    "opcode": {
      "andi": 0
    },
    "cross_comb": {
        '[(addi, andi, sub, add, slti):(addi, andi, sub, add, slti)]::[a=rs1 ; b=rs2:?]::[?:rd==a or rd==b]':0
    }
  }, 
  "sub": {
    "config": [
      "check ISA:=regex(.*E.*) ;def RVTEST_E = True"
    ], 
    "opcode": {
      "sub": 0
    },
    "cross_comb": {
        '[(addi, andi, sub, add, slti):(addi, andi, sub, add, slti)]::[a=rs1 ; b=rs2:?]::[?:rd==a or rd==b]':0
    }
  }, 
  "addi": {
    "config": [
      "check ISA:=regex(.*E.*) ;def RVTEST_E = True"
    ], 
    "opcode": {
      "addi": 0
    },
    "cross_comb": {
        '[(addi, andi, sub, add, slti):?:(addi, andi, sub, add, slti)]::[a=rs1 ; b=rs2:?:?]::[?:?:rd==a or rd==b]':0,
        '[(addi, andi, sub, add, slti):(addi, andi, sub, add, slti)]::[a=rs1 ; b=rs2:?]::[?:rd==a or rd==b]':0,
        '[(addi, andi, sub, add, slti):(addi, andi, sub, add, slti)]::[a=rd:?]::[?:rs1==a or rs2==a]':0,
        '[(addi, andi, sub, add, slti):?:(addi, andi, sub, add, slti)]::[a=rd:?:?]::[?:rs1==a or rs2==a:rd==a]':0

    }
  }
}
compute(cgf,3)
print(cgf)
