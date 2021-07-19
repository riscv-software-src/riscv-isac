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

## Combines string
instr_str = ", ".join(arith_instr + branch_instr + rv64_arith + field_1 + arithi_instr + rv64_arithi + misc_instr + store_instr)

def non_consume( window_len, gap):
    '''
    Args:
    window_len: size of window for evaluation (int)
    gap: number of instructions in between    (int)

    Return coverpoints like [(mul, mulh, mulhsu, mulhu, ):?:?:?:(sb, sh, sw, sd)]::[a=rd:?:?:?:?]::[?:?:?:?:rd==a]

    ''' 
    opcode_list = "[(" + instr_str + ")"
    for i in range(gap):
        opcode_list += ":?"

    opcode_list += ":("+ instr_str + ")" 

    for i in range (window_len - gap - 2):
        opcode_list += ":?"

    opcode_list += "]"
    
    assign_list = ""
    # if hazard in ['RAW', 'WAW']:
    assign_list += '[a=rd'
    for i in range (window_len - 1):
        assign_list += ":?"
    assign_list += "]"
    
    cond_list_rs = ""
    cond_list_rs += "[?"
    for i in range (gap):
        cond_list_rs += ":?"

    cond_list_rd = cond_list_rs
    # if (hazard=='RAW'):
    cond_list_rs += ":rs1==a or rs2==a"
    # if (hazard=='WAW'):
    cond_list_rd += ":rd==a"
    for i in range (window_len - gap - 2):
        cond_list_rs += ":?"
        cond_list_rd += ":?"

    cond_list_rs += "]"
    cond_list_rd += "]"
    
    
    raw = opcode_list + "::" + assign_list + "::" + cond_list_rs
    waw = opcode_list + "::" + assign_list + "::" + cond_list_rd

    return raw, waw

def consume ( window_len, gap):
    '''
    Args:
    window_len: size of window for evaluation (int)
    gap: number of instructions in between    (int)

    Return coverpoints like: [(mul, mulh, mulhsu, mulhu, ):?:?:?:(sb, sh, sw, sd)]::[a=rd:?:?:?:?]::[?:rs1==a || rs2==a:rs1==a || rs2==a:rs1==a || rs2==a:rd==a]

    ''' 
    opcode_list = "[(" + instr_str + ")"
    for i in range(gap):
        opcode_list += ":?"

    opcode_list += ":("+ instr_str + ")" 

    for i in range (window_len - gap - 2):
        opcode_list += ":?"

    opcode_list += "]"
    
    assign_list = ""
    # if hazard in ['RAW', 'WAW']:
    assign_list += '[a=rd'
    for i in range (window_len - 1):
        assign_list += ":?"
    assign_list += "]"
    
    
    cond_list_rs = "[?"
    cond_list_rd = "[?"
    for i in range (gap):
        cond_list_rs += ":rd==a"
        cond_list_rd += ":rs1==a or rs2==a"
    
    # if (hazard=='RAW'):
    cond_list_rs += ":rs1==a or rs2==a"
    # if (hazard=='WAW'):
    cond_list_rd += ":rd==a"
    for i in range (window_len - gap - 2):
        cond_list_rs += ":?"
        cond_list_rd += ":?"

    cond_list_rs += "]"
    cond_list_rd += "]"
    
    raw = opcode_list + "::" + assign_list + "::" + cond_list_rs
    waw = opcode_list + "::" + assign_list + "::" + cond_list_rd

    return waw

print(non_consume(5,3)[0])  




