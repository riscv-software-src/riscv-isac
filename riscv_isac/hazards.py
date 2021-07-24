## Coverpoint - [instr, ? : ? ..... instr]::[a=rd : ?consuming/not: ]::[RAW/WAW/WAR]

'''
Combinations list

Tester list - opcode list against which we check for other instructions (corresponding to queue[0])
Test list - opcode list for which we check for potential hazards (corresponding to next n instructions)

1. In-between instructions (non-consuming)
- Test list - have both rs1 and rs2 fields {arith_instr, branch_instr, rv64_arith}
- Test list - have only rs1 field (the other is immediate) {field_1, arithi_instr, rv64_arithi}
- Test list - Instructions have no rd fields (no WAW) {store_instr}

'''
# Have both rs1, rs2
arith_instr = ('mul','mulh','mulhsu','mulhu','div','divu','rem','remu','add','sub','sll','slt','sltu','xor','srl','sra','or','and')
branch_instr = ('beq','bne','blt','bge','bltu','bgeu')
rv64_arith = ('mulw','divw','divuw','remw','remuw','addw','subw','sllw','srlw','sraw')

# Have only rs1
field_1 = ('jalr','lb','lh','lw','ld','lbu','lhu','lwu')
arithi_instr = ('addi', 'slti', 'sltiu', 'xori', 'ori', 'andi', 'slli', 'srai', 'srli')
rv64_arithi = ('addiw','ssliw','srliw','sraiw')

# No rs1, rs2 - only rd
misc_instr = ('lui', 'auipc', 'jal')

# No rd - both rs1, rs2
store_instr = ('sb', 'sh', 'sw', 'sd')

## Combined string
instr_str = ", ".join(arith_instr + branch_instr + rv64_arith + field_1 + arithi_instr + rv64_arithi + misc_instr + store_instr)

def raw (window_len, instr1, gap, instr2):
    '''
    Args:
    window_len: size of window for evaluation (int)
    gap: number of instructions in between    (int)
    instr1: tuple of intrcutions against which others are checked
    instr2: tuple of intructions that are checked against a given instruction

    Return coverpoints like [(lui, auipc, jal):?:?:(sb, sh, sw, sd):?]::[a=rd:?:?:?:?]::[?:?:?:rs1==a or rs2==a:?]
    '''

    instr_str1 = ", ".join(instr1)
    instr_str2 = ", ".join(instr2)

    opcode_list = "[(" + instr_str1 + ")"
    for i in range(gap):
        opcode_list += ":?"
    opcode_list += ":("+ instr_str2 + ")" 
    for i in range (window_len - gap - 2):
        opcode_list += ":?"
    opcode_list += "]"

    assign_list = ""
    assign_list += '[a=rd'
    for i in range (window_len - 1):
        assign_list += ":?"
    assign_list += "]"

    cond_list_rs = ""
    cond_list_rs += "[?"
    for i in range (gap):
        cond_list_rs += ":?"
    cond_list_rs += ":rs1==a or rs2==a"
    for i in range (window_len - gap - 2):
        cond_list_rs += ":?"
    cond_list_rs += "]"
    
    raw_str = opcode_list + "::" + assign_list + "::" + cond_list_rs
    return raw_str

def waw ( window_len, instr1, gap, instr2 ):
    '''
    Args:
    window_len: size of window for evaluation (int)
    gap: number of instructions in between    (int)
    instr1: tuple of intrcutions against which others are checked
    instr2: tuple of intructions that are checked against a given instruction

    Return coverpoints like [(mul, mulh, mulhsu, mulhu, ):?:?:?:(sb, sh, sw, sd)]::[a=rd:?:?:?:?]::[?:?:?:?:rd==a]

    ''' 
    instr_str1 = ", ".join(instr1)
    instr_str2 = ", ".join(instr2)
    opcode_list = "[(" + instr_str1 + ")"
    for i in range(gap):
        opcode_list += ":?"
    opcode_list += ":("+ instr_str2 + ")" 
    for i in range (window_len - gap - 2):
        opcode_list += ":?"
    opcode_list += "]"
    
    assign_list = ""
    assign_list += '[a=rd'
    for i in range (window_len - 1):
        assign_list += ":?"
    assign_list += "]"
    
    cond_list_rd = ""
    cond_list_rd += "[?"
    for i in range (gap):
        cond_list_rd += ":?"
    cond_list_rd += ":rd==a"
    for i in range (window_len - gap - 2):
        cond_list_rd += ":?"
    cond_list_rd += "]"

    waw_str = opcode_list + "::" + assign_list + "::" + cond_list_rd

    return waw_str

def war ( window_len, instr1, gap, instr2 ):
    '''
    Args:
    window_len: size of window for evaluation (int)
    gap: number of instructions in between    (int)
    instr1: tuple of intrcutions against which others are checked
    instr2: tuple of intructions that are checked against a given instruction

    Return coverpoints like [(mul, mulh, mulhsu, mulhu, ):?:?:?:(sb, sh, sw, sd)]::[a=rs1:?:?:?:?]::[?:?:?:?:rd==a or rd==b]

    ''' 
    instr_str1 = ", ".join(instr1)
    instr_str2 = ", ".join(instr2)
    opcode_list = "[(" + instr_str1 + ")"
    for i in range(gap):
        opcode_list += ":?"
    opcode_list += ":("+ instr_str2 + ")" 
    for i in range (window_len - gap - 2):
        opcode_list += ":?"
    opcode_list += "]"
    
    assign_list = ""
    assign_list += '[rs1=a'
    for i in range (window_len - 1):
        assign_list += ":?"
    assign_list += "]"
    
    cond_list_rd = ""
    cond_list_rd += "[?"
    for i in range (gap):
        cond_list_rd += ":?"
    cond_list_rd += ":rd==a or rd==b"
    for i in range (window_len - gap - 2):
        cond_list_rd += ":?"
    cond_list_rd += "]"

    war_str = opcode_list + "::" + assign_list + "::" + cond_list_rd

    return war_str

def consume_waw ( window_len, instr1, gap, instr2):
    '''
    Args:
    window_len: size of window for evaluation (int)
    gap: number of instructions in between    (int)
    instr1: tuple of intrcutions against which others are checked
    instr2: tuple of intructions that are checked against a given instruction

    Return coverpoints like: [(mul, mulh, mulhsu, mulhu, ):?:?:?:(sb, sh, sw, sd)]::[a=rd:?:?:?:?]::[?:rs1==a || rs2==a:rs1==a || rs2==a:rs1==a || rs2==a:rd==a]

    ''' 
    instr_str1 = ", ".join(instr1)
    instr_str2 = ", ".join(instr2)
    opcode_list = "[(" + instr_str1 + ")"
    for i in range(gap):
        opcode_list += ":?"
    opcode_list += ":("+ instr_str2 + ")" 
    for i in range (window_len - gap - 2):
        opcode_list += ":?"
    opcode_list += "]"
    
    assign_list = ""
    assign_list += '[a=rd'
    for i in range (window_len - 1):
        assign_list += ":?"
    assign_list += "]"
    
    cond_list_rd = "[?"
    for i in range (gap):
        cond_list_rd += ":rs1==a or rs2==a"
    cond_list_rd += ":rd==a"
    for i in range (window_len - gap - 2):
        cond_list_rd += ":?"
    cond_list_rd += "]"
    
    waw = opcode_list + "::" + assign_list + "::" + cond_list_rd

    return waw

print(raw(5,misc_instr,2,store_instr))






