# _*_ coding:utf-8 _*_


import os
import time

import ida_bytes
import ida_frame
import ida_funcs
import ida_idp
import ida_nalt
import ida_segment
import ida_struct
import ida_ua
import idautils


ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

log_file = open(os.path.join(ROOT_PATH, "./output.log"), "w")

binary_info = idaapi.get_inf_structure()
if binary_info.is_64bit():
    BITS = 64
elif binary_info.is_32bit():
    BITS = 32
else:
    BITS = 16
ENDIAN = "big" if binary_info.is_be() else "little"
ARCH = binary_info.procname

text_seg = ida_segment.get_segm_by_name(".text")
if not text_seg:
    log_file.write("<%s>: text_seg is not exists!!!!\n" %
                   get_input_file_path())
#     text_seg = ida_segment.get_segm_by_name("LOAD")

if ARCH == "ARM" and ENDIAN == "little" and BITS == 32:
    # Identify up to four parameters
    ARGU_REGS = ['R0', 'R1', 'R2', 'R3', 'ENDs']
    JMP_INSTRUCTION = ['B', 'BLT', 'BLE', 'BEQ', 'BVC', 'BVS', 'BLS', 'BX',
                       'BLO', 'BCS', 'BCC', 'BMI', 'BPL', 'BGT', 'BGE', 'BNE', 'BHI', 'BHS']
    RETURN_REG = 0   # R0
elif ARCH == "metapc" and ENDIAN == "little" and BITS == 32:
    RETURN_REG = 0   # eax
elif ARCH == "metapc" and ENDIAN == "little" and BITS == 64:
    ARGU_REGS = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9', 'ENDs']
    RETURN_REG = 0   # rax
elif ARCH == "mipsl" and ENDIAN == "little" and BITS == 32:
    ARGU_REGS = ['$a0', '$a1', '$a2', '$a3', 'ENDs']
    RETURN_REG = 2   # v0

