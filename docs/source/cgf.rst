.. See LICENSE.incore for details

.. _cgf:

=================
CGF Specification
=================

A cgf file is a file which is written in the *yaml* format. The higher level node type in a cgf file is a dictionary. 

Covergroup
==========
A covergroup is a dictionary based on the following template. These dictionaries constitute the nodes in a cgf file. Each cover group contains the following type of coverpoints:

* Opcode
* Register
* Register Operand Combinations
* Register/Immediate Value Combinations
* Control and Status Registers Value Combinations

Template
--------

The template for defining a covergroup is as follows:

.. code-block:: yaml

    <label>:
        config:
            - <config-str>
        opcode:
            <opcode-str>: 0
            <opcode-str>: 0
            ...
        rs1:
            <reg-str>: 0
            <reg-str>: 0
            ...
        rs2:
            <reg-str>: 0
            <reg-str>: 0
            ...
        rd:
            <reg-str>: 0
            <reg-str>: 0
            ...
        op_comb:
            <opcomb-str>: 0
            <opcomb-str>: 0
            ...
        val_comb:
            <valcomb-str>: 0
            <valcomb-str>: 0
            abstract_comb:
                <abscomb-str>: 0
                <abscomb-str>: 0
            ...
        csr_comb:
            <csrcomb-str>: 0
            <csrcomb-str>: 0
           

    
Explanation
-----------
The key corresponding to identifying a covergroup uniquely in the cgf is called the *label*. Nodes labelled as *datasets* will be ignored and not be treated as covergroups. This node can be used to define aliases and anchors to enable easy maintenance and keep the cgf file small.

A covergroup contains the following nodes:

* **config**
    *This node is optional.*
    
    This node specifies the configurations under which this particular covergroup is applicable. This node exists to enable correct *RVTEST_CASE* macro generations and covergroup filtering in reports produced by `riscof`_.

        * **config-str**
            The format followed is similar to the `RVTEST_CASE Condition Formating`_ followed in `riscof`_.


.. _RVTEST_CASE Condition Formating: https://riscof.readthedocs.io/en/latest/testformat.html?highlight=Macro#rvtest-case-condition-formating  
.. _riscof: https://riscof.readthedocs.io/en/latest/index.html 