def get_reg_name(reg_value):
    return ida_idp.get_reg_name(reg_value, BITS//8)

def get_reg_value(reg_name):
    r = ida_idp.reg_info_t()
    if ida_idp.parse_reg_name(r, reg_name):
        return r.reg
    else:
        return None

def get_all_importfunc():
    nimps = ida_nalt.get_import_module_qty()
    result = []
    for i in range(nimps):
        name = ida_nalt.get_import_module_name(i)
        if not name:
            # print("Failed to get import module name for #%d" % i)
            # name = "<unnamed>"
            pass

        # print("Walking imports for module %s" % name)
        def imp_cb(ea, name, ordinal):
            if name:
                # print("%08x: %s (ordinal #%d)" % (ea, name, ordinal))
                result.append(name)
            # True -> Continue enumeration
            # False -> Stop enumeration
            return True
        ida_nalt.enum_import_names(i, imp_cb)
    return result

import_funcs = get_all_importfunc()


# Get the name corresponding to the stack variable
def get_stkvar_name(inst_t, op_n):
    operand = inst_t.ops[op_n]
    if operand.addr > 2**31:
        addr = -(2**32-operand.addr)
    else:
        addr = operand.addr

    var = ida_frame.get_stkvar(inst_t, operand, addr)
    if not var:
        log_file.write("<get_stkvar_name><get_stkvar> error: " + hex(inst_t.ea) + "\n")
        return None
    var = var[0]
    var_name = ida_struct.get_member_name(var.id)
    if var_name:
        return var_name
    else:
        # log_file.write("<get_stkvar_name><get_member_name> error: " + hex(inst_t.ea) + "\n")
        # return "STKVAR"
        return None


def extract_operand(inst_t, op_n, x_set):
    # There are three types of data storage locations: registers, stack variables, and memory variables
    full_flags = ida_bytes.get_full_flags(inst_t.ea)
    if ida_bytes.is_stkvar(full_flags, op_n):
        varname = get_stkvar_name(inst_t, op_n)
        if varname:
            x_set.add(varname)
            return

    operand = inst_t.ops[op_n]
    if operand.type == ida_ua.o_void:
        # o_void: No Operand.
        return
    if operand.type == ida_ua.o_mem:
        x_set.add(operand.addr)
        return
    if operand.type == ida_ua.o_reg:
        x_set.add(operand.reg)
        return
    if operand.type == ida_ua.o_phrase:
        x_set.add((operand.reg, operand.phrase))
        return
    if operand.type == ida_ua.o_displ:
        x_set.add((operand.reg, operand.phrase, operand.addr))
    return


def extract_func_rw_info(func_addr, r_set, w_set):
    # extract function read/write info
    # store read/write info into r_set/w_set
    if func_addr in all_func_argu_num.keys():
        argu_num = all_func_argu_num[func_addr]
        if argu_num > 0:
            argu_num = argu_num if argu_num <= 4 else 4

            for i in range(argu_num):
                r_set.add(get_reg_value(ARGU_REGS[i]))
        

def extract_inst_rw_set(inst_addr):
    inst = idautils.DecodeInstruction(inst_addr)
    inst_r_set = set()
    inst_w_set = set()
    inst_feature = inst.get_canon_feature()
    if inst_feature & ida_idp.CF_CALL:
        # Check whether this CALL instruction rewrites the RETURN_REG
        if is_return(inst_addr):
            inst_w_set.add(RETURN_REG)
        dest_func_addr = called_func_addr(inst_addr)
        if dest_func_addr:
            extract_func_rw_info(dest_func_addr, inst_r_set, inst_w_set)

    if inst_feature & ida_idp.CF_CHG1:
        if inst.ops[0].type == ida_ua.o_phrase or inst.ops[0].type == ida_ua.o_displ:
            # the STR instruction need special processing. memory address representation needs to use registers.
            # But if the memory address is a stack variable, you don't need to add it to the r_set
            if not ida_bytes.is_stkvar(ida_bytes.get_full_flags(inst_addr), 0):
                inst_r_set.add(inst.ops[0].reg)
                inst_r_set.add(inst.ops[0].phrase)
        extract_operand(inst, 0, inst_w_set)
    if inst_feature & ida_idp.CF_CHG2:
        if inst.ops[1].type == ida_ua.o_phrase or inst.ops[1].type == ida_ua.o_displ:
            if not ida_bytes.is_stkvar(ida_bytes.get_full_flags(inst_addr), 1):
                inst_r_set.add(inst.ops[1].reg)
                inst_r_set.add(inst.ops[1].phrase)
        extract_operand(inst, 1, inst_w_set)
    if inst_feature & ida_idp.CF_CHG3:
        if inst.ops[2].type == ida_ua.o_phrase or inst.ops[2].type == ida_ua.o_displ:
            if not ida_bytes.is_stkvar(ida_bytes.get_full_flags(inst_addr), 2):
                inst_r_set.add(inst.ops[2].reg)
                inst_r_set.add(inst.ops[2].phrase)
        extract_operand(inst, 2, inst_w_set)
    # Suppose the instruction has at most three operands

    if inst_feature & ida_idp.CF_USE1:
        if inst.ops[0].type == ida_ua.o_phrase or inst.ops[0].type == ida_ua.o_displ:
            # the processing of LDR is linke STR
            if not ida_bytes.is_stkvar(ida_bytes.get_full_flags(inst_addr), 0):
                inst_r_set.add(inst.ops[0].reg)
                inst_r_set.add(inst.ops[0].phrase)
        extract_operand(inst, 0, inst_r_set)
    if inst_feature & ida_idp.CF_USE2:
        if inst.ops[1].type == ida_ua.o_phrase or inst.ops[1].type == ida_ua.o_displ:
            if not ida_bytes.is_stkvar(ida_bytes.get_full_flags(inst_addr), 1):
                inst_r_set.add(inst.ops[1].reg)
                inst_r_set.add(inst.ops[1].phrase)
        extract_operand(inst, 1, inst_r_set)
    if inst_feature & ida_idp.CF_USE3:
        if inst.ops[2].type == ida_ua.o_phrase or inst.ops[2].type == ida_ua.o_displ:
            if not ida_bytes.is_stkvar(ida_bytes.get_full_flags(inst_addr), 2):
                inst_r_set.add(inst.ops[2].reg)
                inst_r_set.add(inst.ops[2].phrase)
        extract_operand(inst, 2, inst_r_set)
    return [inst_feature, tuple(inst_r_set), tuple(inst_w_set)]


# return address of the fucntion called by inst_addr
# make sure inst_addr is CALL instruction
def called_func_addr(inst_addr):
    coderefs = list(CodeRefsFrom(inst_addr, 0))
    if len(coderefs) == 1:
        dest_func = idaapi.get_func(coderefs[0])
        if dest_func:
            return dest_func.start_ea
    return None


# When call_inst_addr is a call instruction, judge whether there is a return value
# At present, I just look down at the two instructions to see if I can read RETURN_REG
def is_return(call_inst_addr):
    FORWARD_COUNT = 3
    if called_func_addr(call_inst_addr):
        inst_addr = next_head(call_inst_addr)
        for i in range(FORWARD_COUNT):
            inst = idautils.DecodeInstruction(inst_addr)
            if not inst:
                return False
            inst_feature = inst.get_canon_feature()
            inst_r_set = set()
            if inst_feature & ida_idp.CF_USE1:
                extract_operand(inst, 0, inst_r_set)
            if inst_feature & ida_idp.CF_USE2:
                extract_operand(inst, 1, inst_r_set)
            if inst_feature & ida_idp.CF_USE3:
                extract_operand(inst, 2, inst_r_set)
            if RETURN_REG in inst_r_set:
                return True
            else:
                inst_addr = next_head(inst_addr)
    return False


def guess_function_argument(func_addr):
    # At present, this function is written for arm32 fastcall
    func_name = get_func_name(func_addr)
    # >>>>>>>> get_type is used to obtain the import function parameter information that IDA Pro can infer
    func_type = get_type(func_addr)
    if func_type:
        if "..." in func_type or "(void)" in func_type:
            argu_num = 0
        else:
            argu_num = len(func_type.split(","))
        return argu_num
    # >>>>>>>> Used to get the parameter information of sub_xxx
    if func_name not in import_funcs:
        try:
            flowchart = idaapi.FlowChart(idaapi.get_func(func_addr))
        except Exception:
            return 0

        def has_regname(inst_addr, regname):
            for i in range(7):
                op_str = print_operand(inst_addr, i)
                if op_str == regname:
                    return True
            return False

        def calc_argu_num(start_inst_addr, end_inst_addr):
            argu_num = 0
            while start_inst_addr < end_inst_addr:
                inst_r_set = extract_inst_rw_set(start_inst_addr)[1]
                inst_r_regnames = [get_reg_name(i) for i in inst_r_set if isinstance(i, int)]
                if ARGU_REGS[argu_num] in inst_r_regnames and has_regname(start_inst_addr, ARGU_REGS[argu_num]):
                    argu_num += 1
                else:
                    return argu_num
                start_inst_addr = next_head(start_inst_addr)
            return argu_num
        for bb in flowchart:
            for inst_addr in Heads(bb.start_ea, bb.end_ea):
                if has_regname(inst_addr, "R0"):
                    return calc_argu_num(inst_addr, bb.end_ea)
    # >>>>>>>>> Custom import function, IDA Pro cannot infer from the open source library, solved by merge_strand_by_arguments()
    return -1


all_func_argu_num = dict()
for func_addr in Functions():
    if get_func_name(func_addr).startswith("__imp_"):
        continue
    all_func_argu_num[func_addr] = guess_function_argument(func_addr)
# DecodeInstruction() insn_t: https://www.hex-rays.com/products/ida/support/sdkdoc/classinsn__t.html
# get_canon_feature() : https://www.hex-rays.com/products/ida/support/sdkdoc/group___c_f__.html
# Op1, Op2 op_t: https://www.hex-rays.com/products/ida/support/sdkdoc/classop__t.html


# Extract the read / write information of each instruction in this function
def extract_rw_set(flowchart):
    func_rw_set = dict()
    for bb in flowchart:
        for inst_addr in Heads(bb.start_ea, bb.end_ea):
            func_rw_set[inst_addr] = extract_inst_rw_set(inst_addr)
    return func_rw_set


# ------------------------ static taint ----------------------------------------

def static_taint(flowchart, func_rw_set, source_inst, sink_inst):
    source_bb = None
    for bb in flowchart:
        if source_inst in list(Heads(bb.start_ea, bb.end_ea)):
            source_bb = bb
    if source_bb == None:
        return None

    def update_source(inst_address, func_rw_set, source_to_sink_insts, sources):
        inst_rw_item = func_rw_set[inst_address]
        inst_r_set = inst_rw_item[1]
        inst_w_set = inst_rw_item[2]

        # If the instruction reads the source, the taint propagates and the propagation path is recorded
        # If you write source, Remove stains
        for source_data in sources.copy():
            if source_data in inst_r_set:
                sources.update(inst_w_set)
                source_to_sink_insts.append(inst_address)
            elif source_data in inst_w_set:
                sources.remove(source_data)

    source_set = set()  # source_set records all current sources
    source_set.update(func_rw_set[source_inst][2])

    # record instructions that taints pass by
    source_to_sink_insts = [source_inst, ]
    for inst_addr in Heads(source_inst+1, source_bb.end_ea):
        update_source(inst_addr, func_rw_set, source_to_sink_insts, source_set)

    bb_state = dict()  # This variable records the relation of base block and its source_set, which will be used in backtracking
    for bb in flowchart:
        bb_state[bb.start_ea] = None

    bb_state[source_bb.start_ea] = source_set.copy()
    print("init source_set: ", end="")
    print(source_set)

    # The path from source to sink can be divided into two types: basic block path and instruction path
    sanitizer_path = []
    import queue
    bb_q = queue.Queue()
    for succ_bb in source_bb.succs():
        bb_q.put(([source_bb], source_to_sink_insts, succ_bb))

    while not bb_q.empty():
        pred_path, ss_insts, this_bb = bb_q.get()

        source_set = bb_state[pred_path[-1].start_ea].copy()

        if not source_set:
            continue
        pred_path.append(this_bb)

        print("explore path: ", end="")
        for b in pred_path:
            print(hex(b.start_ea)+" ", end="")
        print()

        find_one_flag = False
        for inst_addr in Heads(this_bb.start_ea, this_bb.end_ea):
            update_source(inst_addr, func_rw_set, ss_insts, source_set)
            if inst_addr == sink_inst:
                print(" find ONE")
                find_one_flag = True
        if find_one_flag:
            sanitizer_path.append((pred_path[:], ss_insts[:]))
            continue
        if bb_state[this_bb.start_ea]:
            if source_set == bb_state[this_bb.start_ea]:
                continue

        bb_state[this_bb.start_ea] = source_set
        for succ_bb in this_bb.succs():
            bb_q.put((pred_path[:], ss_insts[:], succ_bb))

    # for bb_path, inst_path in sanitizer_path:
    #     print("bb_path: ", end="")
    #     for b in bb_path:
    #         print(hex(b.start_ea)+" ", end="")
    #     print()
    #     print("inst_path: ", end="")
    #     for i in inst_path:
    #         print(hex(i)+" ", end="")
    #     print()
    return sanitizer_path


def taint_start():
    source_addr = 0x04069A0
    sink_addr = 0x04069FE

    func_addr = get_func_attr(source_addr, FUNCATTR_START)
    func_name = get_func_name(func_addr)
    function = idaapi.get_func(func_addr)
    flowchart = idaapi.FlowChart(function, flags=idaapi.FC_PREDS)
    func_rw_set = extract_rw_set(flowchart)

    print("-----------taint_start-------------")
    sanitizer_path = static_taint(flowchart, func_rw_set, source_addr, sink_addr)

    print("-------result----------------")
    path_num = 0
    for _, ss_insts in sanitizer_path:
        for i in ss_insts:
            disasm_line = hex(i)+": " + generate_disasm_line(i, 0)
            print(disasm_line)
        print('--------------')
        path_num += 1


if __name__ == '__main__':
    taint_start()