* **opcode**
    *This node is mandatory for all covergroups except covergroups pertaining to CSR coverpoints (it's optional in this case).*
    
    This node describes the *opcode coverpoints* necessary for the covergroup. Each *opcode* is treated as a valid coverpoint and the arguments of the corresponding instruction are used to update the rest of the coverpoint types.  

        * **opcode-str**
            A valid *opcode* in the RISCV Instruction Set.

* **rs1**
    *This node is optional.*

    This node describes the *register coverpoints* for the *rs1* field in instructions. If the opcode of an instruction is present in the *opcode* node, its *rs1* field is used to evaluate the coverpoints in this node. 

        * **reg-str**
            This string correspond to a valid RISCV register. 

            Note - ABI register names aren't supported currently.

* **rs2**
    *This node is optional.*
    
    This node describes the *register coverpoints* for the *rs2* field in instructions. If the opcode of an instruction is present in the *opcode* node, its *rs2* field is used to evaluate the coverpoints in this node. 

        * **reg-str**
            This string correspond to a valid RISCV register. 

            Note - ABI register names aren't supported currently.

* **rd**
    *This node is optional.*
    
    This node describes the *register coverpoints* for the *rd* field in instructions. If the opcode of an instruction is present in the *opcode* node, its *rd* field is used to evaluate the coverpoints in this node. 

        * **reg-str**
            This string correspond to a valid RISCV register. 

            Note - ABI register names aren't supported currently.

* **op_comb**
    *This node is optional.*

    This node describes the *register operand combination coverpoints* for the covergroup. The field values in the eligible instructions are available for use to describe the coverpoints.

        * **opcomb-str**  
            This string is interpreted as a valid python statement/expression which evaluates to a Boolean value. The variables available for use in the expressions are as follows:
                
                * ``rs1`` : The register number specified in the *rs1* field of the instruction.
                * ``rs2`` : The register number specified in the *rs2* field of the instruction.
                * ``rd`` : The register number specified in the *rd* field of the instruction.

            Along with the above mentioned variables any valid python comparison operators can be used. A few example coverpoints are elaborated below.

            **Examples**
        
            1. A coverpoint where the source and destination registers have to be same.
            
                .. code-block:: python
    
                    rs1 == rs2 == rd

            2. A coverpoint where the destination register is a specific register(x10).
    
                .. code-block:: python

                    rd == 10

            3. A coverpoint where the destination register and the first source register have to be specific registers(x12 and x14).

                .. code-block:: python

                    rs1 == 14 and rd == 12

            4. A coverpoint where one of the source registers has to be same as the destination register.

                .. code-block:: python
                    
                    rs1 == rd or rs2 == rd

* **val_comb**
    *This node is optional.*
    
    This node describes the *register/immediate value combination coverpoints* for the covergroup. The values of the registers specified in the instruction or the value specified immediate field of the instruction are available for use to describe the coverpoints.

        * **valcomb-str**  
            This string is interpreted as a valid python statement/expression which evaluates to a Boolean value. The variables available for use in the expression are as follows:
                
                * ``rs1_val`` : The value(as of the end of previous instruction) in the register specified in the *rs1* field of the instruction.
                * ``rs2_val`` : The value(as of the end of previous instruction) in the register specified in the *rs2* field of the instruction.
                * ``imm_val`` : The value in the *immediate* field of the instruction.
                * ``ea_align`` : The alignment of the effective address calculated(for relevant instructions). It is calculated according to the instruction in consideration.

            Along with the above mentioned variables any valid python comparison operators can be used. A few example coverpoints are elaborated below.

            **Examples**
        
            1. A coverpoint where the value in both of the source registers are the same.
            
                .. code-block:: python
    
                    rs1_val == rs2_val

            2. A coverpoint where the immediate value is specific(32) and the effective address alignment is 4.
    
                .. code-block:: python

                    imm_val == 32 and ea_align == 4

            3. A coverpoint where the value in both the source registers are specific(1024 and 10).

                .. code-block:: python

                    rs1_val == 1024 and rs2_val == 0x0a
            
            Note: Hexadecimal numbers can be used by using the prefix ``0x`` before the hex string.

        * **abstract_comb**
            *This node is optional.*

            This node contains functions/lists which are evaluated to produce coverpoints of the type *register/immediate value combination*.

            * **abscomb-str**
                This string is interpreted as a valid python statement/expression which evalates to a list of coverpoints of type *register/immediate value combination*. The expression can be a valid list comprehension or a function call for a set of predefined funtions which return a list. The function prototypes of the predefined functions and their uses are listed below. 

                    * ``walking_ones(var, size, signed=True, fltr_func=None, scale_func=None)`` 
                        
                        This function generates a set of values based on a walking one pattern.

                            * **var**
                                The name of the variable which should be present in the coverpoint. Any valid variables avaliable in the *valcomb-str* can be specified here.
                            * **size**
                                The bit-width of the values to be generated.
                            * **signed**
                                Whether the binary value of width *bit-width* should be interpreted as a signed(Twos complement) or unsigned.
                            * **fltr_func**
                                A lambda function which takes an integer and returns a boolean value. This function is used to filter the output set after scaling. 
                            * **scale_func**
                                A lambda function which takes an integer and returns an integer. This function is used to scale the generated values.

                    * ``walking_zeros(var, size, signed=True, fltr_func=None, scale_func=None)``
                        
                        This function generates a set of values based on a walking zero pattern.

                            * **var**
                                The name of the variable which should be present in the coverpoint. Any valid variables avaliable in the *valcomb-str* can be specified here.
                            * **size**
                                The bit-width of the values to be generated.
                            * **signed**
                                Whether the binary value of width *bit-width* should be interpreted as a signed(Twos complement) or unsigned.
                            * **fltr_func**
                                A lambda function which takes an integer and returns a boolean value. This function is used to filter the output set after scaling. 
                            * **scale_func**
                                A lambda function which takes an integer and returns an integer. This function is used to scale the generated values.

                    * ``alternate(var, size, signed=True, fltr_func=None,scale_func=None)``
                        
                        This function generates a set of values based on a checkerboard pattern.

                            * **var**
                                The name of the variable which should be present in the coverpoint. Any valid variables avaliable in the *valcomb-str* can be specified here.
                            * **size**
                                The bit-width of the values to be generated.
                            * **signed**
                                Whether the binary value of width *bit-width* should be interpreted as a signed(Twos complement) or unsigned.
                            * **fltr_func**
                                A lambda function which takes an integer and returns a boolean value. This function is used to filter the output set after scaling. 
                            * **scale_func**
                                A lambda function which takes an integer and returns an integer. This function is used to scale the generated values.

                Note: The variable ``xlen`` can be used in expressions to refer to the system width.

                **Examples**

                1. Walking ones for an unsigned immediate field 6 bits wide.

                    .. code-block:: python
                        
                        walking_ones("imm_val",6,signed=False)

                2. Walking zeroes for an signed immediate field 12 bits wide.

                    .. code-block:: python
                        
                        walking_zeros("imm_val",12)

                3. Checkerboard pattern for the first source register where a valid value is only a multiple of 4 and the values are interpreted as signed numbers.
                
                    .. code-block:: python

                        alternate("rs1_val", xlen-2, scale_func = lambda x: x * 4)

                4. The value of the first source register is a multiple of 2 and not a multiple of 8.


                    .. code-block:: python

                        ["rs1_val=="+str(x) for x in filter(lambda x:x%8!=0,range(2,xlen,2))]
* **csr_comb**
    *This node is optional.*
    
    This node describes the *CSRs value combination coverpoints* for a covergroup. ISAC maintains a copy of the architectural csrs, which thereby allows the user to describe the coverpoints based on csrs and their values. All the *Machine level* and *Supervisor level* CSRs are currently supported. If for a particular covergroup, the opcode node is present/not-empty, then the CSR coverpoints are evaluated and updated only for instructions in the log whose opcode matches. If however, the opcode node is not-present/empty in a covergroup, then the csrs coverpoints are evaluated and updated for any event/instruction. 

        * **csrcomb-str**  
            This string is interpreted as a valid python statement/expression which evaluates to a Boolean value. The variables available for use in the expression are as follows:
                
                * ``csr_name`` : The value (as of the end of previous instruction) in the CSR whose name is specified by csr_name.

                * ``xlen`` : The length of the regsiters in the machine.

            Along with the above mentioned variable any valid python comparison operators can be used. An example coverpoint is elaborated below.

            .. note:: The csr coverage reporting is accurate only if a change in the csr is captured in the log.    

            .. tip:: Bit masks and shifts can be used to access the subfields in the csrs. 

            **Examples**
        
            1. A coverpoint where the value in *mcycle* register is 0.
            
                .. code-block:: python
    
                    mcycle == 0x0
                    
            Note: Hexadecimal numbers can be used by using the prefix ``0x`` before the hex string.

            2. A coverpoint which checks whether the *mxl* field of *misa* register is 1.
        
                .. code-block:: python

                    misa >> (xlen-2) == 0x01

            3. A coverpoint which checks whether the *mie* field of *mstatus* register is 1.

                .. code-block:: python

                    mstatus && (0x8) == 0x8



